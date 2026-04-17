# Task: completion

Idempotent completion subtask for changelog-generator. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **CHANGELOG.md update:** Changelog file updated with new entries
2. **No duplicate entries:** No duplicate entries introduced
3. **Categorization consistency:** Branch headers and categories applied consistently
4. **Correct location:** Changes written to correct path (worktree if WORKTREE_PATH set)

## Skill-Specific Completion

1. **CHANGELOG.md update verification** (if not already performed):
   - Check evidence that CHANGELOG.md was modified with new entries
   - If missing: invoke appropriate task (`since-last-release`, `date-range`, or `backfill`) as remediation

2. **Duplicate entry check** (if not already performed):
   - Scan CHANGELOG.md for duplicate entries matching newly added content
   - If duplicates found: remove duplicates, keep single canonical entry

3. **Categorization verification** (if not already performed):
   - Check that branch-header-based categorization follows prefix mapping rules
   - If inconsistent: re-categorize per branch prefix table in SKILL.md

4. **Location verification** (if not already performed):
   - If WORKTREE_PATH is set: confirm changes written to `${WORKTREE_PATH}/CHANGELOG.md`
   - If WORKTREE_PATH not set: confirm changes written to project root `CHANGELOG.md`
   - If wrong location: move changes to correct path

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO changelog-generator workflow ends without a status message.

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