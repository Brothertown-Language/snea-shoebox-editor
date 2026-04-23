# Task: verify-closed-issue

## Purpose

Verify that a closed issue was legitimately closed — checking that a merged PR exists, that success criteria are actually met in the live codebase, and that no premature closure occurred. Verification is transitive: it traverses sub-issues, cross-references, and linked issues recursively to ensure the entire reachable graph is in a consistent state. This task enforces the rule that "closed" does NOT mean "verified" without evidence — and that a merged PR does NOT mean "implementation complete" without success criteria verification.

## Pre-Conditions

- **Load guideline:** `.opencode/guidelines/065-verification-honesty.md` before proceeding — verification claims must be backed by actual tool calls, not memory

## Entry Criteria

- An issue's closed state needs verification (before skipping, autoclosing parent, or classifying as "already implemented")
- The issue number is known

## Exit Criteria

- Closed state is verified as legitimate (merged PR exists AND all success criteria pass) OR
- Closed state is flagged as a VERIFICATION-GAP (no merged PR evidence) with clear reason OR
- Partial implementation detected (some SCs fail) — downgrade to PARTIALLY_IMPLEMENTED OR
- No implementation despite closure (all SCs fail) — downgrade to NOT_IMPLEMENTED_DESPITE_CLOSURE

## Procedure

### Step 1: Retrieve Issue State

```python
issue = github_issue_read(method="get", issue_number=N)

if issue["state"] != "closed":
    # Issue is still open — closed verification does not apply
    REPORT: "Issue #N is open, not closed. No closed-state verification needed."
    EXIT with result: NOT_CLOSED
```

**Evidence artifact:** `github_issue_read(method=get)` response showing `state: "closed"`.

### Step 2: Determine Closure Reason

```python
state_reason = issue.get("state_reason", "")
```

| `state_reason` | Interpretation | Next Step |
|----------------|---------------|-----------|
| `"completed"` | Issue was marked as done | Step 3 (verify merged PR) |
| `"not_planned"` | Issue was intentionally not implemented | Step 4 (handle not_planned) |
| `"duplicate"` | Issue was closed as a duplicate | Step 5 (verify duplicate target) |
| `None` or empty | No reason recorded | Step 3 (assume completed, verify) |

### Step 3: Verify Merged PR Exists (for "completed" or unknown reason)

**🚫 CRITICAL: A closed issue with `state_reason: "completed"` does NOT guarantee implementation.** Verify via GitHub API.

```python
# Search for PRs that reference this issue
prs = github_search_pull_requests(
    query=f"Fixes #{N} repo:{<github.owner>}/{<github.repo>}"
)

merged_pr_found = False
merged_prs = []

for pr in prs:
    pr_detail = github_pull_request_read(
        method="get", owner=<github.owner>, repo=<github.repo>, pullNumber=pr["number"]
    )
    if pr_detail.get("merged_at") is not None:
        merged_pr_found = True
        merged_prs.append({
            "number": pr_detail["number"],
            "merged_at": pr_detail["merged_at"],
            "merged_by": pr_detail.get("merged_by", {})
        })

if merged_pr_found:
    REPORT: f"Issue #{N} closed as completed with merged PR evidence: {', '.join(f'#{p['number']}' for p in merged_prs)}"
    # Do NOT exit here — proceed to Step 6 (sub-issues) then Step 7 (SC verification)
    # Merged PR is a prerequisite, NOT proof of complete implementation
    current_result = VERIFIED_CLOSED  # Provisional — may be downgraded by Step 7
else:
    # No merged PR found — suspicious closure
    REPORT: f"Issue #{N} closed as completed but NO merged PR found via 'Fixes #{N}' search"
    EXIT with result: VERIFICATION_GAP
```

**Evidence artifact:** `github_search_pull_requests` response + `github_pull_request_read` response showing `merged_at` field for each PR found.

### Step 4: Handle "not_planned" Closure

