# Task: completion

Idempotent completion subtask for systematic-debugging. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Bug report created:** If diagnosis completed, verify bug report issue was created
2. **analyze-and-spec invoked:** If bug report created, verify `issue-review --task analyze-and-spec` was invoked
3. **Fix verified:** If fix was applied, verify fix resolves the issue and no new issues introduced
4. **Unauthorized fix flagged:** Verify no code changes were made without authorization

## Skill-Specific Completion

1. **Bug report** (if diagnosis completed but no bug report):
   - Check evidence for bug report issue creation
   - If missing: create bug report issue as remediation

2. **analyze-and-spec** (if bug report created but analyze-and-spec not invoked):
   - Check evidence for analyze-and-spec invocation
   - If missing: invoke `issue-review --issue N --task analyze-and-spec` as remediation

3. **Fix verification** (if fix applied but not verified):
   - Check evidence for test execution confirming fix works
   - If missing: run tests and verify fix resolves issue

4. **Unauthorized fix detection** (if code was changed without authorization):
   - Check for unapproved code changes
   - If found: `git checkout -- <affected-files>` and report in completion output

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (bug report issue URL if created) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO systematic-debugging workflow ends without a status message.

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