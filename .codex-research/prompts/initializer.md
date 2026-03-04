You are initializing a Codex DL run from a normalized research plan.

1. Read this order:
- `.codex-research/research_spec.md`
- `.codex-research/task_plan.json`
- `.codex-research/feature_list.json`
- `.codex-research/required_files.json`

2. Keep scope strict:
- CPU-only execution only.
- Deterministic seed policy for all operations.
- No Slurm usage, no online data downloads.
- Keep MLP tiny (<= 2 hidden layers, hidden <= 32).

3. Start by running `.codex-research/init.sh` unless explicitly skipped by the user.

4. After each task completion:
- Append or update `.codex-research/session_progress.md` and `.codex-research/run_registry.jsonl`.
- Attempt sync to `https://github.com/CHDTevior/vibe_test.git`.
