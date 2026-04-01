# Task: pre-work

## Purpose

Verify branch state, preserve changes, create feature branch BEFORE any implementation work begins.

## Operating Protocol

1. **Automatic invocation (mandatory):** This task is invoked automatically when:
   - User says `approved`, `go`, or similar authorization to begin implementation
   - DO NOT prompt for invocation - the skill is triggered automatically

## Entry Criteria

- User has authorized implementation (explicit `approved` or `go`)
- Authorization is for the correct issue
- Sub-issue structure verified (for multi-task specs)

## Exit Criteria

- Feature branch created from main
- Working tree clean (stashed if needed)
- Verified ready for implementation

## Procedure

### Step 1: Check Current Branch

```bash
git branch --show-current
```

If on `main` → MUST create feature branch first.

### Step 2: Check for Pending Changes

```bash
git status
```

### Step 3: Stash External Changes (If Any)

If ANY files modified (even one line, even external edits):

```bash
git stash push -m "WIP: external changes before <branch-name>"
git stash list  # VERIFY stash was created
git status      # VERIFY clean working tree
```

**CRITICAL:** If `git status` STILL shows modifications after stash → STOP. Report the failure. Do NOT proceed.

### Step 4: Create Feature Branch

```bash
git checkout main && git pull origin main
git checkout -b spec/<short-name>  # or feature/<description>
```

### Step 5: Report Ready

Report: "Ready for implementation on branch: <branch-name>"

## ⚠️ Edge Case: Already Implemented (No Changes Needed)

**When investigation reveals spec is already implemented:**

1. **Detect before branch creation:**
   - After reading files, verify all proposed changes are already present
   - Confirm no modifications needed
   - Document verification in issue comment

2. **Skip branch creation entirely:**
   - Do NOT create feature branch
   - Do NOT push anything
   - Do NOT create PR

3. **Close issue directly:**
   - Post verification comment explaining what was checked
   - Close issue with `state_reason: "completed"`
   - Report completion in chat

**Example Comment:**
```markdown
🤖 ✅ Completed by <AgentName> (<ModelID>)

**Summary:**

Verified all proposed changes were already implemented. No modifications needed.

**Verification Results:**

- [List what was checked and confirmed present]
- [File references with function names for existing content]

**Outcome:** Spec requirements verified complete without additional changes.
```

4. **HALT after closing:**
   - No further steps needed
   - No branch cleanup (no branch was created)

## Context Required

- Guidelines: `110-git-branch-first.md`, `114-git-branch-cleanup.md`
- Related skills: `approval-gate` (authorization check)
- Related tasks: `cleanup` (branch cleanup after PR merge)

## Common Issues

| Issue | Resolution |
|-------|------------|
| Stash failed | STOP. Report failure. Let user resolve manually. |
| Wrong branch detected | STOP. Do not commit. Stash changes, switch to correct branch. |
| Accidental main commit | Create recovery branch, reset main, switch to recovery branch. |

## Safety Checks

Before proceeding, verify ALL:

- Current branch is NOT `main`
- Working tree IS clean (`git status --porcelain` returns empty)
- Branch name follows convention (`spec/` or `feature/` prefix)

**If ANY check fails → STOP and report.**