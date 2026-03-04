# Codex 执行指南（中文）

本文档说明：当 `.codex-research/` 已经由本 skill 生成后，如何在 Codex 中逐步执行任务，以及如何使用 `run_one_task.sh` / `run_plan.sh`。

## 0. 前置信息

- 源计划文件：`/iridisfs/scratch/ts1v23/workspace/vibe_coding/codex_auto_demo/.codex-research/plan/normalized_plan.md`
- 项目根目录：`/iridisfs/scratch/ts1v23/workspace/vibe_coding/codex_auto_demo`
- 任务计划文件：`.codex-research/task_plan.json`

## 1. 在 Codex 里一步步执行（手动模式）

1. 打开 `.codex-research/task_plan.json`，从 `tasks` 中挑选一个 `passes=false` 的任务。
2. 在一次 Codex 会话里只做这一个任务（one-session-one-task）。
3. 执行该任务的实现、最小验证和记录，更新：
   - `.codex-research/session_progress.md`
   - `.codex-research/decision_log.md`
4. 只有在有验证证据时，才把对应任务标记为 `passes=true`。
5. 重复以上步骤直到任务完成。

## 2. 用 run_one_task.sh 执行一个任务（推荐先用）

```bash
PROJECT_ROOT="/iridisfs/scratch/ts1v23/workspace/vibe_coding/codex_auto_demo"
bash "$PROJECT_ROOT/.codex-research/run_one_task.sh" T01
```

## 3. 用 run_plan.sh 连续执行多个任务

```bash
PROJECT_ROOT="/iridisfs/scratch/ts1v23/workspace/vibe_coding/codex_auto_demo"
bash "$PROJECT_ROOT/.codex-research/run_plan.sh"
```

说明：`run_plan.sh` 会按 `T01..T07` 的固定顺序执行全部任务（当前不带次数参数）。

## 4. 这些命令的可运行性如何保证

`scripts/prepare_from_plan.sh` 在生成完成后会自动执行以下预检：

1. 检查 `run_one_task.sh` / `run_plan.sh` 文件存在。
2. 对两个脚本执行 `bash -n` 语法检查。
3. 对本文件给出的两条运行命令执行 shell 命令行语法检查。

如果任一预检失败，生成流程会报错退出，避免后续直接执行时报“命令不可运行”。
