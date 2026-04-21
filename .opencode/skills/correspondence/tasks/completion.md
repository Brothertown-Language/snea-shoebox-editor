# Task: completion

Idempotent completion subtask for correspondence. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Email draft produced:** A draft email exists with both text/plain and text/html parts (or text/plain only when the original was text/plain)
2. **Audience classification recorded:** Audience classification and rationale documented
3. **Content filtering applied:** Content filtered by audience classification (no internal ops details in external content)
4. **Verification gates passed:** Both `verification-enforcement --task verify` (pre-draft) and `verification-enforcement --task revisit` (post-draft) were invoked
5. **AI byline present:** Byline appears in all email parts

## Skill-Specific Completion

1. **Draft existence verification** (if not already performed):
   - Check that an email draft was produced
   - If missing: invoke `draft` task as remediation

2. **Format verification** (if not already performed):
   - Verify email draft contains both text/plain and text/html parts
   - If original email was text/plain and reply is text/plain only: acceptable
   - If reply to HTML email is text/plain only: invoke `draft` task to regenerate with HTML

3. **Content filtering verification** (if not already performed):
   - Verify no internal ops details appear in external-facing content
   - If prohibited content found: remove and regenerate draft

4. **Verification gate verification** (if not already performed):
   - Verify `verification-enforcement --task verify` was invoked before drafting
   - Verify `verification-enforcement --task revisit` was invoked after self-review
   - If either gate was skipped: invoke the skipped gate now

5. **Byline verification** (if not already performed):
   - Verify AI byline appears in all email parts
   - If missing: append byline to the email parts

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO correspondence workflow ends without a status message.

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

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

## Context Required

- Session values: `github.owner`, `github.repo`
- Issue number (if applicable)
- Verification gate results from `verification-enforcement --task verify` and `--task revisit`
- Audience classification result
- Email draft content