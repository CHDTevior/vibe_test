#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:?Usage: $0 <TASK_ID>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

sync_progress() {
  local note="$1"
  if [ "${SKIP_GIT_SYNC:-0}" = "1" ]; then
    return
  fi
  if [ -d .git ]; then
    git add -A
    git commit -m "${note}" >/dev/null 2>&1 || true
    git pull --rebase codex_target main >/dev/null 2>&1 || true
    git push codex_target HEAD >/dev/null 2>&1 || true
  fi
}

record_task() {
  python - "$task_id" <<'PY'
import datetime
import json
import pathlib
import sys

task_id = sys.argv[1]

root = pathlib.Path('.codex-research/run_registry.jsonl')
entry = {
    'run_id': 'run_one_task',
    'status': 'done',
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    'task': task_id,
}
with root.open('a', encoding='utf-8') as f:
    f.write(json.dumps(entry) + '\n')
PY
}

task_id="$TASK_ID"
case "${task_id}" in
  T01)
    bash .codex-research/init.sh ;;
  T02)
    python scripts/generate_data.py --seed 123 --num-samples 2048 --num-features 16 --train-ratio 0.8 --noise-std 0.01 --artifact-root artifacts/data ;;
  T03)
    python -m py_compile src/model.py ;;
  T04)
    bash scripts/run_train.sh --seed 123 --epochs 10 --batch-size 64 --lr 0.01 --hidden-dim 24 --data-root artifacts/data --artifacts-root artifacts ;;
  T05)
    python src/eval.py --seed 123 --checkpoint artifacts/checkpoints/best.pt --data-root artifacts/data ;;
  T06)
    bash .codex-research/checks/smoke_test.sh ;;
  T07)
    python - <<'PY'
from pathlib import Path
import json
root = Path('artifacts/logs')
report = {
    'status': 'completed',
    'train_progress_exists': (root / 'train_progress.jsonl').exists(),
    'eval_progress_exists': (root / 'eval_progress.jsonl').exists(),
}
Path('artifacts/final_report.json').write_text(json.dumps(report, indent=2))
print(report)
PY
    ;;
  T08)
    python - <<'PY'
import json
from pathlib import Path

train_log = Path('artifacts/logs/train_progress.jsonl')
eval_log = Path('artifacts/logs/eval_progress.jsonl')
report = {
    'status': 'completed',
    'train_progress_exists': train_log.exists(),
    'eval_progress_exists': eval_log.exists(),
    'best_epoch': None,
    'best_val_mse': None,
}

if train_log.exists():
    entries = [json.loads(line) for line in train_log.read_text(encoding='utf-8').splitlines() if line.strip()]
    best = min(entries, key=lambda e: float(e.get('val_mse', float('inf')))
    )
    report['best_epoch'] = best.get('epoch')
    report['best_val_mse'] = best.get('val_mse')

if eval_log.exists():
    eval_entries = [json.loads(line) for line in eval_log.read_text(encoding='utf-8').splitlines() if line.strip()]
    last = eval_entries[-1] if eval_entries else {}
    report['latest_eval'] = last

Path('artifacts/final_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
PY
    ;;
  *)
    echo "Unknown task id: ${task_id}" >&2
    echo "Supported: T01, T02, T03, T04, T05, T06, T07, T08" >&2
    exit 1
    ;;
esac

sync_progress "Codex checkpoint ${task_id}"
record_task
