"""Slow loop (RSI, v7): the evolver (27B) edits two layers, the task agents' self harnesses and the
meta-harness; on every problem the meta-agent writes the team and each node's residual harness
(tools, skills from fixed libraries) (org.py, engine.py). The evolver prompt follows AHE (Agentic
Harness Engineering): fixed edit scope, evidence first, the layer that fits the root cause.

  scripts/run.sh math <name> --objective acc [...]      # task agents + meta-agent on local vLLM, evolver on Tinker

Start: the task's hand-written SEED or --init-pool. Each round: dev-A run -> report -> K candidates, each
limited to a layer (task-agent / meta-agent / both) -> gate on dev-B.
--objective acc: the most accurate organization on dev-B wins (cost breaks ties).
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

from . import ROOT, tasks
from .engine import Engine, cost
from .ledger import Ledger
from .llm import LLM, THINK_BUDGET
from .org import LIMITS, apply_ops, meta_prompt, parse_program, program_str, shape, validate

BIG = "Qwen/Qwen3.8-27B"
TOL = 1e-9
WORKERS = 128
TASK = None          # the task module, set in main()
# candidate i may edit LAYERS[i % 3]
LAYERS = [("task-agent",), ("meta-agent",), ("task-agent", "meta-agent")]

REPAIR = """Your output could not be used:
{errors}

Output the corrected complete JSON between <{tag}> and </{tag}>."""


def pct(xs):
    return f"{sum(xs) / len(xs):.0%}" if xs else "-"


def ask_json(llm, prompt, tag, check, seed, max_tokens=4096):
    msgs = [{"role": "user", "content": prompt}]
    for attempt in range(2):
        txt = llm.chat(BIG, msgs, thinking="high", max_tokens=max_tokens, seed=seed + attempt).text
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
        msgs += [{"role": "assistant", "content": txt},
                 {"role": "user", "content": REPAIR.format(errors="\n".join(errs[:15]), tag=tag)}]
    return None, None, 2


def ops_summary(ops):
    return "\n  ".join(json.dumps(op)[:300] for op in ops)


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


def report(rows, pool) -> str:
    s = summarize(rows)
    L = ["# Report (dev-A)", "",
         f"Organization: acc {s['acc']:.1%} (meta-agent prompt {len(meta_prompt(TASK, pool))} chars). "
         f"{s['n_shapes']} distinct architectures, "
         f"{s['nodes']:.1f} nodes per problem. Fallback (unusable meta-agent output): {s['fallback']}.", "",
         "## By category", "| category | n | acc | architectures |", "|---|---|---|---|"]
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
    for it, cnt in items.most_common(25):
        has = lambda pn: (it == "no tools (no Python)" and not pn["tools"]) or \
            (it.startswith("tool:") and it[5:] in pn["tools"]) or \
            (it.startswith("skill:") and it[6:] in pn["skills"])
        yes = [TASK.grade(nd["answer"], r) for r, nd, pn in pairs if has(pn)]
        no = [TASK.grade(nd["answer"], r) for r, nd, pn in pairs if not has(pn)]
        L.append(f"| {it} | {cnt} | {pct(yes)} | {pct(no)} |")
    unused = [t for t in TASK.TOOLS if f"tool:{t}" not in items] + [k for k in TASK.SKILLS if f"skill:{k}" not in items]
    if unused:
        L.append(f"Never given: {', '.join(unused)}.")
    probs = Counter(p for r in rows for p in r["problems"])
    if probs:
        L += ["", "Meta-agent output problems: " + "; ".join(f"{k} ({v})" for k, v in probs.most_common(6))]
    bad = [r for r in rows if not r["correct"]]
    L += ["", f"## Wrong ({len(bad)})"]
    for r in bad[:10]:
        L.append(f"- [{r['bucket']}] {TASK.meta_view(r)[:280]}\n  architecture: {program_str(r['plan'])}; "
                 f"answered {r['pred']}, correct {r['gold']}")
    return "\n".join(L)


OBJECTIVE = {
    "acc": "Objective: maximize accuracy on held-out problems.",
    "keep": "Objective: minimize the average cost per problem while keeping accuracy at the level the "
            "current organization already reaches (at most {delta:.1%} below the best accuracy so far "
            "on held-out problems). The organization was already optimized for accuracy; now find "
            "where it spends more than it needs."}

LAYER_NOTE = {("task-agent",): "This candidate may edit only the task-agent layer.",
              ("meta-agent",): "This candidate may edit only the meta-agent layer.",
              ("task-agent", "meta-agent"): "This candidate may edit both layers."}

PROPOSE = """You improve a multi-agent system whose task agents {team}, by editing its harnesses.
The model (a 9B LLM, no thinking for task agents) is fixed.

