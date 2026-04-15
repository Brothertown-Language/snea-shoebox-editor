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

### Step 1: Verify Git State (MANDATORY FIRST)

**🚫 CRITICAL: This check MUST happen BEFORE any other work.**

```bash
git branch --show-current
git status
```

**If on `main` or `dev`:** This is expected — feature branches are created in worktrees, not by switching branches in the main tree. Proceed to Step 2.

**If on a feature branch already:** Verify you're in the correct worktree. Check `WORKTREE_PATH` environment variable.

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

### Step 5: Verify Sub-Issue Structure (for Plan Approval)

**This gate is the SINGLE AUTHORITATIVE verification point for sub-issue readiness.** The `github-sub-issues` skill's verification gate is superseded — all sub-issue verification logic lives here.

#### 5.1 Determine Plan Type

```
plan_issue = github_issue_read(method="get", issue_number=N)

# Check if this is a plan (has plan label or [PLAN] prefix)
is_plan = "plan" in [l["name"] for l in plan_issue["labels"]] or plan_issue["title"].startswith("[PLAN]")

if is_plan:
    # Determine single-task vs multi-task
    phases = parse_phases_from_plan_body(plan_issue["body"])
    is_single_task = len(phases) == 1
```

#### 5.2 Verify Sub-Issues Under Plan (Multi-Task Only)

**Single-task exemption:** If the plan has exactly ONE implementation phase with no decomposition, skip sub-issue verification entirely.

For multi-task plans:

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=plan_issue)

# Verify sub-issues exist under the plan (NOT the spec)
if not sub_issues:
    # Auto-create sub-issues under the plan
    # Plan approval covers sub-issue creation — no separate auth needed
    # See github-sub-issues --task create-sub-issue for creation procedure
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
    query=f"open label:plan Spec: #{spec_number} repo:{GIT_OWNER}/{GIT_REPO}"
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

### Step 6: Auto-Dispatch After Successful Verification

**🚫 CRITICAL: This step runs ONLY when ALL prior verification gates (Steps 1-5) pass. If ANY gate fails, HALT — do NOT dispatch.**

#### 6.1 Pre-Implementation Worktree Setup (MANDATORY)

**Before any sub-agent dispatch or file modification, the agent MUST invoke `git-workflow --task pre-work` to:**

1. Create the feature branch in a worktree (`.worktrees/`)
2. Set the `WORKTREE_PATH` environment variable
3. Verify branch state and working tree cleanliness

**This step is MANDATORY and CANNOT be skipped.** If the worktree already exists from a previous session, verify it and proceed. If worktree creation fails, HALT — do not proceed without a valid worktree.

**Evidence requirement:** `git worktree list` must show the feature branch worktree, and `WORKTREE_PATH` must be set before any `divide-and-conquer` dispatch.

After all verification gates pass, determine the approval context and auto-dispatch:

#### Auto-Dispatch Context Differentiation

| Approval Context | How to Detect | Auto-Dispatch Target |
|------------------|---------------|----------------------|
| **Spec approval** | Issue title contains `[SPEC` or has `spec` label | `writing-plans --task create` |
| **Plan approval** | Issue has `plan` label or `[PLAN]` prefix in title | `executing-plans --task start` |
| **Already implemented** | `verify-already-implemented` returns positive | No dispatch — auto-close instead |

#### Auto-Dispatch Procedure

1. Determine approval context (spec vs plan) by checking:
   - Issue title format: `[SPEC` prefix = spec approval
   - Issue title format: `[PLAN]` prefix = plan approval
   - Labels: presence of `spec` or `plan` labels
   - Plan detection is via `plan` label or `[PLAN]` prefix in title (NOT via sub-issue relationship to spec)
2. **If spec approval:** Invoke `writing-plans --task create` with context:
   - `spec_issue=#N` (the approved spec issue number)
   - `GIT_OWNER`, `GIT_REPO`, `WORKTREE_PATH` from session
3. **If plan approval:** Invoke `executing-plans --task start` with context:
   - `plan_issue=#N` (the approved plan issue number)
   - `spec_issue=#M` (extracted from plan body — the spec reference)
   - `GIT_OWNER`, `GIT_REPO`, `WORKTREE_PATH` from session
4. **Chat output:** Clearly indicate the transition:
   - Spec approval: "Verification passed → Creating implementation plan"
   - Plan approval: "Verification passed → Starting implementation"

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
- **Batch approval:** Each plan in batch gets its own dispatch cycle after batch state is established

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
- Sub-issue verification gate: This task (Step 5) is the SINGLE AUTHORITATIVE verification point. `github-sub-issues` skill's verification gate is superseded by this gate.
- Auto-dispatch targets: `writing-plans` (spec approval), `executing-plans` (plan approval)
- Dispatch context for plan approval: pass `plan_issue=#N` and `spec_issue=#M` (extracted from plan body)
- Label state machine: `141-planning-status-tracking.md §10` (remove `needs-approval`, add `in-progress` on approval)
- Adversarial verification model: `spec-auditor --task ground-truth` (finding classification and evidence artifacts)