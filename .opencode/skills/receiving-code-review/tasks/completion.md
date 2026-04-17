# Task: completion

Idempotent completion subtask for receiving-code-review. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Comment addressance:** All reviewer comments addressed or replied
2. **Scope integrity:** No changes beyond what reviewer requested
3. **Branch state:** Changes pushed to remote branch
4. **Test health:** All tests still pass after review changes

## Skill-Specific Completion

1. **Comment addressance verification** (if not already performed):
   - Check evidence for all review comments having response or code change
   - If missing: invoke `address` or `respond` task as remediation

2. **Scope creep check** (if not already performed):
   - Check diff against review request — no changes beyond what was asked
   - If scope creep detected: revert extraneous changes, invoke `address` task

3. **Branch push verification** (if not already performed):
   - Check `git status` for uncommitted changes and `git log origin/<branch>..HEAD` for unpushed commits
   - If missing: commit and push as remediation

4. **Test verification** (if not already performed):
   - Run `uv run pytest test/` in worktree
   - If failing: report failures, do not push broken tests

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO receiving-code-review workflow ends without a status message.

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