# Git Protocol: Branch Before Edit

## 1. FIRST ACTION: CREATE BRANCH (MANDATORY)

**🚫 ZERO TOLERANCE: The agent MUST create a feature branch BEFORE ANY filesystem change.**

This is the FIRST and MOST CRITICAL rule. Before writing any code, editing any file, creating any file, or making ANY change to the project:

1. **Check current branch**: `git branch --show-current`
1. **If on `main`**: STOP — you MUST create a feature branch first
1. **Create branch**: `git checkout -b spec/<short-name>` or `git checkout -b feature/<description>`
1. **ONLY THEN**: Proceed with file changes

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

______________________________________________________________________

## 1.1. Preserve External Changes: Stash ALL Unrelated Changes FIRST

**When ANY files are modified on `main` (or current branch), the agent MUST stash them BEFORE creating a new branch.**

### ⚠️ MANDATORY: Stash First, Ask Questions Never

**Before ANY branch creation, this sequence is MANDATORY:**

1. `git status` — Check for modifications
1. **If ANY files modified (even one line, even external edits, even "unrelated" files):**
   - `git stash push --include-untracked -m "WIP: external changes before <branch-name>"`
   - `git stash list` — **VERIFY stash was created**
   - `git status` — **VERIFY working tree is clean** (must show "nothing to commit, working tree clean")
1. **Then and ONLY then**: Create branch
1. **Do NOT pop the stash** on the new branch — those changes belong to the previous branch context

### ⚠️ CRITICAL: Never Restore, Never Discard

**`git restore` on externally-modified files DESTROYS THOSE CHANGES PERMANENTLY.**

```
WRONG SEQUENCE:
git status                           # Shows external changes in project-config.ini
git restore project-config.ini       # ← DESTROYS external changes permanently
git checkout -b feature/my-change

ALSO WRONG:
git status                           # Shows external changes
git checkout -b feature/my-change    # ← Branch created with dirty working tree
git stash push -m "preserving"       # ← WRONG: Too late, wrong branch context

CORRECT SEQUENCE:
git status                           # Shows modified files
git stash push -m "WIP: external changes before my-change"  # ← Stash FIRST
git stash list                       # ← VERIFY: Must show stash entry
git status                           # ← VERIFY: Must show clean working tree
git checkout -b feature/my-change    # ← THEN create branch
# Do your work, commit, push, create PR...
# Stash remains for later restoration on appropriate branch
```

### ⚠️ VERIFICATION IS MANDATORY

**After stashing, you MUST verify:**

```bash
git stash push -m "WIP: external changes before feature-x"
git stash list   # ← MUST show the stash
git status       # ← MUST show "nothing to commit, working tree clean"
```

If `git status` still shows modifications, **STOP** — the stash failed. Do not proceed to branch creation.

### Do NOT Pop Stash on New Branch

The stash preserves changes that belong to the previous context. Those changes may need to be:

- Committed separately on a different branch
- Reviewed by the user
- Discarded intentionally by the user

**Let the user decide when/where to restore the stash.**

______________________________________________________________________

## Enforcement Mechanisms (NO BYPASS)

| Layer | Mechanism | Scope | Bypassable? |
|-------|-----------|-------|-------------|
| **Local** | `.githooks/pre-commit` | Blocks commit to main | No |
| **Local** | `.githooks/post-commit` | Warns after commit to main | N/A (post) |
| **GitHub** | Branch protection rules | Requires PR | No |

**There is NO emergency bypass.** If you need to make an urgent fix:

1. Create a feature branch: `git checkout -b hotfix/urgent-fix`
1. Make your changes and commit
1. Push and create PR with `hotfix` label
1. Request expedited review

______________________________________________________________________

*Source: Content migrated from `110-git-protocol.md`*
