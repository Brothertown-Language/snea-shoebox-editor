# Task: completion

Idempotent completion subtask for writing-plans. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Plan issue created:** Verify plan issue exists with [PLAN] prefix and `needs-approval` label (separate), or combined spec+plan has `## Implementation Plan` section
2. **Sub-issues created:** For multi-task plans, verify sub-issues created under the plan
3. **Self-review completed:** Verify self-review checklist was run (coverage, placeholders, type consistency)
4. **Chat exec summary + URL:** Verify chat output includes exec summary format with plan URL

## Skill-Specific Completion

1. **Plan issue** (if not already created):
   - Check evidence for plan issue creation (separate or combined)
   - If missing: invoke `writing-plans --task create` as remediation

2. **Sub-issues** (if multi-task and not already created):
   - Check evidence for sub-issue creation under the plan
   - If missing: invoke `issue-operations --task link-sub-issue` as remediation

3. **Self-review** (if not already performed):
   - Check evidence for self-review checklist completion
   - If missing: invoke `writing-plans --task validate` as remediation

4. **Chat executive summary** (if not already produced):
   - Verify exec summary was posted to chat with plan URL
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

This is the completion guarantee: NO writing-plans workflow ends without a status message.

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