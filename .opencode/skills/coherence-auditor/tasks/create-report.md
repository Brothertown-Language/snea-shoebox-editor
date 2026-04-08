# Task: create-report

## Purpose

Generate and attach audit report to GitHub Issue for fresh-start context preservation.

## Entry Criteria

- Audit completed (extraction or maintenance mode)
- Findings documented in memory

## Exit Criteria

- Audit report created in `./tmp/coherence-audit-YYYYMMDD-<mode>.md`
- Report attached as GitHub Issue comment
- Temp file deleted

## Procedure

### Step 1: Create Audit Log

Write to `./tmp/coherence-audit-YYYYMMDD-<mode>.md`:

```markdown
# Coherence Audit Log

Date: YYYY-MM-DD
Auditor: coherence-auditor
Mode: <extraction|maintenance>
Scope: .opencode/guidelines/[, .opencode/skills/]

## Summary
- Issues Found: N
- Issues Fixed: M
- Issues Skipped: K
- Remaining: L

## Issues Processed
<List each issue with file, issue class, priority, status, action>

## Baseline Metrics (maintenance mode only)
- Total guideline tokens: N
- Total skill tokens: N
- Combined tokens: N
- Drift from baseline: <+/-N tokens> (<+/-N%>)
```

### Step 2: Attach to GitHub Issue

```python
github_add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=target_issue,
    body=f"AI: {AgentName} {ModelID} 📝 Coherence Audit: {mode}\n\n{report_content}"
)
```

### Step 3: Delete Temp File

```bash
rm ./tmp/coherence-audit-YYYYMMDD-<mode>.md
```

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: All tasks feed into this report