# The system
For each {item} the meta-agent (the 9B model, guided by its meta-harness) writes a team as code:
{example}
Each line is a task agent with its self harness (its role) and the residual harness the meta-agent
gives it for this {item}: tools ({tools_kind}) and skills (how-to texts). {system_note} Nodes
without inputs run in parallel. {final} The meta-agent does not do the {item} itself. Unusable output
-> the first task agent alone with {fallback} (fixed).

# What you edit: two layers
| layer | what | effect |
|---|---|---|
| task-agent | add, remove or edit a task agent (its role = self harness) | always on for that agent |
| meta-agent | add, edit or remove a rule of the meta-harness | how the meta-agent staffs, wires and equips teams |
The tool and skill libraries, the model and the format are fixed.

# Principles
- Evidence first: each change targets a failure pattern in the report (which problems, what went
  wrong, why), not a general best practice.
- Choose the layer that fits the root cause: a practice an agent should always follow -> its role;
  whom to staff, how to wire, which tools and skills -> a meta-harness rule.
- If a failure persists after changes on one layer, revert them and try the other layer.
- Few, decisive changes. Remove rules and agents the evidence does not support.

# Analysis
1. Read the history: which edits were accepted or rejected, with their held-out results.
2. Group the wrong problems into patterns and find each one's root cause.
3. Check which architectures, tools and skills help and which do not.

{objective}
{layer_note}

# Edit operations (a JSON list, applied in order)
task-agent layer:
{{"op": "add_agent", "name": "<name>", "role": "<role, <= {role_chars} chars>"}}
{{"op": "remove_agent", "name": "<name>"}}
{{"op": "edit_agent", "name": "<name>", "role": "<new role>"}}
meta-agent layer (rule numbers as shown below; new rules are appended):
{{"op": "add_rule", "text": "<rule, <= {rule_chars} chars>"}}
{{"op": "edit_rule", "rule": <number>, "text": "<new rule>"}}
{{"op": "remove_rule", "rule": <number>}}
At most {max_agents} task agents and {max_rules} rules. No rule may mention a removed agent.

# Tools (fixed)
{tools}

# Skills (fixed)
{skills}

# Current organization
Task agents:
{agents}
Meta-harness:
{meta}

# Report
{report}

# History (held-out dev-B{ref_note})
{history}

