"""Build data/bench/{aflow_math,gsmhard,aime}_{dev_a,dev_b,test}.jsonl (see mashr/bench.py).
Run from the project root:  ~/miniconda3/envs/mem/bin/python -I scripts/prepare_bench.py
"""
import json
import os
import random
import re

import pandas as pd

D, OUT = "data/_download", "data/bench"
os.makedirs(OUT, exist_ok=True)
norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()


def write(name, split, rows):
    with open(os.path.join(OUT, f"{name}_{split}.jsonl"), "w") as f:
        f.write("\n".join(json.dumps(r) for r in rows) + "\n")
    print(f"{name}_{split}", len(rows))


def splits(name, dev_pool, test):
    random.Random(0).shuffle(dev_pool)
    write(name, "dev_a", dev_pool[:150])
    write(name, "dev_b", dev_pool[150:350])
    write(name, "test", test)


# AFlow MATH: test = AFlow test split; dev = MATH L5 of the same types from prm800k train
test = [json.loads(l) for l in open("data/transfer/aflow_math.jsonl")]
types = {"Prealgebra", "Number Theory", "Precalculus", "Counting & Probability"}
seen = {norm(t["question"]) for t in test}
pool = []
for l in open("data/math/train.jsonl"):
    r = json.loads(l)
    if r["level"] == 5 and r["subject"] in types and norm(r["problem"]) not in seen and r["answer"]:
        pool.append({"id": r["unique_id"], "question": r["problem"], "gold": r["answer"],
                     "bucket": f"{r['subject']} L5", "hard": True})
splits("aflow_math", pool, [{k: v for k, v in t.items() if k != "in_dev"} for t in test])

# GSM-Hard: random split of the 1319
g = [json.loads(l) for l in open("data/transfer/gsmhard.jsonl")]
random.Random(0).shuffle(g)
write("gsmhard", "dev_a", g[:150])
write("gsmhard", "dev_b", g[150:350])
write("gsmhard", "test", sorted(g[350:], key=lambda r: int(r["id"].split("-")[1])))

# AIME: test = 2022-2025 (data/transfer/aime.jsonl); dev = 1983-2021
a = pd.read_csv(f"{D}/hf/aime_1983_2024.csv")
a = a[a.Year <= 2021]
pool = [{"id": f"aime-{r.ID}", "question": r.Question, "gold": str(int(r.Answer)),
         "bucket": f"AIME {r.Year}", "hard": True} for r in a.itertuples()]
splits("aime", pool, [json.loads(l) for l in open("data/transfer/aime.jsonl")])
