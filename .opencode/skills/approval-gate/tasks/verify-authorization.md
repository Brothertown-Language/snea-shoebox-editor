# Task: verify-authorization

## Purpose

Check for explicit authorization and needs-approval label status before implementation.

## Entry Criteria

- User says "approved", "go", or similar authorization
- Spec exists as GitHub Issue

## Exit Criteria

- Authorization verified as explicit and for correct issue
- needs-approval label status checked
- Git state verified (worktree environment ready)
- Authorization recorded for scope tracking

## Procedure

### Step 0: Sub-Agent Result Guard

When `verify-authorization` is executed inline after a sub-agent dispatch returns an empty result, this step provides the fallback path.

**Trigger condition:** After dispatching a `screen-issue` or other sub-agent via `task()`, if the result is empty or whitespace-only:

```python
if not result or not result.strip():
    # Sub-agent returned empty — perform inline verification
    report_warning("Sub-agent for verify-authorization returned empty result, performing inline")
    # Execute Steps 1-6 of this verify-authorization procedure inline
    # Continue the dispatch chain as if verify-authorization completed normally
```

**Fallback execution:** When this guard activates, the agent executes the full verify-authorization procedure (Steps 1-6) inline using direct tool calls rather than dispatching another sub-agent. The inline execution follows the same steps and produces the same result contract format.

**Double-failure protocol:** If inline verification also fails:

1. Report: `"Sub-agent and inline verification both failed for verify-authorization"`
2. Invoke `--task completion` on the `approval-gate` skill
3. HALT with status message + byline

**No regression:** When sub-agent returns a valid result, this guard is not triggered — Steps 1-6 execute normally from the sub-agent's result.

### Step 0.5: Scope Auto-Resolve (MANDATORY BEFORE ANY HUMAN-FACING OUTPUT)

**This step MUST execute before Step 1, Step 2.0, and before any screen-issue dispatch.**

**The agent MUST resolve `authorization_scope` from the authorization phrase using the verb-prefix parsing table BEFORE asking any question or dispatching any sub-agent.** Scope detection is NEVER ambiguous — the parsing table is deterministic. Per `000-critical-rules.md` → "Pushing Agent Intelligence Decisions" and `020-go-prohibitions.md` §1 "ASK FIRST", scope detection via parsing table is NEVER ambiguous.

**Under NO circumstances does the agent ask the user to classify scope.** The verb-prefix parsing table in Step 2.0 is the sole authority. Every possible authorization phrase maps to exactly one scope:

| Authorization Phrase | Resolved Scope |
|----------------------|---------------|
| "approved #N" (no qualifier) | `standard` |
| "approved #N to PR" / "for PR" | `for_pr` |
| "approved #N to implementation" / "for implementation" | `for_implementation` |
| "approved #N to plan" / "for plan" | `for_plan` |
| "approved #N for review" | `for_code_review` |
| "approved #N to spec" / "for spec" | `for_spec` |

**Procedure:**

1. Parse the authorization text using the verb-prefix regex patterns from the approval-gate skill → Authorization Scope Model → Scope Detection (Verb-Prefix Parsing) table
2. If a qualifier matches, set `authorization_scope` to the corresponding scope value with `scope_source = "parsed"`
3. If no qualifier matches, set `authorization_scope = "standard"` with `scope_source = "default"`
4. Derive `halt_at`, `pr_strategy`, and `gap_fill_actions` from the resolved scope per the Authorization Scope Model
5. Record the parsed result as an evidence artifact — no human input is solicited

**Evidence artifact:** The parsed authorization text, matched regex pattern (or default fallback), and resulting `(authorization_scope, scope_source, halt_at, pr_strategy, gap_fill_actions)` tuple MUST be recorded in the verification report without soliciting human input.

### Step 1: Verify Git State (MANDATORY FIRST)

**🚫 CRITICAL: This check MUST happen BEFORE any other work.**

```bash
git branch --show-current
git status
```

**If on `main` or `dev`:** This is expected — feature branches are created in worktrees, not by switching branches in the main tree. Proceed to Step 2.

**If on a feature branch already:** Verify you're in the correct worktree. Check `worktree.path` environment variable.

**🚫 CRITICAL: Do NOT create branches directly in verify-authorization.**

Branch creation is DELEGATED to `git-workflow --task pre-work`, which creates worktrees via the `using-git-worktrees` skill. Creating branches here bypasses worktree isolation — a CRITICAL VIOLATION.

**After git state verification:**
1. Record that git state is verified
2. Proceed to Step 2 (authorization verification)
3. After ALL verification steps, invoke `git-workflow --task pre-work` for worktree creation
4. `pre-work` will handle: sync with `dev`, worktree creation, and environment variable setup

### Step 2: Verify Authorization Is Explicit

Check that authorization is:
- From user (not agent)
- Explicit ("approved", "go", "approved: N.M")
- For the CURRENT issue (not old session)

#### Step 2.0: Authorization Scope Parsing

**Parse the authorization phrase to determine scope horizon and gap-fill actions.**

Authorization phrases carry implicit scope — the pipeline stage the developer expects work to reach. The scope horizon determines where the agent MUST stop, and what intermediate artifacts are gap-filled.

