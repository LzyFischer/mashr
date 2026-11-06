#!/bin/bash
# v8: one RSI run, with the task agents + meta-agent on a vLLM server already running on this node
# (port 8001, Qwen/Qwen3.5-9B) and the evolver (27B) on Tinker. For batch runs (vLLM included) use
# scripts/slurm_v8.sbatch.
# usage: scripts/run.sh <task> <out-name> [extra mashr.rsi args...]
cd "$(dirname "$0")/.." || exit 1
set -a; source "${TINKER_ENV:-/sfs/weka/scratch/vjd5zr/tinker.env}"; set +a
PY=${MASHR_PYTHON:-/sfs/weka/scratch/vjd5zr/envs/mashr/bin/python}
export MASHR_LOCAL_MODELS=Qwen/Qwen3.5-9B MASHR_LOCAL=http://localhost:8001/v1 MASHR_PY=$PY
export HF_HOME=/sfs/weka/scratch/vjd5zr/.cache/huggingface
export MASHR_BIRD=/sfs/weka/scratch/vjd5zr/data/bird/dev_20240627 ALFWORLD_DATA=/sfs/weka/scratch/vjd5zr/data/alfworld
task=$1; name=$2; shift 2
export MASHR_CACHE=${MASHR_CACHE:-results/cache/v8_${task}.sqlite}
mkdir -p "results/v8/$name"
"$PY" -m mashr.rsi --task "$task" --out "results/v8/$name" "$@" > "results/v8/$name/console.out" 2>&1
