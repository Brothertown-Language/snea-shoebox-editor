# Task: analyze-and-spec

## Purpose

Perform root cause analysis on a bug report and auto-create a fix spec sub-issue linked to the bug report parent. This task bridges the gap between bug discovery and fix implementation by ensuring every bug report has a corresponding fix spec before closure.

## Pre-Conditions

- **Load guideline:** `.opencode/guidelines/067-context-completeness.md` before proceeding — ALL comments MUST be read before analysis
- Gathered data from `gather` task available
- Bug language detected by triage (or `bug` label present)

## Entry Criteria

- Triage selected the `analyze-and-spec` path
- Issue contains bug report language ("crash", "error", "broken", "steps to reproduce", "unexpected behavior")
- OR `bug` label present on the issue

## Exit Criteria

- Root cause analysis documented in chat
- Impact assessment completed
- Fix spec sub-issue created via `issue-operations` skill
- Fix spec sub-issue linked to bug report parent via `github_sub_issue_write`
- Smart checkpoint decision made (auto-proceed or HALT)

## Procedure

### Step 1: Verify Bug Classification

Confirm the issue genuinely describes a bug (not a feature request, spec, or other type):

| Signal | Confirms Bug |
|--------|-------------|
| Body describes unexpected/crashing behavior | Yes |
| Body contains "steps to reproduce" | Yes |
| Title contains "bug", "crash", "error", "broken" | Yes |
| `bug` label present | Yes (unless contradicted by content) |
| Body is actually a feature request | No → re-triage to `qa` |

If NOT a bug, report the misclassification in chat and suggest re-triage. HALT.

### Step 2: Perform Root Cause Analysis

Systematically analyze the bug report to identify the root cause:

1. **Read the bug report** — extract error description, reproduction steps, expected vs actual behavior
2. **Examine referenced code** — use `srclight` or code search to find relevant source
3. **Trace the call path** — identify the failing component and its callers
4. **Form hypotheses** — generate at least 2 root cause hypotheses
5. **Document analysis** — produce a prose root cause summary

**Analysis is read-only.** Do NOT make any code changes during this step.

### Step 3: Assess Impact

Evaluate the bug's scope:

| Dimension | Questions |
|-----------|-----------|
| **User impact** | How many users affected? Data loss? Security? |
| **Code scope** | Single function, module, or cross-cutting? |
| **Fix complexity** | Trivial (1-line), simple (1-function), or complex (multi-file)? |
| **Urgency** | Blocker, critical, or minor? |

### Step 4: Generate Fix Spec

Create a fix spec using the `issue-operations` skill. The fix spec must include:

1. **Title**: `[SPEC] Fix: <brief bug description>`
2. **Body** (minimum required sections):
   - **Root Cause**: Prose description of the identified root cause
   - **Fix Approach**: Minimal targeted fix targeting root cause (not symptoms)
   - **Success Criteria**: Testable conditions confirming the fix works
   - **Affected Files**: Files that need modification
   - **Risk Assessment**: Potential regression areas

### Step 5: Smart Checkpoint

Before creating the fix spec sub-issue, evaluate clarity:

| Condition | Action |
|-----------|--------|
| Root cause is clear, fix approach is unambiguous | Auto-proceed — create fix spec sub-issue |
| Multiple plausible root causes, fix approach unclear | HALT — report findings in chat, wait for developer input |
| Bug is a duplicate of an existing issue | HALT — report duplicate in chat, suggest linking instead |
| Bug requires design decisions before fixing | HALT — report design questions in chat, wait for answers |

**When auto-proceeding:** The agent creates the fix spec sub-issue without pausing for confirmation. This is justified because the fix spec still requires explicit authorization before any code changes (per `approval-gate`).

**When HALTing:** Report the analysis findings and open questions in chat. Do NOT create the fix spec until ambiguity is resolved. The developer may provide clarification that allows re-entry at Step 4.

### Step 6: Create Fix Spec Sub-Issue

Invoke `issue-operations` skill to create the fix spec:

```
github_issue_write(
    method="create",
    owner=<github.owner>,
    repo=<github.repo>,
    title="[SPEC] Fix: <brief bug description>",
    body="<fix spec body from Step 4>",
    labels=["spec", "needs-approval"]
)
```

### Step 7: Link Fix Spec to Bug Report

Link the newly created fix spec as a sub-issue of the bug report:

```
github_sub_issue_write(
    method="add",
    owner=<github.owner>,
    repo=<github.repo>,
    issue_number=<bug_report_number>,
    sub_issue_id=<fix_spec_database_id>
)
```

**Note:** Use the database ID (not issue number) returned from the creation call.

### Step 8: Post Analysis Summary to Bug Report

Add a comment to the bug report summarizing the analysis and linking the fix spec:

```
github_add_issue_comment(
    owner=<github.owner>,
    repo=<github.repo>,
    issue_number=<bug_report_number>,
    body="Root cause analysis complete. Fix spec created: #<fix_spec_number>"
)
```

Keep the comment substantive — include the root cause finding, not just a link.

### Step 9: Report to Chat

Produce prose exec summary for chat:

```
<root cause analysis summary>
<impact assessment>
<fix spec created: #N>

🤖 <AgentName> (<ModelId>) 🔍 analysis
```

## Edge Cases

| Case | Handling |
|------|----------|
| Bug report lacks reproduction steps | Note in analysis; proceed if root cause identifiable, HALT if not |
| Multiple bugs in one report | Create separate fix specs for each distinct root cause |
| Bug already has a fix spec sub-issue | Skip creation; report existing fix spec in chat |
| Root cause is in a dependency | Note in fix spec; fix may be "work around" or "update dependency" |
| Bug is actually expected behavior | Report misclassification; suggest closing as not-a-bug |
| Issue is closed bug report | Do NOT skip — verify sub-issues are closed and cross-references resolved; if all verified, classify as `already-handled`; otherwise proceed with analysis or flag for review |
| Fix spec creation fails | HALT; report error in chat; retry is developer's decision |

## Closed Issue Verification Gate

**⚠️ NEVER skip analysis for a closed issue without verification.** A closed issue may have:

1. **Open sub-issues** — The parent is closed but child issues remain open (premature parent closure)
2. **Unresolved cross-references** — The spec → plan chain may still have pending links
3. **Erroneous closure** — No merged PR, `state_reason` is "not_planned" instead of "completed"

### Verification Procedure

Before classifying a closed bug report as `already-handled` or `stale`:

1. **Check sub-issues:** `github_issue_read(method="get_sub_issues", issue_number=N)` — if any sub-issue is open, the parent closure is premature
2. **Check cross-references:** Read issue body for `Spec: #N`, `Plan: #N` references — verify referenced issues are also resolved
3. **Check closure correctness:** Verify `state_reason == "completed"` AND a merged PR exists (search for PRs referencing the issue)
4. **If all verified:** Classify as `already-handled` and skip analysis
5. **If any check fails:** Proceed with analysis (root cause may still need fix spec) or flag for review

**Evidence requirement:** Each check must produce a tool-call artifact. Do NOT assume "closed" = "verified."

## Cross-References

- `issue-operations`: Called for fix spec creation
- `systematic-debugging`: Root cause analysis overlaps with `diagnose` task; this task is for issue-review context, not active debugging
- `approval-gate`: Fix spec requires authorization before code changes proceed
- `067-context-completeness.md`: All comments read before analysis
- `000-critical-rules.md`: Bug reports must have fix spec before closure