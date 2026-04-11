# Task: pre-work

## Purpose

Verify branch state, preserve changes, create feature branch BEFORE any implementation work begins.

## 🚫 ZERO TOLERANCE: Branch Before Edit

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
4. **Do NOT pop the stash** on the new branch — those changes belong to the previous branch context

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

## Operating Protocol

1. **Automatic invocation (mandatory):** This task is invoked automatically when:
   - User says `approved`, `go`, or similar authorization to begin implementation
   - DO NOT prompt for invocation - the skill is triggered automatically

## Entry Criteria

- User has authorized implementation (explicit `approved` or `go`)
- Authorization is for the correct issue
- Sub-issue structure verified (for multi-task specs)
- Working tree is clean (no uncommitted changes)

## Three-Branch Workflow Context

**Branch Model:**
- **Feature branches** (`feature/*` or `spec/*`): Branch from `dev`, merge to `dev`
- **Dev branch** (`dev`): Staging/integration (evergreen, never deleted)
- **Main branches** (`main` or `master`): Production-ready code

**AI Commit Restrictions:**
- AI cannot commit to `main`, `master`, or `dev` (blocked by git hooks)
- AI must create feature branches from `dev` (not `main`)
- AI must sync with `dev` before creating feature branch

## Procedure

### Step 1: Check Git State (Pure Git Operations)

**This task receives authorization context from orchestration layer. DO NOT re-check authorization.**

```bash
git branch --show-current
git status
```

If on `main` → stash changes then create feature branch.

### Step 2: Stash ALL Pending Changes (MANDATORY)

**ALWAYS stash before ANY branch operation. No exceptions.**

```bash
git stash push -u -m "WIP: before <branch-name>"
```

**The `-u` flag includes untracked files. This is mandatory.**

**What gets stashed:**
- Modified files
- Deleted files
- Untracked files
- Staged changes

### Step 3: Verify Stash Succeeded

```bash
git stash list  # VERIFY stash created
git status      # VERIFY clean working tree
```

**CRITICAL VERIFICATION:**

| Check | Command | Expected Result |
|-------|---------|------------------|
| Stash exists | `git stash list` | Shows stash entry |
| Working tree clean | `git status --porcelain` | Empty output |

**If EITHER check fails → STOP. Report failure. Let user resolve.**

### Step 4: Sync and Create Feature Branch

**Three-Branch Workflow:**
- Feature branches branch from `dev` (staging/integration)
- `dev` branches from `main`
- AI must sync with `dev` before creating feature branch

```bash
# Sync with dev branch (staging/integration)
git checkout dev && git pull origin dev

# Create feature branch from dev
git checkout -b spec/<short-name>  # or feature/<description>
```

**Why Branch from Dev:**
- `dev` is the staging/integration branch (evergreen, never deleted)
- Feature branches merge to `dev`, not directly to `main`
- Releases merge from `dev` to `main` via human-triggered workflow
- Branching from `dev` ensures you have the latest integrated changes

**Sync Requirements:**
- ALWAYS `git pull origin dev` before creating feature branch
- Ensure working tree is clean after sync
- If `dev` doesn't exist locally, create it from `main`: `git checkout -b dev origin/dev`

### Step 4a: Worktree Gate (MANDATORY when layout is active)

**When the worktree layout is active, feature branch creation MUST create a worktree — not just a branch in the main folder. Bypassing this gate when the layout is active is a CRITICAL VIOLATION (see `000-critical-rules.md`).**

**Detection (primary = env var, fallback = filesystem):**
```bash
# Primary: Use WORKTREE_STATUS from session-init
# WORKTREE_STATUS values: "ready", "bootstrapped", "skipped", "failed"
# If WORKTREE_STATUS is empty/unset, fall back to filesystem check

# Filesystem fallback:
ls -d worktrees/main .worktrees/main 2>/dev/null
```

**Decision matrix:**

| Condition | Action |
|-----------|--------|
| `WORKTREE_STATUS=ready` or `WORKTREE_STATUS=bootstrapped` + feature branch | **MANDATORY:** Use `using-git-worktrees` skill |
| Filesystem detects `worktrees/main/` or `.worktrees/main/` + feature branch | **MANDATORY:** Use `using-git-worktrees` skill |
| `WORKTREE_STATUS=skipped` or `WORKTREE_STATUS=failed` | Use standard stash+checkout workflow |
| No `WORKTREE_STATUS` env var AND no filesystem worktree dirs | Use standard stash+checkout workflow |
| Worktree layout active + dev-only work | Work in main folder (no worktree needed) |

**If worktree layout is active and creating a feature branch:**
1. Invoke `using-git-worktrees` skill — it is MANDATORY, not optional
2. The worktree skill handles branch creation, isolation, and setup
3. Do NOT fall back to stash+checkout workflow when layout is active

**Why mandatory:** The OR escape hatch (worktree OR stash+checkout) gives agents a path of least resistance. When the layout is active, worktree isolation is the correct default — it prevents conflicting work between parallel agents.

**Why session-init variable:** `WORKTREE_STATUS` is emitted by `session_init.py` during every session. It reflects the actual state of the worktree layout at session start. Using it avoids redundant filesystem checks and ensures agents consume session-init output rather than ignoring it.

**If no worktree layout is active**, proceed with standard branch creation:

