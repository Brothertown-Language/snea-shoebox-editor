# Task: scan-guidelines

## Purpose

Scan all guideline files for ambiguity, conflicts, and LLM compliance issues.

## Entry Criteria

- Guidelines directory exists at `.opencode/guidelines/`
- Skill invoked with `--mode maintenance`

## Exit Criteria

- All guideline files scanned
- Issues identified and categorized
- Audit report created in `./tmp/audit-YYYYMMDD.md`

## Procedure

### Step 1: List Guideline Files

```bash
find .opencode/guidelines -name "*.md" -type f
```

### Step 2: Scan Each File

For each guideline file:

1. Read file content
2. Check for problem classes:
   - AMBIGUOUS: Multiple interpretations
   - CONFLICTING: Contradicts other rules
   - UNENFORCEABLE: Cannot verify compliance
   - REDUNDANT-CROSS-FILE: Duplicates other files
   - CONTEXT-OVERFLOW: Too long/wordy
   - DRY-VIOLATION: Repeated rules
   - KISS-VIOLATION: Unnecessarily complex
   - SEPARATION-OF-CONCERNS-VIOLATION: Blurred boundaries
   - COMMENT-FORMAT-VIOLATION: Wrong format

### Step 3: Categorize Issues

**Problem Class Priority:**
1. CRITICAL: AMBIGUOUS, CONFLICTING, UNENFORCEABLE
2. ARCHITECTURE: DRY-VIOLATION, KISS-VIOLATION, SEPARATION-OF-CONCERNS-VIOLATION
3. STYLE: CONTEXT-OVERFLOW, COMMENT-FORMAT-VIOLATION
4. MINOR: REDUNDANT-CROSS-FILE

### Step 4: Create Audit Report

```markdown
# Guideline Audit Log

Date: YYYYMMDD
Auditor: guideline-auditor
Mode: maintenance

## Issues Found: N

### Issue 1: [Problem Class]

**File:** path/to/file.md
**Rule:** [Quoted rule]
**Explanation:** [Why this is a problem]
**Proposed Fix:** [Minimal change]

[Repeat for each issue]

## Summary

- CRITICAL: N
- ARCHITECTURE: N
- STYLE: N
- MINOR: N
```

### Step 5: Store Report

```bash
# Write to ./tmp/audit-YYYYMMDD.md
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| No issues found | Include "no drift found" with requirement-level coverage |
| Only CRITICAL found | Focus on those first, skip style issues |
| Context overflow detected | Propose trimmed rewrite |

## Context Required

- Related tasks: `check-drift`, `report-violations`
