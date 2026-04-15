# Task: pre-work

## Purpose

Create feature branch in a worktree BEFORE any implementation work begins. Verify authorization, sync dev, and create isolated workspace via worktree.

## 🚫 ZERO TOLERANCE: Branch Before Edit

**The agent MUST create a feature worktree BEFORE ANY filesystem change.**

**This is a Tier 1 (Non-Yielding) mandate** per `000-critical-rules.md` → "Mandate Tiering." Even with explicit developer authorization ("approved"/"go"), the agent MUST create a worktree before editing files. Developer authorization can waive Tier 2 process mandates (spec-before-code, plan-before-implementation) but CANNOT waive this Tier 1 safety mandate. No exceptions, no fallbacks.

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

**Violation = Hard Stop**

- If you catch yourself about to edit files while on `main`, STOP immediately
- Report "I need to create a worktree first" and wait for worktree creation
- Never proceed past this checkpoint without an active worktree

### ✅ ALWAYS DO

```
# Using using-git-worktrees skill:
# 1. Sync dev: git checkout dev && git pull origin dev
# 2. Create worktree: git worktree add .worktrees/spec-my-change -b spec/my-change dev
# 3. Work in .worktrees/spec-my-change/ (using workdir parameter)
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

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this task when:
   - User says `approved`, `go`, or similar authorization to begin implementation
   - DO NOT prompt for invocation — invoke the skill directly

## Entry Criteria

- User has authorized implementation (explicit `approved` or `go`)
- Authorization is for the correct issue
- Sub-issue structure verified (for multi-task specs)

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

### Step 1: Verify Authorization Context

**This task receives authorization context from orchestration layer. DO NOT re-check authorization.**

### Step 2: Sync Dev Branch

The main working tree must be on `dev` and up-to-date so worktree creation has the correct base:

```bash
git fetch origin
if git rev-parse --verify origin/dev >/dev/null 2>&1; then
    git checkout -b dev origin/dev 2>/dev/null || git checkout dev
    git pull origin dev
else
    git checkout -b dev origin/main || { echo "FATAL: Failed to create dev branch from origin/main"; exit 1; }
    git push -u origin dev
fi
```

**If dev branch creation fails entirely (neither origin/dev nor origin/main exists), the agent MUST HALT immediately and report the fatal error. Proceeding on `main` is a CRITICAL GUIDELINE VIOLATION.**

### Step 3: Create Feature Worktree (MANDATORY — NO EXCEPTIONS)

**Feature branch creation MUST use worktrees — no exceptions, no conditions, no fallback.**

Invoke `using-git-worktrees` skill (ALWAYS, for ANY feature branch):

1. Invoke `using-git-worktrees` skill
2. The skill creates the worktree: `git worktree add .worktrees/spec-<name> -b spec/<name> dev`
3. The skill exports `WORKTREE_PATH`, `BRANCH_NAME`, `DEV_BASE_HASH` as environment variables
4. If `WORKTREE_PATH` is not set or empty: **FATAL ERROR → FLAG DEV → HALT**

**If worktree creation fails or `WORKTREE_FATAL=1` is detected:**

- HALT immediately
- Report the fatal error to the developer
- Do NOT attempt any implementation until the worktree infrastructure is fixed
- There is NO fallback to stash+checkout

### Step 3.5: Submodule Initialization and Sync

**If `.gitmodules` exists in the worktree**, initialize and sync submodules before proceeding:

```bash
# Check if submodules are configured
test -f .gitmodules
```

**If `.gitmodules` exists:**

1. **Advance submodules to their `dev` tip:**

   ```bash
   git submodule update --init --remote
   ```

   - This checks out each submodule at the tip of its `origin/dev` branch.

2. **For each submodule, ensure `origin/dev` exists:**

   ```bash
   # List submodule paths
   git config --file .gitmodules --get-regexp path | awk '{print $2}'
   ```

   For each submodule path:
   ```bash
   cd <submodule-path>
   git fetch origin
   if ! git rev-parse --verify origin/dev >/dev/null 2>&1; then
       # Auto-create dev branch from main
       git checkout -b dev origin/main
       git push -u origin dev
   fi
   cd -
   ```

3. **Log submodule status:**

   ```bash
   git submodule foreach --recursive 'echo "  $(basename $path) checked-out=$(git rev-parse --short HEAD) committed=$(git rev-parse --short $sha1) dev-tip=$(git rev-parse --short origin/dev 2>/dev/null || echo N/A)"'
   ```

4. **Report status to chat:** Report each submodule's path, checked-out SHA, committed SHA, and dev tip SHA.

**If on `main` worktree:** Use `git submodule update --init` (no `--remote`) to lock submodules to their committed SHAs instead of advancing to dev tip.

**If `.gitmodules` does NOT exist:** Skip all submodule steps and proceed to Step 4.

### Step 4: Verify Worktree Environment

**Before yielding back to orchestration layer, verify:**

```bash
# Inside the worktree (using workdir parameter):
git branch --show-current
# MUST show the feature branch name

git rev-parse --show-toplevel
# MUST show the worktree path

