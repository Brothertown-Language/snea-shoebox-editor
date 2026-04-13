# Task: completion

Idempotent completion subtask for implementation-workflow. Ensures mandatory steps run regardless of where the workflow halted.

## State Check Phase

1. **Git status:** Check for uncommitted changes
   ```bash
   git status --porcelain
   ```
2. **Push status:** Check for unpushed commits
   ```bash
   git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null
   ```
3. **Existing comments:** Check if completion comment already posted on issue

## Skill-Specific Completion

1. **If verification-before-completion not yet invoked:** Invoke `--task verify`
   - Check if verification evidence exists in issue comments or `./tmp/`
   - If missing: invoke verification before proceeding
2. **If finishing-a-development-branch not yet invoked:** Invoke `--task checklist`
   - Check if branch readiness checklist has been run
   - If missing: invoke checklist before proceeding

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

<What was implemented and its impact>

**Outcome:** <What changed for stakeholders>

Compare URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch>
```

URL is ALWAYS last per `000-critical-rules.md`.
