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

### Step N: EXTRACT URL FROM API RESPONSE

1. The Issue URL MUST be copied verbatim from the `github_issue_write` API response's `html_url` field.
2. Do NOT retype, reconstruct, or assemble the URL from known values (org, repo, number).
3. Paste the URL exactly as returned. If the API response is `{ "html_url": "https://github.com/Org/Repo/issues/42" }`, the output URL is `https://github.com/Org/Repo/issues/42` — character for character.
4. Verification checkpoint: Compare the pasted URL character-by-character against the `html_url` field in the API response before sending.

Generate executive summary in chat:

```
**Summary:**

<Verification result: pass/fail with criteria count>

**Outcome:** <What stakeholders know — task is verified/not verified>

Issue URL: <html_url from github_issue_write API response — NEVER construct from template>
```

URL is ALWAYS last per `000-critical-rules.md`.

## Live Verification: Completion Claims (MANDATORY)

**Before claiming verification complete, verify claims against actual evidence.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Verification completed" | Verify evidence artifacts exist | `glob(pattern="./tmp/verification-*")` | VERIFICATION-GAP |
| "All criteria passed" | Verify each criterion has PASS evidence | Read collection output | MISSING-ELEMENT |

**Evidence artifact:** File existence check or collection output confirming verification was performed.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| No verification report found | VERIFICATION-GAP | conditional | Re-run verification |
| Criterion lacks evidence | MISSING-ELEMENT | conditional | Collect evidence for missing criterion |