# Task: pre-work

## Purpose

Verify branch state, preserve changes, create feature branch BEFORE any implementation work begins.

## Workflow Triggers

**Invoke this task at these workflow points:**
- User says `approved`, `go`, or similar authorization to begin implementation
- DO NOT prompt for invocation - invoke automatically at these triggers

## Preconditions

- User has authorized implementation (explicit `approved` or `go`)
- Authorization is for the correct issue
- Sub-issue structure verified (for multi-task specs)

## Postconditions

- Feature branch created from dev
- Working tree clean (stashed if needed)
- Verified ready for implementation

## Procedure

### Step 1: Verify Branch State and Stash (Subtask)

Invoke the `verify-stash-branch` subtask to check current branch and preserve external changes:

```
/task subagent_type="general" description="Verify stash-branch" prompt="Use the git-workflow skill verify-stash-branch subtask to verify clean working tree and preserve external changes before branch creation."
```

**Subtask returns:**
- `success: true` → Proceed to Step 2
- `success: false` → STOP and report failure
- `branch_state.already_exists: true` → Skip Step 2 (already on feature branch)
- `working_tree_state.stashed: true` → Note stash ref for later restoration

**If subtask fails:**
- STOP immediately
- Report failure details to user
- Let user resolve manually

### Step 2: Create Feature Branch (If Needed)

Only if `branch_state.is_main` or `branch_state.is_dev`:

```bash
git checkout dev && git pull origin dev
git checkout -b spec/<short-name>  # or feature/<description>
```

### Step 3: Report Ready

Report: "Ready for implementation on branch: <branch-name>"

## ⚠️ Edge Case: Already Implemented (No Changes Needed)

**When investigation reveals spec is already implemented:**

1. **Detect before branch creation:**

   - After reading files, verify all proposed changes are already present
   - Confirm no modifications needed
   - Document verification in issue comment

1. **Skip branch creation entirely:**

   - Do NOT create feature branch
   - Do NOT push anything
   - Do NOT create PR

1. **Close issue directly:**

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
