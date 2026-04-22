# Task: completion

Idempotent completion subtask for conflict-resolution. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Conflict classification:** All conflicts classified into tiers
2. **Tier resolution:** Tier 1 and Tier 2 conflicts fully resolved
3. **Tier 3 safety:** No Tier 3 conflicts resolved without developer review
4. **Rebase state:** Git rebase/merge state is clean (no lingering conflicts)

## Skill-Specific Completion

1. **Classification completeness** (if not already performed):
   - Check evidence for all detected conflicts having tier classification
   - If missing: invoke `classify-and-resolve` task as remediation

2. **Tier 1/2 resolution verification** (if not already performed):
   - Check evidence that all Tier 1 and Tier 2 conflicts were resolved
   - If unresolved: resolve and document in chat per notification format

3. **Tier 3 developer review guard** (if not already performed):
   - Confirm no Tier 3 conflict was resolved without explicit developer approval
   - If Tier 3 was auto-resolved: flag as critical violation, HALT for developer review

4. **Rebase state verification** (if not already performed):
   - Run `git status` to confirm no unresolved conflicts remain
   - If conflicts remain: invoke `classify-and-resolve` as remediation

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO conflict-resolution workflow ends without a status message.

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