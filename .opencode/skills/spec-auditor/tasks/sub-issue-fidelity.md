# Task: sub-issue-fidelity

## Purpose

Verify that sub-issues under a Plan align with the Plan's phases. For each Plan phase, confirm a corresponding sub-issue exists. For each sub-issue, confirm its body content matches the Plan phase prose.

**Delegated from:** plan-fidelity-auditor (`sub-issue-fidelity` task). Now a subtask within spec-auditor.

## Procedure

### Step 1: Read the Plan Issue

Read the Plan issue via GitHub MCP (`github_issue_read method=get`). Extract the Plan body with all phases.

### Step 2: Read Sub-Issues

Read all sub-issues under the Plan via GitHub MCP (`github_issue_read method=get_sub_issues`). For each sub-issue, read the full body via `github_issue_read method=get`.

### Step 3: Parse Plan Phases

Parse the Plan body into a structured list of phases with:
- Phase names
- Phase prose content (tasks, deliverables, success criteria)

### Step 4: Verify Phase-to-Sub-Issue Mapping

For each Plan phase:
1. Search sub-issues for a semantic match (title or body references the phase)
2. If no matching sub-issue exists → report `MISSING_SUB_ISSUE`
3. If the sub-issue title/phase name doesn't semantically match → report `MISMATCHED_PHASE_NAME`

### Step 5: Verify Sub-Issue Body Content

For each mapped sub-issue:
1. Compare the sub-issue body against the Plan phase prose
2. Check that key tasks from the Plan phase appear in the sub-issue body
3. Check that success criteria/deliverables from the Plan phase appear in the sub-issue body
4. If sub-issue body is missing substantial Plan prose → report `INCOMPLETE_SUB_ISSUE_BODY`
5. If a Plan phase task is not in the sub-issue → report `TASK_NOT_IN_SUB_ISSUE`

### Step 6: Report Findings

Report all findings using the v3 auto-fix format.

## Finding Types

| Finding Type | Severity | Description |
|-------------|----------|-------------|
| MISSING_SUB_ISSUE | HIGH | Plan phase has no corresponding sub-issue |
| MISMATCHED_PHASE_NAME | MEDIUM | Sub-issue name doesn't semantically match Plan phase name |
| INCOMPLETE_SUB_ISSUE_BODY | MEDIUM | Sub-issue body missing substantial Plan phase content |
| TASK_NOT_IN_SUB_ISSUE | LOW | Plan phase task not represented in sub-issue |

## Auto-Fix Classification

| Finding Type | Classification | Fix Action |
|-------------|----------------|-----------|
| MISSING_SUB_ISSUE | flag-for-review | Creating sub-issues requires authorization per approval-gate |
| MISMATCHED_PHASE_NAME | flag-for-review | Renaming requires author judgment |
| INCOMPLETE_SUB_ISSUE_BODY | auto-fix | Update sub-issue body with Plan phase prose |
| TASK_NOT_IN_SUB_ISSUE | auto-fix | Add traceable tasks to align with Plan phases |

## Semantic Matching

Before reporting `MISSING_SUB_ISSUE`, attempt semantic matching:
- Phase "Database Schema Migration" ↔ Sub-issue "Schema Updates" → match
- Phase "API Endpoints" ↔ Sub-issue "REST API Implementation" → match
- Phase "Authentication" ↔ Sub-issue "OAuth2 Setup" → match if OAuth2 is auth method

Only report `MISSING_SUB_ISSUE` when no semantic match exists.

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

## When to Run

- When a Plan has sub-issues
- When verifying that enriched sub-issue bodies align with Plan phases
- As an extension of `fidelity` subtask for Plans with sub-issues

## When to Skip

- Plans without sub-issues (fall back to `fidelity` only)
- Single-task Plans with no phases

## Scope Boundaries

- Read-only analysis of Plan issue and sub-issues via GitHub MCP
- Auto-fix applies to INCOMPLETE_SUB_ISSUE_BODY and TASK_NOT_IN_SUB_ISSUE only
- Does NOT create or delete sub-issues (MISSING_SUB_ISSUE is flag-for-review)
- Does NOT rename sub-issues (MISMATCHED_PHASE_NAME is flag-for-review)

Co-authored with AI: <AI-Name> (<model-id>)