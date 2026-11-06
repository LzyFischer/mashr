# MAS-HR: residual harness for harnesses

A meta-agent designs a team of task agents for every problem; dataset-level RSI improves the harnesses
it works with (v8). The evolver learns which parts are general (the task agents' roles) and which vary
per problem (skills, tools and the rules for giving them); the meta-agent fills in the varying part on
each problem. Two time scales:

- **fast loop (per problem)**: the meta-agent (Qwen3.5-9B, thinking medium) reads its meta-harness (a
  numbered list of rules), the task agents, the tool and skill libraries and the problem, and
  writes the team as Python-like code (parsed, never executed); it does not solve the problem itself.
  Each node = a task agent (its role: the *self harness*, the same on every problem), its input
  nodes, and the *residual harness* the meta-agent hands it for this problem: tools (Python functions
  preloaded in its sandbox; no tools = no Python) and skills (how-to texts). Task agents do not think.
  Unusable output -> the first task agent alone with the fallback tools (no second try).
- **slow loop (per dataset, offline)**: the evolver (Qwen3.8-27B, thinking high) reads a report of the
  current organization on dev-A (with the full traces of the wrong problems and, after an accepted
  change, the problems it fixed and broke) and proposes edits on three layers: task agents (add /
  remove / edit a role), the meta-harness (add / edit / remove a rule) and the libraries (add / edit a
  skill or a tool; never removed; a new tool must pass its sandbox test). Each change may cite the wrong
  dev-A problems that show its pattern; the prompt carries AHE/RRSI-style
  generality constraints and an annealed edit budget (--max-ops). Of the K=3 candidates per round,
  one may edit only the self harness (roles), one only the residual side (rules + libraries), one
  all. A dev-B gate picks the winner; test is run once at the end. Start: the task's hand-written SEED.

## Layout

```
mashr/llm.py      sampling (Tinker, or local vLLM for MASHR_LOCAL_MODELS), thinking budgets, sqlite cache
mashr/ledger.py   time and token cost per stage (costs.json)
mashr/sandbox.py  the Python sandbox (no network, memory / CPU / file-size limits)
mashr/org.py      the organization: schema, limits, meta-agent prompt, parser, edit ops (incl. libraries)
mashr/engine.py   answer voting, cost; Engine = meta-agent call + plan executor
mashr/rsi.py      the RSI loop: dev-A report with traces, evolver proposals, dev-B gate, history, test
mashr/tasks/      one module per task: starting libraries, seed, baselines, splits, run_node, grader
                  math (+ math_tools, math_skills), bird, alfworld,
                  humaneval_plus, mbpp_plus (_code.py: EvalPlus grading), hotpotqa, twowiki (_qa.py)
scripts/          run.sh (an RSI run), prepare_data.py (v8 benchmarks), prepare_bench.py (v6 data/bench)
data/             math/ (prm800k splits), code/splits.json, qa/ (built by scripts/prepare_data.py),
                  _download/ (raw files, git-ignored), bench/ + transfer/ (v6, unused)
results/          see results/README.md: cache/ (LLM call cache), v8/ (runs of this code), v7/, v6/
docs/             reports, ahe_prompts.md (the AHE paper's prompts, for comparison)
archive/          tarballs: code of v1-v5 and of v6, results of v1-v5, v6 smoke/aborted runs
```

## Benchmarks (v8)

| task | data | splits (dev-A / dev-B / test) | correct = | node |
|---|---|---|---|---|
| `humaneval_plus` | HumanEval+ (EvalPlus v0.1.10) | 50 / 30 / 83 | passes base + plus tests (official checker) | writes the function; with tools runs Python up to 3 times |
| `mbpp_plus` | MBPP+ (EvalPlus v0.2.0) | 100 / 50 / 227 | passes base + plus tests | same |
| `hotpotqa` | HotpotQA dev, distractor (10 paragraphs) | 150 / 50 (pool 200) / 500 | exact match (official normalization) | reads the paragraphs; with tools runs Python on them up to 3 times |
| `twowiki` | 2WikiMultihopQA dev | 150 / 50 (pool 200) / 500 | exact match | same |

Code problems whose canonical solution fails the official check are left out (HumanEval/32, Mbpp/255;
`data/code/splits.json` "excluded"). Setup, once: `python -I scripts/prepare_data.py` (network,
pandas + pyarrow) and, for the code tasks, `pip install --no-deps evalplus==0.3.1 && pip install tempdir
wget appdirs psutil numpy` in the run environment. Grading runs in `MASHR_CODE_CHECKS` (default 8)
spawned worker processes (not forked from the RSI process: EvalPlus caps each check's address space at
4 GB, which a child of the 128-thread RSI process already exceeds); the canonical outputs are cached per
problem in `data/_download/evalplus/expected_<task>/`.

## Run

```
scripts/run.sh math <name> --seed 0 --objective acc --rounds 5 --k 3 --n-dev-b 50 --meta-thinking medium
```

`scripts/run.sh` sources the Tinker env (evolver), points the task agents and the meta-agent at local
vLLM (Qwen/Qwen3.5-9B on port 8001) and writes `results/v8/<name>/` (log.txt, console.out,
round_N/{pool.json, report.md, meta_prompt.md, propose_prompt_<i>.md, candidates.json}, trace.json,
final_pool.json, test.json, costs.json).
Without `MASHR_LOCAL_MODELS` the 9B runs on Tinker too. Phase 2 (cost): `--init-pool
<final_pool.json> --objective cost`.

Two processes share the cache but not the in-flight dedupe: do not start identical evaluations in
parallel processes (the second would resample instead of waiting).
