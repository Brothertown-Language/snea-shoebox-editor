# Task: concern-coverage

## Purpose

Verify that sub-issue bodies reflect the Plan's concern boundaries. For each sub-issue, check that its concern scope matches its corresponding Plan phase. Report mismatches between concern boundaries in sub-issues and Plan phases.

**Trigger:** When `concerns` subtask runs on a Plan that has sub-issues, this task extends the analysis to verify that sub-issue concern boundaries align with Plan phase concern boundaries.

## Procedure

### Step 1: Read the Plan Issue

Read the Plan issue via GitHub MCP (`github_issue_read method=get`). Parse the Plan body to identify phase boundaries and the concern scope of each phase.

### Step 2: Read Sub-Issues

Read all sub-issues under the Plan via GitHub MCP (`github_issue_read method=get_sub_issues`). For each sub-issue:
- Read the full body (`github_issue_read method=get`)
- Record: issue number, title, body content, concern scope

### Step 3: Determine Concern Boundaries per Plan Phase

For each Plan phase, determine its concern boundary:
- What is the primary concern (e.g., data layer, API layer, UI layer)?
- What steps/tasks fall within the concern?
- What steps/tasks fall outside the concern?

Use the same concern analysis logic from `audit-phases`:
- Keyword hints (migration/schema → data layer, API/endpoint → business logic)
- Deployment independence
- Risk profile grouping
- Blast radius considerations

### Step 4: Map Sub-Issues to Plan Phases

For each sub-issue, find the corresponding Plan phase via semantic matching:
- Match by title similarity
- Match by body content overlap
- Record unmatched sub-issues or Plan phases without sub-issues

### Step 5: Compare Concern Boundaries

For each matched sub-issue ↔ Plan phase pair:
1. Extract the concern scope expressed in the sub-issue body
2. Compare against the Plan phase's concern boundary
3. Identify mismatches:
   - **Sub-issue concern is narrower than Plan phase**: Sub-issue omits tasks that belong to the Plan phase's concern
   - **Sub-issue concern is wider than Plan phase**: Sub-issue includes tasks from another concern
   - **Sub-issue concern crosses Plan phase boundaries**: Sub-issue mixes tasks from multiple Plan phases

### Step 6: Report Findings

Report all mismatches as findings using the v3 auto-fix format.

## Finding Types

| Finding Type | Severity | Description |
|-------------|----------|-------------|
| CONCERN_SCOPE_NARROWER | MEDIUM | Sub-issue body omits tasks within the Plan phase's concern boundary |
| CONCERN_SCOPE_WIDER | MEDIUM | Sub-issue body includes tasks outside the Plan phase's concern boundary |
| CONCERN_BOUNDARY_CROSSED | HIGH | Sub-issue body mixes tasks from multiple Plan phase concerns |

## Semantic Matching Before Reporting

Before reporting a concern boundary mismatch:
1. Verify the Plan phase actually defines a single concern (not a mixed-concern phase itself)
2. If the Plan phase itself has mixed concerns, the sub-issue may correctly include cross-boundary tasks
3. Only report mismatches where the sub-issue concern scope deviates from a well-defined Plan phase concern

## Report Format

```
Subtask: concerns (concern-coverage)
Finding: [CONCERN_SCOPE_NARROWER|CONCERN_SCOPE_WIDER|CONCERN_BOUNDARY_CROSSED] - [summary]
Location: [Plan phase name / sub-issue number]
Context: [why concern alignment matters for this Plan/sub-issue pair]
Classification: flag-for-review
Fix Action: flagged for review — [reason]
Severity: [HIGH|MEDIUM|LOW]
```

## Why Flag-for-Review (Not Auto-Fix)

Concern boundary adjustments in sub-issues require context judgment:
- A wider sub-issue scope may intentionally group tightly coupled tasks
- A narrower scope may be a valid scoping decision
- Cross-boundary tasks may reflect legitimate inter-concern dependencies
- The agent has full context about deployment needs and domain constraints

All findings are reported for agent review. The agent decides whether to adjust sub-issue scope.

## When to Run

- After `audit-phases` when the Plan has sub-issues
- When verifying that enriched sub-issue bodies maintain proper concern separation
- As an extension of `concerns` subtask in spec-auditor for Plans with sub-issues

## When to Skip

- Plans without sub-issues (fall back to `audit-phases` only)
- Single-task Plans (no phases to analyze)

## Scope Boundaries

- Read-only analysis of Plan issue and sub-issues via GitHub MCP
- Does NOT modify sub-issue scope or content (flag-for-review only)
- Must use GitHub MCP tools for all issue operations

Co-authored with AI: <AI-Name> (<model-id>)