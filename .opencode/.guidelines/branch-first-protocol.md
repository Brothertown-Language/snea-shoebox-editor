# Fragment: Branch-First Protocol

**🚫 ZERO TOLERANCE: Branch Before Edit (via Worktree)**

**The agent MUST create a feature worktree BEFORE ANY filesystem change.**

This is the FIRST and MOST CRITICAL rule. Before writing any code, editing any file, creating any file, or making ANY change to the project:

1. **Invoke `using-git-worktrees` skill** — creates isolated worktree (MANDATORY, no exceptions)
2. **All work happens in the worktree** — never in the main working directory
3. **ONLY THEN**: Proceed with file changes inside the worktree

**What Counts as a "Change"?**
- Editing any file (code, config, docs, tests)
- Creating new files
- Deleting files
- Renaming files
- Modifying `.gitignore`, `pyproject.toml`, any config
- Updating guidelines in `.opencode/`
- ANY filesystem modification whatsoever
- **Using file-editing MCP tools** (`pycharm_replace_text_in_file`, `pycharm_create_new_file`, etc.) — these ARE filesystem changes

**⚠️ MCP Tools Are NOT an Exception**
- `pycharm_replace_text_in_file` → edits files → MUST be in worktree
- `pycharm_create_new_file` → creates files → MUST be in worktree
- `github_issue_write` → GitHub Issues, NOT local files → NOT a filesystem change
- `github_add_issue_comment` → GitHub comments → NOT a filesystem change

**Why FIRST?**
- No exceptions for "small" changes
- No exceptions for "just one file"
- No exceptions for docs, tests, configs, or guidelines
- No exceptions for hotfixes or urgent changes
- No exceptions for typo fixes or whitespace changes
- The worktree IS the safety net — without it, mistakes have no rollback

**Violation = Hard Stop**
- If you catch yourself about to edit files while on `main`, STOP immediately
- Report "I need to create a worktree first" and invoke `using-git-worktrees`
- Never proceed past this checkpoint without an active worktree

### ✅ ALWAYS DO
```
# Correct order (using worktree):
# 1. Sync dev: git checkout dev && git pull origin dev
# 2. Create worktree: git worktree add .worktrees/spec-my-change -b spec/my-change dev
# 3. Work in .worktrees/spec-my-change/ (using workdir parameter on bash commands)
# IMPORTANT: For read/edit/write/glob/grep tools, prefix filePath with WORKTREE_PATH:
#   read(filePath=f"{WORKTREE_PATH}/src/main.py")  — NOT read(filePath="src/main.py")
```

### 🚫 NEVER DO
```
# WRONG — VIOLATION (stash+checkout):
git stash -u
git checkout -b spec/my-change
# Work in main working directory

# WRONG — VIOLATION (checkout without worktree):
git checkout dev && git pull origin dev
git checkout -b spec/my-change dev
# Work in main working directory
```

## Worktree Isolation (Replaces Stash)

Worktrees provide complete isolation — no stash is needed. Each worktree has its own working directory, so main tree changes are never affected.

**If `WORKTREE_PATH` is not set or empty after worktree creation: FATAL ERROR → FLAG DEV → HALT.**

<!--
Fragment ID: branch-first-protocol
Estimated tokens: 380
Type: text-block
Sync status: synchronized
-->