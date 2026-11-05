#!/bin/bash
# v7: task agents + meta-agent on local vLLM (port 8001), evolver (27B) on Tinker.
# usage: scripts/run.sh <task: math|bird|alfworld> <out-name> [extra mashr.rsi args...]
# Python: ~/envs/alfw (a venv on top of the tinker env, with alfworld installed).
cd ~/project/mas-hr
set -a; source ~/.config/hrsi/tinker.env; set +a
export MASHR_LOCAL_MODELS=Qwen/Qwen3.5-9B MASHR_LOCAL=http://localhost:8001/v1
task=$1; name=$2; shift 2
mkdir -p "results/v7/$name"
~/envs/alfw/bin/python -m mashr.rsi --task "$task" --out "results/v7/$name" "$@" \
  > "results/v7/$name/console.out" 2>&1
