"""Fast loop: the meta-agent writes the team and each node's residual harness (org.py); the executor
runs it layer by layer. How a node works (its prompt, tool use, answer) is up to the task
(tasks/<name>.py: run_node). Task agents do not think (thinking off)."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from .org import fallback_plan, meta_prompt, parse_program

MODEL = "Qwen/Qwen3.5-9B"
PROMPT_WEIGHT = 0.2   # cost = generated tokens + 0.2 * prompt tokens (all calls, incl. the meta-agent's)
SHOW_CHARS = 4000     # how much of an input node's work a node sees (its end)


def majority(answers):
    """Most common non-missing answer; ties go to the earliest."""
    xs = [a for a in answers if a is not None]
    if not xs:
        return None
    c = Counter(xs)
    top = max(c.values())
    return next(a for a in xs if c[a] == top)


def cost(calls) -> float:
    return sum(c["gen_tokens"] + PROMPT_WEIGHT * c["prompt_tokens"] for c in calls)


class Engine:
    def __init__(self, task, llm, model: str = MODEL, seed: int = 0, meta_thinking: str = "medium"):
        self.task, self.llm, self.model, self.seed, self.meta_thinking = task, llm, model, seed, meta_thinking

    def chat(self, msgs, max_tokens):
        """One task-agent call (thinking off)."""
        return self.llm.chat(self.model, msgs, thinking="off", max_tokens=max_tokens, seed=self.seed)

    def orchestrate(self, pool: dict, item: dict):
        """(plan, calls, info). Unusable output -> the fixed fallback plan (no second try)."""
        msgs = [{"role": "system", "content": meta_prompt(self.task, pool)},
                {"role": "user", "content": self.task.meta_view(item)}]
        r = self.llm.chat(self.model, msgs, thinking=self.meta_thinking, max_tokens=900, seed=self.seed)
        calls = [{"agent": "meta", "node": None, "prompt_tokens": r.prompt_tokens,
                  "gen_tokens": r.gen_tokens}]
        plan, probs = parse_program(self.task, pool, r.text)
        if plan is None:
            return fallback_plan(self.task, pool), calls, {"problems": probs[:4], "fallback": True}
        return plan, calls, {"problems": probs[:4], "fallback": False}

    def run(self, pool: dict, item: dict, plan: dict) -> dict:
        done, depth = {}, {}
        for n in plan["nodes"]:
            depth[n["id"]] = 1 + max((depth[i] for i in n["inputs"]), default=-1)
        for d in sorted(set(depth.values())):
            layer = [n for n in plan["nodes"] if depth[n["id"]] == d]

            def one(n):
                work = "\n\n".join(f"[{done[i]['agent']} ({i})]\n{done[i]['text'][-SHOW_CHARS:]}"
                                   for i in n["inputs"])
                out = self.task.run_node(self, pool, n, item, work, n["id"] == plan["output"])
                return {"id": n["id"], "agent": n["agent"], **out}
            if len(layer) == 1:
                outs = [one(layer[0])]
            else:
                with ThreadPoolExecutor(len(layer)) as ex:
                    outs = list(ex.map(one, layer))
            for o in outs:
                done[o["id"]] = o
        answer = done[plan["output"]]["answer"]
        if answer is None and self.task.VOTE_ON_MISSING:
            answer = majority([o["answer"] for o in done.values()])
        calls = [c for n in plan["nodes"] for c in done[n["id"]]["calls"]]
        return {"answer": answer, "calls": calls,
                "nodes": [{k: v for k, v in done[n["id"]].items() if k != "calls"}
                          | {"cost": round(cost(done[n["id"]]["calls"]), 1)} for n in plan["nodes"]]}
