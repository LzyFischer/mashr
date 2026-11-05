"""Write every prompt of v7 (rendered with the real organizations of a run) and a few full example
runs on test problems into one Markdown file. Example calls are replayed from the call cache.

  scripts/run_dump_prompts.sh <run>   -> results/v7/<run>/prompts_and_examples.md
"""
import json
import os
import sys
import threading

from mashr.bench import load_math
from mashr.engine import ANSWER_FMT, MAX_TOKENS, SHOW_CHARS, Engine
from mashr.llm import LLM
from mashr.org import BASELINES, meta_prompt, parse_program, program_str, shape
from mashr.rsi import BIG, LAYERS, OBJECTIVE, REPAIR, evaluate, propose_prompt
from mashr.skills import SKILLS
from mashr.tools import TOOLS, tool_code

RUN = sys.argv[1] if len(sys.argv) > 1 else "math"
D = os.path.join("results", "v7", RUN)
MAX_CHARS = 6000


def fence(text, lang=""):
    text = str(text)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + f"\n... [{len(text) - MAX_CHARS} more chars cut in this file]"
    tick = "````" if "```" in text else "```"
    return f"{tick}{lang}\n{text}\n{tick}"


class Recorder:
    """Wraps llm.chat and keeps (messages, reply)."""
    def __init__(self, llm):
        self.log, self.live, self._chat, self._lock = [], 0, llm.chat, threading.Lock()
        llm.chat = self.chat

    def chat(self, model, messages, **kw):
        r = self._chat(model, messages, **kw)
        with self._lock:
            self.live += not r.cached
            self.log.append({"messages": [dict(m) for m in messages], "kw": kw, "reply": r})
        return r


