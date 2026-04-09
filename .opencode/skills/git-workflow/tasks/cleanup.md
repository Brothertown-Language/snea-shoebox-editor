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

### Step 1: Succinct Confirmation Template (CRITICAL)

**The `cleanup` task is THE END of the PR workflow. It MUST produce a one-line succinct confirmation and then HALT.**

**Succinct Confirmation Template:**

```
PR #<number> merged. Branch `<branch-name>` deleted. Cleanup complete.
```

**⚠️ CRITICAL: Do NOT re-report PR details or issue lists. The PR was already reported at creation time.**

### Step 2: Verify PR Merge (CRITICAL - NO EXCEPTIONS)

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

### Step 3: Switch to Dev

**Three-Branch Workflow:** After feature PR merge, switch to `dev` (not `main`).

```bash
git checkout dev
git pull origin dev
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

### Step 5: Clean Other Merged Branches

**Find merged branches:**
```bash
git branch --merged dev
```

**For each merged branch (except main/master/dev):**
```bash
git branch -d <branch>
```

### Step 6: Verify Clean State

```bash
git status --porcelain  # Must be empty
git branch -vv          # Should show minimal branches
```

## Branch Cleanup After Merge — MANDATORY

**⚠️ CRITICAL: Cleanup is NOT Optional**

After EVERY merged PR, cleanup is MANDATORY — no exceptions, no "I'll do it later".

### ✅ ALWAYS DO — IMMEDIATELY After Merge Confirmation

1. **Delete local feature branch** — `git branch -d <branch-name>`
2. **Delete remote branch** — `git push origin --delete <branch-name>` (if not auto-deleted by GitHub)
3. **Verify cleanup** — `git branch -vv` to confirm deletion
4. **Prune remote references** — `git fetch --prune`

**This is NOT optional.** Cleanup happens in the same session as merge confirmation.

### ✅ ALWAYS DO — When User Asks "cleanup branches"

1. **List merged local branches** — `git branch --merged dev`
2. **Delete merged local branches** — `git branch -d <branch-name>` for each
3. **List merged remote branches** — `git branch -r --merged dev`
4. **Delete merged remote branches** — `git push origin --delete <branch-name>` for each
5. **Prune stale remote refs** — `git fetch --prune`
6. **Verify cleanup** — `git branch -a` to confirm clean state

**⚠️ CRITICAL: Clean BOTH local AND upstream.** Leaving stale remote branches defeats the purpose.

## Branch Status Categories

| Status | Condition | Action |
|--------|-----------|--------|
| **Fully merged** | `ahead=0, behind=0` or PR merged | **DELETE IMMEDIATELY** |
| **Superseded** | PR closed/merged, changes incorporated via other branch | **DELETE IMMEDIATELY** |
| **Stale** | Behind main by many commits, no PR, no recent work | Safe to delete |
| **Active** | Has unmerged commits, open PR, or active work | **Do NOT delete** |

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

### Safety Checks Before Deletion

| Check | Purpose | Method |
|-------|---------|--------|
| Branch merged | Prevent deleting unmerged work | `git branch --merged dev` |
| PR status | Confirm merge (not just closed) | GitHub API |
| Not current | Prevent deleting active branch | `git branch --show-current` |
| Not protected | Block main/master deletion | Hardcoded exclusion |
| Clean working tree | Ensure no uncommitted changes | `git status --porcelain` |

**If ANY check fails → SKIP that branch with warning.**

## Archive Workflow (Completion)

### When to Archive

Archive a spec **immediately** after the final phase is approved and the PR is merged:

1. All steps marked `☑`
2. PR merged (not just created)
3. Add closing summary comment to issue
4. Close the GitHub Issue (state change only)

### Archive Process

**All specs use GitHub Issues as the authoritative source** (no local files needed).

**Archive process:** Add closing summary comment, then close the GitHub Issue.

⚠️ **CRITICAL:** NEVER edit the issue body when closing. Adding `STATUS: completed` or `COMPLETED: YYYY-MM-DD` to the body destroys history. Use comments instead.

## Issue Closure Timing

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

### 🚫 PROHIBITED

1. **NEVER close an issue immediately after implementation**
2. **NEVER close an issue when PR is created but not merged**
3. **NEVER close an issue when PR is submitted for review**
4. **NEVER close an issue based on `git pull` alone** — MUST verify via GitHub API

### ✅ REQUIRED SEQUENCE

| Step | Action | Agent Role |
|------|--------|------------|
| Implementation complete | Create PR with `Fixes #123` | ✅ Agent creates PR |
| PR created | Report URL, HALT | ✅ Agent waits |
| Human merges PR | Merge happens | 🚫 Human ONLY |
| User confirms merge | Call `github_pull_request_read method=get` | ✅ Agent verifies |
| PR state = merged | Close issue | ✅ Agent closes |

## Parent/Child Issue Closure

