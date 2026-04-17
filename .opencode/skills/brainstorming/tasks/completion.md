# Task: completion

Idempotent completion subtask for brainstorming. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Terminal-state dispatch:** Verify spec-creation/writing-plans dispatch occurred (Path A or Path B), or FAILURE documented (Path C)
2. **Chat output format:** Verify chat output follows exec summary format (summary → outcome → URL → byline)

## Skill-Specific Completion

1. **Terminal-state dispatch** (if not already performed):
   - Check evidence for spec-creation or writing-plans dispatch
   - If missing: invoke appropriate skill as remediation (spec-creation for Path A, writing-plans for Path B), or document FAILURE for Path C

2. **Chat output** (if not already produced):
   - Verify exec summary was posted to chat
   - If missing: generate and post exec summary now

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO brainstorming workflow ends without a status message.

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