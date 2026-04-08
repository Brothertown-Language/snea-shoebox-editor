# Task: pre-creation

## Purpose

Validate spec before creating GitHub Issue to prevent conflicts, superseded issues, and missing essential sections.

## Operating Protocol

1. **Mandatory invocation:** This task MUST run before ANY issue creation.

## Entry Criteria

- Spec content is ready for issue creation
- Title follows proper format
- User has authorized creation

## Exit Criteria

- Spec validated (no conflicts, no superseded issues)
- All essential sections present
- Ready to create issue

## Procedure

### Step 1: Check for Superseding Issues

**Query for all open `[SPEC]`, `[SPEC-FIX]`, and `[SPEC-ENHANCEMENT]` issues:**

```
github_list_issues(owner, repo, state="open")
```

For each open spec issue:
1. Compare title/objectives with new spec
2. If superseding issue found:
   - HALT
   - Report conflict: "Later issue #N supersedes this spec"
   - Do NOT proceed with creation
3. If overlapping/conflicting issue found:
   - HALT
   - Report conflict: "Issue #N has overlapping objectives"
   - Suggest resolution

### Step 2: Check for Staleness

**If existing open specs:**
1. Check if any were implemented but left open
2. Check if referenced code locations have changed
3. Check if problem statement still applies

**If stale:**
1. HALT
2. Suggest updating or closing stale spec first

### Step 3: Validate Spec Completeness

**Ensure essential sections are present:**

| Section | Required |
|---------|----------|
| Problem Statement | ✅ YES |
| Context | ✅ YES |
| Success Criteria | ✅ YES |
| Decision Rationale | (for complex specs) |

**If missing sections:**
1. HALT
2. Report missing sections
3. Do NOT proceed with creation

### Step 4: Report Validation Result

**If all checks pass:**
- Report: "Pre-creation validation passed. Ready to create issue."
- Proceed to `single-task-check` task

**If ANY check fails:**
- HALT
- Report specific failure
- Do NOT proceed with creation

## Common Issues

| Issue | Resolution |
|-------|------------|
| Superseding issue found | HALT, report conflict, suggest closing superseded spec |
| Conflicting objectives | HALT, suggest reconciling or splitting scopes |
| Missing sections | HALT, require spec update before creation |
| Stale open spec detected | HALT, suggest updating or closing stale spec |

## Safety Checks

Before proceeding, verify ALL:

- No superseding issues exist
- No conflicting specs exist
- All essential sections present
- Spec is not stale

**If ANY check fails → HALT and report.**

## Example: Superseding Issue Detection

**New Spec:** "[SPEC] Add rate limiting"

**Check:** Query open issues
- Found: Issue #50 "[SPEC-FIX] Rate limiting for API endpoints"

**Result:** HALT. Issue #50 supersedes this spec. Suggest:
1. Review #50 to see if it covers the requirement
2. Close new spec if superseded
3. Update #50 if scope needs expansion

## Context Required

- Related tasks: `creation` (create after validation)
- Related skills: `concern-separation-auditor`, `spec-auditor` (auditors invoked later)