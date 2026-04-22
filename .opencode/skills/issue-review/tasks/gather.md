# Task: gather

## Purpose

Collect all issue data needed by downstream tasks. This is a pure data-collection step — no decisions.

## Pre-Conditions

- **Load guideline:** `.opencode/guidelines/067-context-completeness.md` before proceeding — ALL comments MUST be read before any triage decision

## Entry Criteria

- Issue number provided via `--issue N`
- GitHub MCP available for issue/comment operations

## Exit Criteria

- All issue data collected
- Standard data set extracted for triage
- Sub-issue data recursively gathered if present

## Procedure

### Step 1: Read Issue Body

```
github_issue_read(method="get", issue_number=N)
```

### Step 2: Read All Comments

```
github_issue_read(method="get_comments", issue_number=N)
```

Record comment count for evidence. Note: per `067-context-completeness.md`, ALL comments MUST be read before any triage decision.

### Step 3: Read Labels and Authorization Status

```
github_issue_read(method="get_labels", issue_number=N)
```

Extract:
- `needs-approval` label presence
- Any categorization labels (enhancement, bug, architecture, etc.)
- Authorization status from comments (look for "approved", "go", `#N approved` patterns)

### Step 4: Detect Sub-issues

```
github_issue_read(method="get_sub_issues", issue_number=N)
```

If sub-issues exist, store their issue numbers for recursive gathering.

### Step 5: Recursively Gather Sub-issue Data

For each sub-issue, repeat Steps 1-4:
- Read sub-issue body
- Read sub-issue comments
- Read sub-issue labels
- Check for further nesting (unlikely but handled)

### Step 6: Extract Standard Data Set

From all gathered data, extract prose descriptions of:

1. **Issue type classification hints:**
   - Phases/steps present in body (e.g., "Phase 1:", "Phase 2:")
   - Success criteria section present
   - Bug report language patterns ("crash", "error", "broken", "steps to reproduce")

2. **Comment themes:**
   - Questions asked by commenters
   - Revisions or spec changes noted
   - Blockers reported
   - Audit findings (comments containing finding-class patterns like "finding:", "violation:", "CRITICAL")
   - Authorization comments ("approved", "go")

3. **Last audit timestamp:**
   - Most recent comment containing audit finding patterns
   - Used by `just-review` path to assess staleness

4. **Authorization status:**
   - Explicit approval comments found (quote them)
   - `needs-approval` label present or absent

5. **Spec structure signals:**
   - Has phases? (count them)
   - Has success criteria?
   - Has edge cases?
   - Has affected files table?
   - Has risk assessment?

6. **Fix spec sub-issue check (for bug reports):**
   - Do any sub-issues have titles starting with `[SPEC] Fix:`?
   - Do any sub-issues have the `spec` label?
   - If bug report has existing fix spec sub-issues, note their numbers and status
   - This informs the `analyze-and-spec` task (skip creation if already exists)

### Step 7: Return Data for Downstream

Prose description of gathered data — no structured schema required. The agent carries context forward to the triage task.

## Output Format

Prose summary of all gathered data, organized by the five categories above. Include comment count and specific authorization evidence for audit trail.

## Edge Cases

| Case | Handling |
|------|----------|
| No comments | Proceed normally — comment count = 0 |
| Issue is closed | Note state; triage decides if stale or complete |
| Sub-issues present | Gather each; triage runs independently per sub-issue |
| No sub-issues | Skip recursive gathering |
| API error | Report error and HALT; do not proceed with partial data |

## Live Verification: Gathered Data Claims (MANDATORY)

**Each data claim gathered for downstream tasks MUST be verified via actual tool calls. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Issue has N comments" | Re-count via `get_comments` response | `github_issue_read(method=get_comments)` → count items | VERIFICATION-GAP |
| "Authorization comment exists" | Verify comment author is developer, not bot/agent | `github_issue_read(method=get_comments)` → check `author_association` | CONFLICTING |
| "Sub-issues exist" | Verify sub-issues are accessible and not 404 | `github_issue_read(method=get_sub_issues)` → check each child exists | MISSING-TRACEABILITY |
| "`needs-approval` label present/absent" | Verify label list matches claimed state | `github_issue_read(method=get_labels)` → check label array | STRUCTURE-VIOLATION |
| "Bug report has fix spec" | Verify sub-issue exists with correct prefix | `github_issue_read(method=get_sub_issues)` + `github_issue_read(method=get)` per child | MISSING-ELEMENT |
| "Last audit timestamp" | Verify comment containing audit pattern actually exists | `github_issue_read(method=get_comments)` → search for audit patterns | VERIFICATION-GAP |

**Evidence artifact:** Tool call results for each claim category.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Comment count mismatched | VERIFICATION-GAP | auto-fix | Re-count and report correct number |
| Authorization from bot/agent | CONFLICTING | flag-for-review | Reject as valid authorization |
| Sub-issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve missing issue |
| Label state contradicted claim | STRUCTURE-VIOLATION | auto-fix | Report actual label state |
| Fix spec missing for bug | MISSING-ELEMENT | conditional | Proceed to `analyze-and-spec` to create one |