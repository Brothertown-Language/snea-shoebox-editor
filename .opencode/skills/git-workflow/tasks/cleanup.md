# Task: cleanup

## Purpose

Delete merged branches after PR merge, clean stale references, and verify repository state is ready for next work session.

## Workflow

1. **After PR merge:** Run when human confirms "PR merged" or similar
1. **Automatic detection:** Can also run when invoked to check for merged branches
1. **Mandatory cleanup:** ALL merged branches must be deleted (local and remote)

## TodoWrite Progress Tracking

**Before starting workflow, show progress to developer:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "in_progress", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "pending", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "pending", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "pending", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "pending", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "pending", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "pending", "priority": "medium"},
])
```

**Update after each step completes.**

## Preconditions

- Human confirms "PR merged" or similar
- OR skill invoked with cleanup detection enabled

## Postconditions

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

**Update progress:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "in_progress", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "pending", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "pending", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "pending", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "pending", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "pending", "priority": "medium"},
])
```

### Step 2: Hotfix Dev-Merge Ticket (Hotfix PRs ONLY)

**If PR targets `main` (hotfix), create a ticket for merging `main` → `dev`:**

```python
# Detect hotfix PR
pr_info = github_pull_request_read(method="get", owner=..., repo=..., pullNumber=...)

is_hotfix = (
    pr_info["base"]["ref"] == "main" and
    ("hotfix" in pr_info.get("labels", []) or 
     pr_info["head"]["ref"].startswith("hotfix/"))
)

if is_hotfix and pr_info.get("merged_at"):
    # Create ticket for dev merge
    ticket = github_issue_write(
        method="create",
        owner=...,
        repo=...,
        title=f"[SPEC] Merge main to dev - Hotfix: {pr_info['title']}",
        body=f"""# Dev Merge Required for Hotfix

**Hotfix PR:** #{pr_info['number']}
**Merged to main:** {pr_info['merged_at']}
**Hotfix description:** {pr_info['body']}

## Affected Files

{chr(10).join(pr_info.get('files', []))}

## Action Required

Merge `main` → `dev` to propagate hotfix to integration branch.

```bash
git checkout dev
git merge main
git push origin dev
```

---
🤖 Auto-created by cleanup task after hotfix merge.
""",
        labels=["hotfix", "needs-approval"]
    )
    
    # Post chat message
    print(f"Hotfix merged to main. Ticket #{ticket['number']} created for dev merge.")
```

**Ticket Format:**
- Title: `[SPEC] Merge main to dev - Hotfix: <hotfix title>`
- Labels: `hotfix`, `needs-approval`
- Body: Hotfix PR reference, commit hashes, affected files
- Chat message: "Hotfix merged to main. Ticket #N created for dev merge."

**Skip for non-hotfix PRs:**
- PRs targeting `dev` → no ticket (normal feature workflow)
- PRs without `hotfix` label targeting `dev` → no ticket
- Direct commits to `main` (no PR) → no ticket (hotfix workflow requires PR)

**Update progress:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "completed", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "in_progress", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "pending", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "pending", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "pending", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "pending", "priority": "medium"},
])
```

### Step 3: Switch to Dev

```bash
git checkout dev
git pull origin dev
```

**Update progress:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "completed", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "completed", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "in_progress", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "pending", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "pending", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "pending", "priority": "medium"},
])
```

### Step 4: Delete Current Merged Branch

```bash
# Delete local branch
git branch -d <merged-branch-name>

# Delete remote branch (if not auto-deleted by GitHub)
git push origin --delete <merged-branch-name> 2>/dev/null || echo "Remote already deleted"

# Prune stale remote references
git fetch --prune
```

**Update progress:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "completed", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "completed", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "completed", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "in_progress", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "pending", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "pending", "priority": "medium"},
])
```

### Step 5: Clean Other Merged Branches

**Find merged branches:**

```bash
git branch --merged dev
```

**For each merged branch (except main/master):**

```bash
git branch -d <branch>
```

**Update progress:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "completed", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "completed", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "completed", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "completed", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "in_progress", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "pending", "priority": "medium"},
])
```

### Step 6: Verify Clean State

```bash
git status --porcelain  # Must be empty
git branch -vv          # Should show minimal branches
```

**Update progress:**

```python
todowrite([
    {"content": "Step 1: Verify PR merge", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Hotfix dev-merge ticket", "status": "completed", "priority": "medium"},
    {"content": "Step 3: Switch to dev", "status": "completed", "priority": "high"},
    {"content": "Step 4: Delete current branch", "status": "completed", "priority": "high"},
    {"content": "Step 5: Clean other merged branches", "status": "completed", "priority": "medium"},
    {"content": "Step 6: Verify clean state", "status": "completed", "priority": "high"},
    {"content": "Step 7: Clear workflow todos", "status": "in_progress", "priority": "medium"},
])
```

---

### Step 7: Clear Workflow Todos

**After cleanup complete:**

```python
# Clear any remaining workflow todos
todowrite(todos=[])
```

**Why:** Ensures clean state for next work session. Todo lists track progress within workflows - once workflow completes, todos are no longer needed.

---

## Context Required

- Guidelines: `114-git-branch-cleanup.md`, `124-github-archive-workflow.md`
- Related skills: `approval-gate` (issue closure timing)
- Related tasks: `pr-creation` (after this), `review-prep` (before PR)

## Branch Status Decision Tree

```
Merged PR (current branch just merged)
    │
    ├─► Switch to dev: git checkout dev
    │
    ├─► Pull latest: git pull origin dev
    │
    ├─► Delete local: git branch -d <branch>
    │
    ├─► Delete remote: git push origin --delete <branch>
    │
    └─► Prune: git fetch --prune

Merged PR (other branches from previous sessions)
    │
    ├─► List merged: git branch --merged dev
    │
    └─► For each (except dev):
            git branch -d <branch>
```

## Safety Checks Before Deletion

Before ANY branch deletion:

1. **Merged status:** `git branch --merged dev` includes the branch ✓
1. **GitHub PR status:** PR is "merged" (not "closed") ✓
1. **Not current branch:** `git branch --show-current` ≠ branch to delete ✓
1. **Not protected:** Branch name ≠ `main`, `master` ✓
1. **Clean working tree:** `git status --porcelain` returns empty ✓

**If ANY check fails → SKIP that branch with warning.**

## Sub-Issue Double-Check (Subtask)

After closing child issues addressed by PR, invoke the `verify-sub-issues` subtask to verify remaining sub-issues before closing parent:

```
/task subagent_type="general" description="Verify sub-issues" prompt="Use the git-workflow skill verify-sub-issues subtask to verify all child issues are closed before closing parent issue #PARENT_ISSUE."
```

**Subtask returns:**
- `can_close_parent: true` → Proceed to close parent
- `can_close_parent: false` → BLOCK parent closure
- `open_children: [...]` → List of blocking issues with analysis
- `action: "POST_WARNING"` → Post warning comment to parent

**If `can_close_parent: false`:**
- DO NOT close parent issue
- Post warning comment from subtask response
- Inform user that remaining sub-issues must be addressed

**If `can_close_parent: true`:**
- Close parent issue with summary
- Report completion

**Why this is a subtask:**
- Sub-issue classification requires agent intelligence
- Superseded links, PR links, state reasons require verification
- Isolates complex logic from main cleanup flow
- Returns structured data for decision-making

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
