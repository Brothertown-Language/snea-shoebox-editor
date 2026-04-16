# Task: merge

## Purpose

Combine sub-agent results into a final aggregated output. Each sub-agent returns a structured result (status, files_changed, summary). The orchestrator collects all results, composes a final summary, and identifies any conflicts between results. This task performs NO implementation work — pure aggregation.

## Entry Criteria

- All sub-agents have returned results (DONE, DONE_WITH_CONCERNS, or OVERFLOW completed portions)
- No sub-agents are still running

## Exit Criteria

- Final aggregated summary is produced
- Conflicts between sub-agent results are identified (if any)
- Executive summary is ready for chat output

## Procedure

### Step 1: Collect All Results

Gather Sub-agent Result Contract outputs from every sub-agent:

```yaml
results:
  - sub_task_id: D1
    status: DONE
    files_changed: ["src/module_a.py", "src/module_b.py"]
    summary: "<implemented X with approach Y>"
    verification_passed: true
  - sub_task_id: D2
    status: DONE_WITH_CONCERNS
    files_changed: ["src/module_c.py"]
    summary: "<implemented Z, concern about edge case W>"
    concerns: "<description of concern>"
    verification_passed: true
  - sub_task_id: D3
    status: OVERFLOW
    completed_work:
      files_changed: ["src/module_d.py"]
      summary: "<partial: sections 1-3 done>"
    remaining: "<sections 4-5 dispatched to sub-agents>"
```

### Step 2: Identify Conflicts

Check for conflicts between sub-agent results:

| Conflict Type | Detection | Resolution |
| -- | -- | -- |
| Same file modified by multiple sub-agents | Overlapping `files_changed` entries | Flag for developer review |
| Contradictory design decisions | Divergent summaries for related code | Flag for developer review |
| Verification failures | `verification_passed: false` | HALT — do not proceed to completion |

### Step 3: Compose Final Summary

```markdown
**Summary:**

Implemented <task description> via <N> sub-agents.

**Outcome:**

- D1: <summary> ✅
- D2: <summary> ⚠️ (<concern>)
- D3 (overflow): <completed summary> ✅, <remaining> dispatched and completed ✅
```

### Step 4: Delegate to Completion

After merge, invoke `--task completion` for:
- Push verification
- Compare URL generation
- Executive summary in chat
- Status comments (substantive only)
- Review-prep invocation (`git-workflow --task review-prep`) if not yet run
- Chat output format verification (exec summary first, URL last, AI byline after URL)

## Edge Cases

### All Sub-agents Failed

Report all failures clearly. Do NOT proceed to completion with empty results. HALT and report.

### Partial Completion

Some sub-agents succeeded, some failed. Include successful results in summary, flag failures clearly. Proceed to completion with partial results.

### No Conflicts but Verification Failures

If any sub-agent returned `verification_passed: false`, HALT. Do NOT proceed. Report which sub-tasks failed verification and why.
## Live Verification: Merge State Claims (MANDATORY)

**Verify merge state claims against actual git state per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Feature branch merged into batch branch" | Verify merge commit exists | `git log --oneline --merges` | VERIFICATION-GAP |
| "No conflicts remaining" | Verify clean merge | `git status --porcelain` → check for conflict markers | CONFLICTING |
| "All sub-agent changes included" | Verify diff matches expected | `git diff dev --name-only` | VERIFICATION-GAP |

**Evidence artifact:** Git log and status output confirming merge state.
