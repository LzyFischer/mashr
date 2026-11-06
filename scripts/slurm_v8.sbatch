#!/usr/bin/env bash
#SBATCH -A uvadm
#SBATCH -p gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100_80gb
#SBATCH -c 32
#SBATCH --mem=160G
#SBATCH -t 2-00:00:00
#SBATCH -o /sfs/weka/scratch/vjd5zr/project/mashr/results/v8/_logs/%x_%j.out
# v8 RSI runs on one A100-80G: a local vLLM server (Qwen3.5-9B: task agents + meta-agent) and the RSI
# processes of the given tasks on the same node; the evolver (Qwen3.8-27B) runs on Tinker.
#   sbatch -J v8_a scripts/slurm_v8.sbatch math humaneval_plus mbpp_plus
# Each task first gets a smoke run (1 round, 8 problems per split, results/v8/_smoke/<task>); the full
# run (results/v8/<task>) starts only if its smoke run finished. Extra rsi args: RSI_ARGS="...".
set -uo pipefail
ROOT=/sfs/weka/scratch/vjd5zr/project/mashr
PY=${MASHR_PYTHON:-/sfs/weka/scratch/vjd5zr/envs/mashr/bin/python}          # venv on top of memrx
VLLM=${VLLM_BIN:-/project/uvadm/zhenyu/miniconda3/envs/memrx/bin/vllm}
TINKER_ENV=${TINKER_ENV:-/sfs/weka/scratch/vjd5zr/tinker.env}
MODEL=Qwen/Qwen3.5-9B
# one vLLM per job: several jobs can land on one node, so the port comes from the job id (and must be free)
PORT=${PORT:-$((20000 + ${SLURM_JOB_ID:-1} % 20000))}
while (echo > /dev/tcp/127.0.0.1/$PORT) 2>/dev/null; do PORT=$((PORT + 1)); done
echo "[job] vLLM port $PORT"
cd "$ROOT" || exit 1
mkdir -p results/v8/_logs results/cache

[[ -f "$TINKER_ENV" ]] || { echo "[job] $TINKER_ENV not found (it must set TINKER_API_KEY)"; exit 1; }
set -a; source "$TINKER_ENV"; set +a
[[ -n "${TINKER_API_KEY:-}" ]] || { echo "[job] TINKER_API_KEY is not set by $TINKER_ENV"; exit 1; }

module load gcc/14.2.0 2>/dev/null   # compute-node libstdc++ lacks CXXABI_1.3.15
export HF_HOME=/sfs/weka/scratch/vjd5zr/.cache/huggingface PYTHONUNBUFFERED=1
export MASHR_LOCAL_MODELS=$MODEL MASHR_LOCAL=http://localhost:$PORT/v1 MASHR_PY=$PY
export MASHR_BIRD=/sfs/weka/scratch/vjd5zr/data/bird/dev_20240627
export ALFWORLD_DATA=/sfs/weka/scratch/vjd5zr/data/alfworld

hostname; nvidia-smi --query-gpu=name,memory.total --format=csv
VLOG=results/v8/_logs/vllm_${SLURM_JOB_ID:-local}.log
"$VLLM" serve "$MODEL" --served-model-name "$MODEL" --port "$PORT" --language-model-only \
    --gpu-memory-utilization 0.90 --max-model-len 32768 --dtype bfloat16 --seed 0 > "$VLOG" 2>&1 &
VPID=$!
trap 'kill $VPID 2>/dev/null; pkill -P $$ 2>/dev/null' EXIT
for t in $(seq 360); do
  curl -sf "http://localhost:$PORT/health" >/dev/null 2>&1 && break
  kill -0 $VPID 2>/dev/null || { echo "[vllm] died, see $VLOG"; tail -20 "$VLOG"; exit 1; }
  sleep 5
done
curl -sf "http://localhost:$PORT/health" >/dev/null || { echo "[vllm] not ready after 30 min"; exit 1; }
echo "[vllm] ready $(date)"

run_task() {   # smoke run, then the full run
  local task=$1
  export MASHR_CACHE=$ROOT/results/cache/v8_${task}.sqlite      # one sqlite per process (network FS)
  mkdir -p "results/v8/_smoke/$task" "results/v8/$task"
  local base
  base=$("$PY" -c "from mashr import tasks; print(next(iter(tasks.get('$task').BASELINES)))") || return 1
  echo "[$task] smoke start $(date)"
  if ! "$PY" -m mashr.rsi --task "$task" --out "results/v8/_smoke/$task" --rounds 1 --k 3 \
        --n-dev-a 8 --n-dev-b 8 --n-test 8 --baselines "$base" > "results/v8/_smoke/$task/console.out" 2>&1; then
    echo "[$task] SMOKE FAILED $(date): $(tail -3 results/v8/_smoke/$task/console.out | tr '\n' ' ')"
    return 1
  fi
  echo "[$task] smoke ok $(date); full run start"
  if "$PY" -m mashr.rsi --task "$task" --out "results/v8/$task" --seed 0 --rounds 5 --k 3 \
        --meta-thinking medium ${RSI_ARGS:-} > "results/v8/$task/console.out" 2>&1; then
    echo "[$task] DONE $(date): $(grep '^TEST' results/v8/$task/log.txt | cut -c1-300)"
  else
    echo "[$task] FULL RUN FAILED $(date): $(tail -3 results/v8/$task/console.out | tr '\n' ' ')"
  fi
}

for task in "$@"; do run_task "$task" & done
wait $(jobs -p | grep -v "^$VPID$")
echo "[job] all tasks finished $(date)"
