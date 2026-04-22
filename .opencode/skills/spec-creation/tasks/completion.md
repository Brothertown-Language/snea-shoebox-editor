# Task: completion

Idempotent completion subtask for spec-creation. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Spec issue created:** Verify spec issue exists with [SPEC] prefix and `needs-approval` label
2. **spec-auditor invoked:** Verify spec-auditor was invoked after spec creation
3. **Self-review evidence:** Verify self-review was performed (placeholder scan, consistency check, ambiguity check)
4. **Chat exec summary + URL:** Verify chat output includes exec summary format with spec URL

## Skill-Specific Completion

1. **Spec issue** (if not already created):
   - Check evidence for spec issue creation with [SPEC] prefix
   - If missing: invoke `spec-creation --task write` as remediation

2. **spec-auditor** (if not already invoked):
   - Check evidence for spec-auditor invocation
   - If missing: invoke `spec-auditor --issue N` as remediation

3. **Self-review** (if not already performed):
   - Check evidence for self-review completion
   - If missing: perform self-review (placeholder scan, consistency check)

4. **Chat executive summary** (if not already produced):
   - Verify exec summary was posted to chat with spec URL
   - If missing: generate and post exec summary now

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (spec issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO spec-creation workflow ends without a status message.

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