"""Where does MAS-HR lose? Final organizations of v7 runs on MATH test: the same HR plans, with parts
of the residual harness removed from every node.

  scripts/run_test_ablation.sh <out.json> <meta-thinking> <run>:<seed> [<run>:<seed> ...]
  e.g. scripts/run_test_ablation.sh results/v7/ablations/math.json medium math:0
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor

from mashr.bench import load_math
from mashr.engine import Engine, cost
from mashr.llm import LLM

VARIANTS = {"full": {}, "no_skills": {"skills": []}, "no_tools": {"tools": []},
            "structure_only": {"skills": [], "tools": []}}
out_path, meta_thinking, runs = sys.argv[1], sys.argv[2], [a.split(":") for a in sys.argv[3:]]
llm, res = LLM(), {}
test = load_math("test", 0, 156)
for name, s in runs:
    s = int(s)
    eng = Engine(llm, seed=s, meta_thinking=meta_thinking)
    pool = json.load(open(f"results/v7/{name}/final_pool.json"))
    with ThreadPoolExecutor(64) as ex:
        plans = list(ex.map(lambda it: eng.orchestrate(pool, it["question"]), test))

    def run(job):
        name, ch, it, (plan, calls, _) = job
        p = {**plan, "nodes": [{**n, **ch} for n in plan["nodes"]]}
        out = eng.run(pool, it["question"], p)
        return name, out["answer"] == it["gold"], cost(calls + out["calls"])
    jobs = [(k, ch, it, pl) for k, ch in VARIANTS.items() for it, pl in zip(test, plans)]
    tot = {k: [0, 0.0] for k in VARIANTS}
    with ThreadPoolExecutor(128) as ex:
        for k, ok, c in ex.map(run, jobs):
            tot[k][0] += ok
            tot[k][1] += c
    res[s] = {k: {"acc": round(v[0] / len(test), 4), "cost": round(v[1] / len(test), 1)} for k, v in tot.items()}
    print(s, res[s], flush=True)
    json.dump(res, open(out_path, "w"), indent=1)
