"""The debugger (after AHE's Agent Debugger): the evolver reads analyses of the wrong problems, not their
raw traces. Each wrong dev-A problem gets one call (the evolver's model, thinking low) that reads the
problem's full run and returns a structured diagnosis; the excerpt it quotes is checked against the
trace. One more call groups the diagnoses into key weaknesses (fallback: grouping by error type).
Diagnoses of an unchanged run hit the LLM cache, so a round whose organization did not change costs
nothing here.
"""
import json
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from .org import program_str

NODE_CHARS = 12000      # per node in the trace the debugger reads: first quarter and last three quarters
WORKERS = 16            # parallel diagnosis calls
LAYERS = ("role", "meta-rule", "skill-or-tool")

DIAGNOSE = """You debug one failed run of a multi-agent system whose task agents {team}. The task agents and the
meta-agent are a 9B LLM; the meta-agent wrote the team below for this {item} and gave each node its tools
and skills. Find where and why the run went wrong.

# The {item}
{view}

Correct answer: {gold}
Grader on the final answer: {grader}
Team: {program}

# Task agents (roles)
{roles}

# The run (every node's full output, in order)
{nodes}

# What to output
A JSON object between <diagnosis> and </diagnosis>:
{{"node": "<id of the first node whose work went wrong>",
  "step": "<what it did wrong, one sentence>",
  "error_type": "<a short general label, 2-5 words, e.g. 'misread the spec', 'wrong bridge entity', 'tool output ignored', 'answer format'>",
  "root_cause": "<why it went wrong: missing knowledge, misreading, a wrong method, a tool misused or missing, bad team wiring, a verifier that copied an error, ...>",
  "excerpt": "<a verbatim quote from the run, at most 300 characters, where the error is visible>",
  "format_only": <true if the final answer is right in substance and only its form or wording differs from the correct one, else false>,
  "fix_direction": "<a general change that would also help similar {item}s; nothing specific to this {item}, and nothing that needs the correct answer (the system never sees it)>",
  "where_fix": "<role | meta-rule | skill-or-tool: role = a practice the agent should always follow; meta-rule = whom to staff, how to wire, which tools and skills to give; skill-or-tool = knowledge or a helper that only some {item}s need>"}}"""

AGGREGATE = """Below are diagnoses of the wrong runs of a multi-agent system whose task agents {team} (one line per
wrong {item}: label, category, failing node, error type, what went wrong, root cause, fix direction,
where to fix). Group them into the key weaknesses of the system: failure patterns shared by several
{item}s, each with one root cause. Order them by the number of {item}s. A {item} may belong to one
weakness only; put singletons into one weakness called "other".

{lines}

Output a JSON list between <weaknesses> and </weaknesses>:
[{{"weakness": "<name, a few words>", "labels": ["<labels>"], "root_cause": "<the shared root cause>",
   "where_fix": "<role | meta-rule | skill-or-tool>", "fix_direction": "<a general fix>"}}]"""


def _clip(text, n=NODE_CHARS):
    if len(text) <= n:
        return text
    head = n // 4
    return f"{text[:head]}\n[... {len(text) - n} chars omitted ...]\n{text[-(n - head):]}"


def _json(text, tag):
    m = re.search(rf"<{tag}>(.*?)</{tag}>", text or "", re.S)
    try:
        return json.loads(m.group(1)) if m else None
    except json.JSONDecodeError:
        return None


def _norm(s):
    return " ".join(str(s).split()).lower()


def diagnose_one(task, llm, model, pool, r, seed=0):
    nodes = []
    for pn, nd in zip(r["plan"]["nodes"], r["nodes"]):
        ok = "correct" if task.grade(nd["answer"], r) else "wrong"
        nodes.append(f"## node {nd['id']} = {nd['agent']}(inputs={pn['inputs']}, tools={pn['tools']}, "
                     f"skills={pn['skills']}) -> answer {nd['answer']!s:.300} ({ok}"
                     f"{', cut at the token limit' if nd['cut'] else ''})\n{_clip(nd.get('text', ''))}")
    used = {nd["agent"] for nd in r["plan"]["nodes"]}
    grader = task.feedback(r["pred"], r)[1] if hasattr(task, "feedback") else f"answered {r['pred']!s:.300}"
    prompt = DIAGNOSE.format(
        team=task.META["team"], item=task.META["item"], view=task.meta_view(r), gold=f"{r['gold']!s:.1500}",
        grader=grader, program=program_str(r["plan"]),
        roles="\n".join(f"- {a}: {pool['agents'][a]['role']}" for a in sorted(used) if a in pool["agents"]),
        nodes="\n\n".join(nodes))
    d = None
    try:
        d = _json(llm.chat(model, [{"role": "user", "content": prompt}], thinking="low", max_tokens=1500,
                           seed=seed).text, "diagnosis")
    except Exception as e:                       # noqa: BLE001  (a failed call leaves the problem undiagnosed)
        d = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    if not isinstance(d, dict) or "error_type" not in d:
        d = {"error_type": "undiagnosed", **(d if isinstance(d, dict) else {})}
    d = {k: (str(v)[:600] if not isinstance(v, bool) else v) for k, v in d.items()}
    run = _norm("\n".join(nd.get("text", "") for nd in r["nodes"]))
    ex = d.get("excerpt", "")
    d["excerpt_verified"] = bool(ex) and _norm(ex)[:200] in run
    d.update(label=r["label"], bucket=r["bucket"],
             agent=next((nd["agent"] for nd in r["nodes"] if nd["id"] == d.get("node")), "?"))
    return d


