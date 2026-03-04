# Mini MLP Training Plan on Pre-Generated Random Data

## Objectives

- Build a minimal, reproducible ML workflow that trains a very small MLP on synthetic data generated in advance.
- Verify that training loss decreases and validation metric improves over baseline.
- Keep implementation simple enough to run on CPU in under 2 minutes.

## Constraints

- Use pre-generated random data only (no online data fetching).
- Keep model small: <= 2 hidden layers, hidden size <= 32.
- Use deterministic seeds for dataset generation and training.
- Keep dependencies minimal (prefer Python + PyTorch only).

## Environment and Resources

- Runtime: local Python 3.10+.
- Framework: PyTorch.
- Hardware: CPU only is sufficient.
- Output artifacts should be stored under `artifacts/`.

## Milestones

1. Create reproducible synthetic dataset generation script and save train/val files.
2. Implement tiny MLP model and training loop.
3. Add evaluation, logging, and a quick smoke test.
4. Confirm end-to-end run works from clean environment.

## Task Checklist

- [ ] Create project skeleton: `src/`, `configs/`, `scripts/`, `artifacts/`.
- [ ] Implement `scripts/generate_data.py` to pre-generate random features and labels.
- [ ] Save dataset files to disk (e.g., `artifacts/data/train.pt`, `artifacts/data/val.pt`).
- [ ] Implement `src/model.py` with a tiny MLP (input -> hidden -> output).
- [ ] Implement `src/train.py` with DataLoader, optimizer, loss, and train loop.
- [ ] Add command-line arguments or config for epochs, batch size, lr, seed, hidden dim.
- [ ] Implement `src/eval.py` for validation metric and simple report output.
- [ ] Add logging of per-epoch train/val loss to console and `artifacts/logs/`.
- [ ] Add `scripts/run_train.sh` to execute full pipeline deterministically.
- [ ] Add `scripts/smoke_test.sh` to run a very short training (e.g., 2 epochs) and verify outputs exist.
- [ ] Document usage in `README.md`.
- [ ] Record final summary: best validation loss and runtime.

## Evaluation and Success Criteria

- Primary metric: validation MSE (or BCE if using binary labels) decreases compared with epoch-0 baseline.
- Sanity checks:
  - Training loss decreases for most epochs.
  - No NaN/Inf in loss.
  - Checkpoint/log files are generated.
- Reproducibility checks:
  - Running with same seed gives near-identical metrics.
  - Smoke test passes on a clean run.

## Risks and Mitigations

- Risk: random labels may be unlearnable.
  - Mitigation: generate labels from a known function of inputs plus small noise.
- Risk: overfitting due to tiny dataset.
  - Mitigation: keep train/val split and monitor both losses.
- Risk: nondeterministic behavior.
  - Mitigation: set seeds for Python, NumPy, and PyTorch.

## Open Questions

- Should task target be regression or binary classification? (default: regression with MSE)
- Should checkpoints save every epoch or only best model?
- Preferred config style: argparse-only or YAML config?

## human add:
- 使用conda创建虚拟环境vibe_test，默认使用pip安装依赖
- 只训练10个epoch
- 进展文件需要记录关键metric
- 每次进展需要更新到的git仓库路径：https://github.com/CHDTevior/vibe_test.git
- 该项目不使用slurm系统，只使用cpu