"""Download and split the v8 benchmarks: HumanEval+, MBPP+ (EvalPlus), HotpotQA (distractor) and
2WikiMultihopQA. Run from the project root (needs network, pandas + pyarrow, and evalplus for the code
check):

    python -I scripts/prepare_data.py [--code-only]

Writes
  data/_download/...                      raw files (git-ignored; the code tasks read EvalPlus from here)
  data/code/splits.json                   {humaneval_plus|mbpp_plus: {dev_a|dev_b|test: [task ids]}}
  data/qa/{hotpotqa,twowiki}_{split}.jsonl  questions with their 10 context paragraphs

Code tasks whose canonical solution fails the official EvalPlus check three times are left out
(HumanEval/32, Mbpp/84, Mbpp/255, Mbpp/392 in the current releases). Splits are shuffled with seed 0. QA: dev-A, dev-B and test are
disjoint samples of the official dev set (the test sets have no public answers); dev-B keeps a pool of
200 (the task uses the first --n-dev-b, default 50).
"""
import gzip
import json
import os
import random
import shutil
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DL = os.path.join(ROOT, "data", "_download")
URLS = {
    "evalplus/HumanEvalPlus.jsonl.gz":
        "https://github.com/evalplus/humanevalplus_release/releases/download/v0.1.10/HumanEvalPlus.jsonl.gz",
    "evalplus/MbppPlus.jsonl.gz":
        "https://github.com/evalplus/mbppplus_release/releases/download/v0.2.0/MbppPlus.jsonl.gz",
    "hotpotqa/validation.parquet":
        "https://huggingface.co/datasets/hotpotqa/hotpot_qa/resolve/main/distractor/validation-00000-of-00001.parquet",
    "2wiki/dev.parquet": "https://huggingface.co/datasets/xanhho/2WikiMultihopQA/resolve/main/dev.parquet",
}
CODE_SPLITS = {"humaneval_plus": (50, 30), "mbpp_plus": (100, 50)}     # dev-A, dev-B; test = the rest
QA_SPLITS = (150, 200, 500)                                            # dev-A, dev-B pool, test


def download():
    for rel, url in URLS.items():
        path = os.path.join(DL, rel)
        if os.path.exists(path):
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print("download", url)
        with urllib.request.urlopen(url, timeout=600) as r, open(path + ".part", "wb") as f:
            shutil.copyfileobj(r, f)
        os.replace(path + ".part", path)
        if path.endswith(".gz"):
            with gzip.open(path, "rb") as fi, open(path[:-3], "wb") as fo:
                shutil.copyfileobj(fi, fo)


def canonical_ok(name, tid):
    """The canonical solution's check, in its own process: a problem whose canonical outputs are huge or
    that crashes the interpreter counts as failed instead of taking a worker pool down."""
    import subprocess
    try:
        r = subprocess.run([sys.executable, "-m", "mashr.tasks._code", "canonical", name, tid], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print("  timeout:", tid)
        return False
    ok = r.stdout.strip().endswith("OK")
    if not ok and not r.stdout.strip().endswith("FAIL"):
        print(f"  crashed: {tid} (exit {r.returncode}) {r.stderr.strip()[-200:]}")
    return ok


def code_splits():
    from concurrent.futures import ThreadPoolExecutor
    sys.path.insert(0, ROOT)
    from mashr.tasks import _code
    out = {}
    for name, (na, nb) in CODE_SPLITS.items():
        ids = sorted(_code.problems(name))
        # each canonical solution is checked (up to three times: a timeout can be load noise) in a fresh
        # process, so that one problem's huge outputs do not inflate the next check's memory
        with ThreadPoolExecutor(8) as ex:
            ok = dict(zip(ids, ex.map(lambda t: canonical_ok(name, t), ids)))
        bad = [t for t in ids if not ok[t]]
        ids = [t for t in ids if ok[t]]
        random.Random(0).shuffle(ids)
        out[name] = {"dev_a": ids[:na], "dev_b": ids[na:na + nb], "test": ids[na + nb:], "excluded": bad}
        print(name, {k: len(v) for k, v in out[name].items()}, "excluded:", bad)
    os.makedirs(os.path.join(ROOT, "data", "code"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "code", "splits.json"), "w") as f:
        json.dump(out, f, indent=1)
    # the expected outputs were cached per problem by the checks above (expected_<task>/); drop the
    # excluded problems' (Mbpp/255's are hundreds of MB)
    for name, sp in out.items():
        for tid in sp["excluded"]:
            path = os.path.join(_code.DL, f"expected_{name}", tid.replace("/", "_") + ".pkl")
            if os.path.exists(path):
                os.remove(path)


def qa_rows(name):
    import pandas as pd
    if name == "hotpotqa":
        for r in pd.read_parquet(os.path.join(DL, "hotpotqa", "validation.parquet")).to_dict("records"):
            ctx = [[t, list(ss)] for t, ss in zip(r["context"]["title"], r["context"]["sentences"])]
            yield {"id": f"hotpotqa/{r['id']}", "question": r["question"], "gold": r["answer"], "context": ctx,
                   "bucket": r["type"], "hard": r["type"] == "bridge"}
    else:
        for r in pd.read_parquet(os.path.join(DL, "2wiki", "dev.parquet")).to_dict("records"):
            yield {"id": f"twowiki/{r['_id']}", "question": r["question"], "gold": r["answer"],
                   "context": json.loads(r["context"]), "bucket": r["type"],
                   "hard": r["type"] in ("compositional", "bridge_comparison", "inference")}


def qa_splits():
    os.makedirs(os.path.join(ROOT, "data", "qa"), exist_ok=True)
    na, nb, nt = QA_SPLITS
    for name in ("hotpotqa", "twowiki"):
        rows = list(qa_rows(name))
        random.Random(0).shuffle(rows)
        for split, part in (("dev_a", rows[:na]), ("dev_b", rows[na:na + nb]), ("test", rows[na + nb:na + nb + nt])):
            with open(os.path.join(ROOT, "data", "qa", f"{name}_{split}.jsonl"), "w") as f:
                f.write("\n".join(json.dumps(r, ensure_ascii=False) for r in part) + "\n")
        print(name, len(rows), "->", na, nb, nt)


if __name__ == "__main__":
    download()
    if "--code-only" not in sys.argv:
        qa_splits()
    code_splits()
