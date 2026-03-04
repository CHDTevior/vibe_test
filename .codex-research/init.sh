#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_NAME="${ENV_NAME:-vibe_test}"
REPO_URL="https://github.com/CHDTevior/vibe_test.git"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Install conda/miniforge and retry." >&2
  exit 1
fi

eval "$(conda shell.bash hook)"

if ! conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  conda create -n "${ENV_NAME}" python=3.10 -y
fi
conda activate "${ENV_NAME}"

python -m pip install --upgrade pip
python -m pip install --no-cache-dir torch numpy

mkdir -p "${PROJECT_ROOT}/src" \
  "${PROJECT_ROOT}/configs" \
  "${PROJECT_ROOT}/scripts" \
  "${PROJECT_ROOT}/artifacts" \
  "${PROJECT_ROOT}/artifacts/data" \
  "${PROJECT_ROOT}/artifacts/logs" \
  "${PROJECT_ROOT}/artifacts/checkpoints" \
  "${PROJECT_ROOT}/.codex-research/checks"

cat > "${PROJECT_ROOT}/requirements.txt" <<'EOF'
torch
numpy
EOF

if [ -d "${PROJECT_ROOT}/.git" ]; then
  git -C "${PROJECT_ROOT}" remote remove codex_target 2>/dev/null || true
  git -C "${PROJECT_ROOT}" remote add codex_target "${REPO_URL}" || true
fi

touch "${PROJECT_ROOT}/artifacts/.init_marker"
echo "Initialized project at ${PROJECT_ROOT} with conda env ${ENV_NAME}"
