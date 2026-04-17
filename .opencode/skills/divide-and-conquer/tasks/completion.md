# Task: completion

Migrated from `implementation-workflow` task completion.

Idempotent completion subtask for divide-and-conquer. Ensures mandatory steps run regardless of where the workflow halted.

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
3. **If git-workflow review-prep not yet invoked:** Invoke `git-workflow --task review-prep`
   - Check if compare URL and executive summary exist in chat output
   - If missing: invoke review-prep before proceeding

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

Compare URL: <GitBucketHtmlUrl><GitOwner>/<GitRepo>/compare/dev...<branch>
```

URL is ALWAYS last per `000-critical-rules.md`.

Co-authored with AI: <AgentName> (<ModelId>)

## Live Verification: Completion State (MANDATORY)

**Verify completion claims against actual state before halting.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "All commits pushed" | Verify no unpushed commits | `git diff @{u} HEAD` | VERIFICATION-GAP |
| "Verification invoked" | Verify evidence exists | `glob(pattern="./tmp/verification-*")` | MISSING-ELEMENT |
| "Checklist completed" | Verify branch readiness | `git status --porcelain` → check clean | VERIFICATION-GAP |
| "Compare URL generated" | Verify URL exists in context | Check chat output for URL | MISSING-ELEMENT |

**Evidence artifact:** Git command output confirming each claim.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Unpushed commits | VERIFICATION-GAP | auto-fix | Push immediately |
| Verification not invoked | MISSING-ELEMENT | conditional | Invoke verification-now |
| Working tree dirty | VERIFICATION-GAP | conditional | Commit remaining changes |
| No compare URL | MISSING-ELEMENT | auto-fix | Generate URL now |