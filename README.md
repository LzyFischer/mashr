# MAS-HR: residual harness for harnesses

A meta-agent designs a team of task agents for every problem; dataset-level RSI improves the harnesses
it works with (v7). Two time scales:

- **fast loop (per problem)**: the meta-agent (Qwen3.5-9B, thinking medium) reads its meta-harness (a
  numbered list of rules), the task agents, the fixed tool and skill libraries and the problem, and
  writes the team as Python-like code (parsed, never executed); it does not solve the problem itself.
  Each node = a task agent (its role: the *self harness*), its input nodes, and
  the *residual harness* the meta-agent hands it for this problem: tools (Python functions preloaded
  in its sandbox; no tools = no Python; one run) and skills (how-to texts). Task agents do not think.
  Unusable output -> the first task agent alone with python (no second try).
- **slow loop (per dataset, offline)**: the evolver (Qwen3.8-27B, thinking high) reads a report of the
  current organization on dev-A and proposes edits on two layers: task agents (add / remove / edit a
  role) and the meta-harness (add / edit / remove a rule). Of the K=3 candidates per round, one may
  edit only the task-agent layer, one only the meta-agent layer, one both. A dev-B gate picks the
  winner; test is run once at the end. Start: the hand-written org.SEED.

## Layout

```
mashr/llm.py      sampling (Tinker, or local vLLM for MASHR_LOCAL_MODELS), thinking budgets, sqlite cache
mashr/ledger.py   time and token cost per stage (costs.json)
mashr/tools.py    the tool library (hand-written, fixed, each with a sandbox test)
mashr/skills.py   the skill library (hand-written for MATH, fixed)
mashr/org.py      the organization: schema, limits, meta-agent prompt, parser, edit ops, seed, baselines
mashr/engine.py   Python sandbox, answer extraction, cost; Engine = meta-agent call + plan executor
mashr/rsi.py      the RSI loop: dev-A report, evolver proposals (AHE-style prompt), dev-B gate, test
mashr/bench.py    datasets (math, aflow_math, gsmhard, aime): splits, answer formats, graders
scripts/          run.sh (an RSI run), dump_prompts, test_ablation, prepare_bench
data/             MATH (prm800k splits), data/bench/ (built by scripts/prepare_bench.py)
results/          see results/README.md: cache/ (LLM call cache), v7/ (runs of this code), v6/
docs/             reports; ahe_prompts.md (the AHE paper's prompts, for comparison)
archive/          tarballs: code of v1-v5 and of v6, results of v1-v5, v6 smoke/aborted runs
```

## Run

```
scripts/run.sh math <name> --seed 0 --objective acc --rounds 5 --k 3 --n-dev-b 50 --meta-thinking medium
```

`scripts/run.sh` sources the Tinker env (evolver), points the task agents and the meta-agent at local
vLLM (Qwen/Qwen3.5-9B on port 8001) and writes `results/v7/<name>/` (log.txt, console.out,
round_N/{pool.json, report.md, candidates.json}, trace.json, final_pool.json, test.json, costs.json).
Without `MASHR_LOCAL_MODELS` the 9B runs on Tinker too. Phase 2 (cost): `--init-pool
<final_pool.json> --objective cost`. `scripts/run_dump_prompts.sh <name>` writes every prompt and
example runs of a finished run to `results/v7/<name>/prompts_and_examples.md`.

Two processes share the cache but not the in-flight dedupe: do not start identical evaluations in
parallel processes (the second would resample instead of waiting).
