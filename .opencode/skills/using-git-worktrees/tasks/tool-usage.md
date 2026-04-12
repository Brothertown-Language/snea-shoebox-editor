# Task: tool-usage

Tool usage compliance rules for operating inside git worktrees.

## Bash Tool (workdir parameter)

| Method | Example | Compliant? |
|--------|---------|------------|
| `workdir` parameter on Bash tool | `workdir=".worktrees/$BRANCH_NAME"` | YES |
| Relative path from project root | `uv run --directory .worktrees/$BRANCH_NAME pytest` | YES |
| `cd .worktrees/$BRANCH_NAME && ...` | `cd .worktrees/xyz && uv sync` | NO — zero tolerance |

Per AGENTS.md and `060-tool-usage.md`, `cd` commands are a zero-tolerance violation.

## File Operation Tools (filePath parameter) — CRITICAL

The `read`, `edit`, `write`, `glob`, and `grep` tools do NOT have a `workdir` parameter. When `WORKTREE_PATH` is set, relative paths resolve to the **main repo**, causing silent errors — edits go to the wrong file.

| Tool | WRONG (main repo) | CORRECT (worktree) |
|------|-------------------|---------------------|
| `read` | `read(filePath="src/main.py")` | `read(filePath=f"{WORKTREE_PATH}/src/main.py")` |
| `edit` | `edit(filePath="src/main.py", ...)` | `edit(filePath=f"{WORKTREE_PATH}/src/main.py", ...)` |
| `write` | `write(filePath="src/new.py", ...)` | `write(filePath=f"{WORKTREE_PATH}/src/new.py", ...)` |
| `glob` | `glob(pattern="src/**/*.py")` | `glob(pattern="src/**/*.py", path=WORKTREE_PATH)` |
| `grep` | `grep(pattern="TODO", path="src/")` | `grep(pattern="TODO", path=f"{WORKTREE_PATH}/src/")` |

**Rule:** When `WORKTREE_PATH` is set, every file operation tool call MUST prefix paths with the worktree path. No exceptions.

When NOT in a worktree (working in main repo), relative paths function correctly as-is.