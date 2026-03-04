# CODEX Workflow for this Harness

## Inputs
- Normalized plan and metadata files in `.codex-research/`.
- Existing project code under `src/`, `scripts/`, and `artifacts/`.

## Execution Model
1. Read `research_spec.md` and `task_plan.json`.
2. Run `.codex-research/init.sh` once unless already initialized.
3. Execute ordered tasks via `.codex-research/run_plan.sh`.
4. For each task:
   - Mark status in `session_progress.md`.
   - Append a structured record to `run_registry.jsonl`.
   - Run the requested command or script.
   - Sync repository state to configured remote target.

## State Rules
- `passes:false` means incomplete or not verified.
- On successful completion, set `passes:true` in tracking records.
- If any step fails, stop current run and record failure with error context in registry.

## Determinism Contracts
- Fixed seeds across generation, training, and evaluation.
- Explicitly pinned defaults for epochs, batch size, LR, and hidden size.
- Artifact paths must remain under `artifacts/`.
