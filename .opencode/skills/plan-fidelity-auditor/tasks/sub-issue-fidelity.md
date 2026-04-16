# Task: sub-issue-fidelity

## Purpose

Verify that sub-issues under a Plan align with the Plan's phases. For each Plan phase, confirm a corresponding sub-issue exists. For each sub-issue, confirm its body content matches the Plan phase prose. Reports discrepancies as findings — does NOT auto-fix.

**Trigger:** When a Plan has sub-issues and plan-fidelity audit needs to verify alignment between Plan phases and sub-issue content.

## Procedure

### Step 1: Read the Plan Issue

Read the Plan issue via GitHub MCP (`github_issue_read method=get`). Extract:
- Issue number
- Issue title
- Issue body (the Plan prose with phases)

### Step 2: Read Sub-Issues

Read all sub-issues under the Plan via GitHub MCP (`github_issue_read method=get_sub_issues`). For each sub-issue:
- Read the full body (`github_issue_read method=get`)
- Record: issue number, title, body content

### Step 3: Parse Plan Phases

Parse the Plan body into a structured list of phases:
- Extract phase names and their prose content
- Identify each phase's key tasks, deliverables, and success criteria as stated in the Plan

### Step 4: Verify Phase-to-Sub-Issue Mapping

For each Plan phase:
1. Search sub-issues for a semantic match (title or body references the phase)
2. If no matching sub-issue exists → report `MISSING_SUB_ISSUE`
3. If the sub-issue title/phase name doesn't semantically match → report `MISMATCHED_PHASE_NAME`

### Step 5: Verify Sub-Issue Body Content

For each sub-issue that maps to a Plan phase:
1. Compare the sub-issue body against the Plan phase prose
2. Check that key tasks from the Plan phase appear in the sub-issue body
3. Check that success criteria or deliverables from the Plan phase appear in the sub-issue body
4. If the sub-issue body is missing substantial Plan prose → report `INCOMPLETE_SUB_ISSUE_BODY`
5. If a task in the sub-issue is not traceable to the Plan phase → report `TASK_NOT_IN_SUB_ISSUE`

### Step 6: Report Findings

Report all findings using the v3 auto-fix format.

## Finding Types

| Finding Type | Severity | Description |
|-------------|----------|-------------|
| MISSING_SUB_ISSUE | HIGH | Plan phase has no corresponding sub-issue |
| MISMATCHED_PHASE_NAME | MEDIUM | Sub-issue name doesn't semantically match Plan phase name |
| INCOMPLETE_SUB_ISSUE_BODY | MEDIUM | Sub-issue body is missing substantial Plan phase content |
| TASK_NOT_IN_SUB_ISSUE | LOW | A Plan phase task is not represented in the sub-issue |

## Semantic Matching

Before reporting `MISSING_SUB_ISSUE`, attempt semantic matching:
- Phase "Database Schema Migration" ↔ Sub-issue "Schema Updates" → match (same concept)
- Phase "API Endpoints" ↔ Sub-issue "REST API Implementation" → match (same concept)
- Phase "Authentication" ↔ Sub-issue "OAuth2 Setup" → match if OAuth2 is the auth method

Only report `MISSING_SUB_ISSUE` when no semantic match exists after thorough comparison.

## Report Format

```
Subtask: sub-issue-fidelity
Finding: [MISSING_SUB_ISSUE|MISMATCHED_PHASE_NAME|INCOMPLETE_SUB_ISSUE_BODY|TASK_NOT_IN_SUB_ISSUE] - [summary]
Location: [Plan phase name / sub-issue number]
Context: [why this matters for plan-sub-issue alignment]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Auto-Fix Classification

| Finding Type | Classification | Fix Action |
|-------------|----------------|-----------|
| MISSING_SUB_ISSUE | flag-for-review | Creating sub-issues requires authorization per approval-gate |
| MISMATCHED_PHASE_NAME | flag-for-review | Renaming requires author judgment about scope |
| INCOMPLETE_SUB_ISSUE_BODY | auto-fix | Sub-issue body should reflect Plan phase prose per the spec |
| TASK_NOT_IN_SUB_ISSUE | auto-fix | Adding traceable tasks aligns sub-issues with Plan phases |

## Scope Boundaries

- Read-only analysis of Plan issue and sub-issues via GitHub MCP
- Auto-fix applies to INCOMPLETE_SUB_ISSUE_BODY and TASK_NOT_IN_SUB_ISSUE findings only (updating sub-issue bodies with Plan phase prose)
- Does NOT create or delete sub-issues (MISSING_SUB_ISSUE is flag-for-review)
- Does NOT rename sub-issues (MISMATCHED_PHASE_NAME is flag-for-review)
- Must use GitHub MCP tools for all issue operations

Co-authored with AI: <AI-Name> (<model-id>)

## Live Verification: Sub-Issue Alignment Claims (MANDATORY)

**Each sub-issue alignment claim MUST be verified against actual GitHub state. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Sub-issue exists for Plan phase" | Verify sub-issue is accessible via API | `github_issue_read(method=get, issue_number=N)` → confirm non-404 | MISSING-TRACEABILITY |
| "Sub-issue body matches Plan phase" | Verify body content actually aligns with Plan prose | `github_issue_read(method=get)` → compare sub-issue vs Plan body | VERIFICATION-GAP |
| "Sub-issue state matches expected" | Verify sub-issue is open/closed as expected | `github_issue_read(method=get, issue_number=N)` → check `state` field | STRUCTURE-VIOLATION |
| "Plan phase exists in Plan body" | Verify the referenced phase actually exists | `github_issue_read(method=get)` → search for phase header | MISSING-TRACEABILITY |

**Evidence artifact:** GitHub MCP call results for each sub-issue and Plan verification.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Sub-issue returns 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve missing issue |
| Sub-issue body contradicts alignment claim | VERIFICATION-GAP | flag-for-review | Report — alignment needs re-verification |
| Sub-issue state unexpected | STRUCTURE-VIOLATION | flag-for-review | May indicate premature closure |
| Plan phase not found in body | MISSING-TRACEABILITY | flag-for-review | Plan may have been revised |