```python
# Issue was intentionally not implemented
REPORT: f"Issue #{N} closed as not_planned — work was intentionally deferred or rejected"
REPORT: "This issue may need reopening or a new fix spec if the underlying problem persists"
EXIT with result: NOT_PLANNED_CLOSURE
```

**Action for callers:**

| Caller Context | Action |
|---------------|--------|
| `verify-authorization` auto-dispatch | Do NOT autoclose; flag for review |
| `verify-already-implemented` | Do NOT classify as "already implemented" |
| `pre-implementation-analysis` screening | Do NOT exclude from implementation; may need scope reduction |
| `cleanup` pre-closure gate | Allow parent closure only if remaining scope is verified |

### Step 5: Verify Duplicate Target (for "duplicate" closure)

```python
# Extract duplicate target from issue body or comments
# GitHub typically adds "Duplicate of #M" automatically
# Also check comments for duplicate reference

body = issue.get("body", "")
comments = github_issue_read(method="get_comments", issue_number=N)

duplicate_target = None

# Search body for duplicate reference
for line in body.split("\n"):
    if "duplicate" in line.lower() and "#" in line:
        # Extract issue number reference
        import re
        match = re.search(r'#(\d+)', line)
        if match:
            duplicate_target = int(match.group(1))
            break

# Search comments for duplicate reference
if not duplicate_target:
    for comment in comments:
        if "duplicate" in comment.get("body", "").lower():
            match = re.search(r'#(\d+)', comment.get("body", ""))
            if match:
                duplicate_target = int(match.group(1))
                break

if duplicate_target:
    # Verify the duplicate target exists and is not also prematurely closed
    target = github_issue_read(method="get", issue_number=duplicate_target)
    REPORT: f"Issue #{N} closed as duplicate of #{duplicate_target} (state: {target['state']})"
    # Recursively verify the duplicate target if it's also closed
    # (Call verify-closed-issue recursively for the target, with depth limit)
    EXIT with result: DUPLICATE_OF, target=duplicate_target
else:
    REPORT: f"Issue #{N} closed as duplicate but no duplicate target found"
    EXIT with result: VERIFICATION_GAP
```

### Step 6: Check Sub-Issues (After Verifying Parent Closure)

If the issue is a parent with sub-issues, verify EACH sub-issue's closure is legitimate before closing the parent:

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)

if sub_issues:
    for sub_issue in sub_issues:
        # Recursively verify each sub-issue
        sub_result = verify_closed_issue(sub_issue["number"])

        if sub_result == VERIFICATION_GAP:
            REPORT: f"Sub-issue #{sub_issue['number']} closure is a verification gap"
            # Parent CANNOT be closed until sub-issue is resolved
            EXIT with result: BLOCKED_BY_SUB_ISSUE

        elif sub_result == NOT_PLANNED_CLOSURE:
            REPORT: f"Sub-issue #{sub_issue['number']} was closed as not_planned"
            # Parent MAY be closed for remaining scope only
            NOTE sub_issue["number"] as "intentionally skipped"
```

### Step 7: Success Criteria Verification (MANDATORY — ZERO TOLERANCE)

**🚫 CRITICAL: Step 7 is MANDATORY and BLOCKING. Skipping this step is a CRITICAL GUIDELINE VIOLATION.** A merged PR proves code was merged, NOT that success criteria are met. This step enforces the rule from `000-critical-rules.md` §"Assuming Closed Issues Are Verified".

For legitimately closed issues (VERIFIED_CLOSED from Step 3), verify that EACH success criterion from the issue body is actually met in the live codebase:

```python
body = issue.get("body", "")
sc_list = extract_success_criteria(body)  # Parse "- [ ]" or "- [x]" checklist items under "Success Criteria" heading

if not sc_list:
    # No success criteria found in issue body
    # Cannot verify SCs — result depends on merged PR evidence
    REPORT: f"Issue #{N}: No success criteria found in issue body. Cannot verify implementation completeness."
    REPORT: f"Result remains: {current_result} (merged PR evidence only, no SC verification possible)"
    # Do NOT downgrade — proceed with PR-only evidence
    # But flag that SC verification was not performed
    NOTE: "SC_VERIFICATION_NOT_PERFORMED: no_sc_found"
    PROCEED to Step 8

