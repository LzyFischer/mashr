"""Slow loop (RSI, v8): the evolver (27B) edits three layers: the task agents' self harnesses (roles),
the meta-harness (rules) and the skill and tool libraries the residual harness is drawn from; on every
problem the meta-agent writes the team and gives each node its residual harness (org.py, engine.py).
Story: the evolver learns which parts are general (roles) and which vary per problem (skills, tools,
the rules for giving them); the meta-agent fills in the varying part on each problem.

The evolver prompt follows AHE (Agentic Harness Engineering) and RRSI: evidence first, the layer that
fits the root cause, hard generality constraints and an annealed edit budget. The evidence is an
analysis, not raw traces (debugger.py, after AHE's Agent Debugger): every wrong dev-A problem is
diagnosed from its full run (failing node, step, error type, root cause, a verified excerpt, fix
direction), and the diagnoses are grouped into key weaknesses. There is no history of past rounds in
the prompt; the report says what the last accepted change fixed and broke on dev-A and which of the
problems its changes cited were fixed. Skills and tools are added or edited, never removed.

  scripts/run.sh math <name> --objective acc [...]      # task agents + meta-agent on local vLLM, evolver on Tinker

Start (--start): minimal (default; one agent with a one-sentence role, no rules, the hand-written
libraries) or hand (the task's hand-written SEED), or --init-pool. Test baselines use the hand SEED. Each round: dev-A run -> report -> K candidates, each
limited to layers (self / residual / both) -> gate on dev-B.
--objective acc: the most accurate candidate on dev-B wins (cost breaks ties among candidates) if it is
strictly more accurate than the incumbent; otherwise the incumbent stays (a tie is not accepted).
--objective cost (needs --init-pool; phase 2): floor = the starting organization's dev-B acc - delta.
A candidate is admissible if acc >= floor and acc >= the best accepted acc so far - delta; among the
incumbent and the admissible candidates H = the most accurate (ties: cheaper); the winner is the
cheapest whose acc >= H's - delta and whose cost <= (1 - tau) x H's, else H.
A residual ablation of skills / tools (--abl-n) is saved per round (round_N/ablation.json) for
analysis and is not shown to the evolver.
"""
import argparse
import copy
import json
import os
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

from . import ROOT, debugger, tasks
from .engine import Engine, cost
from .ledger import Ledger
from .llm import LLM, THINK_BUDGET
from .org import (LIMITS, apply_ops, example, meta_prompt, minimal_seed, parse_program, program_str, shape,
                  skills_of, tools_of, validate, with_libs)
from .sandbox import run_python

BIG = "Qwen/Qwen3.8-27B"
BIG_CTX = int(os.environ.get("MASHR_EVOLVER_CTX", 65536))   # the evolver's context window on Tinker
PROPOSE_TOKENS = 8000                                        # the evolver's answer budget (max_tokens)
# llm._sample with thinking "high" asks for THINK_BUDGET["high"] + max_tokens and, if the answer runs out,
# continues it once with max_tokens more: the prompt must leave room for both
PROPOSE_RESERVE = THINK_BUDGET["high"] + 2 * PROPOSE_TOKENS
REPAIR_REPLY_CHARS = 6000                                    # of the failed reply, kept in the repair turn
TOL = 1e-9
WORKERS = 128
TASK = None          # the task module, set in main()
# candidate i may edit LAYERS[i % 3]: the self harness, the residual side, both
LAYERS = [("task-agent",), ("meta-agent", "library"), ("task-agent", "meta-agent", "library")]

REPAIR = """Your output could not be used:
{errors}

Output the corrected complete JSON between <{tag}> and </{tag}>."""


def pct(xs):
    return f"{sum(xs) / len(xs):.0%}" if xs else "-"


def ask_json(llm, prompt, tag, check, seed, max_tokens=4096):
    """(object, check result, repairs), or (None, None, 2). A failed call (e.g. over the context window)
    makes this candidate invalid; it never ends the run."""
    msgs = [{"role": "user", "content": prompt}]
    for attempt in range(2):
        try:
            txt = llm.chat(BIG, msgs, thinking="high", max_tokens=max_tokens, seed=seed + attempt).text
        except Exception as e:                     # noqa: BLE001
            check({"_call_error": f"{type(e).__name__}: {str(e)[:300]}"})
            return None, None, 2
        m = re.search(rf"<{tag}>(.*?)</{tag}>", txt, re.S)
        try:
            obj = json.loads(m.group(1)) if m else None
            errs = [f"no <{tag}> block"] if obj is None else []
        except json.JSONDecodeError as e:
            obj, errs = None, [f"bad JSON: {e}"]
        if obj is not None:
            res, errs = check(obj)
            if not errs:
                return obj, res, attempt
        reply = txt if len(txt) <= REPAIR_REPLY_CHARS else "[...]\n" + txt[-REPAIR_REPLY_CHARS:]
        msgs += [{"role": "assistant", "content": reply},
                 {"role": "user", "content": REPAIR.format(errors="\n".join(errs[:15]), tag=tag)}]
    return None, None, 2