##### Scope Detection (Regex-Based)

```python
import re

SCOPE_PRIORITY = [
    ("for_pr",          r"(?:to\s+PR|for\s+PR|up\s+to\s+PR|through\s+PR)\b"),
    ("for_code_review", r"(?:to\s+(?:code\s*)?review|for\s+(?:code\s*)?review|through\s+(?:code\s*)?review)\b"),
    ("for_implementation", r"(?:to\s+implementation|for\s+implementation|through\s+implementation)\b"),
    ("for_plan",        r"(?:to\s+plan|for\s+plan|through\s+plan)\b"),
    ("for_spec",        r"(?:to\s+spec|for\s+spec|through\s+spec)\b"),
    ("pr_only",         r"\bPR\s+(?:only|just)\b"),
    ("review_only",     r"\b(?:code\s*)?review\s+(?:only|just)\b"),
    ("standard",        r"\bapproved\b|\bgo\b"),
]

def parse_authorization_scope(authorization_text: str) -> dict:
    """
    Parse authorization text to determine scope horizon.
    Returns the FIRST matching scope by priority order.
    """
    text_lower = authorization_text.lower()
    for scope, pattern in SCOPE_PRIORITY:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return {
                "authorization_scope": scope,
                "scope_source": "parsed",
            }
    return {
        "authorization_scope": "standard",
        "scope_source": "default",
    }
```

##### Scope Values and Pipeline Stages

| Scope | Pipeline Stage Reached | Gap-Fill Actions | HALT After |
|-------|----------------------|------------------|------------|
| `standard` | Full pipeline | None (all artifacts must exist upfront) | After review-prep (default) |
| `for_spec` | Spec creation only | None | Spec created |
| `for_plan` | Through plan approval | Auto-create spec if missing | Plan created |
| `for_implementation` | Through implementation | Auto-create spec+plan if missing | Implementation complete |
| `for_code_review` | Through code review | Auto-create spec+plan, auto-approve plan | Review-ready |
| `for_pr` | Through PR creation | Auto-create spec+plan, auto-approve plan, auto-create PR | PR created |
| `pr_only` | PR creation only | None (assumes code exists on branch) | PR created |
| `review_only` | Code review only | None (assumes code exists) | Review posted |

##### Scope Result Fields

After parsing, add these fields to the verification result:

```yaml
authorization_scope: <scope_value>
scope_source: parsed | default
halt_at: <pipeline_stage>  # Derived from scope horizon
gap_fill_actions: [<action_list>]  # Derived from scope
pr_strategy: stacked | individual | none  # Derived from scope
```

**Evidence artifact:** The parsed authorization text, matched regex pattern, and resulting scope fields MUST be recorded in the verification report.

#### Step 2.1: Authorization Cascade by Output Lineage

When user approves issue #P, and #P's body or comments explicitly state that it created issue #C (e.g., "Spec created: #966"), authorization cascades from #P to #C if ALL conditions are met:

