#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

export PYTHONHASHSEED=123
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

python scripts/generate_data.py \
  --seed 123 \
  --num-samples 400 \
  --num-features 16 \
  --train-ratio 0.8 \
  --noise-std 0.02 \
  --artifact-root artifacts/data

bash scripts/run_train.sh \
  --seed 123 \
  --epochs 2 \
  --batch-size 32 \
  --lr 0.01 \
  --hidden-dim 24 \
  --data-root artifacts/data \
  --artifacts-root artifacts \
  --no-git-sync

python src/eval.py \
  --seed 123 \
  --checkpoint artifacts/checkpoints/last_epoch_2.pt \
  --data-root artifacts/data

python - <<'PY'
import pathlib, json, sys
checks = {
    "train": pathlib.Path("artifacts/logs/train_progress.jsonl"),
    "eval": pathlib.Path("artifacts/logs/eval_progress.jsonl"),
    "ckpt_last": pathlib.Path("artifacts/checkpoints/last_epoch_2.pt"),
    "ckpt_best": pathlib.Path("artifacts/checkpoints/best.pt"),
}
for name, path in checks.items():
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {path}")

for path in [checks["train"], checks["eval"]]:
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    if not lines:
        raise SystemExit(f"Empty progress log: {path}")

print(json.dumps({"smoke_test": "passed"}))
PY
