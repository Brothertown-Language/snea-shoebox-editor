# Task: completion

Idempotent completion subtask for finishing-a-development-branch. Ensures mandatory steps run regardless of where the workflow halted.

## State Check Phase

1. **Push status:** Check for unpushed commits
   ```bash
   git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null
   ```
2. **Compare URL generated:** Check if compare URL was already produced
3. **Existing comments:** Check if completion comment already posted on issue

## Skill-Specific Completion

1. **Verify push** — ensure all commits are on remote
2. **Generate compare URL** (dev...branch)

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for steps 3-6:

1. Push branch (with idempotency check)
2. Generate compare URL (dev...branch)
3. Post status comment on issue (with idempotency check)
4. Report executive summary in chat (always runs)

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<Branch readiness verification result>

**Outcome:** <What stakeholders get — branch is ready/not ready for PR>

Compare URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch>
```

URL is ALWAYS last per `000-critical-rules.md`.
