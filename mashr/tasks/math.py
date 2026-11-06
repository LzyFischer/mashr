"""Task: MATH level 4-5 problems with integer answers. A node answers in one call; with tools it may
run Python once (tools preloaded) and then gives its final answer."""
import json
import os
import random
import re

from .. import ROOT
from ..sandbox import CODE, run_python
from .math_skills import SKILLS
from .math_tools import TOOLS, tool_code

NAME = "math"
ANSWER_FMT = "End your response with a final line of the form '#### <number>'."
MAX_TOKENS = 4096    # per task-agent call
VOTE_ON_MISSING = True
FALLBACK_TOOLS = ("python",)
TOOLS_ARE_CODE = True    # the evolver may add / edit tools (Python, with a sandbox test)
TOOL_ENV = ("Tool code runs in a sandbox (Python 3, numpy and sympy, no network, 10 s); the code of a "
            "node's tools is preloaded before the code the agent writes.")
SPLITS = {"dev_a": 150, "dev_b": 50, "test": 156}
META = {"team": "solve math problems", "item": "problem",
        "node": "the agent reads the problem, its skills and the full work of its inputs, then answers.",
        "final": "`return x`: x's answer is final.",
        "no_solve": "no solution, no computation, no answer.",
        "tools": "Python functions (no tools = no Python)"}
EXAMPLE = ['a = solver(tools=["number_theory"], skills=["modular"])',
           'v = verifier(a, tools=["check_answer"])', "return v"]
SYSTEM_NOTE = ("A node with tools may run Python once (tools preloaded). It reads the problem, its "
               "skills and the full work of its inputs.")

SEED = {
    "agents": {
        "solver": {"role": "You are a careful math solver. Reason step by step."},
        "coder": {"role": "You are a math solver who computes with short, correct Python and reasons "
                           "about its output."},
        "verifier": {"role": "You check the solutions you are given: re-derive the answer "
                              "independently, find any error, and give the answer you believe is "
                              "correct."},
    },
    "rules": [
        "Easy problem: one solver.",
        "Harder problem: solver, then a verifier that reads its work.",
        "Heavy computation, counting or search: a coder with python or a matching tool, then a verifier.",
        "Give skills that match the problem type.",
    ],
}

BASELINES = {
    "single": "a = solver()\nreturn a",
    "coder_tools": 'a = coder(tools=["python", "exact_solve", "brute_force"])\nreturn a',
    "solve_verify": 'a = solver()\nv = verifier(a, tools=["check_answer"])\nreturn v',
}


def extract(text: str) -> str | None:
    m = re.findall(r"####\s*\$?\s*(-?[\d,]*\.?\d+)", text)
    if not m:
        m = re.findall(r"\\boxed\{\s*\$?(-?[\d,]*\.?\d+)", text) or re.findall(r"-?[\d,]*\.?\d+", text)
    if not m:
        return None
    s = m[-1].replace(",", "")
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return None


def load_math(split, lo, hi):
    """MATH level 4-5 problems with integer answers (split: train | test), shuffled with seed 0; items
    carry a report bucket and a 'hard' flag (level 5)."""
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "data", "math", f"{split}.jsonl"))]
    rows = [r for r in rows if r["level"] in (4, 5)
            and re.fullmatch(r"-?\d+", r["answer"].replace(",", "").strip())]
    random.Random(0).shuffle(rows)
    return [{"id": r["unique_id"], "question": r["problem"], "gold": extract(r["answer"]),
             "bucket": f"{r['subject']} L{r['level']}", "hard": r["level"] == 5}
            for r in rows][lo:hi]


def load(split, n=None):
    lo, hi = {"dev_a": (0, SPLITS["dev_a"]),
              "dev_b": (SPLITS["dev_a"], SPLITS["dev_a"] + (n or SPLITS["dev_b"]))}.get(split, (0, n or SPLITS["test"]))
    items = load_math("test" if split == "test" else "train", lo, hi)
    return items[:n] if n else items


def tool_prelude():
    """Prepended to a tool's code and test when the evolver adds or edits a tool."""
    return ""


def meta_view(item):
    return f"Problem: {item['question']}"


def grade(pred, item):
    return pred is not None and pred == item["gold"]


def run_node(eng, pool, node, item, work, is_output):
    if not work:
        user = f"Problem: {item['question']}\n\n{ANSWER_FMT}"
    else:
        user = (f"Problem: {item['question']}\n\nWork from your teammates:\n{work}\n\nGive your own "
                f"solution and final answer.\n\n{ANSWER_FMT}")
    S, T = pool.get("skills", SKILLS), pool.get("tools", TOOLS)
    system = pool["agents"][node["agent"]]["role"]
    if node["skills"]:
        system += "\n\nSkills to apply:\n" + "\n".join(f"- {k}: {S[k]['text']}" for k in node["skills"])
    if node["tools"]:
        helpers = [t for t in node["tools"] if T[t].get("code", "").strip()]
        system += ("\n\nYou can run Python (numpy and sympy available) once: write one ```python``` "
                   "code block that prints what you need, then stop and wait for its output.")
        if helpers:
            system += " These functions are already defined:\n" + "\n".join(
                f"- {T[t]['doc']}" for t in helpers)
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    r = eng.chat(msgs, MAX_TOKENS)
    calls = [{"agent": node["agent"], "node": node["id"], "prompt_tokens": r.prompt_tokens,
              "gen_tokens": r.gen_tokens}]
    shown, out = [r.text], None
    code = CODE.findall(r.text)
    if node["tools"] and code and "####" not in r.text.split("```")[-1]:
        out, _ = run_python(tool_code(node["tools"], T) + "\n" + code[-1])
        shown.append(f"[Python output]\n{out}")
        msgs += [{"role": "assistant", "content": r.text},
                 {"role": "user", "content": f"Output:\n{out}\n\nGive the final answer now. {ANSWER_FMT}"}]
        r = eng.chat(msgs, MAX_TOKENS)
        calls.append({"agent": node["agent"], "node": node["id"], "prompt_tokens": r.prompt_tokens,
                      "gen_tokens": r.gen_tokens})
        shown.append(r.text)
    text = r.text
    ans = extract(text) if ("####" in text or "boxed" in text or out is None) else extract(out)
    return {"text": "\n\n".join(shown), "answer": ans, "calls": calls,
            "cut": any(c["gen_tokens"] >= MAX_TOKENS for c in calls)}
