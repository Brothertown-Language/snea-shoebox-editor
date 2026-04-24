# Task: cleanup/branch-cleanup

## Purpose

Delete merged branches, clean stale references, remove worktrees, sync dev, and verify clean repository state after PR merge.

## Entry Criteria

- PR merge verified (cleanup/verify-merge completed)
- Issue closure completed (cleanup/issue-closure completed)

## Exit Criteria

- Local merged branch deleted
- Remote merged branch deleted (if applicable)
- Stale remote references pruned
- Dev branch synced with remote (verified via hash comparison)
- Working tree clean

## Procedure

### Step 1: Switch to Dev and Sync (Fast-Forward Only)

```bash
git checkout dev
git pull origin dev --ff-only
```

**🚫 CRITICAL: The `--ff-only` flag is MANDATORY.** A plain `git pull origin dev` can silently succeed with a merge commit, hiding divergence issues.

**If `--ff-only` fails (diverged history):**
```bash
# HALT and report. Suggest manual resolution.
# Do NOT proceed with stale codebase
```

**Verify local dev matches the merge commit:**
```bash
git log --oneline -1 origin/dev
git log --oneline -1 dev
```

The two commit hashes MUST match. If they differ, re-pull and verify.

**Worktree context:** If running from a worktree, operate on the main working tree:
```bash
git -C /path/to/main/repo checkout dev && git -C /path/to/main/repo pull origin dev --ff-only
```

### Step 1.5: Dev Sync Verification Gate (MANDATORY — ZERO TOLERANCE)

1. Run: `git checkout dev && git pull origin dev --ff-only`
2. Capture local hash: `git log --oneline -1 dev`
3. Capture remote hash: `git log --oneline -1 origin/dev`
4. Compare hashes — they MUST match exactly
5. If hashes differ → re-pull and verify again (maximum 3 attempts)
6. If still different after 3 attempts → HALT and report

**Evidence artifact (MANDATORY):** Tool-call output showing matching hashes MUST be present before proceeding.

🚫 FORBIDDEN: Proceeding past this gate without matching hash evidence.

### Step 2: Remove Feature Worktree

```bash
SANITIZED=$(echo "<merged-branch-name>" | tr '/' '-')
WT_PATH=".worktrees/${SANITIZED}"

if [ -d ".worktrees" ] && git worktree list | grep -q "$WT_PATH"; then
    git worktree remove "$WT_PATH"
fi
```

### Step 2.5: Check for Active Parallel Worktrees

```bash
REMAINING=$(git worktree list | grep -c ".worktrees/spec-\|.worktrees/feature-")
if [ "$REMAINING" -gt 0 ]; then
    echo "Other feature worktrees still active: $REMAINING remaining"
    echo "Skipping git worktree prune"
else
    git worktree prune
fi
```

In parallel sub-agent mode, other agents may still be working in their worktrees. Only prune when ALL parallel work is confirmed complete.

### Step 3: Delete Current Merged Branch

```bash
git branch -d <merged-branch-name>
git push origin --delete <merged-branch-name> 2>/dev/null || echo "Remote already deleted"
git fetch --prune
git remote prune origin
```

**Why `git remote prune origin` is mandatory:** Stale remote-tracking references cause confusion and can interfere with new branch creation.

### Step 3.5: Work Branch Cleanup

When the merged branch was a work branch (created by `assemble-work`):

1. Delete individual feature branches that were squash-merged into the work branch
2. Delete the work branch itself
3. Remove individual feature worktrees
4. Remove work state file: `rm .opencode/tmp/work-*.md`
5. Prune remote references

**⚠️ CRITICAL: Never delete a work branch or its feature branches until the work PR is confirmed merged via GitHub API.**

### Step 4: Clean Other Merged Branches

```bash
git branch --merged dev
```

For each merged branch (except main/master/dev): `git branch -d <branch>`

### Step 5: Verify Clean State

```bash
git status --porcelain  # Must be empty
git branch -vv          # Should show minimal branches
```

### Step 6: Succinct Confirmation

**The `cleanup` task is THE END of the PR workflow. It MUST produce a one-line succinct confirmation and then HALT.**

```
PR #<number> merged. Branch `<branch-name>` deleted. Cleanup complete.
```

**⚠️ CRITICAL: Do NOT re-report PR details or issue lists. The PR was already reported at creation time.**

### Final HALT (CRITICAL)

After cleanup, the agent MUST HALT. No prompting, no questions, no next steps.

| Action | Status |
| -- | -- |
| Close issues | ✅ Done |
| Delete branches | ✅ Done |
| Post final summary | ✅ Done |
| Ask "What's next?" | 🚫 NEVER |

## Context Required

- Related tasks: `cleanup/verify-merge`, `cleanup/issue-closure`
- Related guidelines: `000-critical-rules.md` (branch deletion rules)