sc_results = []
for sc in sc_list:
    # Verify each SC against the live codebase
    # Use read, grep, srclight_get_symbol, or test execution
    # Each SC MUST produce a tool-call artifact as evidence
    evidence = verify_sc_against_codebase(sc, merged_prs)
    sc_results.append({
        "criterion": sc,
        "passed": evidence.passed,
        "evidence_tool": evidence.tool_name,
        "evidence_detail": evidence.detail
    })

# Produce per-SC pass/fail table
REPORT: f"Success Criteria Verification for Issue #{N}:"
for result in sc_results:
    status = "PASS" if result["passed"] else "FAIL"
    REPORT: f"  [{status}] {result['criterion']}: {result['evidence_detail']} (evidence: {result['evidence_tool']})"

all_passed = all(r["passed"] for r in sc_results)
some_passed = any(r["passed"] for r in sc_results)

if all_passed:
    REPORT: f"All {len(sc_results)} success criteria PASS. Issue #{N} is verified complete."
    # Keep VERIFIED_CLOSED result
elif some_passed:
    REPORT: f"Partial implementation: {sum(1 for r in sc_results if r['passed'])}/{len(sc_results)} SCs pass."
    DOWNGRADE result to: PARTIALLY_IMPLEMENTED
else:
    REPORT: f"No success criteria pass. Issue #{N} appears closed but no SCs are met."
    DOWNGRADE result to: NOT_IMPLEMENTED_DESPITE_CLOSURE
```

**Evidence requirement (ZERO TOLERANCE):** Each success criterion MUST produce a tool-call artifact (`read`, `grep`, `srclight_get_symbol`, `github_pull_request_read`, or test execution output) as evidence. Stating "I checked" without a tool call is a CRITICAL GUIDELINE VIOLATION per `065-verification-honesty.md`.

**Downgrade rules:**

| SC Verification Result | Original Result | Downgraded Result |
|------------------------|-----------------|-------------------|
| All SCs pass | VERIFIED_CLOSED | VERIFIED_CLOSED (no change) |
| Some SCs pass | VERIFIED_CLOSED | PARTIALLY_IMPLEMENTED |
| No SCs pass | VERIFIED_CLOSED | NOT_IMPLEMENTED_DESPITE_CLOSURE |
| No SCs found | VERIFIED_CLOSED | VERIFIED_CLOSED (note: SC_VERIFICATION_NOT_PERFORMED) |

**🚫 It is a CRITICAL VIOLATION to report a downgraded result as VERIFIED_CLOSED.** If any SC fails, the result MUST be downgraded. The default comparison mode is `exact` — each criterion must pass character-for-character. Use `semantic` comparison only for code behavior where multiple implementations achieve the same spec intent, and justify each semantic comparison explicitly.

### Step 8: Transitive Graph Traversal (MANDATORY)

**Verification of a single issue is insufficient.** The verified issue may be part of a graph — sub-issues, cross-references, and linked issues must also be verified for consistency. This step traverses the reachable graph from the root issue and verifies every node.

#### 8.1 Collect Adjacent Issues

From the root issue (already verified in Steps 1-7), collect all adjacent issues:

```python
adjacent = set()

# Edge type 1: Sub-issues
sub_issues = github_issue_read(method="get_sub_issues", issue_number=root_issue_number)
for sub in sub_issues:
    adjacent.add(sub["number"])

# Edge type 2: Cross-references in body
body = root_issue.get("body", "")
for pattern in [r"Spec:\s*#(\d+)", r"Plan:\s*#(\d+)", r"Implements\s*#(\d+)",
                r"Fixes\s*#(\d+)", r"Closes\s*#(\d+)", r"Related\s*#(\d+)",
                r"Duplicate\s+of\s*#(\d+)"]:
    for match in re.finditer(pattern, body):
        adjacent.add(int(match.group(1)))