**Parent issues MUST NOT be closed while ANY child issues remain open.**

### 🚫 PROHIBITED

1. **NEVER close a parent `[SPEC]` issue when ANY child `[Task]` issues are still open**
2. **NEVER close a parent after PR merge if other child tasks are incomplete**
3. **NEVER assume "the PR covers everything" when sub-issues exist**

### Example Workflow

```
SPEC #100 (parent)
├── Task #101: Phase 1 - Database schema
├── Task #102: Phase 2 - API endpoints
└── Task #103: Phase 3 - UI components

PR merges for Phase 1 → Close #101 ONLY
#100 remains open (children #102, #103 pending)

Later, PR merges for Phase 2 → Close #102 ONLY
#100 remains open (child #103 pending)

Later, PR merges for Phase 3 → Close #103 AND #100 (all children done)
```

### Exception: All Children Completed

When ALL child issues are completed by a single PR merge:

1. Close the child issue corresponding to the PR
2. **ALSO close the parent issue** (all children are now complete)
3. Add summary comment to the parent explaining all work is complete

## Closing Summary (Required)

Before closing any issue (SPEC or Task), the AI agent MUST provide a final summary comment.

### Summary Requirements

- **Summary of Changes**: High-level overview of what was implemented
- **Test Results**: Summary of verification steps (tests run, coverage, manual checks)
- **Impacts**: Any impacts on other issues or project components
- **Superseded/Not Implemented**: Explicitly state if any planned items were superseded, deferred, or intentionally skipped

### Example Closing Comment

```
🤖 ✅ **Issue Closing Summary**
- **Changes**: Implemented the new rate limiting middleware in `pubmed_client.py` and updated workflow docs.
- **Test Results**: All 12 unit tests passed. Manual verification confirmed retry logic works.
- **Impacts**: None on existing issues.
- **Superseded/Not Implemented**: The "Phase 3: Circuit breaker" was deferred to a follow-up issue #165.

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### When to Close

**Only close after PR merge:**

1. PR has been reviewed
2. PR has been merged by human
3. CI/CD passed (if applicable)
4. THEN close the issue with summary comment

## Branch Status Decision Tree

```
Merged PR (current branch just merged)
    │
    ├─► Switch to main: git checkout dev
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
    ├─► List merged: git branch --merged dev
    │
    └─► For each (except main/master):
            git branch -d <branch>
```

## Safety Checks Before Deletion

Before ANY branch deletion:

1. **Merged status:** `git branch --merged dev` includes the branch ✓
2. **GitHub PR status:** PR is "merged" (not "closed") ✓
3. **Not current branch:** `git branch --show-current` ≠ branch to delete ✓
4. **Not protected:** Branch name ≠ `main`, `master` ✓
5. **Clean working tree:** `git status --porcelain` returns empty ✓

**If ANY check fails → SKIP that branch with warning.**

## Sub-Issue Closure Enforcement (CRITICAL)

**⚠️ CRITICAL: Sub-issues are closed by the platform via "Fixes #N" annotations, NOT manually by the agent.**

### 🚫 FORBIDDEN

- **Closing sub-issues after implementation but BEFORE PR merge**
- **Closing sub-issues when PR is created but not merged**
- **Manually closing sub-issues that have "Fixes #N" in PR description**
- **Closing sub-issues without verifying PR merge via GitHub API**

### ✅ REQUIRED WORKFLOW

**The platform (GitBucket/GitHub) closes issues automatically via "Fixes #N" annotations.**

1. **Implement sub-issue** → Create PR with `Fixes #N` in description
2. **PR created** → Report URL, HALT
3. **Human merges PR** → Platform automatically closes sub-issue
4. **User confirms "pr merged"** → Agent verifies merge via GitHub API
5. **Agent verifies sub-issues are closed** → API check (`state: "closed"`)
6. **If sub-issue still open (edge case)** → Agent closes it manually
7. **All sub-issues closed?** → Close parent issue

### Verification Sequence

```python
# Step 1: Verify PR merge via GitHub API
pr = github_pull_request_read(method="get", owner=..., repo=..., pullNumber=...)
if pr.get("merged_at") is None:
    halt("PR not merged yet")

# Step 2: Check all sub-issues are closed (platform should have done this)
children = github_issue_read(method="get_sub_issues", issue_number=parent)
open_children = [c for c in children if c["state"] == "open"]

if open_children:
    # Edge case: Platform failed to auto-close
    for child in open_children:
        github_issue_write(method="update", issue_number=child["number"], 
                          state="closed", state_reason="completed")

# Step 3: Close parent only after all children closed
if not open_children:
    github_issue_write(method="update", issue_number=parent,
                       state="closed", state_reason="completed")
```

### "Fixes #N" Annotation (MANDATORY)

**PR descriptions MUST include sub-issue numbers:**

```markdown
Fixes #86, #87, #88

[PR body...]
```