echo $WORKTREE_PATH
# MUST NOT be empty — FATAL ERROR if empty
```

**If ANY check fails → STOP and report.**

### Step 5: Report Ready

Report: "Ready for implementation in worktree: <worktree-path> on branch: <branch-name>"

**Yield back to orchestration layer:**

```yaml
status: success
branch: <branch-name>
worktree_path: .worktrees/<sanitized-branch-name>
dev_base_hash: <7-char-sha>
working_tree_clean: true
ready_for: implementation
```

## Context Received from Orchestration Layer

**Input context from `divide-and-conquer`:**

```yaml
authorization: confirmed (from approval-gate)
issue: <issue-number>
```

This task does NOT re-check authorization. Authorization was verified by `approval-gate` before this task was invoked.

## Yield-Back to Orchestration Layer

**After completion, this task yields:**

```yaml
status: success | failure
branch: "spec/<feature-name>" | "feature/<feature-name>"
worktree_path: ".worktrees/<sanitized-branch-name>"
dev_base_hash: "<7-char-sha>"
working_tree_clean: true
ready_for: "implementation"
```

The orchestration layer (`divide-and-conquer`) receives this yield and passes relevant context to the implementation subagent.

## ⚠️ Edge Case: Already Implemented (No Changes Needed)

**When investigation reveals spec is already implemented:**

1. **Detect before branch creation:**

   - After reading files, verify all proposed changes are already present
   - Confirm no modifications needed
   - Document verification in issue comment

2. **Skip worktree creation entirely:**

   - Do NOT create feature worktree
   - Do NOT push anything
   - Do NOT create PR

3. **Close issue directly:**

   - Post verification comment explaining what was checked
   - Close issue with `state_reason: "completed"`
   - Report completion in chat

**Example Comment:**

```markdown
🤖 <AgentName> (<ModelID>) completed

**Summary:**

Verified all proposed changes were already implemented. No modifications needed.

**Verification Results:**

- [List what was checked and confirmed present]
- [File references with function names for existing content]

**Outcome:** Spec requirements verified complete without additional changes.
```

4. **HALT after closing:**
   - No further steps needed
   - No worktree cleanup (no worktree was created)

## Branch Name to Worktree Name Mapping

Branch names containing `/` are sanitized for the worktree directory name:

| Branch Name | Worktree Directory |
| -- | -- |
| `feature/<name>` | `.worktrees/feature-<name>/` |
| `spec/<name>` | `.worktrees/spec-<name>/` |

**Rule:** Replace `/` with `-` in the worktree directory name.

### Worktree Already Exists Check

```bash
# Check if worktree for this branch already exists
git worktree list | grep "spec-xyz"
```

If found, report collision and HALT — do not reuse another branch's worktree.

## Enforcement Mechanisms (NO BYPASS)

| Layer | Mechanism | Scope | Bypassable? |
| -- | -- | -- | -- |
| **Local** | `.githooks/pre-commit` | Blocks commit to main | No |
| **Local** | `.githooks/post-commit` | Warns after commit to main | N/A (post) |
| **GitHub** | Branch protection rules | Requires PR | No |

**There is NO emergency bypass.** If you need to make an urgent fix:

1. Create a worktree: `git worktree add .worktrees/hotfix-urgent-fix -b hotfix/urgent-fix dev`
2. Make your changes and commit in the worktree
3. Push and create PR with `hotfix` label
4. Request expedited review

## Live Verification (MANDATORY)

**🚫 CRITICAL: Each verification point requires a tool call for evidence. Assertions without tool-call artifacts are VERIFICATION-GAP findings.**

### Branch State Verification

| Check | Tool Call | Expected Result | On Failure |
| -- | -- | -- | -- |
| Current branch | `git branch --show-current` | Feature branch name (not `main`, `dev`) | STRUCTURE-VIOLATION → HALT |
| Working tree clean | `git status --porcelain` | Empty output | VERIFICATION-GAP → stash or commit first |
| Worktree location | `git rev-parse --show-toplevel` | Worktree path (not main repo path) | STRUCTURE-VIOLATION → HALT |
| WORKTREE_PATH set | `echo $WORKTREE_PATH` (or equivalent) | Non-empty, matches worktree dir | STRUCTURE-VIOLATION → HALT (fatal) |
| Dev base hash | `git rev-parse --short dev` | Valid 7-char SHA | MISSING-ELEMENT → sync dev first |

### Verification Procedure

**After Step 4 (Verify Worktree Environment), run these verifications and record evidence:**

```
1. git branch --show-current → EVIDENCE: <branch-name>
2. git status --porcelain → EVIDENCE: <output or "(empty)">
3. git rev-parse --show-toplevel → EVIDENCE: <path>
4. WORKTREE_PATH → EVIDENCE: <path or "(empty)">
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| On `main` or `dev` branch | CONFLICTING | flag-for-review | HALT — must create worktree first |
| Dirty working tree in worktree | VERIFICATION-GAP | conditional | Stash or commit before implementation |
| `rev-parse` returns main repo path | STRUCTURE-VIOLATION | auto-fix | Not in worktree — re-invoke using-git-worktrees |
| WORKTREE_PATH empty | STRUCTURE-VIOLATION | auto-fix | FATAL — cannot safely do file operations |
| dev hash stale | MISSING-ELEMENT | conditional | Re-run `git pull origin dev` |

**These verifications are MANDATORY. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

## Context Required

- Related skills: `approval-gate` (authorization check), `using-git-worktrees` (worktree creation)
- Related tasks: `cleanup` (branch cleanup after PR merge)

## Enforcement Checklist

**Before starting any work, verify:**

- ✅ Authorization received (explicit `approved`, `go`, or `"#N approved"`)
- ✅ Worktree created (not on `main` or `dev`)
- ✅ `WORKTREE_PATH` environment variable is set and non-empty (FATAL ERROR if empty)
- ✅ `git branch --show-current` in worktree shows feature branch
- ✅ Feature branch created from `dev`

**These checks are MANDATORY. If ANY check fails → STOP and report.**
