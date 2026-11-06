#!/usr/bin/env bash
#SBATCH -A uvadm
#SBATCH -p gpu
#SBATCH --gres=gpu:1
#SBATCH --constraint=a100_80gb|a6000|a40|rtxpro6000|b200
#SBATCH -c 16
#SBATCH --mem=128G
#SBATCH -t 1-00:00:00
#SBATCH -o /sfs/weka/scratch/vjd5zr/project/mashr/results/v8/_logs/%x_%j.out
# A v8 worker: one GPU, one vLLM server (Qwen3.5-9B), and RSI runs taken one after another from the
# queue results/v8/_queue/pending/ (scripts/queue_v8.sh add ...), up to PAR at a time. The GPU is kept
# while there is work: when the queue has been empty (and nothing runs) for IDLE_MIN minutes, the worker
# exits. Each run: a smoke run (1 round, 8 problems per split, results/v8/_smoke/<name>), then the full
# run (results/v8/<name>). The evolver (Qwen3.8-27B) runs on Tinker.
#   sbatch -J v8_worker scripts/worker_v8.sbatch
set -uo pipefail
ROOT=/sfs/weka/scratch/vjd5zr/project/mashr
PY=${MASHR_PYTHON:-/sfs/weka/scratch/vjd5zr/envs/mashr/bin/python}
VLLM=${VLLM_BIN:-/project/uvadm/zhenyu/miniconda3/envs/memrx/bin/vllm}
TINKER_ENV=${TINKER_ENV:-/sfs/weka/scratch/vjd5zr/tinker.env}
MODEL=Qwen/Qwen3.5-9B
PAR=${PAR:-2}              # runs at a time on this GPU
IDLE_MIN=${IDLE_MIN:-30}   # minutes with an empty queue and nothing running before the GPU is released
Q=$ROOT/results/v8/_queue
ME=${SLURM_JOB_ID:-local}
cd "$ROOT" || exit 1
mkdir -p results/v8/_logs results/cache "$Q"/{pending,running,done,failed}

if [[ -z "${DRY_RUN:-}" ]]; then     # DRY_RUN=1: test the queue loop without Tinker, vLLM or RSI
  [[ -f "$TINKER_ENV" ]] || { echo "[worker] $TINKER_ENV not found (it must set TINKER_API_KEY)"; exit 1; }
  set -a; source "$TINKER_ENV"; set +a
  [[ -n "${TINKER_API_KEY:-}" ]] || { echo "[worker] TINKER_API_KEY is not set by $TINKER_ENV"; exit 1; }
fi

# one vLLM per job: several jobs can land on one node, so the port comes from the job id (and must be free)
PORT=${PORT:-$((20000 + ${SLURM_JOB_ID:-1} % 20000))}
while (echo > /dev/tcp/127.0.0.1/$PORT) 2>/dev/null; do PORT=$((PORT + 1)); done
module load gcc/14.2.0 2>/dev/null   # compute-node libstdc++ lacks CXXABI_1.3.15
export HF_HOME=/sfs/weka/scratch/vjd5zr/.cache/huggingface PYTHONUNBUFFERED=1
export MASHR_LOCAL_MODELS=$MODEL MASHR_LOCAL=http://localhost:$PORT/v1 MASHR_PY=$PY
export MASHR_BIRD=/sfs/weka/scratch/vjd5zr/data/bird/dev_20240627
export ALFWORLD_DATA=/sfs/weka/scratch/vjd5zr/data/alfworld

echo "[worker] $(hostname) port $PORT PAR $PAR IDLE_MIN $IDLE_MIN"
VLOG=results/v8/_logs/vllm_$ME.log
if [[ -n "${DRY_RUN:-}" ]]; then
  sleep infinity & VPID=$!
  run_task() { echo "[$(sed -n 2p "$1")] dry run $(date +%T)"; sleep "${DRY_SECONDS:-3}"; }
else
nvidia-smi --query-gpu=name,memory.total --format=csv
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

run_task() {   # <queue file in running/>: line 1 task, line 2 run name (default: the task), line 3 rsi args
  local f=$1 task name args base rc=0
  task=$(sed -n 1p "$f"); name=$(sed -n 2p "$f"); args=$(sed -n 3p "$f"); name=${name:-$task}
  export MASHR_CACHE=$ROOT/results/cache/v8_${task}.sqlite      # one sqlite per task (network FS)
  mkdir -p "results/v8/_smoke/$name" "results/v8/$name"
  base=$("$PY" -c "from mashr import tasks; print(next(iter(tasks.get('$task').BASELINES)))") || return 1
  echo "[$name] smoke start $(date)"
  if ! "$PY" -m mashr.rsi --task "$task" --out "results/v8/_smoke/$name" --rounds 1 --k 3 \
        --n-dev-a 8 --n-dev-b 8 --n-test 8 --baselines "$base" $args > "results/v8/_smoke/$name/console.out" 2>&1; then
    echo "[$name] SMOKE FAILED $(date): $(tail -3 results/v8/_smoke/$name/console.out | tr '\n' ' ')"
    return 1
  fi
  echo "[$name] smoke ok $(date); full run start"
  if "$PY" -m mashr.rsi --task "$task" --out "results/v8/$name" --seed 0 --rounds 5 --k 3 \
        --meta-thinking medium $args > "results/v8/$name/console.out" 2>&1; then
    echo "[$name] DONE $(date): $(grep '^TEST' results/v8/$name/log.txt | cut -c1-300)"
  else
    echo "[$name] FULL RUN FAILED $(date): $(tail -3 results/v8/$name/console.out | tr '\n' ' ')"; rc=1
  fi
  return $rc
}
fi

claim() {      # move the first pending task to running/ (rename is atomic: one worker wins)
  local f
  for f in $(ls "$Q/pending" 2>/dev/null | sort); do
    mv "$Q/pending/$f" "$Q/running/$f.$ME" 2>/dev/null && { echo "$Q/running/$f.$ME"; return 0; }
  done
  return 1
}

idle_since=$(date +%s)
pids=()
while true; do
  kill -0 $VPID 2>/dev/null || { echo "[worker] vLLM died $(date), see $VLOG"; break; }
  alive=(); for p in "${pids[@]}"; do kill -0 "$p" 2>/dev/null && alive+=("$p"); done; pids=("${alive[@]}")
  n=${#pids[@]}
  if (( n < PAR )) && f=$(claim); then
    ( run_task "$f" && dest=done || dest=failed; b=$(basename "$f"); mv "$f" "$Q/$dest/${b%.$ME}" ) &
    pids+=($!); idle_since=$(date +%s); sleep 5; continue
  fi
  (( n > 0 )) && idle_since=$(date +%s)
  if (( n == 0 && $(date +%s) - idle_since >= IDLE_MIN * 60 )); then
    echo "[worker] queue empty and nothing running for $IDLE_MIN min; releasing the GPU $(date)"; break
  fi
  sleep "${POLL_SECONDS:-30}"
done
for p in "${pids[@]}"; do wait "$p" 2>/dev/null; done
echo "[worker] finished $(date)"