def gate(inc, cands, floor, anchor, delta, tau):
    """Index of the winning candidate, or None to keep the incumbent. inc/cands: summaries."""
    orgs = [inc] + list(cands)
    feas = [i for i, s in enumerate(orgs) if s["acc"] >= floor - TOL]
    if not feas:                                         # nobody at the floor yet: accuracy first
        best = max(range(len(orgs)), key=lambda i: (orgs[i]["acc"], -orgs[i]["cost"]))
        return None if best == 0 or orgs[best]["acc"] <= inc["acc"] + TOL else best - 1
    adm = [i for i in feas if i == 0 or orgs[i]["acc"] >= anchor - delta - TOL]
    if inc["acc"] < floor - TOL:                         # an infeasible incumbent is not compared
        adm = [i for i in adm if i != 0] or [0]
    h = max(adm, key=lambda i: (orgs[i]["acc"], -orgs[i]["cost"]))
    cheap = [i for i in adm if orgs[i]["acc"] >= orgs[h]["acc"] - delta - TOL
             and orgs[i]["cost"] <= (1 - tau) * orgs[h]["cost"]]
    win = min(cheap, key=lambda i: orgs[i]["cost"]) if cheap else h
    return None if win == 0 else win - 1


def evaluate(eng, pool, items, plan=None):
    def one(it):
        if plan is not None:
            p, pre, info = plan, [], {"problems": [], "fallback": False}
        else:
            p, pre, info = eng.orchestrate(pool, it)
        out = eng.run(pool, it, p)
        calls = pre + out["calls"]
        return {**it, "plan": p, "nodes": out["nodes"], "pred": out["answer"],
                "correct": TASK.grade(out["answer"], it), "calls": calls, "cost": cost(calls),
                "meta_cost": cost(pre), **info}
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(one, items))


def summarize(rows):
    n = len(rows)
    hard = [r for r in rows if r["hard"]]
    return {"n": n, "acc": round(sum(r["correct"] for r in rows) / n, 4),
            "cost": round(sum(r["cost"] for r in rows) / n, 1),
            "meta_cost": round(sum(r["meta_cost"] for r in rows) / n, 1),
            "acc_hard": round(sum(r["correct"] for r in hard) / max(1, len(hard)), 4),
            "nodes": round(sum(len(r["plan"]["nodes"]) for r in rows) / n, 2),
            "shapes": dict(Counter(shape(r["plan"]) for r in rows).most_common(4)),
            "n_shapes": len({shape(r["plan"]) for r in rows}),
            "fallback": sum(r["fallback"] for r in rows)}


def flips(before, after):
    """(fixed, broken) item ids between two evaluations of the same items."""
    was = {r["id"]: r["correct"] for r in before}
    fixed = [r["id"] for r in after if r["correct"] and not was.get(r["id"], True)]
    broken = [r["id"] for r in after if not r["correct"] and was.get(r["id"], False)]
    return fixed, broken


def residual_ablation(eng, pool, rows, n):
    """Re-run up to n questions with one residual component removed from every node: the skills or
    the tools (no tools = no Python). Returns {component: [(was, now)]}."""
    sample = [r for r in rows if any(nd["skills"] or nd["tools"] for nd in r["plan"]["nodes"])][:n]
    jobs = [(r, comp, {**r["plan"], "nodes": [{**nd, comp: []} for nd in r["plan"]["nodes"]]})
            for r in sample for comp in ("skills", "tools") if any(nd[comp] for nd in r["plan"]["nodes"])]

    def one(job):
        r, comp, p = job
        out = eng.run(pool, r, p)
        return comp, r["correct"], TASK.grade(out["answer"], r)
    res = defaultdict(list)
    with ThreadPoolExecutor(WORKERS) as ex:
        for comp, was, now in ex.map(one, jobs):
            res[comp].append((was, now))
    return dict(res), len(sample)


