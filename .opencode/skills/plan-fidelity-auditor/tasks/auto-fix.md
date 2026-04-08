# Task: auto-fix

## Purpose

Apply auto-fix corrections to the spec issue and flag substantive discrepancies for human review. Uses AI agent intelligence to differentiate simple fixes from changes requiring human decision.

## Operating Protocol

1. **Invoked by:** audit task (Step 6) after comparison is complete
2. **NOT invoked in `--check-only` mode**
3. **Requires:** Discrepancy list from compare task

## Entry Criteria

- Comparison results available from `compare` task
- Discrepancy list classified (auto-fix vs flag-for-review)
- Issue number for updates

## Exit Criteria

- Auto-fixes applied to the GitHub Issue
- Substantive discrepancies flagged in a comment
- Executive summary posted

## Procedure

### Step 1: Classify Discrepancies

**Review each discrepancy from the comparison results:**

| Discrepancy Type | Classification | Action |
|-----------------|----------------|--------|
| `MISSING_PHASE` | Flag for human | New phases are substantive scope changes |
| `EXTRA_PHASE` | Flag for human | May be intentional scope or scope creep |
| `MISSING_STEP` (file refs) | Auto-fix | Adding file references is a simple completeness fix |
| `MISSING_STEP` (verification) | Auto-fix | Adding verification steps is quality improvement |
| `MISSING_STEP` (other) | Flag for human | Missing implementation steps need review |
| `EXTRA_STEP` | Flag for human | May be scope creep or intentional addition |
| `MISSING_FILE_REF` | Auto-fix | Adding affected files to existing steps |
| `MISSING_EDGE_CASE` | Flag for human | Edge cases need architectural consideration |
| `APPROACH_DIFFERENCE` | Flag for human | Different approaches need design decisions |
| `ORDERING_DIFFERENCE` | Flag for human | May be intentional dependency order |
| `SCOPE_EXPANSION` | Flag for human | Significant scope increase needs approval |
| `POSSIBLE_SCOPE_CREEP` | Flag for human | Original may include unnecessary work |
| `VAGUE_PROBLEM` | Already handled | Triggered brainstorming in audit task |

### Step 2: Apply Auto-Fixes

**For each auto-fix discrepancy:**

2.1. **Read the current issue body**
```
github_issue_read(method="get", owner=OWNER, repo=REPO, issue_number=N)
```

2.2. **Determine the fix location in the issue body**
- `MISSING_FILE_REF`: Add file to the Affected Files table
- `MISSING_STEP` (verification): Add verification step to appropriate phase
- `MISSING_STEP` (file refs): Add file reference to existing step

2.3. **Apply the fix via issue update**
```
github_issue_write(method="update", owner=OWNER, repo=REPO, issue_number=N, body=updated_body)
```

**Fix application rules:**
- Only modify the specific section that needs the fix
- Preserve all existing content, markers, and formatting
- Add a comment indicating what was auto-fixed: `<!-- Auto-fixed by plan-fidelity-auditor -->`
- Do NOT add new phases — that's a substantive change
- do NOT remove existing phases — that's a substantive change

### Step 3: Flag Substantive Discrepancies

**For each flag-for-review discrepancy:**

3.1. **Do NOT modify the issue body**
3.2. **Prepare a flag entry describing:**
   - What the discrepancy is
   - Why it needs human review
   - What the clean-room suggests instead
   - The specific section of the spec affected

**Flag entry format:**
```markdown
- **[DISCREPANCY_TYPE]**: <description>
  - Clean-room suggests: <suggestion>
  - Affected section: <section reference>
  - Recommendation: <brief recommendation>
```

### Step 4: Generate Executive Summary

**Compose the executive summary:**

```markdown
## Plan Fidelity Audit

**Summary:** <1-2 sentences: X discrepancies found, Y auto-fixed, Z flagged for review>

**Outcome:** <Link to revised spec OR "X simple fixes applied. Z items flagged for human review. See details below.">

### Auto-Fixed (<count>)
<list of auto-fixes with brief descriptions>

### Flagged for Review (<count>)
<list of substantive discrepancies with recommendations>

---
🤖 ✅ Completed by <AgentName> (<ModelID>): Plan Fidelity Auto-Audit
```

### Step 5: Post Comment

**Post the executive summary as a comment on the issue:**
```
github_add_issue_comment(owner=OWNER, repo=REPO, issue_number=N, body=executive_summary)
```

### Step 6: Clean Up

**Remove temporary files:**
```bash
rm -f ./tmp/clean-room-input-N.md
rm -f ./tmp/clean-room-plan-N.md
rm -f ./tmp/comparison-results-N.json
```

## Edge Cases

| Scenario | Action |
|----------|--------|
| No auto-fixes needed | Skip Step 2, report "no auto-fixes" in summary |
| No discrepancies found | Report "no discrepancies found" with link to original spec |
| Issue update fails | Document in comment, continue with reporting |
| All discrepancies are substantive | No auto-fixes, all flagged for review |
| Auto-fix introduces formatting error | Revert the fix, flag for manual application |

## Context Yielded

```yaml
status: "auto-fix-complete"
auto_fixes_applied: M
flagged_for_review: K
total_discrepancies: N
issue_updated: true|false
comment_posted: true|false
next_auditor: "concern-separation-auditor"
```

## Context Required

- Related tasks: `audit` (invokes this), `compare` (provides discrepancy list)
- Related skills: `concern-separation-auditor` (next in audit chain)