def main():
    final = json.load(open(os.path.join(D, "final_pool.json")))
    pool1 = json.load(open(os.path.join(D, "round_1", "pool.json")))
    report1 = open(os.path.join(D, "round_1", "report.md")).read()
    first = open(os.path.join(D, "log.txt")).read().split("round 0 incumbent dev-B ")[1].split("\n")[0]
    acc0, cost0 = eval(first)["acc"], eval(first)["cost"]   # our own log line (a dict repr)
    llm = LLM()
    rec = Recorder(llm)
    eng = Engine(llm, seed=0, meta_thinking="medium")
    test = load_math("test", 0, 156)

    out = [f"# MAS-HR v7: every prompt, and example runs ({RUN})", "",
           "Task agents and meta-agent = Qwen3.5-9B (task agents: thinking off; meta-agent: thinking "
           "medium = 2048 tokens); evolver = Qwen3.8-27B (thinking high). Seed 0.", "",
           "| Step | Model | Prompt |", "|---|---|---|",
           "| Per problem: meta-agent writes the team (one try; unusable -> fallback) | 9B | §1 |",
           "| Per node: task agent solves | 9B | §2 |",
           "| Node wrote Python -> output returned once | 9B | §2.3 |",
           "| Per round: K=3 evolver candidates (task-agent layer / meta-agent layer / both) | 27B | §4 |",
           "| Invalid edit -> repair once | 27B | §4.2 |", "",
           f"Answer format: `{ANSWER_FMT}`", "",
           "## 1. Meta-agent", "", "System prompt (final organization):", "", fence(meta_prompt(final)), "",
           "User message:", "", fence("Problem: {question}"), "",
           "Unusable output -> fixed fallback: the first task agent alone with tools=[\"python\"].", "",
           "## 2. Task agents", "",
           "### 2.1 System prompt = self harness (role) + residual harness (skills, tools)", "",
           "Example: a verifier given one skill and `check_answer`:", ""]
    sysm = (final["agents"].get("verifier", next(iter(final["agents"].values())))["role"]
            + "\n\nSkills to apply:\n- check_answer_form: " + SKILLS["check_answer_form"]["text"]
            + "\n\nYou can run Python (numpy and sympy available) once: write one ```python``` code block "
              "that prints what you need, then stop and wait for its output. These functions are already "
              "defined:\n- " + TOOLS["check_answer"]["doc"])
    out += [fence(sysm), "", "### 2.2 User message", "", "Node without inputs:", "",
            fence(f"Problem: {{question}}\n\n{ANSWER_FMT}"), "", "Node with inputs:", "",
            fence(f"Problem: {{question}}\n\nWork from your teammates:\n[solver (a)]\n{{last {SHOW_CHARS} "
                  f"chars of a's work}}\n\nGive your own solution and final answer.\n\n{ANSWER_FMT}"), "",
            "### 2.3 After the Python run", "",
            fence(f"Output:\n{{python output}}\n\nGive the final answer now. {ANSWER_FMT}"), "",
            f"Each task-agent call may generate up to {MAX_TOKENS} tokens.", "",
            "### 2.4 Tool library (fixed; only the doc line is shown to the model)", ""]
    out += [f"- **{t}**: {v['doc']}" for t, v in TOOLS.items()]
    out += ["", "<details><summary>Preloaded code</summary>", "", fence(tool_code(list(TOOLS)), "python"),
            "", "</details>", "", "### 2.5 Skill library (fixed)", ""]
    out += [f"- **{k}** (when: {v['when']}): {v['text']}" for k, v in SKILLS.items()]
    out += ["", "### 2.6 Fixed baselines", ""] + [f"- **{k}**: `{v.replace(chr(10), '; ')}`"
                                                  for k, v in BASELINES.items()]

    rows = evaluate(eng, final, test)
    picks = []
    for f, why in [(lambda r: r["correct"] and len(r["plan"]["nodes"]) == 1, "one task agent, correct"),
                   (lambda r: r["correct"] and len(r["plan"]["nodes"]) >= 2, "a team, correct"),
                   (lambda r: not r["correct"] and r["plan"]["nodes"], "task agents, wrong")]:
        c = [r for r in rows if f(r) and r not in picks]
        if c:
            c[0]["why"] = why
            picks.append(c[0])
    out += ["", "## 3. Example runs (final organization, test)", "",
            f"Final organization on test: {sum(r['correct'] for r in rows)}/{len(rows)} correct.", ""]
    for k, r in enumerate(picks, 1):
        rec.log.clear()
        plan, _, _ = eng.orchestrate(final, r["question"])
        res = eng.run(final, r["question"], plan)
        out += [f"### Example {k}: {r['why']}", "",
                f"- {r['bucket']}; gold **{r['gold']}**, answer **{res['answer']}**; cost {r['cost']:.0f} "
                f"(meta-agent {r['meta_cost']:.0f}); architecture `{shape(plan)}`", "",
                "**Problem**", "", fence(r["question"]), ""]
        for c in rec.log:
            msgs, rep = c["messages"], c["reply"]
            is_meta = msgs[0]["content"].startswith("You are the meta-agent")
            who = "meta-agent" if is_meta else " / ".join(
                f"{n['id']} = {n['agent']}" for n in plan["nodes"]
                if msgs[0]["content"].startswith(final["agents"][n["agent"]]["role"])) or "task agent"
            out += [f"#### {who} ({rep.prompt_tokens} prompt + {rep.gen_tokens} generated tokens)", ""]
            if not is_meta:
                out += ["User message:" if len(msgs) == 2 else "Follow-up (Python output):", "",
                        fence(msgs[-1]["content"]), ""]
            out += ["Response:", "", fence(rep.text), ""]
            if is_meta:
                p, probs = parse_program(final, rep.text)
                out += ["Parsed: " + (f"`{program_str(p)}`" if p else f"unusable: {probs} -> fallback"), ""]

    history = f"round 0 (starting organization): acc {acc0:.1%}, cost {cost0:.0f}"
    prompts = [propose_prompt(pool1, report1, history, OBJECTIVE["acc"], layers) for layers in LAYERS]
    rec.live, rec.log[:] = 0, []
    reply = llm.chat(BIG, [{"role": "user", "content": prompts[0]}], thinking="high", max_tokens=6000,
                     seed=1000).text
    out += ["## 4. Evolver (27B)", "", "### 4.1 Proposal prompt (round 1, candidate 0, exactly as sent)", "",
            "Candidates 1 and 2 differ only in the layer line: "
            + "; ".join(f"candidate {i}: {'+'.join(l)}" for i, l in enumerate(LAYERS)) + ".", "",
            fence(prompts[0]), "",
            "Its answer " + ("(from the cache of the real run)" if not rec.live else "(re-sampled)") + ":", "",
            fence(reply), "", "### 4.2 Repair message", "", fence(REPAIR), ""]
    path = os.path.join(D, "prompts_and_examples.md")
    open(path, "w").write("\n".join(out))
    print(path, "live calls:", rec.live, "examples:", len(picks))


if __name__ == "__main__":
    main()
