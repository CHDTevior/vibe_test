Task execution rules for Codex worker:

- Implement tasks in order from `task_plan.json`.
- If required input files are missing, fail explicitly with a concrete error and the exact path.
- All scripts should be deterministic and CPU-safe.
- Log progress before and after each task using `.codex-research/session_progress.md`.
- Append each checkpoint to `.codex-research/run_registry.jsonl` with status `started`, `passed`, or `failed`.
- Progress sync is mandatory: run git commit/push to remote target at every checkpoint unless `SKIP_GIT_SYNC=1`.
- Never skip quality gates (smoke test, loss finiteness, artifact presence).

Recommended CLI conventions:
- Seeds are fixed in every execution path unless user overrides.
- Train default is 10 epochs.
- Smoke test default is 2 epochs.