def report(rows, pool, since=None, last_change="", analysis="") -> str:
    """since: (fixed, broken) dev-A item ids of the last accepted change, or None; last_change: which of
    its changes' cited problems were fixed; analysis: the debugger's section on the wrong problems."""
    s = summarize(rows)
    lab = {r["id"]: r["label"] for r in rows}
    L = ["# Report (dev-A)", "",
         f"Organization: acc {s['acc']:.1%} (meta-agent prompt {len(meta_prompt(TASK, pool))} chars; "
         f"roles {sum(len(a['role']) for a in pool['agents'].values())} chars). {s['n_shapes']} distinct "
         f"architectures, {s['nodes']:.1f} nodes per problem. Fallback (unusable meta-agent output): "
         f"{s['fallback']}.", ""]
    if since is not None:
        fixed, broken = since
        L += ["## Since the last accepted change (same dev-A problems)",
              f"Fixed ({len(fixed)}): {' '.join(lab[i] for i in fixed) or '-'}",
              f"Broken ({len(broken)}): {' '.join(lab[i] for i in broken) or '-'}"
              + (" <- regressions: address these first" if broken else ""), last_change, ""]
    L += ["## By category", "| category | n | acc | architectures |", "|---|---|---|---|"]
    by = defaultdict(list)
    for r in rows:
        by[r["bucket"]].append(r)
    for b in sorted(by):
        rs = by[b]
        L.append(f"| {b} | {len(rs)} | {pct([r['correct'] for r in rs])} | "
                 + ", ".join(f"{k} {v}" for k, v in Counter(shape(r['plan']) for r in rs).most_common(3))
                 + " |")
    arch = defaultdict(list)
    for r in rows:
        arch[shape(r["plan"])].append(r)
    L += ["", "## Architectures", "| architecture | uses | acc |", "|---|---|---|"]
    for k, rs in sorted(arch.items(), key=lambda kv: -len(kv[1]))[:15]:
        L.append(f"| {k} | {len(rs)} | {pct([r['correct'] for r in rs])} |")
    nodes = defaultdict(lambda: [0, 0, 0, [], 0, 0, 0])
    for r in rows:
        ans = {nd["id"]: nd["answer"] for nd in r["nodes"]}
        for pn, nd in zip(r["plan"]["nodes"], r["nodes"]):
            g = nodes[nd["agent"] + (" (with inputs)" if pn["inputs"] else "")]
            g[0] += 1
            g[1] += TASK.grade(nd["answer"], r)
            g[2] += nd["cut"]
            g[3].append(nd["cost"])
            if pn["inputs"]:
                before = Counter(ans[i] for i in pn["inputs"]).most_common(1)[0][0]
                if nd["answer"] != before:
                    g[4] += 1
                    g[5] += TASK.grade(nd["answer"], r)
                    g[6] += TASK.grade(before, r)
    L += ["", "## Task agents",
          "answer correct = the node's own answer; cut = its output hit the token limit; for nodes with "
          "inputs: changed = its answer differs from its inputs' majority.",
          "| agent | uses | answer correct | cut | changed | to correct | to wrong |",
          "|---|---|---|---|---|---|---|"]
    for k, g in sorted(nodes.items(), key=lambda kv: -kv[1][0]):
        L.append(f"| {k} | {g[0]} | {g[1] / g[0]:.0%} | {g[2] / g[0]:.0%} | "
                 f"{g[4] or '-'} | {g[5] or '-'} | {g[6] or '-'} |")
    pairs = [(r, nd, pn) for r in rows for nd, pn in zip(r["nodes"], r["plan"]["nodes"])]
    items = Counter()
    for _, _, pn in pairs:
        items.update([f"tool:{t}" for t in pn["tools"]] + [f"skill:{k}" for k in pn["skills"]]
                     + (["no tools (no Python)"] if not pn["tools"] else []))
    L += ["", "## Residual harness (what the meta-agent gave each node)",
          "| item | nodes given it | node answer correct when given | otherwise |", "|---|---|---|---|"]
    for it, cnt in items.most_common(30):
        has = lambda pn: (it == "no tools (no Python)" and not pn["tools"]) or \
            (it.startswith("tool:") and it[5:] in pn["tools"]) or \
            (it.startswith("skill:") and it[6:] in pn["skills"])
        yes = [TASK.grade(nd["answer"], r) for r, nd, pn in pairs if has(pn)]
        no = [TASK.grade(nd["answer"], r) for r, nd, pn in pairs if not has(pn)]
        L.append(f"| {it} | {cnt} | {pct(yes)} | {pct(no)} |")
    unused = [t for t in tools_of(TASK, pool) if f"tool:{t}" not in items] + \
        [k for k in skills_of(TASK, pool) if f"skill:{k}" not in items]
    if unused:
        L.append(f"Never given: {', '.join(unused)}.")
    probs = Counter(p for r in rows for p in r["problems"])
    if probs:
        L += ["", "Meta-agent output problems: " + "; ".join(f"{k} ({v})" for k, v in probs.most_common(6))]
    L += ["", analysis]
    return "\n".join(L)