def diagnose(task, llm, model, pool, rows, seed=0):
    """Diagnoses of the wrong rows, in label order."""
    bad = [r for r in rows if not r["correct"]]
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(lambda r: diagnose_one(task, llm, model, pool, r, seed), bad))


def line(d):
    return (f"{d['label']} [{d['bucket']}] node {d.get('node', '?')} ({d['agent']}): {d.get('error_type', '')} | "
            f"{d.get('step', '')} | cause: {d.get('root_cause', '')} | fix: {d.get('fix_direction', '')} | "
            f"where: {d.get('where_fix', '')}" + (" | format only" if d.get("format_only") is True else ""))


def aggregate(task, llm, model, diags, seed=0):
    """Key weaknesses: [{weakness, labels, root_cause, where_fix, fix_direction}], most frequent first."""
    if not diags:
        return []
    labels = {d["label"] for d in diags}
    prompt = AGGREGATE.format(team=task.META["team"], item=task.META["item"],
                              lines="\n".join(f"- {line(d)}" for d in diags))
    ws = None
    try:
        ws = _json(llm.chat(model, [{"role": "user", "content": prompt}], thinking="medium", max_tokens=4000,
                            seed=seed).text, "weaknesses")
    except Exception:                            # noqa: BLE001
        ws = None
    out, seen = [], set()
    if isinstance(ws, list):
        for w in ws:
            if not isinstance(w, dict):
                continue
            ls = [x for x in w.get("labels", []) if x in labels and x not in seen]
            if ls:
                seen.update(ls)
                out.append({"weakness": str(w.get("weakness", "?"))[:120], "labels": ls,
                            "root_cause": str(w.get("root_cause", ""))[:500],
                            "where_fix": str(w.get("where_fix", ""))[:40],
                            "fix_direction": str(w.get("fix_direction", ""))[:500]})
    rest = [d for d in diags if d["label"] not in seen]
    if rest:                                      # the aggregation failed or missed some: group by error type
        by = defaultdict(list)
        for d in rest:
            by[_norm(d.get("error_type", "other"))].append(d)
        for k, ds in by.items():
            out.append({"weakness": k, "labels": [d["label"] for d in ds],
                        "root_cause": ds[0].get("root_cause", ""), "where_fix": ds[0].get("where_fix", ""),
                        "fix_direction": ds[0].get("fix_direction", "")})
    return sorted(out, key=lambda w: (w["weakness"] == "other", -len(w["labels"])))


def section(diags, weaknesses, excerpts=2):
    """The report's analysis of the wrong problems: key weaknesses, then one line per wrong problem."""
    by = {d["label"]: d for d in diags}
    n_fmt = sum(d.get("format_only") is True for d in diags)
    L = [f"## Key weaknesses ({len(diags)} wrong problems, each analysed from its full run; "
         f"{n_fmt} judged right in substance but wrong in form)"]
    for i, w in enumerate(weaknesses, 1):
        L += [f"### W{i}: {w['weakness']} ({len(w['labels'])}: {' '.join(w['labels'])})",
              f"Root cause: {w['root_cause']}", f"Where to fix: {w['where_fix']}. Direction: {w['fix_direction']}"]
        ex = [by[x] for x in w["labels"] if x in by and by[x].get("excerpt") and by[x].get("excerpt_verified")]
        for d in ex[:excerpts]:
            L.append(f'- {d["label"]}, node {d.get("node", "?")} ({d["agent"]}): "{d["excerpt"][:300]}"')
    L += ["", "## Wrong problems, one line each (label [category] node (agent): error type | what went wrong | "
              "cause | fix | where)"]
    L += [f"- {line(by[x])}" for x in sorted(by, key=lambda s: int(s[1:]) if s[1:].isdigit() else 0)]
    return "\n".join(L)
