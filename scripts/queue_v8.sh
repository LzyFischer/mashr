#!/bin/bash
# The v8 run queue read by scripts/worker_v8.sbatch.
#   scripts/queue_v8.sh add <task> [run-name] [rsi args...]   e.g. add math math_s1 --seed 1
#   scripts/queue_v8.sh status
#   scripts/queue_v8.sh retry <run-name>                     move a failed run back to pending
Q=$(cd "$(dirname "$0")/.." && pwd)/results/v8/_queue
mkdir -p "$Q"/{pending,running,done,failed}
case "$1" in
  add)
    task=$2; name=${3:-$2}; shift 3 2>/dev/null || shift $#
    f="$Q/pending/$(date +%Y%m%d%H%M%S%N)_$name"
    printf '%s\n%s\n%s\n' "$task" "$name" "$*" > "$f.tmp" && mv "$f.tmp" "$f" && echo "queued $name ($task) $*" ;;
  status)
    for s in pending running done failed; do
      echo "$s: $(ls "$Q/$s" 2>/dev/null | sed -E 's/^[0-9]+_//' | tr '\n' ' ')"; done
    echo "workers: $(squeue -u "$USER" -h -n v8_worker -o '%i:%T:%N' | tr '\n' ' ')" ;;
  retry)
    f=$(ls "$Q/failed" | grep -E "_$2$" | head -1)
    [ -n "$f" ] && mv "$Q/failed/$f" "$Q/pending/$f" && echo "requeued $2" || echo "no failed run $2" ;;
  *) sed -n 2,5p "$0" ;;
esac
