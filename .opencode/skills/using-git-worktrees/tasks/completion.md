# Task: completion

Idempotent completion subtask for using-git-worktrees. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Worktree creation:** Worktree was created and verified to exist
2. **Environment export:** WORKTREE_PATH, BRANCH_NAME, DEV_BASE_HASH exported
3. **Gitignore:** `.worktrees/` directory is gitignored
4. **Test baseline:** Clean test baseline established after setup

## Skill-Specific Completion

1. **Worktree existence verification** (if not already performed):
   - Check evidence that worktree directory exists at expected path
   - If missing: invoke `create-worktree` task as remediation

2. **Environment variable verification** (if not already performed):
   - Check evidence for WORKTREE_PATH, BRANCH_NAME, DEV_BASE_HASH being set/output
   - If missing: re-export from worktree state as remediation

3. **Gitignore verification** (if not already performed):
   - Check `.gitignore` for `.worktrees/` entry
   - If missing: add entry and commit as remediation

4. **Test baseline verification** (if not already performed):
   - Run `uv run pytest test/` from worktree directory
   - If failing: report failures, flag for developer decision on proceeding

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO using-git-worktrees workflow ends without a status message.

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<1-2 sentences describing impact>

**Outcome:** <What the result means for stakeholders>

<URL if applicable, ALWAYS LAST>

🤖 <AgentName> (<ModelId>) <status>
```

### Format Verification Before Halt (MANDATORY)

**Idempotent — safe to invoke multiple times. This verification runs before EVERY halt, regardless of path.**

- [ ] Executive summary present as **first** element
- [ ] Outcome line present after summary
- [ ] URL present IF relevant (after outcome, before byline)
- [ ] AI byline present as **LAST** element
- [ ] No stale todowrite items remain (all cleared or N/A)