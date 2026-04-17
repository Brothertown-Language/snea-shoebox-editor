# Task: completion

Idempotent completion subtask for spec-auditor. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **All selected subtasks completed:** Verify all baseline and conditional subtasks ran to completion
2. **Auto-fixes documented:** Verify all auto-fix findings were applied and documented
3. **Flag-for-review findings in exec summary:** Verify all flag-for-review findings are reported in executive summary
4. **Chat exec summary posted:** Verify chat executive summary was posted

## Skill-Specific Completion

1. **Subtask completion** (if not all completed):
   - Check evidence for each selected subtask execution
   - If any missing: invoke missing subtask as remediation

2. **Auto-fix documentation** (if not fully documented):
   - Check evidence for auto-fix application and documentation
   - If missing: document what was applied during this session

3. **Flag-for-review in exec summary** (if not included):
   - Check exec summary includes all flag-for-review findings
   - If missing: regenerate exec summary with all findings

4. **Chat executive summary** (if not already posted):
   - Verify exec summary was posted to chat
   - If missing: generate and post exec summary now

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (audited issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO spec-auditor workflow ends without a status message.

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