# Task: pre-creation

## Purpose

Validate spec before creating GitHub Issue to prevent conflicts, superseded issues, and missing essential content.

## Operating Protocol

1. **Mandatory invocation:** This task MUST run before ANY issue creation.

## Entry Criteria

- Spec content is ready for issue creation
- Title follows proper format
- User has authorized creation

## Exit Criteria

- Spec validated (no conflicts, no superseded issues)
- Essential content coverage confirmed
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

### Step 3: Validate Spec Content Coverage

**Ensure essential content is present, regardless of section header names.**

The check is content-coverage, not structural conformity. A spec that covers all required concerns under different section names passes. A spec with the exact "correct" headers but missing content fails.

| Content Area | What to Check |
|-------------|---------------|
| Problem description | Does the spec describe what problem it solves and why it matters? |
| Context | Does the spec provide enough background for a fresh agent to understand? |
| Success criteria | Does the spec include testable, binary pass/fail completion criteria? |

**Content coverage check examples:**

- A spec with "Background", "The Issue", "How We Know It Works" passes ✅ (covers problem, context, criteria)
- A spec with "Problem Statement", "Context", "Success Criteria" passes ✅ (covers problem, context, criteria)
- A spec with "Problem Statement" header but empty content fails ❌ (missing actual content)
- A spec with no problem description but a detailed implementation plan fails ❌ (what problem is it solving?)

**If content coverage is missing:**
1. HALT
2. Report missing content areas (not missing headers, missing *content*)
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
| Missing content coverage | HALT, require spec update before creation |
| Stale open spec detected | HALT, suggest updating or closing stale spec |

## Safety Checks

Before proceeding, verify ALL:

- No superseding issues exist
- No conflicting specs exist
- Essential content coverage is present (problem, context, success criteria)
- Spec is not stale

**If ANY check fails → HALT and report.**

## Example: Content Coverage Check

**New Spec:** "Add rate limiting to API endpoints"

**Check:** Content coverage
- Problem described? Yes — "API calls average 150ms, causing slow page loads"
- Context provided? Yes — "Current queries hit DB directly, 85% cache hit potential"
- Success criteria testable? Yes — "API response <20ms for cached queries, >80% cache hit rate"

**Result:** PASS. Content coverage is sufficient regardless of section headers.

**New Spec:** "Improve the API"

**Check:** Content coverage
- Problem described? No — "improve" is vague, no measurable problem stated
- Context provided? No — no background on what's wrong
- Success criteria testable? No — "better API" is not testable

**Result:** FAIL. Missing content coverage, not missing headers.

## Context Required

- Related tasks: `creation` (create after validation)
- Related skills: `concern-separation-auditor`, `spec-auditor` (auditors invoked later)