1. #P is a meta/investigation/review issue (no implementation criteria of its own)
2. #P's sole or primary deliverable is the creation of #C
3. #C is a spec or plan with implementation criteria
4. No contradictory evidence (e.g., #P's body says "spec rejected, try again")

When cascade applies:
- #C is treated as if the user said "Approved: #C"
- Add comment to #C: "Authorization cascaded from #P (approvable output of approved issue)"
- Remove `needs-approval` label from #C

When cascade does NOT apply (conditions not met):
- HALT and inform user: "#P was approved but it is an investigation issue — its spec #C was not named. Please confirm: approve #C?"
- This is a genuine authorization gap where the developer's intent is ambiguous

**Evidence artifact:** `github_issue_read(method=get_comments)` showing lineage evidence in #P, and `github_issue_write` / `github_add_issue_comment` responses confirming cascade actions on #C.

### Step 3: Check needs-approval Label

```python
# Get issue labels
issue = github_issue_read(method="get", issue_number=N)
has_label = "needs-approval" in [l["name"] for l in issue["labels"]]

if has_label and explicit_authorization:
    # Label is informational, NOT blocking
    # Proceed with implementation
    # Optionally note: "needs-approval label can be removed"
```

### Step 4: Record Authorization Scope

Authorization applies to:
- Specific issue only
- Current phase/task only
- This session only (no carryover)

## Critical: Explicit Authorization Priority

When user provides explicit authorization, it **OVERRIDES** the needs-approval label.

| Scenario | Action |
|----------|--------|
| "approved" AND label present | PROCEED - explicit auth wins |
| "approved" AND no label | PROCEED |
| NO auth AND label present | HALT - wait for authorization |
| NO auth AND no label | Check other blockers |

### Step 4.5: Verify Item Decomposition

**Before implementation proceeds, verify that the plan includes item-level decomposition as required by `091-incremental-build.md`.** This gate applies to ALL scopes (GREENFIELD, NEW_FEATURE, FIX, ENHANCEMENT) and ALL authorization types.

**Verification checks:**

1. **Item enumeration exists** — The plan lists every implementation unit as a discrete item with name, scope, and deliverable
2. **Dependency ordering exists** — Items are ordered so that each item's dependencies are satisfied by preceding items
3. **Acceptance criteria per item** — Each item has testable acceptance criteria that can be verified independently

**Procedure:**

```
plan_issue = github_issue_read(method="get", issue_number=plan_number)
plan_body = plan_issue["body"]

# Check for item enumeration
has_items = "Item" in plan_body and ("Dependencies" in plan_body or "Acceptance Criteria" in plan_body)

# Check for TDD step structure
has_tdd_steps = "RED" in plan_body and "GREEN" in plan_body and "COMMIT" in plan_body

if not has_items:
    # STRUCTURE-VIOLATION: No item decomposition found
    finding = "Plan lacks item decomposition — no item enumeration found"
    action = "BLOCK implementation; require plan revision with top-down item decomposition"
    severity = "STRUCTURE-VIOLATION"

if not has_tdd_steps:
    # STRUCTURE-VIOLATION: No TDD cycle defined
    finding = "Plan lacks TDD cycle definition — no RED/GREEN/COMMIT steps found"
    action = "BLOCK implementation; require plan revision with per-item TDD steps"
    severity = "STRUCTURE-VIOLATION"

# If both checks pass, proceed to Step 5
```

**Exemption:** Single-task plans (0 or 1 phases) are exempt from the item decomposition check. The check applies ONLY to multi-task plans with more than one phase.

**Cross-reference:** See `091-incremental-build.md` for the complete discipline rules, scope classification, and per-item TDD cycle.

### Step 5: Verify Sub-Issue Structure (for Plan Approval)

**This gate is the SINGLE AUTHORITATIVE verification point for sub-issue readiness.** The `issue-operations` `link-sub-issue` task's verification logic is superseded — all sub-issue verification logic lives here.

#### 5.1 Determine Plan Type

```
plan_issue = github_issue_read(method="get", issue_number=N)

# Check if this is a plan (has plan label or [PLAN] prefix)
is_plan = "plan" in [l["name"] for l in plan_issue["labels"]] or plan_issue["title"].startswith("[PLAN]")

if is_plan:
    # All plans use unified dispatch path (work-of-1)
    phases = parse_phases_from_plan_body(plan_issue["body"])
```

#### 5.2 Verify Sub-Issues Under Plan (All Plans)

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

#### 5.2.1 Phase-Count Cross-Reference Check

**For multi-task plans, verify that the number of sub-issues matches the number of phases in the plan body.** A mismatch indicates incomplete sub-issue linkage — phases exist in the plan but lack corresponding formal GitHub sub-issues.

```python
import re

def count_plan_phases(plan_body: str) -> int:
    heading_patterns = [
        r"^###\s+Phase\s+\d+",
        r"^####\s+Task\s+\d+",
        r"^##\s+Phase\s+\d+",
    ]
    phase_count = 0
    for line in plan_body.splitlines():
        for pattern in heading_patterns:
            if re.match(pattern, line.strip()):
                phase_count += 1
                break
    return phase_count

expected_phases = count_plan_phases(plan_body)
actual_sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_issue)
actual_count = len(actual_sub_issues)

if expected_phases > 1 and actual_count < expected_phases:
    # STRUCTURE-VIOLATION: Plan has N phases but fewer than N sub-issues
    # Block implementation and offer remediation
    findings.append({
        "finding": f"Plan has {expected_phases} phases but only {actual_count} sub-issues",
        "problem_class": "STRUCTURE-VIOLATION",
        "classification": "auto-fix",
        "action": "block_implementation",
        "remediation": "issue-operations --task link-sub-issue"
    })
elif expected_phases <= 1:
    # Single-task plan — skip count check, pass
    pass
```

**Finding Classification:**

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| Plan has N > 1 phases, sub-issues < N | STRUCTURE-VIOLATION | auto-fix | Block implementation; offer `issue-operations --task link-sub-issue` to create missing linkages |
| Plan has N > 1 phases, sub-issues >= N | VERIFIED | auto-proceed | Phase count matches; continue verification |
| Plan has 0 or 1 phases | VERIFIED | auto-proceed | Single-task plan; count check skipped |

**Evidence artifact:** `count_plan_phases()` result and `github_issue_read(method=get_sub_issues)` count MUST be recorded in the verification report.

#### 5.3 Adversarial Verification of Sub-Issue State

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

#### 5.4 Closed-Issue Verification Before Skipping

**Before skipping a closed issue in any workflow gate (already-implemented, already-handled, auto-dispatch), verify it was closed for the right reason. A closed state alone does NOT mean work is done.**

```
For each closed issue encountered during verification:
  issue = github_issue_read(method="get", issue_number=closed_issue_number)

  if issue.state == "closed":
    # CRITICAL: Do NOT assume closed = verified. Verify closure reason.

    # Check 1: Was it closed via merged PR?
    # Search for PRs referencing this issue
    prs = github_search_pull_requests(query=f"Fixes #{closed_issue_number} repo:{<github.owner>}/{<github.repo>}")
    merged_pr_found = False
    for pr in prs:
      pr_detail = github_pull_request_read(method="get", owner=<github.owner>, repo=<github.repo>, pullNumber=pr["number"])
      if pr_detail.get("merged_at") is not None:
        merged_pr_found = True
        break

    # Check 2: Was it closed as "not planned" or duplicate?
    state_reason = issue.get("state_reason", "")
    if state_reason == "not_planned":
      # Issue was intentionally not implemented — may still need implementation
      # Do NOT skip; treat as if the issue were open for verification purposes
      VERIFICATION-GAP — flag-for-review
    elif state_reason == "completed" and not merged_pr_found:
      # Closed as "completed" but no merged PR found
      # May have been closed manually without implementation
      VERIFICATION-GAP — flag-for-review
    elif state_reason == "completed" and merged_pr_found:
      # Closed as "completed" with merged PR — legitimate closure
      # Verify success criteria are actually met (see verify-already-implemented)
      PROCEED to verify-already-implemented
    else:
      # State reason unclear or missing
      VERIFICATION-GAP — flag-for-review
```

**Closed-Issue Verification Gate for Auto-Dispatch:**

The "Already implemented" row in the Auto-Dispatch table (Step 6) MUST NOT skip a closed issue without this verification gate passing. Update auto-dispatch logic:

```
# In auto-dispatch, when detect "already implemented":
# 1. Run closed-issue verification (Step 5.4)
# 2. If verification confirms legitimate closure (merged PR + success criteria met):
#    → Proceed to verify-already-implemented → autoclose if all criteria pass
# 3. If verification finds closure without merged PR:
#    → flag-for-review, do NOT autoclose
# 4. If verification finds "not_planned" closure:
#    → flag-for-review, treat as open for implementation purposes
```

**Finding Classification for Closed-Issue Verification:**

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| Closed + merged PR + criteria met | VERIFIED | auto-proceed | Skip to autoclose workflow |
| Closed + merged PR + criteria NOT met | CONFLICTING | flag-for-review | Investigation needed — PR may not cover full scope |
| Closed as "completed" + no merged PR | VERIFICATION-GAP | flag-for-review | Manual closure without implementation evidence |
| Closed as "not_planned" | VERIFICATION-GAP | flag-for-review | Intentionally deferred — may need reopening |
| Closed as "duplicate" | MISSING-TRACEABILITY | conditional | Verify duplicate target exists and covers scope |
| Closed state unclear (no reason) | VERIFICATION-GAP | flag-for-review | Do NOT skip — verify implementation manually |

#### 5.5 Transitive Issue Graph Verification (MANDATORY on Authorization and Re-Approval)

**When any issue is authorized (approved, re-approved, or `Fixes`-closed), the agent MUST traverse the entire reachable issue graph to verify every node is in a consistent state.** Single-issue verification is insufficient — an authorized issue may have open sub-issues, dangling cross-references, or linked issues in an inconsistent state.

##### Three Edge Types Traversed

| Edge Type | Source | Example | API Access |
|-----------|--------|---------|------------|
| **Sub-issue** | GitHub sub-issue link | Plan → Phase sub-issue | `github_issue_read(method=get_sub_issues, issue_number=N)` |
| **Cross-reference** | Issue body references | `Spec: #M`, `Plan: #N`, `Implements #K` | Parse body text + `github_issue_read(method=get, issue_number=M)` |
| **Linked issue** | PR/closure references | `Fixes #N`, `Closes #N`, `Related #N` | Parse body text + `github_issue_read(method=get, issue_number=N)` |

##### Graph Traversal Algorithm

```python
def traverse_issue_graph(root_issue_number, depth_limit=5):
    """
    Transitively traverse the issue graph from a root issue.
    Follows sub-issue, cross-reference, and linked-issue edges.
    Returns a verification report for every node in the reachable graph.
    """
    visited = set()
    queue = [(root_issue_number, 0)]  # (issue_number, current_depth)
    findings = []

    while queue:
        issue_number, depth = queue.pop(0)

        if issue_number in visited:
            continue
        visited.add(issue_number)

        if depth > depth_limit:
            findings.append({
                "issue": issue_number,
                "depth": depth,
                "result": "DEPTH_LIMIT_REACHED",
                "action": "flag-for-review"
            })
            continue

        # Step 1: Read the issue
        issue = github_issue_read(method="get", issue_number=issue_number)

        # Step 2: Verify the issue's state
        # (reuse verify-closed-issue logic for closed issues)
        if issue["state"] == "closed":
            # Run closed-issue verification (Steps 1-6 of verify-closed-issue)
            # Record finding
            pass

        # Step 3: Follow sub-issue edges
        sub_issues = github_issue_read(method="get_sub_issues", issue_number=issue_number)
        for sub in sub_issues:
            queue.append((sub["number"], depth + 1))

        # Step 4: Parse body for cross-references
        body = issue.get("body", "")
        for pattern in [r"Spec:\s*#(\d+)", r"Plan:\s*#(\d+)", r"Implements\s*#(\d+)",
                        r"Fixes\s*#(\d+)", r"Closes\s*#(\d+)", r"Related\s*#(\d+)",
                        r"Duplicate\s+of\s*#(\d+)"]:
            for match in re.finditer(pattern, body):
                ref_num = int(match.group(1))
                if ref_num not in visited:
                    queue.append((ref_num, depth + 1))

    return findings

# After traversal completes:
findings = traverse_issue_graph(root_issue_number)

# INVOKE reconcile-issue-graph to act on findings
# (previously, findings were only reported as flag-for-review)
reconcile_result = reconcile_issue_graph(
    root_issue_number=root_issue_number,
    findings=findings,
    GitOwner=GitOwner,
    GitRepo=GitRepo
)
```

##### When to Traverse

| Trigger | When | Depth Limit |
|---------|------|-------------|
| Issue approved/re-approved | `verify-authorization` receives explicit authorization | 5 |
| Issue closed by `Fixes` keyword (post-merge) | `cleanup` processes merged PR | 5 |
| Issue being verified as already-implemented | `verify-already-implemented` encounters a closed issue | 3 |
| Issue encountered during triage | `triage` classifies a closed issue | 3 |

##### Finding Classification for Graph Verification

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| All nodes verified (closed with merged PR or open and consistent) | VERIFIED | auto-proceed | Graph is consistent |
| Open + merged PR exists | VERIFIED | auto-close | Auto-close as completed via reconcile-issue-graph |
| Open + code in repo verified | VERIFIED | auto-close | Auto-close as completed via reconcile-issue-graph |
| Closed + no merged PR + code NOT in repo | VERIFICATION-GAP | reopen | Reopen as open via reconcile-issue-graph |
| Open sub-issue on closed parent | VERIFICATION-GAP | flag-for-review | Parent closure may be premature — uncertain, requires dev judgment |
| Cross-reference to open/closed mismatch | CONFLICTING | flag-for-review | Spec closed but plan open, or vice versa — uncertain |
| Sub-issue closed without merged PR | VERIFICATION-GAP | reopen | Reopen via reconcile-issue-graph |
| Closed + state_reason not_planned | VERIFIED | no-action | Intentionally skipped — do not change |
| Closed + state_reason duplicate + target OK | VERIFIED | no-action | Duplicate properly resolved |
| Depth limit reached | VERIFICATION-GAP | flag-for-review | Graph too deep — investigate manually |
| Cross-reference 404 | MISSING-TRACEABILITY | flag-for-review | Referenced issue does not exist |
| Cannot determine | CONFLICTING | flag-for-review | Conflicting signals — report for dev action |

##### Evidence Requirement

Every node in the reachable graph MUST produce an evidence artifact — a `github_issue_read` tool call result. Graph traversal without per-node evidence is a verification honesty violation.

**Report format:**

```
Issue Graph Verification Report for #<root>
Nodes visited: <N>
Max depth: <D>
Findings:
  - #<issue>: <state> — <finding> (<classification>)
  ...
Reconciliation: (via reconcile-issue-graph)
  Auto-closed: #<n1> (merged PR #<pr1>), #<n2> (code verified)
  Reopened: #<n3> (no merged PR, code not in repo)
  No action: #<n5> (not_planned), #<n6> (duplicate of #<n7>)
  Requires dev action: (if uncertain findings remain)
    - #<n8>: current=<state>, needed=<state> — <reason>
Overall: CONSISTENT / HAS_FLAGS / RECONCILED
```

#### Finding Classification for Sub-Issue Verification

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| No sub-issues on multi-task plan | MISSING-ELEMENT | auto-create | Auto-create under plan, proceed |
| Sub-issue linked under spec (not plan) | STRUCTURE-VIOLATION | auto-fix | Re-link under correct parent |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Report — may be premature closure |
| Sub-issue needs-approval stale (parent authorized) | STRUCTURE-VIOLATION | auto-fix | Remove label |
| Sub-issue body lacks phase context | MISSING-ELEMENT | conditional | Report, fall back to plan body |
| Sub-issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve |

### Step 5b: Spec-to-Plan Approval Cascade

**When a spec is approved and a plan already exists for that spec, the plan inherits the spec's approval status.** This eliminates the redundant second approval step when a plan faithfully implements an already-approved spec.

#### 5b.1 Detect Approval Cascade Conditions

This step runs ONLY when the approved issue is a spec (detected in Step 5 Auto-Dispatch context differentiation).

```python
# Determine if this is a spec approval
is_spec = "spec" in [l["name"] for l in issue["labels"]] or issue["title"].startswith("[SPEC")

if not is_spec:
    # Skip cascade — only applies to spec approvals
    proceed to Step 6

# Search for plans referencing this spec
spec_number = issue["number"]
plan_issues = github_search_issues(
    query=f"open label:plan Spec: #{spec_number} repo:{<github.owner>}/{<github.repo>}"
)
```

#### 5b.2 Process Cascade Approval

If one or more plans reference the approved spec:

```python
if plan_issues:
    # Multiple plans: approve the most recent, supersede the rest
    if len(plan_issues) > 1:
        # Sort by creation date, most recent first
        plan_issues.sort(key=lambda p: p["created_at"], reverse=True)
        most_recent = plan_issues[0]
        older_plans = plan_issues[1:]

        # Cascade-approve the most recent plan
        github_issue_write(
            method="update",
            issue_number=most_recent["number"],
            labels=[l for l in most_recent["labels"] if l != "needs-approval"],
        )
        github_add_issue_comment(
            issue_number=most_recent["number"],
            body="Approval cascaded from spec #{spec_number}. Plan approved automatically because spec is already approved and this is the most recent plan referencing it.",
        )

        # Supersede older plans
        for old_plan in older_plans:
            github_add_issue_comment(
                issue_number=old_plan["number"],
                body="Superseded by #{most_recent_number} — cascade approval applies to the most recent plan only.",
            )

    else:
        # Single plan: cascade-approve it
        plan_issue = plan_issues[0]
        github_issue_write(
            method="update",
            issue_number=plan_issue["number"],
            labels=[l for l in plan_issue["labels"] if l != "needs-approval"],
        )
        github_add_issue_comment(
            issue_number=plan_issue["number"],
            body="Approval cascaded from spec #{spec_number}. Plan approved automatically because spec is already approved.",
        )

elif not plan_issues:
    # No plan exists — cascade does NOT apply
    # Current flow is correct: spec approval → writing-plans create → plan needs approval
    proceed to Step 6 (auto-dispatch to writing-plans)
```

#### 5b.3 Cascade Does NOT Apply When

- The approved issue is a plan (not a spec) — cascade is spec-to-plan only
- No plan exists for the spec — current flow is correct, writing-plans will create a new plan
- The spec has been revised — existing revocation rules apply; cascade approval is revoked per Step 6 "Spec Revision Revocation Detection"
- The plan does not faithfully implement the spec — `plan-fidelity-auditor` catches this during implementation review

#### 5b.4 Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Multiple plans for same spec | Cascade approves the most recent plan by creation date; older plans are superseded |
| Plan created after spec approval | Handled by `writing-plans --task create` post-creation step (see writing-plans tasks/create.md) |
| Spec revised after cascade | Existing revocation rules apply — see Step 6 "Spec Revision Revocation Detection" |
| No plan exists | Cascade does NOT apply; current flow (spec approval → writing-plans) is correct |
| Plan already approved (no `needs-approval` label) | No action needed — plan is already approved |

**Evidence artifact:** `github_search_issues` response showing plan issues referencing the spec, and `github_issue_write` response confirming label removal and comment posting.

### Step 5c: Scope-Aware Gap-Fill Cascade

**When `authorization_scope` from Step 2.0 is >= `for_plan`, missing intermediate artifacts are gap-filled automatically.** This eliminates the "catch-22" where pipeline authorization says "go to PR" but the plan doesn't exist yet — the scope horizon authorizes its creation.

#### 5c.1 Detect Scope Horizon

```python
SCOPE_HORIZON = {
    "standard":         "review_prep",
    "for_spec":         "spec_created",
    "for_plan":         "plan_created",
    "for_implementation": "implementation_complete",
    "for_code_review":  "code_review_ready",
    "for_pr":           "pr_created",
    "pr_only":          "pr_created",
    "review_only":      "code_review_ready",
}

# From Step 2.0 result
scope = verification_result["authorization_scope"]
halt_at = SCOPE_HORIZON[scope]
```

#### 5c.2 Gap-Fill Actions by Scope

```python
GAP_FILL = {
    "for_spec": [],  # Spec is the target; no upstream gap
    "for_plan": ["auto_create_spec"],  # Missing spec is gap-filled
    "for_implementation": ["auto_create_spec", "auto_create_plan", "auto_approve_plan"],
    "for_code_review": ["auto_create_spec", "auto_create_plan", "auto_approve_plan"],
    "for_pr": ["auto_create_spec", "auto_create_plan", "auto_approve_plan", "auto_create_pr"],
    "pr_only": [],  # Assumes branch exists; no gap-fill
    "review_only": [],  # Assumes code exists; no gap-fill
    "standard": [],  # No gap-fill; all artifacts must pre-exist
}
```

#### 5c.3 Execute Gap-Fill

```python
def execute_gap_fill(scope, issue_number, issue_labels, issue_title):
    """Auto-create missing artifacts when scope authorizes it."""
    actions = GAP_FILL.get(scope, [])
    results = []

    if "auto_create_spec" in actions:
        # Check if spec already exists
        is_spec = "spec" in [l["name"] for l in issue_labels] or issue_title.startswith("[SPEC")
        if not is_spec:
            # Invoke brainstorming --task explore to create spec
            results.append({"action": "auto_create_spec", "status": "dispatched", "target": "brainstorming"})
        else:
            results.append({"action": "auto_create_spec", "status": "skipped", "reason": "spec_exists"})

    if "auto_create_plan" in actions:
        # Check if plan already exists
        is_plan = "plan" in [l["name"] for l in issue_labels] or issue_title.startswith("[PLAN]")
        if not is_plan:
            # Invoke writing-plans --task create to create plan
            # Plan auto-approval handled by writing-plans scope awareness
            results.append({"action": "auto_create_plan", "status": "dispatched", "target": "writing-plans"})
        else:
            results.append({"action": "auto_create_plan", "status": "skipped", "reason": "plan_exists"})

    if "auto_approve_plan" in actions:
        # Cascade approval already handled by Step 5b for existing plans
        # For gap-filled plans, writing-plans auto-approves when scope >= for_plan
        results.append({"action": "auto_approve_plan", "status": "delegated", "target": "writing-plans"})

    if "auto_create_pr" in actions:
        # PR creation is handled by git-workflow scope awareness after implementation
        results.append({"action": "auto_create_pr", "status": "deferred", "target": "git-workflow"})

    return results
```

#### 5c.4 PR Strategy Determination

PR strategy is derived from scope, NOT from issue count:

```python
PR_STRATEGY = {
    "standard":         "individual",   # Separate PR per issue
    "for_spec":         "none",         # Spec creation only, no PR
    "for_plan":         "none",         # Plan creation only, no PR
    "for_implementation": "individual",  # Implementation done, standard PR
    "for_code_review":  "individual",   # Code review needs PR
    "for_pr":           "stacked",      # Single stacked PR for all issues
    "pr_only":          "stacked",      # Single PR for existing code
    "review_only":      "individual",   # Review existing PRs
}
```

**Evidence artifact:** Gap-fill actions dispatched, their results, and the derived PR strategy MUST be recorded in the verification report.

### Step 6: Scope-Aware Auto-Dispatch After Successful Verification

**🚫 CRITICAL: This step runs ONLY when ALL prior verification gates (Steps 1-5) pass. If ANY gate fails, HALT — do NOT dispatch.**

#### 6.1 Pre-Implementation Worktree Setup (MANDATORY)

**Before any sub-agent dispatch or file modification, the agent MUST invoke `git-workflow --task pre-work` to:**

1. Create the feature branch in a worktree (`.worktrees/`)
2. Set the `worktree.path` environment variable
3. Verify branch state and working tree cleanliness

**This step is MANDATORY and CANNOT be skipped.** If the worktree already exists from a previous session, verify it and proceed. If worktree creation fails, HALT — do not proceed without a valid worktree.

**Evidence requirement:** `git worktree list` must show the feature branch worktree, and `worktree.path` must be set before any `divide-and-conquer` dispatch.

After all verification gates pass, determine the approval context and auto-dispatch:

#### Auto-Dispatch Context Differentiation

| Approval Context | How to Detect | Auto-Dispatch Target |
|------------------|---------------|----------------------|
| **Spec approval** | Issue title contains `[SPEC` or has `spec` label | `writing-plans --task create` (or `brainstorming --task explore` if gap-fill) |
| **Plan approval** | Issue has `plan` label or `[PLAN]` prefix in title | `executing-plans --task start` |
| **Already implemented** | `verify-already-implemented` returns positive (after closed-issue verification in Step 5.4 confirms legitimate closure) | No dispatch — auto-close instead |
| **Reconciled during verification** | reconcile-issue-graph returned auto-closed or reopened tickets | Include reconciled tickets in chat output; proceed with dispatch |
| **Closed but NOT verified** | Step 5.4 closed-issue verification finds closure without merged PR evidence | flag-for-review — do NOT autoclose |

#### Scope-Aware Dispatch Targets

The dispatch target is modified by `authorization_scope` from Step 2.0:

| Scope | Dispatch Target | HALT After |
|-------|----------------|------------|
| `standard` | Existing dispatch path (spec→writing-plans, plan→executing-plans) | After review-prep (default) |
| `for_spec` | `brainstorming --task explore` (gap-fill: create spec) | Spec created |
| `for_plan` | `brainstorming --task explore` then `writing-plans --task create` | Plan created |
| `for_implementation` | Full pipeline (gap-fill spec+plan, then executing-plans) | Implementation complete |
| `for_code_review` | Full pipeline through implementation | Code review ready |
| `for_pr` | Full pipeline through PR creation | PR created |
| `pr_only` | `git-workflow --task pr-creation` (skip implementation) | PR created |
| `review_only` | `requesting-code-review` (skip implementation) | Review posted |

**🚫 HARD HALT AT SCOPE BOUNDARY:** The agent MUST NOT proceed past the pipeline stage specified by `halt_at`. If the dispatch chain reaches the `halt_at` stage, the agent reports completion and STOPS. Proceeding past `halt_at` without re-authorization is a CRITICAL GUIDELINE VIOLATION.

#### Auto-Dispatch Procedure

1. Determine approval context (spec vs plan) by checking:
   - Issue title format: `[SPEC` prefix = spec approval
   - Issue title format: `[PLAN]` prefix = plan approval
   - Labels: presence of `spec` or `plan` labels
   - Plan detection is via `plan` label or `[PLAN]` prefix in title (NOT via sub-issue relationship to spec)
2. Determine scope from Step 2.0 result (`authorization_scope`, `halt_at`, `pr_strategy`)
3. Execute gap-fill from Step 5c if scope >= `for_plan`
4. **If spec approval:** Invoke `writing-plans --task create` with context:
   - `spec_issue=#N` (the approved spec issue number)
   - `authorization_scope=<scope>` and `halt_at=<stage>`
   - `<github.owner>`, `<github.repo>`, `<worktree.path>` from session
5. **If plan approval:** Invoke `executing-plans --task start` with context:
   - `plan_issue=#N` (the approved plan issue number)
   - `spec_issue=#M` (extracted from plan body — the spec reference)
   - `authorization_scope=<scope>`, `halt_at=<stage>`, `pr_strategy=<strategy>`
   - `<github.owner>`, `<github.repo>`, `<worktree.path>` from session
6. **Chat output:** Clearly indicate the transition and scope:
   - Spec approval: "Verification passed → Creating implementation plan (scope: <scope>)"
   - Plan approval: "Verification passed → Starting implementation (scope: <scope>, halt_at: <stage>)"

#### Spec Revision Revocation Detection

If a spec is revised (status contains `REVISED - NEEDS APPROVAL` — in either prose or numeric format):

Prose format: `STATUS: in progress — {concern} (REVISED - NEEDS APPROVAL)`
Numeric format: `STATUS: 1.1 (REVISED - NEEDS APPROVAL)`

1. Search for `[PLAN]` issues that reference the spec number in their body
2. Mark found plans for audit (their authorization is revoked by the spec revision)
3. Report affected plans in chat output

#### Auto-Dispatch Edge Cases

- **Spec already has a plan:** `writing-plans --task create` handles this (skips or updates per its existing logic)
- **Multi-task plan with missing sub-issues:** Step 5 sub-issue verification gate fails → HALT, no dispatch
- **Authorization set dispatch:** Each plan in the work set gets its own dispatch cycle after work state is established
- **Scope requires gap-fill but artifact exists:** Skip gap-fill for that artifact (check before creating)
- **`pr_only` or `review_only` scope with no existing branch/PR:** HALT and report — these scopes assume existing work

### Step 2.5: Adversarial Verification — Verify Authorization Against Actual State

**🚫 CRITICAL: Before trusting any authorization claim, verify it against actual GitHub state. Do NOT rely on cached values, assumed labels, or claimed authorization without direct evidence.**

#### 2.5.1 Verify Author Identity

```
comments = github_issue_read(method="get_comments", issue_number=N)

For each comment claiming "approved", "go", or "approved: X.Y":
  - Verify comment author is a developer (not bot/agent)
  - Check author_association: "MEMBER", "OWNER", or "COLLABORATOR" = human developer
  - Check author_association: "FIRST_TIME_CONTRIBUTOR", "NONE" = not authorized
  - Bot/agent comments (login contains "[bot]") are NOT authorization
```

**Evidence artifact:** `github_issue_read(method=get_comments)` response showing author details for the authorization comment.

#### 2.5.2 Verify Authorization Scope

```
For each valid authorization comment found:
  - Does the comment scope match the current issue number?
  - "approved #N" where N ≠ current issue → NOT scoped to this issue
  - "approved" without issue number → scoped to the issue where it appears
  - "go" without issue number → scoped to the issue where it appears
```

**Evidence artifact:** Comment text and issue number showing scope match or mismatch.

#### 2.5.3 Verify Authorization Currency

```
comments = github_issue_read(method="get_comments", issue_number=N)

For each authorization comment:
  - Compare comment timestamp against spec revision history
  - If spec body was edited AFTER the authorization comment → authorization may be stale
  - Check for "REVISED - NEEDS APPROVAL" in spec body → authorization is revoked
  - If authorization comment is the most recent relevant comment → current
```

**Evidence artifact:** Comparison of authorization comment timestamp vs spec update timestamp.

#### 2.5.4 Verify Sub-Issue State

```
For plan issues (detected in Step 5):
  sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)
  
  For each sub-issue:
    - Verify state matches claimed state (open/closed) via API
    - Do NOT trust cached or previously-read sub-issue state
    - If sub-issue state is "closed" but no merged PR → VERIFICATION-GAP (flag-for-review)
```

**Evidence artifact:** `github_issue_read(method=get_sub_issues)` response showing actual state of each sub-issue.

#### Finding Classification for Authorization Verification

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| Authorization from bot/agent | CONFLICTING | flag-for-review | Reject as authorization source |
| Authorization scoped to different issue | CONFLICTING | flag-for-review | Reject — not scoped to current issue |
| Authorization superseded by revision | STRUCTURE-VIOLATION | auto-fix | Mark authorization as stale, require re-approval |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Report — may be premature closure |
| `needs-approval` label stale (auth exists) | MISSING-ELEMENT | conditional | Remove label after verifying auth scope |
| STATUS marker mismatched to content | STRUCTURE-VIOLATION | auto-fix | Update STATUS to reflect actual maturity |

## Context Required

- Related tasks: `verify-sub-issues` (delegated sub-issue verification detail), `verify-codebase`
- Sub-issue verification gate: This task (Step 5) is the SINGLE AUTHORITATIVE verification point. `issue-operations` `link-sub-issue` verification logic is superseded by this gate.
- Auto-dispatch targets: `writing-plans` (spec approval), `executing-plans` (plan approval)
- Dispatch context for plan approval: pass `plan_issue=#N` and `spec_issue=#M` (extracted from plan body)
- Label state machine: `141-planning-status-tracking.md §10` (remove `needs-approval`, add `in-progress` on approval)
- Adversarial verification model: `spec-auditor --task ground-truth` (finding classification and evidence artifacts)