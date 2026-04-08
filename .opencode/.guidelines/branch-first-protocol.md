# Fragment: Branch-First Protocol

**🚫 ZERO TOLERANCE: Branch Before Edit**

**The agent MUST create a feature branch BEFORE ANY filesystem change.**

This is the FIRST and MOST CRITICAL rule. Before writing any code, editing any file, creating any file, or making ANY change to the project:

1. **Check current branch**: `git branch --show-current`
2. **If on `main`**: STOP — you MUST create a feature branch first
3. **Create branch**: `git checkout -b spec/<short-name>` or `git checkout -b feature/<description>`
4. **ONLY THEN**: Proceed with file changes

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
- `pycharm_replace_text_in_file` → edits files → MUST be on feature branch
- `pycharm_create_new_file` → creates files → MUST be on feature branch
- `github_issue_write` → GitHub Issues, NOT local files → NOT a filesystem change
- `github_add_issue_comment` → GitHub comments → NOT a filesystem change

**Why FIRST?**
- No exceptions for "small" changes
- No exceptions for "just one file"
- No exceptions for docs, tests, configs, or guidelines
- No exceptions for hotfixes or urgent changes
- No exceptions for typo fixes or whitespace changes
- The branch IS the safety net — without it, mistakes have no rollback

**Violation = Hard Stop**
- If you catch yourself about to edit files while on `main`, STOP immediately
- Report "I need to create a branch first" and wait for the branch creation
- Never proceed past this checkpoint without a feature branch

### ✅ ALWAYS DO
```
# Correct order:
git checkout main && git pull origin main
git checkout -b spec/my-change      # ← FIRST
# NOW edit files, write code, etc.   # ← SECOND
```

### 🚫 NEVER DO
```
# WRONG ORDER — VIOLATION:
# edit files, write code...           # ← WRONG: No branch yet
git checkout -b spec/my-change        # ← Too late!
```

## Preserve External Changes: Stash ALL Unrelated Changes FIRST

**When ANY files are modified on `main` (or current branch), the agent MUST stash them BEFORE creating a new branch.**

### ⚠️ MANDATORY: Stash First, Ask Questions Never

**Before ANY branch creation, this sequence is MANDATORY:**

1. `git status` — Check for modifications
2. **ALWAYS stash ALL pending changes (modified, deleted, untracked):**
   - `git stash push -u -m "WIP: before <branch-name>"`
   - **The `-u` flag includes untracked files — MANDATORY.**
   - `git stash list` — **VERIFY stash was created**
   - `git status` — **VERIFY working tree is clean** (must show "nothing to commit, working tree clean")
3. **Then and ONLY then**: Create branch

<!--
Fragment ID: branch-first-protocol
Estimated tokens: 425
Type: text-block
Sync status: synchronized
-->