OBJECTIVE = {
    "acc": "Objective: maximize accuracy on held-out problems.",
    "keep": "Objective: minimize the average cost per problem while keeping accuracy at the level the "
            "current organization already reaches (at most {delta:.1%} below the best accuracy so far "
            "on held-out problems). The organization was already optimized for accuracy; now find "
            "where it spends more than it needs."}

LAYER_NOTE = {("task-agent",): "This candidate may edit only the self harness: the task-agent layer.",
              ("meta-agent", "library"): "This candidate may edit only the residual side: the meta-agent "
                                         "and library layers.",
              ("task-agent", "meta-agent", "library"): "This candidate may edit all three layers."}

TOOL_OPS_CODE = """{{"op": "add_tool", "name": "<name>", "doc": "<signature and what it prints or returns>", "code": "<Python source defining it>", "test": "<Python asserts; must pass>"}}
{{"op": "edit_tool", "name": "<name>", "doc": "<optional>", "code": "<optional>", "test": "<optional>"}}
{tool_env} A new or edited tool is run with its test first; if the test fails, the candidate is sent back."""
TOOL_OPS_FIXED = "(The tools of this task are built-in aids: they cannot be added or edited.)"

PROPOSE = """You improve a multi-agent system whose task agents {team}, by editing its harnesses.
The model (a 9B LLM, no thinking for task agents) is fixed.

# The system
For each {item} the meta-agent (the 9B model, guided by its meta-harness) writes a team as code:
{example}
Each line is a task agent with its self harness (its role) and the residual harness the meta-agent
gives it for this {item}: tools ({tools_kind}) and skills (how-to texts), chosen from the libraries
below. {system_note} Nodes without inputs run in parallel. {final} The meta-agent does not do the
{item} itself. Unusable output -> the first task agent alone with {fallback} (fixed).

# Self vs residual
A role is the same on every {item}, so it can hold only practices that help on every {item} that agent
works on. Whatever helps only some {item}s (a method, a check, domain knowledge, a helper function)
belongs to the residual side: a skill or a tool, plus a meta-harness rule that says when to give it.
You learn which parts are general and which vary per {item}; the meta-agent fills in the varying part
on each {item}. Before putting a sentence into a role, ask: is it right for every {item} this agent
sees? If not, make it a skill or a tool and a rule. Conversely, a skill the meta-agent gives to nearly
every node of an agent can move into that agent's role.

# What you edit: three layers
| layer | side | what | effect |
|---|---|---|---|
| task-agent | self | add, remove or edit a task agent (its role) | always on for that agent |
| meta-agent | residual | add, edit or remove a rule of the meta-harness | how the meta-agent staffs, wires and equips teams |
| library | residual | add or edit a skill{or_tool} (never removed) | what the meta-agent can give; a new item has no effect until the meta-agent gives it |
The model, the answer format and the grader are fixed.

# Principles
- Evidence first: each change targets a key weakness in the report (which problems, which node, which
  step went wrong, why), not a general best practice.
- Choose the layer that fits the root cause (see Self vs residual): a practice an agent should always
  follow -> its role; whom to staff, how to wire, which tools and skills -> a meta-harness rule;
  knowledge or a helper that only some {item}s need -> a skill or tool and a rule.
- Regressions first: if the last accepted change broke problems, find out why before adding more.
- If the last change did not fix the problems it cited, revert it and try another layer.
- Few, decisive changes. Remove rules and agents the evidence does not support. Skills and tools are
  never removed: an unhelpful one is fixed by editing it or by the rules that say when to give it.

# Generality (hard constraints)
- Held-out {item}s are different {item}s of the same kind. Write nothing that only fits one {item} in
  this report: no answers, constants, entity, table or column names, or wording copied from a report
  {item}. A rule must name a class of {item}s that can be recognized from the {item} text alone.
- Target patterns shared by several wrong {item}s (cite them in evidence), not a single failure.
- No ban lists or name lists ("never give X", "only these tools") unless the cited failures were
  caused by X.
- Prefer removing, merging or shortening rules and roles over adding; if a new rule overlaps an old
  one, edit the old one. Every role, rule and skill costs tokens on each {item}, and a 9B model follows long
  instructions less reliably.
- A tool is a general helper (compute, check, search, inspect) with a test. It must not contain an
  answer or a special case for one {item}.
- At most {max_ops} operations in this candidate (all changes together).

# Analysis
1. Read "Since the last accepted change" in the report: regressions first; keep what worked, revert
   what did not.
2. Read the key weaknesses and the one-line diagnoses of the wrong {item}s (each made from the full
   run): which node failed, at which step, why, and where the fix belongs. Diagnoses can be wrong:
   trust a weakness shared by several {item}s more than a single one.
3. Check which architectures, tools and skills help and which do not.

{objective}
{layer_note}

# Output
A JSON object between <edit> and </edit>:
{{"changes": [{{"pattern": "<the failure pattern, one sentence>",
               "rationale": "<its root cause in the traces, and why this layer and these ops fix it>",
               "evidence": ["<labels of the wrong dev-A {item}s that show this pattern, e.g. A12>"],
               "ops": [<edit operations, applied in order>]}}]}}
One change per failure pattern. If the candidate is accepted, the next round reports which of its
cited {item}s were fixed.

# Edit operations
task-agent layer:
{{"op": "add_agent", "name": "<name>", "role": "<role>"}}
{{"op": "remove_agent", "name": "<name>"}}
{{"op": "edit_agent", "name": "<name>", "role": "<new role>"}}
meta-agent layer (rule numbers as shown below; new rules are appended):
{{"op": "add_rule", "text": "<rule>"}}
{{"op": "edit_rule", "rule": <number>, "text": "<new rule>"}}
{{"op": "remove_rule", "rule": <number>}}
library layer:
{{"op": "add_skill", "name": "<name>", "when": "<when to give it (shown to the meta-agent)>", "text": "<the procedure (shown to the task agent)>"}}
{{"op": "edit_skill", "name": "<name>", "when": "<optional>", "text": "<optional>"}}
{tool_ops}
At most {max_agents} task agents, {max_rules} rules, {max_skills} skills and {max_tools} tools. No rule may
mention a removed agent. Names: a letter, then letters, digits or underscores.

# Tools
{tools}

# Skills
{skills}

# Current organization
Task agents:
{agents}
Meta-harness:
{meta}

# Report
{report}

Output the JSON object between <edit> and </edit>."""


