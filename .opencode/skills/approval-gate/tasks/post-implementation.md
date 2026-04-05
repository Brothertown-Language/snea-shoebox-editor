# Task: post-implementation

## Purpose

Push feature branch, generate compare URL, and report completion for developer review.

## Workflow Triggers

**Invoke this task at these workflow points:**
- After implementation completes (mandatory - no decision point)

The sequence is:

1. Implementation complete → **invoke post-implementation**
1. Branch pushed, compare URL generated → HALT
1. Wait for developer to say "create a PR"

**DO NOT skip this task after implementation. DO NOT ask the developer if they want review. Just push the branch.**

## Preconditions

- Implementation work complete
- All changes committed on feature branch
- Authorization scope verified

## Postconditions

- Feature branch pushed to remote
- GitHub compare URL generated
- Completion reported to issue and chat
- HALT for developer review

## Procedure

### Step 0: Determine Implementation Outcome

**Check if any changes were made:**

```bash
git status --porcelain
```

**If EMPTY (no file changes):**

- Skip to "No-Changes Path" below
- This means implementation was already complete or no changes needed

**If NOT EMPTY (file changes exist):**

- Continue to Step 1 (Push Feature Branch)

______________________________________________________________________

### No-Changes Path (Already Implemented)

**When implementation determined no changes were needed:**

1. **Close issue directly:**

   - Post verification comment explaining what was checked
   - Use `github_issue_write(method="update", state="closed", state_reason="completed")`

1. **Comment format:**

```markdown
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Summary:**

Verified all proposed changes were already implemented. No modifications needed.

**Verification Results:**

- [List what was checked with file references and function names]
- [Confirm each requirement from spec is present]

**Outcome:** <What the verification confirmed>
```

3. **HALT after closing:**
   - No branch push
   - No compare URL
   - No PR needed
   - Report completion in chat

______________________________________________________________________

### Step 1: Push Feature Branch

```bash
git push -u origin <branch-name>
```

This pushes the branch WITHOUT creating a PR.

### Step 2: Generate Compare URL

Using session values (GIT_OWNER, GIT_REPO):

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/main...<branch-name>
```

### Step 3: Report Completion

Format for issue and chat:

```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Ready for Review:**

https://github.com/<owner>/<repo>/compare/main...<branch-name>
```

### Step 4: HALT

**DO NOT:**

- Create PR (requires explicit "create a PR")
- Squash commits (happens at PR creation)
- Push again (already pushed)

**WAIT for:**

- Developer to review via GitHub diff viewer
- Explicit "create a PR" instruction

## Context Required

- Session values: GIT_OWNER, GIT_REPO, branch name
- Guidelines: `113-git-pr-workflow.md` (review phase)
- Related tasks: `commit-prep` (squash), `pr-creation` (PR)

## Why This Task Is Critical

- Developers need visibility before PR creation
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"
