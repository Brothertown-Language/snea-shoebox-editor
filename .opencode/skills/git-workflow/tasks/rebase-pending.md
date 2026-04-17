# Task: rebase-pending

## Purpose

After a PR merge is verified, automatically rebase all other pending PRs from the same developer onto the updated `dev` branch. Classify conflicts using the conflict-resolution skill's Tier 1-3 system: Tier 1-2 auto-resolve, Tier 3 (intent) conflicts HALT for developer review.

## Operating Protocol

1. **After merge verification:** Run immediately after Step 2 (verify PR merge) in cleanup
2. **Before dev sync:** Must complete before Step 3 (switch to dev and sync)
3. **Sequential processing:** Rebase one PR at a time to avoid worktree collisions
4. **Force-push after rebase:** Rebased branches must be force-pushed to update remote PRs

## Entry Criteria

- PR merge verified via GitHub API (Step 2 of cleanup complete)
- `merged_at` timestamp confirmed on the just-merged PR
- Local dev branch is up to date (`git pull origin dev`)

## Exit Criteria

- All pending PRs rebased onto updated `dev` OR
- Tier 3 conflicts identified and reported to developer with rebase paused
- Summary report generated listing: rebased cleanly, auto-resolved, blocked
- Existing cleanup steps can proceed after rebase-pending completes

## Procedure

### Step 0: Verify PR Merge (Existing Cleanup Step 2)

This task assumes Step 2 (verify PR merge) has already been completed. The merged PR number is available as context.

```python
# Already verified by cleanup Step 2:
merged_pr_number = <PR number from context>
pr_merge_verified = True  # Passed as entry criteria
```

### Step 1: Identify Pending PRs

List all open PRs and identify candidates for rebasing.

```python
# List all open PRs on the repo
open_prs = github_list_pull_requests(
    owner=<github.owner>,
    repo=<github.repo>,
    state="open"
)

# Filter out the just-merged PR
pending_prs = [pr for pr in open_prs if pr["number"] != merged_pr_number]
```

**If no pending PRs:** Skip to Step 6 (proceed to existing cleanup steps).

**Report candidate PRs:**

```
Rebase candidates: #<N1> (<title1>), #<N2> (<title2>), ...
```

### Step 2: Attempt Rebase for Each Pending PR

Process one PR at a time to avoid worktree collisions.

For each pending PR:

```
a. Fetch latest remote: git fetch origin
b. Create temporary worktree for the PR branch:
   git worktree add .worktrees/rebase-<branch-name> -b <branch-name> origin/<branch-name>
   (If branch already has a worktree, use existing)
c. In worktree, rebase onto updated dev:
   git rebase origin/dev
d. Handle outcome:
   - Clean rebase → proceed to Step 5 (force-push)
   - Conflicts → proceed to Step 3 (conflict classification)
```

**Worktree management:**

```bash
# Create temporary worktree for rebase
WORKTREE_PATH=".worktrees/rebase-<sanitized-branch-name>"
git worktree add "$WORKTREE_PATH" -b <branch-name> origin/<branch-name>

# After rebase (success or HALT), clean up temporary worktree
git worktree remove "$WORKTREE_PATH"
```

**Important:** Always clean up temporary worktrees between PRs. Never leave rebase worktrees dangling.

### Step 3: Conflict Classification

When rebase produces conflicts, invoke the conflict-resolution skill's tier system:

**For each conflicting file, classify:**

| Tier | Name | Criteria | Action |
|------|------|----------|--------|
| 1 | **Trivial** | Whitespace, formatting, reordering of unchanged lines | Auto-resolve, silent |
| 2 | **Textual but safe** | Same intent on both sides, just different text | Auto-resolve, note in chat |
| 3 | **Intent conflict** | Different goals, or resolution could alter spec compliance | HALT for developer review |

**Classification rule:** When in doubt, classify UP to the next tier. Tier 2 vs Tier 3 → treat as Tier 3.

**Auto-resolution for Tier 1-2:**

```bash
# After classifying as Tier 1 or Tier 2:
git add <resolved-files>
git rebase --continue
# Then proceed to Step 5 (force-push)
```

**Tier 2 notification (chat only):**

```
**Conflict Resolution (Tier 2 - Textual):**
- File: <path>
- Reason: <why it's textual but safe>
- Resolution: <which side was accepted>
```

**Tier 3 conflicts:** Proceed to Step 4.

### Step 4: Tier 3 Intent Analysis

When a Tier 3 conflict is detected, perform spec-aware analysis:

```
a. Read the conflicting file content (both sides of the conflict markers)
b. Read the merged PR's issue/spec body:
   github_issue_read(method="get", owner=<github.owner>, repo=<github.repo>, issue_number=<merged_pr_number>)
   (Or locate the spec issue linked from the PR)
c. Read the conflicting PR's issue/spec body:
   github_issue_read(method="get", owner=<github.owner>, repo=<github.repo>, issue_number=<conflicting_pr_number>)
   (Or locate the spec issue linked from the PR)
d. Compare intent:
   - Same intent: Both PRs modify the same file for compatible purposes
     → Auto-resolve (keep both changes), note in chat
   - Different intent: PRs make contradictory changes to the same file/section
     → HALT rebase, report to developer
```

**Intent comparison framework:**

| Scenario | Merged PR Intent | Conflicting PR Intent | Classification |
|----------|-----------------|----------------------|----------------|
| Same file, compatible changes | Add new function | Add different new function | Same intent, auto-resolve |
| Same file, contradictory changes | Delete function X | Modify function X | Different intent, HALT |
| Same file, overlapping changes | Refactor module A | Also refactor module A | Needs analysis, HALT if ambiguous |
| Different files | N/A | N/A | Not Tier 3 (misclassified) |

