#!/bin/bash
# usage: scripts/run_dump_prompts.sh <run-name>   (same env as run.sh; examples come from the cache)
cd ~/project/mas-hr
set -a; source ~/.config/hrsi/tinker.env; set +a
export MASHR_LOCAL_MODELS=Qwen/Qwen3.5-9B MASHR_LOCAL=http://localhost:8001/v1
~/miniconda3/envs/tinker/bin/python -c "import runpy,sys; sys.path.insert(0,'.'); sys.argv=['dump']+sys.argv[1:]; runpy.run_path('scripts/dump_prompts.py', run_name='__main__')" "$@"