def propose_prompt(task, pool, rep, objective, layers, max_ops):
    m = task.META
    code = task.TOOLS_ARE_CODE

    def tool(t, v):
        s = f"- {t}: {v['doc']}"
        if code and v.get("code", "").strip():
            s += f"\n```python\n{v['code'].strip()}\n```"
        return s
    tool_ops = TOOL_OPS_CODE.format(tool_env=task.TOOL_ENV) if code else TOOL_OPS_FIXED
    return PROPOSE.format(
        team=m["team"], item=m["item"], example="\n".join("    " + l for l in example(task, pool)),
        tools_kind=m["tools"], system_note=task.SYSTEM_NOTE, final=m["final"],
        fallback=", ".join(task.FALLBACK_TOOLS) or "no tools", or_tool=" or a tool" if code else "",
        objective=objective, layer_note=LAYER_NOTE[layers],
        max_agents=LIMITS["agents"], max_rules=LIMITS["rules"], max_skills=LIMITS["skills"],
        max_tools=LIMITS["tools"], max_ops=max_ops, tool_ops=tool_ops,
        tools="\n".join(tool(t, v) for t, v in tools_of(task, pool).items()),
        skills="\n".join(f"- {k} (when: {v['when']}): {v['text']}" for k, v in skills_of(task, pool).items()),
        agents="\n".join(f"- {n}: {a['role']}" for n, a in pool["agents"].items()),
        meta="\n".join(f"{i}. {r}" for i, r in enumerate(pool["rules"], 1)),
        report=rep)


def check_edit(pool, o, layers, wrong, max_ops):
    """The evolver's <edit> object -> ((organization, changes), errors). wrong: labels of the wrong
    dev-A problems."""
    if isinstance(o, dict) and "_call_error" in o:
        return None, [f"evolver call failed: {o['_call_error']}"]
    if not isinstance(o, dict) or not isinstance(o.get("changes"), list) or not o["changes"]:
        return None, ['expected {"changes": [...]} with at least one change']
    errs, ops, changes = [], [], []
    for j, c in enumerate(o["changes"], 1):
        if not isinstance(c, dict):
            errs.append(f"change {j}: not an object")
            continue
        for f in ("pattern", "rationale"):
            if not isinstance(c.get(f), str) or not c[f].strip():
                errs.append(f"change {j}: {f!r} (a non-empty string) is required")
        ev = c.get("evidence", [])
        if not isinstance(ev, list) or not all(isinstance(x, str) for x in ev):
            errs.append(f"change {j}: evidence must be a list of labels")
            ev = []
        bad = [x for x in ev if x not in wrong]
        if bad:
            errs.append(f"change {j}: evidence {bad} are not labels of wrong dev-A problems in the report")
        if not isinstance(c.get("ops"), list) or not c["ops"]:
            errs.append(f"change {j}: 'ops' must be a non-empty list")
            continue
        ops += c["ops"]
        changes.append({"pattern": c["pattern"], "rationale": c.get("rationale", ""),
                        "evidence": [x for x in ev if x in wrong], "ops": c["ops"]})
    if len(ops) > max_ops:
        errs.append(f"{len(ops)} operations; at most {max_ops} in this candidate")
    if errs:
        return None, errs
    new, errs, changed = apply_ops(pool, ops, layers, code_tools=TASK.TOOLS_ARE_CODE)
    if errs:
        return None, errs
    for name in sorted(changed):
        t = new["tools"][name]
        out, ok = run_python(TASK.tool_prelude() + t.get("code", "") + "\n" + t["test"] + "\nprint('TEST OK')",
                             timeout=30)
        if not ok or "TEST OK" not in out:
            errs.append(f"tool {name!r}: its test failed:\n{out[-600:]}")
    return (None, errs) if errs else ((new, changes), [])