**Same-intent auto-resolve (Tier 3 → resolved):**

```
**Tier 3 Conflict Resolved (Same Intent):**
- File: <path>
- Merged PR (#N): <spec intent summary>
- Conflicting PR (#M): <spec intent summary>
- Classification: Same intent — both PRs make compatible changes
- Resolution: Kept both changes
```

**Different-intent HALT (Tier 3 → blocked):**

```
⚠️ Intent Conflict Detected (Tier 3)

**File:** <path>
**Merged PR (#N):** <merged PR title> — <spec intent for this file>
**Conflicting PR (#M):** <conflicting PR title> — <spec intent for this file>
**Conflict type:** <description of conflicting goals>

**Agent recommendation:** <summary of why intents differ>

Rebase paused for PR #M. Developer action required:
1. Review the conflict in <worktree-path>/<file>
2. Resolve manually: cd <worktree-path> && git rebase --continue (after editing)
3. Force-push: git push --force-with-lease origin <branch-name>
```

### Step 5: Force-Push Rebased Branches

After successful rebase (or after auto-resolving all conflicts):

```bash
# In the worktree for the rebased branch:
git push --force-with-lease origin <branch-name>
```

**Why `--force-with-lease`:** Prevents overwriting changes made by others since the last fetch. Safer than bare `--force`.

**Report force-push:**

```
PR #<N> (<title>): Rebased and force-pushed successfully.
```

### Step 6: Proceed to Existing Cleanup Steps

After all pending PRs are processed (rebased, auto-resolved, or blocked for developer):

1. Clean up any temporary rebase worktrees
2. Report summary to developer
3. Continue with existing cleanup: Step 3 (switch to dev and sync), Step 4+ (delete branch, close issues, etc.)

**If any Tier 3 conflicts blocked a rebase:**

```
⚠️ Rebase Summary — Action Required

**Cleanly rebased:** #<N1>, #<N2>
**Auto-resolved (Tier 1-2):** #<N3> (files: <list>)
**Blocked for developer review (Tier 3):** #<M1> (files: <list>)
  - See Tier 3 conflict details above

**Next steps for blocked PRs:**
1. Resolve conflicts manually in each blocked worktree
2. Continue rebase: git rebase --continue
3. Force-push: git push --force-with-lease origin <branch-name>

Continuing with cleanup for the merged PR...
```

**If all PRs rebased successfully:**

```
Rebase Summary: All <count> pending PRs rebased onto updated dev.
Continuing with cleanup for the merged PR...
```

## Live Verification (MANDATORY)

**🚫 CRITICAL: Each verification point requires a tool call for evidence. Assertions without tool-call artifacts are VERIFICATION-GAP findings. Rebasing without verified branch state is a CRITICAL GUIDELINE VIOLATION.**

### Branch State Verification Before Rebase

| Check | Tool Call | Expected Result | On Failure |
| -- | -- | -- | -- |
| On correct branch | `git branch --show-current` | PR branch name (not `main`/`dev`) | STRUCTURE-VIOLATION → HALT |
| Worktree location | `git rev-parse --show-toplevel` | Worktree path (not main repo) | STRUCTURE-VIOLATION → HALT |
| Working tree clean | `git status --porcelain` | Empty output | VERIFICATION-GAP → stash or commit first |
| Dev is up to date | `git fetch origin && git log --oneline origin/dev -1` | Recent SHA, post-merge | MISSING-ELEMENT → re-fetch |

### Verification Procedure

**Before each rebase attempt (Step 2), verify branch state:**

```
1. git branch --show-current → EVIDENCE: <branch-name>
2. git rev-parse --show-toplevel → EVIDENCE: <worktree-path-or-main-repo>
3. git status --porcelain → EVIDENCE: "(empty)" for clean tree
4. git fetch origin → EVIDENCE: fetch result
5. git log --oneline origin/dev -1 → EVIDENCE: recent dev SHA
```

### Finding Classification

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| On wrong branch | CONFLICTING | flag-for-review | Switch to correct branch before rebase |
| Not in worktree | STRUCTURE-VIOLATION | auto-fix | Create worktree or use existing one |
| Dirty working tree | VERIFICATION-GAP | conditional | Stash changes before rebase (`git stash`) |
| Dev SHA is stale | MISSING-ELEMENT | auto-fix | `git fetch origin` to update |
| Rebase conflicts (Tier 1-2) | VERIFICATION-GAP | auto-fix | Auto-resolve, note in chat |
| Rebase conflicts (Tier 3) | CONFLICTING | flag-for-review | HALT for developer review |

**These verifications are MANDATORY before each rebase. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

## Edge Cases

| Scenario | Action |
|----------|--------|
| No pending PRs | Skip rebase-pending entirely, proceed to cleanup |
| PR branch force-push fails (stale remote) | Refetch and retry once, then report |
| Worktree already exists for a branch | Use existing worktree, rebase in it |
| Rebase has many Tier 1-2 conflicts | Auto-resolve all, report summary |
| Rebase has even one Tier 3 conflict | HALT that PR's rebase, continue others |
| Developer resolves Tier 3 and continues | Not handled by this task — developer runs `git rebase --continue` and force-pushes manually |
| Branch has been updated by another developer since last fetch | `--force-with-lease` will fail — report and move on |

## Integration Points

| Skill | When |
|-------|------|
| `conflict-resolution` | Invoked when rebase produces conflicts (Tier classification) |
| `git-workflow --task cleanup` | Rebase-pending runs between Steps 2 and 3 of cleanup |
| `git-workflow --task review-prep` | May also produce conflicts during pre-PR rebase |

## Cross-References

- Related skills: `conflict-resolution` (conflict classification and resolution)
- Related guidelines: `000-critical-rules.md` → "Critical Violation: Blind Conflict Resolution"