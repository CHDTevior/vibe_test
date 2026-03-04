# Research Specification: Deterministic Mini MLP CPU Harness

## Source
- Normalized plan: `.codex-research/plan/normalized_plan.md`
- Execution target: fully local, CPU-only, minimal dependencies

## Objective
Build an end-to-end, reproducible micro-workflow that trains a tiny MLP on pre-generated synthetic data and validates that performance improves with deterministic execution.

## Core Requirements
1. Use only pre-generated local synthetic data.
2. Model is small: at most 2 hidden layers, hidden size at most 32.
3. Deterministic seeds for all stochastic components.
4. Train for a fixed 10 epochs by default.
5. Defaults:
   - Environment: conda `vibe_test`
   - Backend: PyTorch + Python + NumPy
   - Hardware: CPU only (no Slurm)
   - Workspace: `artifacts/`
   - Repository synchronization path: `https://github.com/CHDTevior/vibe_test.git`

## Workflow
- Generate synthetic train/validation data from known function plus controlled noise.
- Train deterministic tiny MLP for 10 epochs.
- Evaluate validation MSE and ensure it improves relative to epoch-0 baseline.
- Log metrics to console and to `artifacts/logs/*.jsonl`.
- Maintain `session_progress.md` and `.codex-research/run_registry.jsonl` checkpoints.
- Sync progress updates to the configured repository at each checkpoint.

## Success Criteria
- Validation MSE improves versus baseline and remains finite.
- No NaN/Inf during training or evaluation.
- Required artifacts exist: train/val datasets, logs, checkpoints, final report.
- Smoke test passes with at least 2 deterministic epochs.
- Re-runs with same seed produce stable metric trajectory.

## Reproducibility Signals
- Use fixed seeds for Python, NumPy, and PyTorch.
- Deterministic DataLoader ordering.
- Explicit fixed defaults and no accidental runtime-dependent branch in model/training/eval.
