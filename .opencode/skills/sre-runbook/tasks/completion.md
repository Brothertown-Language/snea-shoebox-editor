# Task: completion

Idempotent completion subtask for sre-runbook. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Runbook produced:** Verify runbook was produced (file or issue body) with dual-output contract (AI-parseable + human-readable)
2. **Incident issue created:** If `track` was invoked, verify incident GitHub Issue was created with structured labels
3. **Verification documented:** Verify runbook claims were verified against live documentation (evidence artifacts produced)
4. **Chat exec summary:** Verify chat executive summary was posted

## Skill-Specific Completion

1. **Runbook output** (if not already produced):
   - Check evidence for runbook generation
   - If missing: invoke `sre-runbook --task generate` as remediation

2. **Incident issue** (if track was invoked and issue not created):
   - Check evidence for incident issue creation
   - If missing: invoke `sre-runbook --task track` as remediation

3. **Verification** (if not already documented):
   - Check evidence for live verification of runbook claims
   - If missing: flag in completion report that verification was skipped

4. **Chat executive summary** (if not already produced):
   - Verify exec summary was posted to chat
   - If missing: generate and post exec summary now

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (incident issue URL if created, or runbook file path) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO sre-runbook workflow ends without a status message.

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