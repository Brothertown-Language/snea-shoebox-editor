# Task: completion

Idempotent completion subtask for subagent-driven-development. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **All tasks dispatched:** Verify all plan tasks were dispatched to sub-agent implementers
2. **Post-implementation skills invoked:** Verify verification-before-completion and finishing-a-development-branch were invoked
3. **No BLOCKED/NEEDS_CONTEXT unresolved:** Verify no sub-agent returned unresolved BLOCKED or NEEDS_CONTEXT status
4. **Chat exec summary:** Verify chat executive summary was posted

## Skill-Specific Completion

1. **Task dispatch** (if not all dispatched):
   - Check evidence for each task's implementer dispatch
   - If any missing: dispatch missing tasks as remediation

2. **Post-implementation skills** (if not already invoked):
   - Check evidence for verification-before-completion invocation
   - If missing: invoke `verification-before-completion --task verify` as remediation
   - Check evidence for finishing-a-development-branch invocation
   - If missing: invoke `finishing-a-development-branch --task checklist` as remediation

3. **Unresolved statuses** (if any remain):
   - Check for any BLOCKED or NEEDS_CONTEXT sub-agent results
   - If found: report in completion report; escalate to developer if unresolvable

4. **Chat executive summary** (if not already produced):
   - Verify exec summary was posted to chat
   - If missing: generate and post exec summary now

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (compare URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO subagent-driven-development workflow ends without a status message.

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