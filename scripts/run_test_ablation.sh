#!/bin/bash
# usage: scripts/run_test_ablation.sh <out.json> <hr-thinking> <run>:<seed> ...   (see test_ablation.py)
cd ~/project/mas-hr
export MASHR_LOCAL_MODELS=Qwen/Qwen3.5-9B MASHR_LOCAL=http://localhost:8001/v1
PYTHONPATH=. ~/miniconda3/envs/tinker/bin/python scripts/test_ablation.py "$@" > "${1%.json}.out" 2>&1
