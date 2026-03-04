# Mechanism Document

Source plan: `/scratch/ts1v23/workspace/vibe_coding/codex_auto_demo/plan_mlp_random_data.md`  
Aligned plan: `/scratch/ts1v23/workspace/vibe_coding/codex_auto_demo/.codex-research/plan/normalized_plan.md`

## What this harness controls
This harness defines a deterministic experiment lifecycle for the `vibe_test` project:
- deterministic data generation
- deterministic training/evaluation
- checkpointed progress and run registry
- mandatory repository synchronization policy

## Artifact contract
- Data: `artifacts/data/train.pt`, `artifacts/data/val.pt`
- Logs: `artifacts/logs/train_progress.jsonl`, `artifacts/logs/eval_progress.jsonl`
- Checkpoints: `artifacts/checkpoints/last.pt`, `artifacts/checkpoints/best.pt`
- Reports: `artifacts/final_report.json`

## Control loops
1. Task orchestration loop (`run_plan.sh`): executes T01..T07 in fixed order.
2. Task execution loop (`run_one_task.sh`): maps a task ID to concrete command(s).
3. Progress loop: each transition is recorded in `run_registry.jsonl` and mirrored in `session_progress.md`.
4. Sync loop: checkpoint routine attempts git commit and push to `https://github.com/CHDTevior/vibe_test.git`.

## Failure behavior
- Any missing mandatory artifact or NaN/Inf causes explicit failure.
- Failures are recorded in registry with timestamp and task context.
- A failed checkpoint does not silently continue to next checkpoint in full plan run.

## Deterministic defaults
- seed: 123
- full training epochs: 10
- smoke test epochs: 2
- model constraints: max 2 hidden layers, hidden <= 32
- hardware: CPU
