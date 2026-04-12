# Task: create-report

## Purpose

Generate and attach audit report to GitHub Issue for fresh-start context preservation.

## Entry Criteria

- Audit completed (extraction or maintenance mode)
- Findings documented in memory

## Exit Criteria

- Audit report created in `./tmp/coherence-audit-YYYYMMDD-<mode>.md`
- Report retained in `./tmp/` for session reference

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
- Total guideline words: N
- Total skill words: N
- Combined words: N
- Drift from baseline: <+/-N words> (<+/-N%>)
```

### Step 2: Report to Chat

Report audit findings summary to chat (NOT as GitHub Issue comment). The full audit log is retained in `./tmp/` for session reference.

### Step 3: Retain Temp File

Retain the audit log in `./tmp/` for session reference. Do NOT delete — it may be needed for follow-up work.

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: All tasks feed into this report