# Edge type 3: Linked issues from merged PR body
if merged_pr_found:
    pr_body = pr_detail.get("body", "")
    for pattern in [r"Fixes\s*#(\d+)", r"Closes\s*#(\d+)", r"Implements\s*#(\d+)"]:
        for match in re.finditer(pattern, pr_body):
            adjacent.add(int(match.group(1)))
```

#### 8.2 Recursively Verify Each Adjacent Issue

For each issue collected, verify it (recursively) with depth limit:

```python
visited = set()
max_depth = 5

def verify_recursive(issue_number, depth):
    if issue_number in visited or depth > max_depth:
        return
    visited.add(issue_number)

    issue = github_issue_read(method="get", issue_number=issue_number)

    # If closed: verify closure (reuse Steps 1-7)
    if issue["state"] == "closed":
        result = run_steps_1_through_7(issue_number)

    # If open: check if it SHOULD be closed
    # (e.g., sub-issue of a closed parent with deliverables in merged PR)

    # Collect further adjacent issues from this node
    new_adjacent = collect_adjacent(issue_number)
    for adj in new_adjacent:
        verify_recursive(adj, depth + 1)

for adj_issue in adjacent:
    verify_recursive(adj_issue, 1)
```

#### 8.3 Graph Verification Findings

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| Open sub-issue on closed parent where PR covers deliverables | VERIFICATION-GAP | auto-close | Auto-close sub-issue with comment referencing PR via reconcile-issue-graph |
| Open sub-issue on closed parent where PR does NOT cover deliverables | VERIFICATION-GAP | flag-for-review | Sub-issue work remains — report for dev action |
| Cross-reference to open issue when parent is closed | CONFLICTING | flag-for-review | Chain incomplete — uncertain, requires dev judgment |
| Closed issue without merged PR | VERIFICATION-GAP | reopen | Reopen via reconcile-issue-graph — premature closure |
| Closed + state_reason not_planned | VERIFIED | no-action | Intentionally skipped |
| Depth limit reached | VERIFICATION-GAP | flag-for-review | Graph too deep — investigate manually |
| Cross-reference 404 | MISSING-TRACEABILITY | flag-for-review | Referenced issue does not exist |

#### 8.4 Report

After traversal, produce a graph verification report:

```
Transitive Graph Verification Report:
Root: #<root_issue>
Nodes visited: <N> (of which <M> closed, <K> open)
Max depth reached: <D>
Findings:
  - #<issue>: VERIFICATION-GAP — <description>
  ...