def verdicts(t, cand, fixed_labels, broken_labels):
    """History line for the candidate accepted in round t, from the next dev-A run (no extra cost):
    which of each change's cited problems were fixed (changes are measured together)."""
    L = [f"The last accepted change (round {t}, {'+'.join(cand['layers'])}):"]
    for j, ch in enumerate(cand["changes"], 1):
        ev = ch["evidence"]
        hit = [x for x in ev if x in fixed_labels]
        v = ("no evidence" if not ev else "EFFECTIVE" if len(hit) == len(ev)
             else "PARTIAL" if hit else "INEFFECTIVE")
        L.append(f"  change {j} [{v}" + (f": {len(hit)}/{len(ev)} cited fixed" if ev else "")
                 + (f" ({' '.join(hit)})" if hit else "") + f"]: {ch['pattern'][:200]}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["math", "bird", "alfworld", "humaneval_plus", "mbpp_plus", "hotpotqa", "twowiki"], default="math")
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--k", type=int, default=3, help="candidates per round; candidate i edits LAYERS[i % 3]")
    ap.add_argument("--delta", type=float, default=0.005)
    ap.add_argument("--tau", type=float, default=0.10)
    ap.add_argument("--meta-thinking", choices=list(THINK_BUDGET), default="medium",
                    help="the meta-agent's reasoning budget (medium = 2048 tokens; task agents: off)")
    ap.add_argument("--objective", choices=["cost", "acc"], default="acc",
                    help="acc: maximize accuracy (cost only breaks ties); cost: phase 2, needs --init-pool")
    ap.add_argument("--n-dev-a", type=int, help="default: the task's split size")
    ap.add_argument("--n-dev-b", type=int)
    ap.add_argument("--n-test", type=int)
    ap.add_argument("--abl-n", type=int, default=0, help="residual ablation questions per round (0 = off)")
    ap.add_argument("--max-ops", type=int, default=8,
                    help="edit budget of a candidate in round 1; annealed by 1 per round down to 3")
    ap.add_argument("--baselines", help="default: all of the task's baselines")
    ap.add_argument("--out", help="default: results/v8/<task>")
    ap.add_argument("--skip-test", action="store_true")
    ap.add_argument("--seed", type=int, default=0, help="sampling seed of the task agents, meta-agent and evolver")
    ap.add_argument("--init-pool", help="start from this organization (JSON); with --objective cost the floor "
                                         "is its own dev-B accuracy - delta")
    ap.add_argument("--start", choices=["minimal", "hand"], default="minimal",
                    help="without --init-pool: minimal = one agent with a one-sentence role, no rules, the "
                         "hand-written libraries (org.minimal_seed); hand = the task's hand-written SEED")
    a = ap.parse_args()
    if a.objective == "cost" and not a.init_pool:
        raise SystemExit("--objective cost keeps the accuracy of a starting organization: give --init-pool")
    global TASK
    TASK = tasks.get(a.task)
    a.out = a.out or os.path.join(ROOT, "results", "v8", a.task)
    os.makedirs(a.out, exist_ok=True)
    llm = LLM()
    eng = Engine(TASK, llm, seed=a.seed, meta_thinking=a.meta_thinking)
    dev_a, dev_b, test = TASK.load("dev_a", a.n_dev_a), TASK.load("dev_b", a.n_dev_b), TASK.load("test", a.n_test)
    for i, it in enumerate(dev_a, 1):
        it["label"] = f"A{i}"

    def log(msg):
        print(msg, flush=True)
        with open(os.path.join(a.out, "log.txt"), "a") as f:
            f.write(msg + "\n")

    def dump(name, obj):
        path = os.path.join(a.out, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(obj if isinstance(obj, str) else json.dumps(obj, indent=1))

    led = Ledger(llm, log)
    floor = 0.0
    log(f"task {a.task}: dev-A {len(dev_a)}, dev-B {len(dev_b)}, test {len(test)}; delta "
        f"{a.delta}, tau {a.tau}, meta-agent thinking {a.meta_thinking}, objective {a.objective}; "
        f"max ops {a.max_ops} (annealed); evidence: debugger analyses of the wrong dev-A problems")
    pool = with_libs(TASK, json.load(open(a.init_pool)) if a.init_pool else
                     TASK.SEED if a.start == "hand" else minimal_seed(TASK))
    errs = validate(pool)
    if errs:
        raise SystemExit(f"invalid organization: {errs}")
    log(f"starting organization: {a.init_pool or a.start + ' seed'}: agents {list(pool['agents'])}, "
        f"{len(pool['rules'])} rules, {len(pool['skills'])} skills, {len(pool['tools'])} tools")
    pool0 = copy.deepcopy(pool)
    dump("round_0/pool.json", pool)

    with led.stage("round 0 / dev-B eval"):
        inc_rows_b = evaluate(eng, pool, dev_b)
    inc_b = summarize(inc_rows_b)
    objective = OBJECTIVE["acc"]
    if a.objective == "cost":       # phase 2: keep the accuracy already reached
        floor, best_acc = inc_b["acc"] - a.delta, inc_b["acc"]
        objective = OBJECTIVE["keep"].format(delta=a.delta)
        objective += (f" Held-out dev-B: the starting organization has acc {inc_b['acc']:.1%}, cost "
                      f"{inc_b['cost']:.0f}; floor {floor:.1%}.")
        log(f"phase 2 (cost): floor on dev-B {floor:.3f}")
    else:
        best_acc = inc_b["acc"]
    log(f"round 0 incumbent dev-B {inc_b}")
    trace_log = [{"round": 0, "accepted": True, "dev_b": inc_b}]
    prev_rows_a, accepted_last = None, None      # accepted_last: the candidate accepted last round

    for t in range(1, a.rounds + 1):
        d = f"round_{t}"
        max_ops = max(3, a.max_ops - (t - 1))
        with led.stage(f"round {t} / dev-A eval"):
            rows_a = evaluate(eng, pool, dev_a)
        if a.abl_n:         # kept for our analysis; not shown to the evolver
            with led.stage(f"round {t} / residual ablation"):
                abl, abl_n = residual_ablation(eng, pool, rows_a, a.abl_n)
            dump(f"round_{t}/ablation.json", {"questions": abl_n, "results": {
                comp: {"uses": len(xs), "needed": sum(w and not n for w, n in xs),
                       "harmful": sum(n and not w for w, n in xs)} for comp, xs in abl.items()}})
        since = flips(prev_rows_a, rows_a) if accepted_last else None
        last_change = ""
        if since:
            lab = {r["id"]: r["label"] for r in rows_a}
            last_change = verdicts(t - 1, accepted_last, {lab[i] for i in since[0]}, [lab[i] for i in since[1]])
        with led.stage(f"round {t} / debugger (27B, {sum(not r['correct'] for r in rows_a)} wrong problems)"):
            diags = debugger.diagnose(TASK, llm, BIG, pool, rows_a, seed=a.seed)
            weak = debugger.aggregate(TASK, llm, BIG, diags, seed=a.seed)
        dump(f"{d}/diagnoses.json", diags)
        dump(f"{d}/weaknesses.json", weak)
        # the analysis is short; if the prompt still does not fit the evolver's context, drop the
        # excerpts, then the one-line diagnoses of the problems outside the top half of the weaknesses
        limit = BIG_CTX - PROPOSE_RESERVE - 1000
        top = {x for w in weak[:max(1, (len(weak) + 1) // 2)] for x in w["labels"]}
        for excerpts, ds in ((2, diags), (0, diags), (0, [x for x in diags if x["label"] in top])):
            rep = report(rows_a, pool, since, last_change, debugger.section(ds, weak, excerpts=excerpts))
            n_tok = max(llm.count_tokens(BIG, propose_prompt(TASK, pool, rep, objective, layers, max_ops))
                        for layers in LAYERS)
            if n_tok <= limit:
                break
        log(f"round {t}: proposal prompt {n_tok} tokens (limit {limit}); {len(diags)} wrong problems diagnosed "
            f"({sum(x['error_type'] == 'undiagnosed' for x in diags)} undiagnosed), {len(weak)} key weaknesses")
        wrong = {r["label"] for r in rows_a if not r["correct"]}
        dump(f"{d}/pool.json", pool)
        dump(f"{d}/report.md", rep)
        dump(f"{d}/meta_prompt.md", meta_prompt(TASK, pool))
        log(f"round {t}: incumbent dev-A {summarize(rows_a)}"
            + (f"; since the last accepted change: fixed {len(since[0])}, broke {len(since[1])}" if since else ""))

        def propose(i):
            layers = LAYERS[i % len(LAYERS)]
            prompt = propose_prompt(TASK, pool, rep, objective, layers, max_ops)
            dump(f"{d}/propose_prompt_{i}.md", prompt)
            last = []

            def check(o):
                res, errs = check_edit(pool, o, layers, wrong, max_ops)
                last[:] = errs
                return res, errs
            obj, res, tries = ask_json(llm, prompt, "edit", check,
                                       seed=1000 * t + 10 * i + 100000 * a.seed, max_tokens=PROPOSE_TOKENS)
            new, changes = res if res else (None, None)
            return {"layers": list(layers), "changes": changes, "pool": new, "repairs": tries,
                    "prompt_chars": len(prompt),
                    "fail": None if new is not None else (last[:5] or ["no <edit> block or bad JSON"])}
        with led.stage(f"round {t} / evolver proposals (27B)"):
            with ThreadPoolExecutor(a.k) as ex:
                cands = list(ex.map(propose, range(a.k)))
        valid = [c for c in cands if c["pool"] is not None]

        with led.stage(f"round {t} / dev-B gate ({len(valid)} candidates)"):
            with ThreadPoolExecutor(len(valid) or 1) as ex:
                judged = list(ex.map(lambda c: evaluate(eng, c["pool"], dev_b), valid))
        for c, rows_b in zip(valid, judged):
            c["rows_b"], c["dev_b"] = rows_b, summarize(rows_b)
            fx, br = flips(inc_rows_b, rows_b)
            c["flip_b"] = (len(fx), len(br))
        for i, c in enumerate(cands):
            log(f"  cand {i} ({'+'.join(c['layers'])}): " + (
                f"invalid after repair: {c['fail']}" if c["pool"] is None else
                f"{len(c['changes'])} changes, {sum(len(ch['ops']) for ch in c['changes'])} ops, repairs "
                f"{c['repairs']}, dev-B fixed/broke "
                f"{c['flip_b']}, dev-B {c['dev_b']}"))
        if a.objective == "acc":    # the most accurate candidate (cost breaks ties among candidates) wins,
            # but only if it is strictly more accurate than the incumbent: a tie keeps the incumbent
            w = max(range(len(valid)), key=lambda i: (valid[i]["dev_b"]["acc"], -valid[i]["dev_b"]["cost"]),
                    default=None)
            if w is not None and valid[w]["dev_b"]["acc"] <= inc_b["acc"] + TOL:
                w = None
        else:
            w = gate(inc_b, [c["dev_b"] for c in valid], floor, best_acc, a.delta, a.tau)
        best = valid[w] if w is not None else None
        dump(f"{d}/candidates.json", [{k: v for k, v in c.items() if k not in ("pool", "rows_b")} for c in cands])
        prev_rows_a, accepted_last = rows_a, best
        if best is not None:
            pool, inc_b, inc_rows_b = best["pool"], best["dev_b"], best["rows_b"]
            if inc_b["acc"] >= floor - TOL:
                best_acc = max(best_acc, inc_b["acc"])
        trace_log.append({"round": t, "accepted": best is not None, "dev_b": inc_b})
        log(f"round {t}: {'accepted' if best is not None else 'no change'}; incumbent dev-B {inc_b}")
        dump("trace.json", trace_log)
        led.dump(os.path.join(a.out, "costs.json"), quiet=True)

    dump("final_pool.json", pool)
    if not a.skip_test:
        jobs = {"org_round0": lambda: summarize(evaluate(eng, pool0, test)),
                "org_final": lambda: summarize(evaluate(eng, pool, test))}
        for name in (a.baselines.split(",") if a.baselines else TASK.BASELINES):
            jobs[name] = lambda p=parse_program(TASK, TASK.SEED, TASK.BASELINES[name])[0]: summarize(
                evaluate(eng, TASK.SEED, test, p))
        with led.stage(f"test ({len(jobs)} systems)"):
            with ThreadPoolExecutor(len(jobs)) as ex:
                res = dict(zip(jobs, ex.map(lambda f: f(), jobs.values())))
        dump("test.json", res)
        log(f"TEST: {json.dumps(res)}")
    led.dump(os.path.join(a.out, "costs.json"))


if __name__ == "__main__":
    main()
