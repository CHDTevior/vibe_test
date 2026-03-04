#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

TASKS=(T01 T02 T03 T04 T05 T06 T07 T08)

append_registry() {
  local task="$1"
  local status="$2"
  python - "$task" - "$status" <<'PY'
import datetime
import json
import pathlib
import sys

task = sys.argv[1]
status = sys.argv[2]

root = pathlib.Path('.codex-research/run_registry.jsonl')
entry = {
    'run_id': 'full_plan',
    'task': task,
    'status': status,
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
}
with root.open('a', encoding='utf-8') as f:
    f.write(json.dumps(entry) + '\n')
PY
}

for task_id in "${TASKS[@]}"; do
  append_registry "${task_id}" "started"
  bash .codex-research/run_one_task.sh "${task_id}"
  append_registry "${task_id}" "passed"

done

cat >> .codex-research/session_progress.md <<'EOF'
- [x] run_plan.sh completed all task IDs: T01 T02 T03 T04 T05 T06 T07 T08
EOF