```bash
git checkout -b spec/<short-name>
```

### Step 5: Verify Clean Working Tree

**Before yielding back to orchestration layer, verify:**

```bash
git status --porcelain
```

**Expected output:** Empty (nothing to commit, working tree clean)

**If dirty:**
- STOP and report
- Let orchestration layer decide next action

### Step 6: Report Ready

Report: "Ready for implementation on branch: <branch-name>"

**Yield back to orchestration layer:**
```yaml
status: success
branch: <branch-name>
stash_created: <true/false>
working_tree_clean: true
ready_for: "implementation"
```

## Context Received from Orchestration Layer

**Input context from `implementation-workflow`:**
```yaml
authorization: confirmed (from approval-gate)
issue: <issue-number>
working_tree_status: checked
```

This task does NOT re-check authorization. Authorization was verified by `approval-gate` before this task was invoked.

## Yield-Back to Orchestration Layer

**After completion, this task yields:**
```yaml
status: success | failure
branch: "spec/<feature-name>" | "feature/<feature-name>"
stash_created: true | false
working_tree_clean: true
ready_for: "implementation"
```

The orchestration layer (`implementation-workflow`) receives this yield and passes relevant context to the implementation subagent.

## ⚠️ Edge Case: Already Implemented (No Changes Needed)

**When investigation reveals spec is already implemented:**

1. **Detect before branch creation:**
   - After reading files, verify all proposed changes are already present
   - Confirm no modifications needed
   - Document verification in issue comment

2. **Skip branch creation entirely:**
   - Do NOT create feature branch
   - Do NOT push anything
   - Do NOT create PR

3. **Close issue directly:**
   - Post verification comment explaining what was checked
   - Close issue with `state_reason: "completed"`
   - Report completion in chat

**Example Comment:**
```markdown
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Summary:**

Verified all proposed changes were already implemented. No modifications needed.

**Verification Results:**

- [List what was checked and confirmed present]
- [File references with function names for existing content]

**Outcome:** Spec requirements verified complete without additional changes.
```

4. **HALT after closing:**
   - No further steps needed
   - No branch cleanup (no branch was created)

## Worktree Integration

### Feature Worktree Creation

When the worktree layout is active (`worktrees/main/` or `.worktrees/main/` exists), feature branches MUST use worktrees instead of stash+checkout. This is enforced by the Worktree Gate in Step 4a.

**Before (stash-based):**
1. `git stash -u` → 2. `git checkout -b feature/xyz dev` → 3. Work in same folder

**After (worktree-based):**
1. Ensure main folder is on `dev`: `git checkout dev && git pull origin dev`
2. Create worktree: `git worktree add worktrees/feature-xyz -b feature/xyz dev`
3. Work in `worktrees/feature-xyz/`

### Branch Name to Worktree Name Mapping

Branch names containing `/` must be sanitized for the worktree directory name:

| Branch Name | Worktree Directory |
|-------------|-------------------|
| `feature/my-change` | `worktrees/feature-my-change/` |
| `spec/604-worktree-model` | `worktrees/spec-604-worktree-model/` |

**Rule:** Replace `/` with `-` in the worktree directory name.

### Edge Cases

- **Dev-only work** (no feature branch): Work in main folder directly, no worktree needed
- **Worktree already exists**: Skip creation, use existing worktree directory
- **Worktree layout not active**: Fall back to stash+checkout workflow

### Worktree Already Exists Check

```bash
# Check if worktree for this branch already exists
git worktree list | grep "feature-xyz"
```

If found, skip worktree creation and work in the existing directory.

## Enforcement Mechanisms (NO BYPASS)

| Layer | Mechanism | Scope | Bypassable? |
|-------|-----------|-------|-------------|
| **Local** | `.githooks/pre-commit` | Blocks commit to main | No |
| **Local** | `.githooks/post-commit` | Warns after commit to main | N/A (post) |
| **GitHub** | Branch protection rules | Requires PR | No |

**There is NO emergency bypass.** If you need to make an urgent fix:
1. Create a feature branch: `git checkout -b hotfix/urgent-fix`
2. Make your changes and commit
3. Push and create PR with `hotfix` label
4. Request expedited review

## Context Required

- Related skills: `approval-gate` (authorization check)
- Related tasks: `cleanup` (branch cleanup after PR merge)

## Common Issues

| Issue | Resolution |
|-------|------------|
| Stash failed | STOP. Report failure. Let user resolve manually. |
| Wrong branch detected | STOP. Do not commit. Stash changes, switch to correct branch. |
| Accidental main commit | Create recovery branch, reset main, switch to recovery branch. |

## Safety Checks

Before proceeding, verify ALL:

- Current branch is NOT `main`
- Working tree IS clean (`git status --porcelain` returns empty)
- Branch name follows convention (`spec/` or `feature/` prefix)

**If ANY check fails → STOP and report.**

## Enforcement Checklist

**Before starting any work, verify:**

- ✅ Authorization received (explicit `approved`, `go`, or `"#N approved"`)
- ✅ Current branch is NOT `main` (or stash and create feature branch)
- ✅ Working tree is clean (`git status --porcelain` returns empty)
- ✅ Stash created if needed (`git stash list` shows entry)
- ✅ Feature branch created from `main`

**These checks are MANDATORY. If ANY check fails → STOP and report.**