Output the JSON list between <ops> and </ops>."""


def propose_prompt(task, pool, rep, history, objective, layers, ref_note=""):
    m = task.META
    return PROPOSE.format(
        team=m["team"], item=m["item"], example="\n".join("    " + l for l in task.EXAMPLE),
        tools_kind=m["tools"], system_note=task.SYSTEM_NOTE, final=m["final"],
        fallback=", ".join(task.FALLBACK_TOOLS) or "no tools",
        objective=objective, layer_note=LAYER_NOTE[layers], role_chars=LIMITS["role_chars"],
        rule_chars=LIMITS["rule_chars"], max_agents=LIMITS["agents"], max_rules=LIMITS["rules"],
        tools="\n".join(f"- {t}: {v['doc']}" for t, v in task.TOOLS.items()),
        skills="\n".join(f"- {k} (when: {v['when']}): {v['text']}" for k, v in task.SKILLS.items()),
        agents="\n".join(f"- {n}: {a['role']}" for n, a in pool["agents"].items()),
        meta="\n".join(f"{i}. {r}" for i, r in enumerate(pool["rules"], 1)),
        report=rep, history=history, ref_note=ref_note)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["math", "bird", "alfworld"], default="math")
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
    ap.add_argument("--baselines", help="default: all of the task's baselines")
    ap.add_argument("--out", help="default: results/v7/<task>")
    ap.add_argument("--skip-test", action="store_true")
    ap.add_argument("--seed", type=int, default=0, help="sampling seed of the task agents, meta-agent and evolver")
    ap.add_argument("--init-pool", help="start from this organization (JSON) instead of the task's SEED; with "
                                         "--objective cost the floor is its own dev-B accuracy - delta")
    a = ap.parse_args()
    if a.objective == "cost" and not a.init_pool:
        raise SystemExit("--objective cost keeps the accuracy of a starting organization: give --init-pool")
    global TASK
    TASK = tasks.get(a.task)
    a.out = a.out or os.path.join(ROOT, "results", "v7", a.task)
    os.makedirs(a.out, exist_ok=True)
    llm = LLM()
    eng = Engine(TASK, llm, seed=a.seed, meta_thinking=a.meta_thinking)
    dev_a, dev_b, test = TASK.load("dev_a", a.n_dev_a), TASK.load("dev_b", a.n_dev_b), TASK.load("test", a.n_test)

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
    floor, ref_note = 0.0, ""
    log(f"task {a.task}: dev-A {len(dev_a)}, dev-B {len(dev_b)}, test {len(test)}; delta "
        f"{a.delta}, tau {a.tau}, meta-agent thinking {a.meta_thinking}, objective {a.objective}")
    pool = json.load(open(a.init_pool)) if a.init_pool else copy.deepcopy(TASK.SEED)
    errs = validate(pool)
    if errs:
        raise SystemExit(f"invalid organization: {errs}")
    log(f"starting organization: {a.init_pool or 'the seed'}")
    pool0 = copy.deepcopy(pool)
    dump("round_0/pool.json", pool)

    with led.stage("round 0 / dev-B eval"):
        inc_b = summarize(evaluate(eng, pool, dev_b))
    objective = OBJECTIVE["acc"]
    if a.objective == "cost":       # phase 2: keep the accuracy already reached
        floor, best_acc = inc_b["acc"] - a.delta, inc_b["acc"]
        objective = OBJECTIVE["keep"].format(delta=a.delta)
        ref_note = (f"; the starting organization: acc {inc_b['acc']:.1%}, cost {inc_b['cost']:.0f}; "
                    f"floor {floor:.1%}")
        log(f"phase 2 (cost): floor on dev-B {floor:.3f}")
    else:
        best_acc = inc_b["acc"]
    log(f"round 0 incumbent dev-B {inc_b}")
    history = [f"round 0 (starting organization): acc {inc_b['acc']:.1%}"]
    trace = [{"round": 0, "accepted": True, "dev_b": inc_b}]

    for t in range(1, a.rounds + 1):
        d = f"round_{t}"
        with led.stage(f"round {t} / dev-A eval"):
            rows_a = evaluate(eng, pool, dev_a)
        if a.abl_n:         # kept for our analysis; not shown to the evolver
            with led.stage(f"round {t} / residual ablation"):
                abl, abl_n = residual_ablation(eng, pool, rows_a, a.abl_n)
            dump(f"round_{t}/ablation.json", {"questions": abl_n, "results": {
                comp: {"uses": len(xs), "needed": sum(w and not n for w, n in xs),
                       "harmful": sum(n and not w for w, n in xs)} for comp, xs in abl.items()}})
        rep = report(rows_a, pool)
        dump(f"{d}/pool.json", pool)
        dump(f"{d}/report.md", rep)
        log(f"round {t}: incumbent dev-A {summarize(rows_a)}")

        def propose(i):
            layers = LAYERS[i % len(LAYERS)]
            prompt = propose_prompt(TASK, pool, rep, "\n".join(history), objective, layers, ref_note)
            last = []

            def check(o):
                res, errs = apply_ops(pool, o, layers)
                last[:] = errs
                return res, errs
            ops, new, tries = ask_json(llm, prompt, "ops", check,
                                       seed=1000 * t + 10 * i + 100000 * a.seed, max_tokens=6000)
            return {"layers": list(layers), "ops": ops, "pool": new, "repairs": tries,
                    "fail": None if new is not None else (last[:5] or ["no <ops> block or bad JSON"])}
        with led.stage(f"round {t} / evolver proposals (27B)"):
            with ThreadPoolExecutor(a.k) as ex:
                cands = list(ex.map(propose, range(a.k)))
        valid = [c for c in cands if c["pool"] is not None]
        with led.stage(f"round {t} / dev-B gate ({len(valid)} candidates)"):
            with ThreadPoolExecutor(len(valid) or 1) as ex:
                gated = list(ex.map(lambda c: summarize(evaluate(eng, c["pool"], dev_b)), valid))
        for c, g in zip(valid, gated):
            c["dev_b"] = g
        for i, c in enumerate(cands):
            log(f"  cand {i} ({'+'.join(c['layers'])}): " + (
                f"invalid after repair: {c['fail']}" if c["pool"] is None else
                f"{len(c['ops'])} ops, repairs {c['repairs']}, dev-B {c['dev_b']}"))
        if a.objective == "acc":                 # most accurate wins; cost only breaks ties
            orgs = [inc_b] + [c["dev_b"] for c in valid]
            i = max(range(len(orgs)), key=lambda i: (orgs[i]["acc"], -orgs[i]["cost"]))
            w = None if i == 0 else i - 1
        else:
            w = gate(inc_b, [c["dev_b"] for c in valid], floor, best_acc, a.delta, a.tau)
        best = valid[w] if w is not None else None
        for c in cands:
            if c["pool"] is None:
                history.append(f"round {t} [{'+'.join(c['layers'])}, invalid]")
                continue
            status = "ACCEPTED" if c is best else "rejected"
            history.append(f"round {t} [{'+'.join(c['layers'])}, {status}]: acc {c['dev_b']['acc']:.1%}\n  "
                           + ops_summary(c["ops"]))
        dump(f"{d}/candidates.json", [{k: v for k, v in c.items() if k != "pool"} for c in cands])
        if best is not None:
            pool, inc_b = best["pool"], best["dev_b"]
            if inc_b["acc"] >= floor - TOL:
                best_acc = max(best_acc, inc_b["acc"])
        trace.append({"round": t, "accepted": best is not None, "dev_b": inc_b})
        log(f"round {t}: {'accepted' if best is not None else 'no change'}; incumbent dev-B {inc_b}")
        dump("trace.json", trace)
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
