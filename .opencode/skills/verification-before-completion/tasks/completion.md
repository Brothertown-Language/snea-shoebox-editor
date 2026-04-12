# Task: completion

Idempotent completion subtask for verification-before-completion. Ensures mandatory steps run regardless of where the workflow halted.

## State Check Phase

1. **Verification result determined:** Was an evidence-based verification completed?

## Skill-Specific Completion

1. **Record verification result** in `./tmp/` if not already recorded

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) if applicable (ALWAYS last)

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<Verification result: pass/fail with criteria count>

**Outcome:** <What stakeholders know — task is verified/not verified>

Issue URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/issues/<number>
```

URL is ALWAYS last per `000-critical-rules.md`.