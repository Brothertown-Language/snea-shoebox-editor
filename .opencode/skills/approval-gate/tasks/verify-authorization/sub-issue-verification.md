# Task: verify-authorization — Step 5: Verify Sub-Issue Structure

## Purpose

This gate is the SINGLE AUTHORITATIVE verification point for sub-issue readiness. The `issue-operations` `link-sub-issue` task's verification logic is superseded — all sub-issue verification logic lives here.

## Procedure

### 5.1 Determine Plan Type

```
plan_issue = github_issue_read(method="get", issue_number=N)

# Check if this is a plan (has plan label or [PLAN] prefix)
is_plan = "plan" in [l["name"] for l in plan_issue["labels"]] or plan_issue["title"].startswith("[PLAN]")

if is_plan:
    # All plans use unified dispatch path (work-of-1)
    phases = parse_phases_from_plan_body(plan_issue["body"])
```

### 5.2 Verify Sub-Issues Under Plan (All Plans)

**All plans follow the unified dispatch path (work-of-1).** There is no single-task exemption — sub-issue verification applies to every plan regardless of phase count.

For all plans:

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_issue)

# Verify sub-issues exist under the plan (NOT the spec)
if not sub_issues:
    # Auto-create sub-issues under the plan
    # Plan approval covers sub-issue creation — no separate auth needed
    # See issue-operations --task link-sub-issue for creation procedure
    pass

# Verify sub-issue structure matches plan phases
for phase in phases:
    matching_sub_issue = find_sub_issue_for_phase(sub_issues, phase)
    if not matching_sub_issue:
        # HALT: sub-issue structure incomplete
        pass

# Verify sub-issue bodies contain phase context (Phase 1 enrichment)
for sub_issue in sub_issues:
    body = github_issue_read(method="get", issue_number=sub_issue["number"])["body"]
    if phase_context_insufficient(body):
        # Report: sub-issue body lacks phase context
        pass
```

### 5.2.1 Phase-Count Cross-Reference Check

For multi-task plans, verify that the number of sub-issues matches the number of phases in the plan body. A mismatch indicates incomplete sub-issue linkage. See `enforcement/sub-issue-graph-traversal.md` for the phase-count cross-reference algorithm.

**Finding Classification:**

| Finding | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Plan has N > 1 phases, sub-issues < N | STRUCTURE-VIOLATION | auto-fix | Block implementation; offer `issue-operations --task link-sub-issue` to create missing linkages |
| Plan has N > 1 phases, sub-issues >= N | VERIFIED | auto-proceed | Phase count matches; continue verification |
| Plan has 0 or 1 phases | VERIFIED | auto-proceed | Single-task plan; count check skipped |

**Evidence artifact:** `count_plan_phases()` result and `github_issue_read(method=get_sub_issues)` count MUST be recorded in the verification report.

### 5.3 Adversarial Verification of Sub-Issue State

**Before trusting any sub-issue claim, verify against actual GitHub API state.**

```
For each sub-issue:
  child = github_issue_read(method="get", issue_number=sub_issue_number)
  - Verify child.state matches claimed state (do NOT trust cache)
  - If child.state == "closed" → verify merged PR exists (not premature closure)
  - Verify child is linked under plan (NOT spec) → STRUCTURE-VIOLATION if under spec
  - Verify needs-approval label absent if parent plan has explicit authorization
```

**Evidence artifact:** `github_issue_read(method=get)` for each sub-issue showing actual state, title, labels, and parent link.

### 5.4 Closed-Issue Verification Before Skipping

Before skipping a closed issue in any workflow gate, verify it was closed for the right reason. See `enforcement/closed-issue-verification.md` for the complete closed-issue verification procedure.

**Finding Classification for Closed-Issue Verification:**

| Finding | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Closed + merged PR + criteria met | VERIFIED | auto-proceed | Skip to autoclose workflow |
| Closed + merged PR + criteria NOT met | CONFLICTING | flag-for-review | Investigation needed |
| Closed as "completed" + no merged PR | VERIFICATION-GAP | flag-for-review | Manual closure without implementation evidence |
| Closed as "not_planned" | VERIFICATION-GAP | flag-for-review | Intentionally deferred — may need reopening |
| Closed as "duplicate" | MISSING-TRACEABILITY | conditional | Verify duplicate target exists and covers scope |
| Closed state unclear (no reason) | VERIFICATION-GAP | flag-for-review | Do NOT skip — verify implementation manually |

### 5.5 Transitive Issue Graph Verification (MANDATORY on Authorization and Re-Approval)

When any issue is authorized (approved, re-approved, or `Fixes`-closed), the agent MUST traverse the entire reachable issue graph to verify every node is in a consistent state. See `enforcement/sub-issue-graph-traversal.md` for the complete traversal algorithm, edge types, depth limits, and finding classification.

**When to Traverse:**

| Trigger | When | Depth Limit |
| -- | -- | -- |
| Issue approved/re-approved | `verify-authorization` receives explicit authorization | 5 |
| Issue closed by `Fixes` keyword (post-merge) | `cleanup` processes merged PR | 5 |
| Issue being verified as already-implemented | `verify-already-implemented` encounters a closed issue | 3 |
| Issue encountered during triage | `triage` classifies a closed issue | 3 |

After traversal completes, invoke `reconcile-issue-graph` to act on findings. See `tasks/reconcile-issue-graph.md` for the reconciliation procedure.

**Every node in the reachable graph MUST produce an evidence artifact** — a `github_issue_read` tool call result. Graph traversal without per-node evidence is a verification honesty violation.

### Finding Classification for Sub-Issue Verification

| Finding | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| No sub-issues on multi-task plan | MISSING-ELEMENT | auto-create | Auto-create under plan, proceed |
| Sub-issue linked under spec (not plan) | STRUCTURE-VIOLATION | auto-fix | Re-link under correct parent |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Report — may be premature closure |
| Sub-issue needs-approval stale (parent authorized) | STRUCTURE-VIOLATION | auto-fix | Remove label |
| Sub-issue body lacks phase context | MISSING-ELEMENT | conditional | Report, fall back to plan body |
| Sub-issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve |

## Work State I/O

- **Reads from:** `## scope-auto-resolve`, `## item-decomposition-check`
- **Writes to:** `## sub-issue-verification`

After completing this task, write results to the work state file under section `## sub-issue-verification` using the YAML format defined in `enforcement/work-state-schema.md`.