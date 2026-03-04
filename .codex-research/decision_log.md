# Decision Log

## 2026-03-04

1. Problem type: choose regression (MSE)
- Decision: Use MSE as primary metric (matches numeric targets from synthetic generator).
- Rationale: lower regression noise and better aligns with deterministic synthetic labels.

2. Checkpoint policy: best + latest
- Decision: Save both `best.pt` and `last.pt`.
- Rationale: best enables quick reporting while last preserves full step continuity.

3. Config style: argparse-first with optional YAML
- Decision: Use argparse for all required CLI commands; optionally read YAML blocks where supported.
- Rationale: minimal dependencies and clear deterministic defaults while allowing extension.

4. Sync granularity
- Decision: synchronize on each major checkpoint and after each task in run flow.
- Rationale: satisfies plan requirement on progress propagation and avoids silent stale metadata.

5. Deterministic run target
- Decision: enforce 10 epochs in full path and 2 epochs in smoke path.
- Rationale: fixed schedule is required and provides predictable runtime.
