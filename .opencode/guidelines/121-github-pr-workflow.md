# GitHub Workflow: PR Workflow

## ⚠️ MANDATORY: PRs Required for All Code Changes

**When GitHub MCP tools are available, Pull Requests are MANDATORY for ALL code changes.**

### 🚫 ABSOLUTELY PROHIBITED
- Direct commits to `main` branch
- Local merges to `main` (including `git merge --squash`)
- Skipping PR for "small" or "quick" changes
- Skipping PR for "documentation only" changes
- Skipping PR for "urgent" changes

### ✅ ALWAYS REQUIRED
1. Create a feature branch BEFORE any code changes
2. Make commits to the feature branch
3. Push branch and create PR
4. Wait for human review and merge

---

## ⚠️ SQUASH MERGE REQUIRED

**All PRs must be squash-merged to `main`.**

- Never use regular merge — always squash
- Never use rebase-merge — always squash
- This maintains clean commit history — one commit per PR

**For humans merging PRs:**
- GitHub "Squash and merge" button is required
- Never click "Merge" or "Rebase and merge" buttons

---

## 🚫 ABSOLUTE PROHIBITION: AGENTS MUST NEVER MERGE PRs

- **PR merging is HUMAN-ONLY.** The agent MUST NOT call `github_merge_pull_request` at any time.
- **ALL PRs require human review before merge** — no exceptions, no self-merging.
- **"go" does NOT authorize merging.** "go" means "proceed to the next task or phase" — NOT "merge the PR". If all tasks are complete, report summary and HALT.
- The agent creates PRs, addresses feedback, and waits for human approval and merge.
- After PR creation, the agent MUST report the PR URL and HALT.
- If PR is open and user says "go", the agent must clarify that merging requires explicit "merge" instruction.

---

## PR Creation Workflow

### Before Creating PR — ALWAYS:

1. **Rebase on main**: Ensure branch is up-to-date with latest main
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Squash commits**: ALWAYS squash to single commit before pushing
   ```bash
   git reset --soft origin/main
   git commit -m "<descriptive message>"
   ```
   
   **⚠️ CRITICAL**: Every PR must have exactly ONE commit. No exceptions.

3. **Force push after squash**: `git push --force-with-lease origin <branch>`

4. **Then create PR**: Only after branch has single clean commit

### ⚠️ When Adding Updates to Existing PR — ALWAYS RE-SQUASH:

If you've already created a PR and need to add more changes:

1. **Make new commits** on the feature branch as needed
2. **Re-squash before pushing**: Combine all commits into one
   ```bash
   git reset --soft origin/main
   git commit -m "<updated descriptive message>"
   git push --force-with-lease origin <branch>
   ```
3. **Never push multiple commits** to an existing PR — always maintain single commit

**Why re-squash?**
- Each PR should represent ONE logical change
- Multiple commits clutter history when squash-merged
- Clean history: one PR = one commit on main

### PR Requirements
- Reference issue: `Fixes #123` in PR description
- Pass CI checks
- **Human review required** — Copilot review is supplemental, not sufficient for merge

### PR Workflow Steps
1. Create feature branch: `git checkout -b feature/issue-123-description`
2. Commit changes to feature branch
3. Push to remote: `git push origin feature/issue-123-description`
4. Create PR: `github_create_pull_request` with `Fixes #123` in description
5. Request review: `github_request_copilot_review` or mention reviewers
6. **HALT — report PR URL to user**
7. Address feedback with new commits on branch (when user provides feedback)
8. **Wait for human to merge** — NEVER merge automatically.

---

## Permission Requirements

| Operation | Permission | Notes |
|-----------|------------|-------|
| Create PR | `pull_requests: write` | Agent can create PRs |
| Create Issue | `issues: write` | Agent can create/update issues |
| Merge PR | `pull_requests: write` | **PROHIBITED by guidelines** — human only |
| Push to branch | `contents: write` | Agent can push to feature branches |

---

## When GitHub MCP Tools Unavailable

**Use local squash-merge:**
- Follow 110-git-protocol.md Section 6
- Script-based workflow for merges
- Wait for explicit "merge" instruction

---

*Source: Content migrated from `020-github-workflow.md`*