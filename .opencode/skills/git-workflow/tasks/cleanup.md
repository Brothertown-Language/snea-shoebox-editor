# Task: cleanup

## Purpose

Delete merged branches after PR merge, clean stale references, and verify repository state is ready for next work session.

## Operating Protocol

1. **After PR merge:** Run when human confirms "PR merged" or similar
2. **Automatic detection:** Can also run when invoked to check for merged branches
3. **Mandatory cleanup:** ALL merged branches must be deleted (local and remote)

## Entry Criteria

- Human confirms "PR merged" or similar
- OR skill invoked with cleanup detection enabled

## Exit Criteria

- Local merged branch deleted
- Remote merged branch deleted (if applicable)
- Stale remote references pruned
- Other merged branches cleaned up
- Working tree clean

## Procedure

### Step 1: Verify PR Merge (CRITICAL - NO EXCEPTIONS)

**🚫 CRITICAL VIOLATION: Closing issues without PR merge verification is a CRITICAL GUIDELINE VIOLATION.**

**DO NOT trust `git pull` or local fast-forward. You MUST verify via GitHub API.**

```python
# MUST use GitHub API to verify merge
pr = github_pull_request_read(method="get", owner=..., repo=..., pullNumber=...)

# Verify merged_at timestamp exists
if pr.get("merged_at") is None:
    # PR is not merged, STOP
    report = f"PR #{pullNumber} is not yet merged. Cannot close issues."
    return report

# ONLY after verified merge:
proceed_to_close_issues()
```

**Why API verification is mandatory:**
- `git pull` shows local fast-forward success
- Does NOT verify PR was merged (could be closed/rejected)
- GitHub API `merged_at` field is the ONLY reliable merge indicator
- Closing issues without merged PR loses tracking and audit trail

### Step 2: Switch to Main

```bash
git checkout main
git pull origin main
```

### Step 3: Delete Current Merged Branch

```bash
# Delete local branch
git branch -d <merged-branch-name>

# Delete remote branch (if not auto-deleted by GitHub)
git push origin --delete <merged-branch-name> 2>/dev/null || echo "Remote already deleted"

# Prune stale remote references
git fetch --prune
```

### Step 4: Clean Other Merged Branches

**Find merged branches:**
```bash
git branch --merged main
```

**For each merged branch (except main/master):**
```bash
git branch -d <branch>
```

### Step 5: Verify Clean State

```bash
git status --porcelain  # Must be empty
git branch -vv          # Should show minimal branches
```

## Context Required

- Guidelines: `114-git-branch-cleanup.md`, `124-github-archive-workflow.md`
- Related skills: `approval-gate` (issue closure timing)
- Related tasks: `pr-creation` (after this), `review-prep` (before PR)

## Branch Status Decision Tree

```
Merged PR (current branch just merged)
    │
    ├─► Switch to main: git checkout main
    │
    ├─► Pull latest: git pull origin main
    │
    ├─► Delete local: git branch -d <branch>
    │
    ├─► Delete remote: git push origin --delete <branch>
    │
    └─► Prune: git fetch --prune

Merged PR (other branches from previous sessions)
    │
    ├─► List merged: git branch --merged main
    │
    └─► For each (except main/master):
            git branch -d <branch>
```

## Safety Checks Before Deletion

Before ANY branch deletion:

1. **Merged status:** `git branch --merged main` includes the branch ✓
2. **GitHub PR status:** PR is "merged" (not "closed") ✓
3. **Not current branch:** `git branch --show-current` ≠ branch to delete ✓
4. **Not protected:** Branch name ≠ `main`, `master` ✓
5. **Clean working tree:** `git status --porcelain` returns empty ✓

**If ANY check fails → SKIP that branch with warning.**

## Sub-Issue Double-Check (CRITICAL)

After closing child issues addressed by PR, ALWAYS verify remaining sub-issues before closing parent.

**This requires agent intelligence, not just script logic.**

