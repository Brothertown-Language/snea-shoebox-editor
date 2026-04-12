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

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<Authorization verification result and scope>

**Outcome:** <What the result means for stakeholders>

Issue URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/issues/<number>
```

URL is ALWAYS last per `000-critical-rules.md`.