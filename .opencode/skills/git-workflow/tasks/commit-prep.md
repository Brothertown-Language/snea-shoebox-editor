# Task: commit-prep

## Purpose

Prepare commit message for squash commit during PR creation. This is a read-only analysis phase - no commits are executed.

## Commit Policy (User-Initiated Only)

### 🚫 NEVER DO

- **NEVER run `git restore`, `git checkout`, `git reset`, `git clean`** — these discard or modify working tree state
- **NEVER discard uncommitted changes** — even if they appear to be formatting-only, unintended, or erroneous
- **Analysis commands are read-only** — no modifications to working tree
- **NEVER commit or merge without direct instruction** — commits may ONLY be initiated by the developer
- **NEVER create a PR without direct instruction** — PRs require explicit developer request

### STOP ASKING FOR COMMITS AND PRS

The developer will say "commit" or "create a PR" when they want git operations. Until then, do nothing:

1. **After completing implementation**: Report completion concisely, then STOP and wait silently
2. **Do NOT ask**: "Commit?", "Ready to commit?", "Should I commit?", "Ready for a PR?", "Create a PR?", "Push and PR?"
3. **Do NOT automatically create PRs**: PR creation requires the same explicit instruction as commits

### ✅ ALWAYS DO

- **Include co-author trailers for both AI and human collaborator** — every implementation commit MUST include TWO trailers
- **Re-run discovery** (`git status`, `git diff`) before any commit workflow
- **If `pyproject.toml` changed, include `uv.lock`** — this is an application/CI repo
- **Use dynamic AI identity** — the AI knows its own name and email
- **Use cached human identity** — from session start values (`DEV_NAME`, `DEV_EMAIL`)

## Operating Protocol

1. **User-initiated only:** This task runs when user says "commit" or "prepare a commit"
2. **Read-only analysis:** Discover changes but DO NOT execute commits
3. **HALT after analysis:** Wait for user to review and approve

## Entry Criteria

- User says "commit" or "prepare a commit"
- Implementation is complete
- Feature branch pushed to remote

## Exit Criteria

- Commit script created in `./tmp/`
- Proposed commit message documented
- User has reviewed and can execute script

## Procedure

### Step 1: Discovery (Read-Only)

```bash
git status          # What files changed?
git diff            # What are the changes?
git diff --cached   # What's already staged?
git log --oneline -10  # Recent commits for context
```

### Step 2: Summarize Changes

Group changes logically:

- Feature changes
- Test changes
- Documentation changes
- Configuration changes

### Step 3: Create Commit Script

Write to `./tmp/commit-<branch>.sh`:

```bash
#!/bin/bash
# Commit script for <branch-name>
# 🤖 <AgentName> (<ModelID>) created

git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

### Step 4: HALT

**DO NOT execute the script.**

Report:

- Script path: `./tmp/commit-<branch>.sh`
- Proposed commit message
- Summary of changes being committed

## Co-Author Trailer Requirements (MANDATORY)

Every implementation commit MUST include:

### AI Author Trailer

- **Use your actual identity dynamically** — the AI knows its own name and email
- **DO NOT use generic placeholders like "AI"** — use the actual AI agent name detected from runtime context
- **Email format**: Use a noreply address associated with the AI service (e.g., `noreply@opencode.ai`, `noreply@anthropic.com`)
- **NEVER use the project domain** — those belong to the human collaborators
- **Include model info**: Format is `Agent-Name (model-id) <email>`

**Example:**

```
Co-authored-by: <AI-Name> (<model-id>) <noreply@example.com>
```

### Human Collaborator Trailer

- **Use cached values from session start** — `DEV_NAME` and `DEV_EMAIL`
- **Do NOT re-run `git config`** — use stored session values

**Example:**

```
Co-authored-by: <DEV_NAME> <DEV_EMAIL>
```

### Complete Example

```bash
git commit -m "feat: Add user authentication" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <noreply@example.com>" \
    --trailer "Co-authored-by: <DEV_NAME> <DEV_EMAIL>"
```

## When Commits Happen

Commits occur during the PR creation workflow, not as a separate step:

1. **Implementation completes** → review-prep task pushes branch
2. **Developer reviews** → Developer says "create a PR"
3. **PR creation** → Squash commit is executed as part of PR creation
4. **No intermediate scripts** → No `./tmp/commit.sh` or manual steps

## Reading Historical Content

### ✅ ALWAYS DO

- To inspect a file at a historical commit: `git show <ref>:<path> > ./tmp/historical_file.ext`
- Process the saved file with appropriate `.opencode/tools/` or IDE tool

### 🚫 NEVER DO

- Using `python3`, `python -c`, `json.tool`, `grep`, or `sed` to process `git show` output is a critical violation

## Lockfile Policy

- This repository is an application/CI repo — **commit `uv.lock`**
- If `pyproject.toml` changed, ensure `uv.lock` is staged

## Live Verification (MANDATORY)

**🚫 CRITICAL: Each verification point requires a tool call for evidence. Committing without verified staged state is a CRITICAL GUIDELINE VIOLATION.**

### Staged State Verification

| Check | Tool Call | Expected Result | On Failure |
| -- | -- | -- | -- |
| Staged diff matches intent | `git diff --staged` | Shows exactly what should be committed | CONFLICTING → re-stage |
| No unintended unstaged changes | `git diff` | Empty or only expected changes | VERIFICATION-GAP → review and stage |
| On correct branch | `git branch --show-current` | Feature branch (not `main`/`dev`) | STRUCTURE-VIOLATION → HALT |
| Worktree location | `git rev-parse --show-toplevel` | Worktree path | STRUCTURE-VIOLATION → HALT |
| Status shows expected files | `git status --porcelain` | Only intended files shown | VERIFICATION-GAP → review |

### Verification Procedure

**Between Step 1 (Discovery) and Step 2 (Summarize Changes), verify staged state:**

```
1. git diff --staged → EVIDENCE: <staged changes diff>
2. git diff → EVIDENCE: <unstaged changes or "(empty)">
3. git branch --show-current → EVIDENCE: <feature-branch-name>
4. git rev-parse --show-toplevel → EVIDENCE: <worktree-path>
5. git status --porcelain → EVIDENCE: <file status list>
```

**Compare `git diff --staged` output against the intended commit scope. If staged changes include files NOT intended for this commit, re-stage selectively.**

### Finding Classification

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Staged files not matching intent | CONFLICTING | flag-for-review | Selective `git add` to correct staging |
| Unstaged changes present | VERIFICATION-GAP | conditional | Review — may need `git add` or `.gitignore` |
| On `main` or `dev` | STRUCTURE-VIOLATION | auto-fix | HALT — must be on feature branch in worktree |
| Wrong toplevel path | STRUCTURE-VIOLATION | auto-fix | HALT — not in worktree context |
| Locked/deleted files in status | VERIFICATION-GAP | flag-for-review | Investigate — may need `git rm` or recovery |

**These verifications are MANDATORY before committing. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

## Why This Task Is Separate from PR Creation

- User needs to review commit message BEFORE creation
- Commit preparation is read-only (safer)
- Gives user chance to clarify, adjust, request changes
- PR creation requires explicit "create a PR"
