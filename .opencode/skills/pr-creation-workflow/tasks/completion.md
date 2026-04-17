# Task: completion

Idempotent completion subtask for pr-creation-workflow. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Pre-PR checklist:** All checks passed before PR creation
2. **PR creation outcome:** PR was created or not created with documented reason
3. **URL reporting:** PR URL or compare URL reported in chat
4. **Issue closure safety:** No issues prematurely closed before PR merge

## Skill-Specific Completion

1. **Pre-PR checklist verification** (if not already performed):
   - Check evidence for squash, changelog, branch state, co-author trailers
   - If missing: invoke `pre-pr-checklist` task as remediation

2. **PR creation status** (if not already determined):
   - Check whether PR was created via `github_list_pull_requests` for branch
   - If PR exists: verify URL was reported in chat
   - If PR not created: verify reason was documented (e.g., no explicit instruction)

3. **URL reporting verification** (if not already performed):
   - Confirm PR URL or compare URL appears in chat output
   - If missing: report URL now

4. **Issue closure guard** (if not already performed):
   - Confirm no issues were closed before PR merge confirmation
   - If premature closure found: reopen issue, flag for developer

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO pr-creation-workflow workflow ends without a status message.

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