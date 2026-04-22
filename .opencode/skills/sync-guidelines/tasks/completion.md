# Task: completion

Idempotent completion subtask for sync-guidelines. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Classification completion:** All files classified as core or project-specific
2. **Sync issue creation:** Sync issues created for core changes (not direct file edits)
3. **Sync state file:** `.opencode/sync-state.yml` updated after sync operation
4. **No direct modifications:** No target repository files modified directly

## Skill-Specific Completion

1. **Classification verification** (if not already performed):
   - Check evidence that all relevant files were read and classified
   - If missing: invoke `classify` task as remediation

2. **Sync issue creation verification** (if not already performed):
   - Check evidence that sync issues exist in target repository for core changes
   - If missing: invoke `sync-push` or `sync-pull` task as remediation

3. **Sync state file verification** (if not already performed):
   - Check `.opencode/sync-state.yml` has updated timestamp and file list
   - If stale: update sync state with current operation details

4. **No direct modification guard** (if not already performed):
   - Verify no files were directly edited in target repository
   - If direct edits found: create sync issue to propose those changes formally

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO sync-guidelines workflow ends without a status message.

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