### Step 1: Query Sub-Issues

```python
children = github_issue_read(method="get_sub_issues", issue_number=parent_issue)
```

### Step 2: Classify Each Sub-Issue

**Already Closed:**
- `state: "closed"` + `state_reason: "completed"` → Done
- `state: "closed"` + `state_reason: "not_planned"` → Intentionally not done
- Closed with "Superseded by #N" comment → Check replacement exists

**Open but May Be Complete:**
- Check comments for "Superseded by #N" → Verify new issue covers work
- Check body for PR link ("Fixes #N") → If merged, work is done

**Open and Incomplete:**
- No PR, no superseded link, no completion comment → BLOCK parent closure

### Step 3: Take Action

```python
open_children = [c for c in children if c.state == "open"]

if open_children:
    # Classify each open child
    truly_incomplete = []
    
    for child in open_children:
        # Agent intelligence required here:
        # - Check state_reason
        # - Check comments for superseded links
        # - Check for merged PR links
        # - Determine if work is actually done
        
        if child_is_truly_incomplete(child):
            truly_incomplete.append(child)
    
    if truly_incomplete:
        # POST WARNING - do NOT close parent
        post_warning_comment(parent, truly_incomplete)
        # DO NOT close parent
    else:
        # All open children have justification
        close_parent_with_summary(parent)
else:
    # All children closed
    close_parent_with_summary(parent)
```

### Step 4: Warning Comment Template

If parent cannot be closed:

```markdown
🤖 ⚠️ **Cannot Close Parent — Open Sub-Issues Detected**

This parent issue cannot be closed because the following sub-issue(s) remain incomplete:

- #N: [Title] — [status analysis]

**Status Analysis:**
- [Explain why each open child cannot be closed]

**To close this parent:**
1. Complete the remaining sub-issue(s)
2. Close each sub-issue when work is complete
3. Or close as "not planned" with explanation if intentionally skipped

---
🤖 ⚠️ Blocked by OpenCode (ollama-cloud/glm-5)
```

**See Also:** `.opencode/guidelines/124-github-archive-workflow.md` → "Parent Closure Pre-Check" section for detailed logic.

## Common Issues

| Issue | Resolution |
|-------|------------|
| Remote branch already deleted | Skip remote deletion, clean local |
| Local has extra commits | Warn user, ask before deleting |
| Multiple PRs from same branch | Wait until ALL PRs merged |
| Stash exists from pre-work | Preserve stash, inform user |

## Automatic Cleanup Detection

When invoked, can check for merged branches:

```python
# Query GitHub for merged PRs
github_list_pull_requests(state="merged", perPage=50)

# For each merged PR:
#   - Check if local branch exists
#   - Check if merged into main
#   - Report cleanup candidate
```

## Why This Task Is Critical

- Feature branches accumulate over time
- Previous sessions may leave merged branches uncleaned
- Stale remote references clutter `git branch -a`
- Clean repository state required for next work session
- Prevents confusion from stale branch references
- **Issues ONLY closed after VERIFIED PR merge**

## Correct vs Incorrect Workflow

### ✅ CORRECT Workflow (Issue Closure)

```
PR created
    ↓
Developer reviews and merges PR
    ↓
Developer confirms "PR merged"
    ↓
cleanup task invoked
    ↓
Verify merge via GitHub API (merged_at field)
    ↓
API confirms merge → Proceed
    ↓
Close child issues addressed by PR
    ↓
Check parent for remaining sub-issues
    ↓
If all children closed → Close parent with summary
```

### 🚫 INCORRECT Workflow (CRITICAL VIOLATION)

```
PR created (or just branch pushed)
    ↓
Immediately close issues (NO MERGE)
    ↓
NO GitHub API verification
NO PR merge status check
NO parent/child structure check
```

**This incorrect workflow VIOLATES critical rules and causes:**
- Issues closed without PR tracking
- No merge verification
- Potential reopen of closed issues if PR rejected
- Lost audit trail