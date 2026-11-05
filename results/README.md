# Results index

MATH test (156 questions, level 4-5, integer answers); cost = generated + 0.2 x prompt tokens per
question. Employees thinking off (`MASHR_MAX_THINK=off`), employees + HR on local Qwen3.5-9B, designer
Qwen3.8-27B on Tinker.

```
cache/cache.sqlite   shared LLM call cache (mashr/llm.py; MASHR_CACHE overrides)
v7/<run>/            one v7 RSI run (scripts/run.sh <task> <run>); v6/<run>/ the same for v6: (scripts/run.sh): log.txt, console.out, round_N/ (pool.json,
                     report.md, candidates.json), trace.json, final_pool.json, test.json, costs.json
v6/ablations/        test ablations of final organizations (scripts/test_ablation.py)
```

Earlier versions (v1-v5) and their results, and v6 smoke/aborted runs, are tarballs in `../archive/`.

## v7 (current code): meta-agent + residual harness, seed 0, dev-B 50, task agents without thinking

| task (test) | run | seed org | final org (5 RSI rounds) | best fixed baseline |
|---|---|---|---|---|
| MATH (156) | `v7/math` (prompts still asked to save cost) | 91.7% | **96.2%** | 91.7% (single, solve_verify) |
| BIRD dev (300) | `v7/bird` | **63.0%** | 61.0% | 58.7% (write_check) |
| ALFWorld valid_unseen (134) | `v7/alfworld` | 82.8% | **85.8%** | 48.5% (react with valid_actions) |

Aborted or crashed runs keep their partial output: `v7/math_direct_answer_aborted` (meta-agent was
allowed to answer itself), `v7/{bird,alfworld}_with_cost_prompt_aborted`, `v7/alfworld_crashed_disk_full{,_2}`
(fast-downward library copies filled the disk; fixed).

## v6

### Runs

| run | setting | round-0 org | final org | fixed baselines |
|---|---|---|---|---|
| `math_off` | HR thinking off, dev-B 200, leave-one-out on (before only_if was removed) | 94.2% @5.2k | 93.6% @5.4k | solve_verify_off 96.8% @2.8k, single_off 91.7% @1.5k |
| `math_off_s{0,1,2}` | 3 seeds, HR thinking off, dev-B 200 | mean 91.7% @4.9k | mean 90.6% @4.7k | solve_verify_off mean 94.7% @2.8k |
| `math_hrthink` | HR thinking medium, dev-B 50, seed 0 | 92.3% @6.6k | 92.3% @6.1k (HR 3.3k) | solve_verify_off 96.8% @2.8k |

`math_hrthink/prompts_and_examples.md`: every prompt and four full example runs
(`scripts/run_dump_prompts.sh <run>`).

### Ablations (same HR plans, one residual part removed from every node)

| file | organizations | full | no notes | no skills | no tools | structure only |
|---|---|---|---|---|---|---|
| `notes_skills_tools_off_s0-2.json` | final orgs of math_off_s0-2 (mean) | 90.4% | 94.2% | 91.0% | 90.0% | 94.4% |
| `notes_skills_tools_hrthink.json` | final org of math_hrthink | 92.3% | 94.9% | 93.0% | 91.7% | 93.6% |