This enables automatic closure by GitBucket/GitHub.

### Edge Case Handling

| Scenario | Action |
|----------|--------|
| Platform fails to auto-close sub-issue | Agent closes manually after PR merge verification |
| PR closed without merge | Sub-issues remain open (correct behavior) |
| Draft PR | Sub-issues remain open until PR is merged (correct behavior) |
| Multiple sub-issues in one PR | Include all in "Fixes #N, #M, #P" annotation |

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

## Final HALT (CRITICAL)

**After closing issues and posting final summary, the agent MUST HALT.**

**HALT = Stop all further action. No prompting, no questions, no next steps.**

### What HALT Means After Cleanup

| Action | Status |
|--------|--------|
| Close issues | ✅ Done |
| Delete branches | ✅ Done |
| Post final summary | ✅ Done |
| Ask "What's next?" | 🚫 NEVER |
| Prompt for next task | 🚫 NEVER |
| Suggest new work | 🚫 NEVER |

**The workflow is complete. The agent stops. The human decides what happens next.**

### Correct Final Output

```
PR #81 merged. Branch `spec/github-issue-creation-skill` deleted. Cleanup complete.
```

**That's it. ONE LINE. Succinct confirmation. Then stop.**

### 🚫 CRITICAL VIOLATIONS After Cleanup

| Violation | Example |
|-----------|---------|
| Continue without new instruction | "Ready for next task?" |
| Suggest next work | "Should I start on #75?" |
| Prompt for anything | "What would you like me to do?" |
| Not posting final summary | Missing executive summary |

**The cleanup task is the END. HALT means STOP.**# Git Protocol: Merge Protocol

## 5. Spec Implementation Branches

### ✅ ALWAYS DO

When implementing an approved spec:

1. **Branch Naming**: Derive from spec filename or issue — `spec/<short-name>` (e.g., `plans/SPEC-mesh-descriptor-lookup.md` → `spec/mesh-descriptor-lookup` or Issue #15 → `spec/project-first-strategy`)

2. **Branch Creation**: Before any implementation, create and checkout the branch:
   ```bash
   git checkout dev
   git pull origin main
   git checkout -b spec/<short-name>
   ```

3. **Work in Isolation**: All implementation commits go on the spec branch, never on main

4. **Easy Rollback**: If implementation fails, simply `git checkout dev && git branch -D spec/<short-name>`

### 📋 Merging Spec Branches

**When GitHub MCP Tools Available:**

Use PR workflow instead of local merge:

**Before creating PR:**
1. **Rebase on main**: `git fetch origin && git rebase origin/dev`
2. **Squash commits**: Interactive rebase to consolidate multiple commits
3. **Force push**: `git push --force-with-lease origin <branch>`
4. **Then create PR**: Only after branch is clean and rebased

**PR Workflow Steps:**
1. Create feature branch: `git checkout -b feature/issue-123-description`
2. Commit changes to feature branch
3. Push to remote: `git push origin feature/issue-123-description`
4. Create PR: `github_create_pull_request` with `Fixes #123` in description
5. Request review: `github_request_copilot_review`
6. Address feedback with new commits
7. **WAIT for human to merge** — NEVER call `github_merge_pull_request` yourself
8. Delete branch after human merges

### ⚠️ MANDATORY: SQUASH MERGE ONLY

**All PRs MUST be squash-merged to `main`.**

- Never use regular merge — always squash
- Never use rebase-merge — always squash
- This maintains a clean commit history on `main`
- One commit per PR, with PR number in commit message

**For humans merging PRs:**
- GitHub "Squash and merge" button is required
- Never click "Merge" or "Rebase and merge" buttons

**When Local Merge is Acceptable (even with MCP tools):**
- Trivial fixes (typos, whitespace, single-line changes)
- Urgent hotfixes requiring immediate deployment
- Docs-only changes that don't affect production code

---

## When GitHub MCP Tools Unavailable

**Use local squash-merge:**

### ✅ ALWAYS DO

**When merging a feature branch into main:**
- Use **squash-merge** to create a single clean commit
- Delete the feature branch after merge
- Include spec reference in commit message

**When keeping a feature branch up-to-date:**
- Use **rebase** (not merge) to pull latest changes from dev
- `git fetch origin && git rebase origin/dev`

### 🚫 NEVER DO
- **NEVER use regular merge** (`git merge`) to merge feature branches into main — creates messy history
- **NEVER use merge** to sync feature branch with main — use rebase instead
- **NEVER force-push to main**

### Rebase Workflow

```bash
# On feature branch
git fetch origin
git rebase origin/dev

# If conflicts occur, resolve them and continue
git status  # see which files conflict
# edit conflicting files
git add <resolved-files>
git rebase --continue
```

---

*Source: Content migrated from `110-git-protocol.md`*
---
*Source: Migrated from .opencode/guidelines/112-git-merge-protocol.md*
