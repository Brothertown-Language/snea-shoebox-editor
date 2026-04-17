# Task: completion

Idempotent completion subtask for executing-plans. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **assemble-work dispatch:** Verify divide-and-conquer/assemble-work dispatch was attempted
2. **Plan issue STATUS:** Verify plan issue STATUS reflects actual outcome (completed, partial, failed)
3. **Chat exec summary:** Verify chat output follows exec summary format (summary → outcome → URL → byline)

## Skill-Specific Completion

1. **assemble-work dispatch** (if not already performed):
   - Check evidence for assemble-work invocation
   - If missing: invoke `divide-and-conquer --task assemble-work` as remediation

2. **Plan issue STATUS** (if not already updated):
   - Check plan issue STATUS marker against actual completion state
   - If mismatched: update STATUS to reflect current state

3. **Chat executive summary** (if not already produced):
   - Verify exec summary was posted to chat
   - If missing: generate and post exec summary now

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (plan issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO executing-plans workflow ends without a status message.

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