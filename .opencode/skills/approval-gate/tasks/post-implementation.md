# Task: post-implementation

## Purpose

Push feature branch, generate compare URL, and report completion for developer review.

## ⚠️ MANDATORY INVOCATION

**This task is ALWAYS invoked automatically after implementation completes. There is NO decision point.**

The sequence is:
1. Implementation complete → **post-implementation invoked automatically**
2. Branch pushed, compare URL generated → HALT
3. Wait for developer to say "create a PR"

**DO NOT skip this task after implementation. DO NOT ask the developer if they want review. Just push the branch.**

## Entry Criteria

- Implementation work complete
- All changes committed on feature branch
- Authorization scope verified

## Exit Criteria

- Feature branch pushed to remote
- GitHub compare URL generated
- Completion reported to issue (NO URL) and chat (with URL)
- HALT for developer review

## Procedure

### Step 1: Determine Implementation Outcome

**Check if any changes were made:**

```bash
git status --porcelain
```

**If EMPTY (no file changes):**
- Skip to "No-Changes Path" below
- This means implementation was already complete or no changes needed

**If NOT EMPTY (file changes exist):**
- Continue to Step 2 (Push Feature Branch)

---

### No-Changes Path (Already Implemented)

**When implementation determined no changes were needed:**

1. **Report completion to chat:**
    - Summarize what was completed
    - No compare URL needed

2. **HALT after reporting:**
    - No branch push (already pushed)
    - No PR creation

---

### Step 2: Push Feature Branch

```bash
git push -u origin <branch-name>
```

This pushes the branch WITHOUT creating a PR.

### Step 3: Generate Compare URL

Using session values (GIT_OWNER, GIT_REPO):

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

### Step 4: Report Completion

Report to chat (exec summary + URL):
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

Compare URL: https://github.com/<owner>/<repo>/compare/dev...<branch-name>
```

### Step 5: HALT

**DO NOT:**
- Create PR (requires explicit "create a PR")
- Squash commits (happens at PR creation)
- Push again (already pushed)

**WAIT for:**
- Developer to review via GitHub diff viewer
- Explicit "create a PR" instruction

## Context Required

- Session values: GIT_OWNER, GIT_REPO, branch name
- Related tasks: `pr-creation` (PR)

## Why This Task Is Critical

- Developers need visibility before PR creation
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"