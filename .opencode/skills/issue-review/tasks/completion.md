# Task: completion

Idempotent completion subtask for issue-review. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Full workflow completion:** Gather → triage → dispatch completed for target issue
2. **Fix spec sub-issue:** If analyze-and-spec path, fix spec sub-issue was created
3. **Spec-auditor invocation:** If audit path, spec-auditor was invoked
4. **Executive summary channel:** Output routed to correct channel (chat for audit, issue for qa)

## Skill-Specific Completion

1. **Workflow completeness** (if not already performed):
   - Check evidence that gather, triage, and dispatch all ran
   - If incomplete: invoke missing task as remediation

2. **Fix spec sub-issue verification** (if analyze-and-spec path was taken):
   - Check evidence for fix spec sub-issue linked to bug report parent
   - If missing: invoke `analyze-and-spec` task as remediation

3. **Spec-auditor invocation verification** (if audit path was taken):
   - Check evidence that spec-auditor was invoked for the issue
   - If missing: invoke `audit` task as remediation

4. **Executive summary channel verification** (if not already performed):
   - Audit path: summary went to chat only (not GitHub comments)
   - QA path: durable outcomes posted to issue
   - If wrong channel: repost to correct channel

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO issue-review workflow ends without a status message.

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