Overall: CONSISTENT / HAS_FLAGS
```

**Evidence requirement:** Every node in the graph MUST have a corresponding `github_issue_read` tool call artifact. Graph breadth determines the number of API calls required — this is expected and necessary for thorough verification.

## Verification Result Types

| Result | Meaning | Action for Callers |
|--------|---------|-------------------|
| `NOT_CLOSED` | Issue is still open | Not applicable — caller should treat as open issue |
| `VERIFIED_CLOSED` | Closed with merged PR evidence AND all success criteria pass | Safe to treat as legitimately closed |
| `VERIFICATION_GAP` | Closed without merged PR evidence | Do NOT trust closed state — flag for review |
| `PARTIALLY_IMPLEMENTED` | Closed + merged PR exists, but some success criteria fail verification | Include remaining work in authorization scope; do NOT autoclose |
| `NOT_IMPLEMENTED_DESPITE_CLOSURE` | Closed + merged PR exists, but NO success criteria pass verification | Reopen via reconcile-issue-graph — premature closure |
| `NOT_PLANNED_CLOSURE` | Closed as "not_planned" | Work was intentionally skipped — may need reopening |
| `DUPLICATE_OF` | Closed as duplicate of another issue | Verify target issue covers the scope |
| `BLOCKED_BY_SUB_ISSUE` | Parent cannot close because a sub-issue has a verification gap | Resolve sub-issue verification first |
| `GRAPH_HAS_FLAGS` | Graph traversal found one or more verification gaps | Resolve flagged issues or acknowledge accepted risk |
| `GRAPH_CONSISTENT` | All nodes in reachable graph are in a consistent state | Safe to treat as verified — no action needed |
| `ACTION_TAKEN` | Reconciliation took action on one or more findings (auto-closed or reopened tickets) | Process reconcile result for updated ticket states |

## Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Closed + merged PR + all SCs pass | VERIFIED | auto-proceed | Trust closed state |
| Closed + merged PR + some SCs fail | VERIFICATION-GAP | conditional | Downgrade to PARTIALLY_IMPLEMENTED; include remaining work |
| Closed + merged PR + no SCs pass | VERIFICATION-GAP | reopen | Downgrade to NOT_IMPLEMENTED_DESPITE_CLOSURE; reopen via reconcile-issue-graph |
| Closed + merged PR + no SCs found in body | VERIFIED | auto-proceed | Trust PR evidence; note SC_VERIFICATION_NOT_PERFORMED |
| Closed "completed" + no merged PR | VERIFICATION-GAP | reopen | Reopen via reconcile-issue-graph — premature closure |
| Closed "not_planned" | VERIFIED | no-action | Work intentionally skipped — do not change |
| Closed "duplicate" + target verified | VERIFIED | no-action | Duplicate properly resolved |
| Closed "duplicate" + target not found | MISSING-TRACEABILITY | flag-for-review | Cannot verify duplicate chain |
| Closed + no reason recorded | VERIFICATION-GAP | flag-for-review | Investigate closure reason — uncertain |
| Parent closed + sub-issue verification gap | VERIFICATION-GAP | flag-for-review | Resolve sub-issue first — uncertain |
| Open + merged PR exists + all SCs pass | VERIFIED | auto-close | Auto-close as completed via reconcile-issue-graph |
| Open + merged PR exists + some SCs fail | VERIFICATION-GAP | conditional | Include remaining work; do NOT auto-close |
| Open + code in repo verified + all SCs pass | VERIFIED | auto-close | Auto-close as completed via reconcile-issue-graph |

## Integration Points

This task is invoked by:

1. **`verify-authorization` Step 5.4** — Before skipping closed issues in auto-dispatch
2. **`verify-already-implemented`** — Before autoclosing as "already implemented"
3. **`pre-implementation-analysis` Step 0** — Before excluding "already implemented" issues from work set
4. **`cleanup` pre-closure gate** — Before closing parent issues in post-merge workflow
5. **`verify-fix-spec`** — Before skipping closed bug reports
6. **`reconcile-issue-graph`** — Acts on findings from graph traversal (auto-close, reopen, flag uncertain)
7. **`screen-issue` Gate 2** — Before classifying issues as "already-implemented" in screening

This task now performs transitive graph traversal (Step 8). Callers should handle `GRAPH_HAS_FLAGS` and `GRAPH_CONSISTENT` result types in addition to the single-issue result types.

## Context Required

- Issue number to verify
- `<github.owner>` and `<github.repo>` from session
- Downstream callers should handle the result type to make appropriate decisions

## Cross-References

- `000-critical-rules.md`: Assuming closed issues are verified without checking success criteria — critical violation
- `000-critical-rules.md`: Closed issues skip SC verification at agent's peril — mandatory verification
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `approval-gate/tasks/verify-authorization.md` Step 5.4: Closed-issue verification gate
- `approval-gate/tasks/verify-already-implemented.md`: Pre-autoclose sub-issue verification
- `approval-gate/tasks/screen-issue.md` Gate 2: SC verification gate for already-implemented classification
- `git-workflow/tasks/cleanup.md`: Pre-closure sub-issue verification gate
- `010-approval-gate.md §Assuming Closed Issues Are Verified`: Graph traversal prevents this violation## Enforcement References
-  Evidence format + finding classification: see `enforcement/adversarial-verification.md`
-  Scope parsing: see `enforcement/scope-parsing.md`
-  Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
-  Closed-issue verification: see `enforcement/closed-issue-verification.md`
-  Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`
