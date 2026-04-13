# Task: completion

Idempotent completion subtask for approval-gate. Ensures mandatory steps run regardless of where the workflow halted.

## State Check Phase

1. **Authorization result determined:** Was a yes/no decision reached?
2. **Existing comments:** Check if authorization result comment already posted on issue

## Skill-Specific Completion

1. **Post authorization result comment** (if not already posted):
   - Check issue comments for existing authorization result (byline pattern)
   - If missing: post result comment with authorization status and scope

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Label State Machine

Before adding or removing labels in completion, consult `141-planning-status-tracking.md §10` for the complete label transition matrix and the GitHub `labels` parameter warning (replaces all labels, not additive).

## Completion Guarantee

**MANDATORY:** Regardless of authorization outcome (approved, rejected, blocked, error), produce a status message containing:
1. Authorization decision (approved/rejected/blocked)
2. Issue number and branch (if applicable)
3. What happens next (workflow forward, HALT, or error)

This is the completion guarantee: NO authorization check ends without a status message.

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<Authorization verification result and scope>

**Outcome:** <What the result means for stakeholders>

Issue URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/issues/<number>
```

URL is ALWAYS last per `000-critical-rules.md`.