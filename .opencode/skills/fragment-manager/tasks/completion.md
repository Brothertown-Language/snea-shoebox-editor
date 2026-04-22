# Task: completion

Idempotent completion subtask for fragment-manager. Ensures mandatory steps ran regardless of where the workflow halted.

## State Check Phase

1. **Registry update:** Fragment registry (`.opencode/.guidelines/registry.yaml`) updated after operation
2. **Destination synchronization:** All destinations synchronized from master
3. **No drift remaining:** Master and destination hashes match
4. **Backup preservation:** Backup preserved before destructive operations

## Skill-Specific Completion

1. **Registry update verification** (if not already performed):
   - Check evidence that `.opencode/.guidelines/registry.yaml` was modified with correct entries
   - If missing: update registry with current operation details as remediation

2. **Destination sync verification** (if not already performed):
   - Verify all destinations listed in registry have been synchronized
   - If any destination not synced: invoke `sync-fragment` task as remediation

3. **Drift check** (if not already performed):
   - Run `check-drift` to confirm zero drift between masters and destinations
   - If drift found: invoke `resolve-conflict` or `sync-fragment` as remediation

4. **Backup verification** (if not already performed):
   - Check `.opencode/.backups/` exists and contains expected backup files
   - If missing from destructive operation: flag for developer, cannot recreate

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Completion Guarantee

**MANDATORY:** Regardless of workflow outcome (success, partial, error), produce a status message containing:
1. What was completed
2. What was attempted but not completed
3. Why the halt occurred

This is the completion guarantee: NO fragment-manager workflow ends without a status message.

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