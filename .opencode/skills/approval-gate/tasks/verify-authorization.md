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

Parse the authorization text to determine scope horizon and gap-fill actions. Scope detection is NEVER ambiguous — the parsing table is deterministic. The agent MUST NOT ask the user to classify scope.

→ **Full procedure:** See `tasks/verify-authorization/scope-auto-resolve.md`

### Step 1: Verify Git State (MANDATORY FIRST)

**🚫 CRITICAL: This check MUST happen BEFORE any other work.**

```bash
git branch --show-current
git status
```

**If on `main` or `dev`:** This is expected — feature branches are created in worktrees, not by switching branches in the main tree. Proceed to Step 2.

**If on a feature branch already:** Verify you're in the correct worktree. Check `worktree.path` environment variable.

**🚫 CRITICAL: Do NOT create branches directly in verify-authorization.** Branch creation is DELEGATED to `git-workflow --task pre-work`, which creates worktrees via the `using-git-worktrees` skill. Creating branches here bypasses worktree isolation — a CRITICAL VIOLATION.

**After git state verification:**

1. Record that git state is verified
2. Proceed to Step 2 (authorization verification)
3. After ALL verification steps, invoke `git-workflow --task pre-work` for worktree creation
4. `pre-work` will handle: sync with `dev`, worktree creation, and environment variable setup

### Step 2: Verify Authorization Is Explicit

Check that authorization is:

- From user (not agent)
- Explicit ("approved", "go", "approved: N.M")
- for the CURRENT issue (not old session)

#### Step 2.0: Authorization Scope Parsing

Parse the authorization phrase to determine scope horizon and gap-fill actions.

→ **Scope detection regex and values:** See `enforcement/scope-parsing.md`
→ **Auto-dispatch routing:** See `enforcement/auto-dispatch-table.md`

Authorization phrases carry implicit scope — the pipeline stage the developer expects work to reach. The scope horizon determines where the agent MUST stop, and what intermediate artifacts are gap-filled.

**Evidence artifact:** The parsed authorization text, matched regex pattern, and resulting scope fields MUST be recorded in the verification report.

#### Step 2.1: Authorization Cascade by Output Lineage

→ **Full procedure:** See `tasks/verify-authorization/auto-dispatch.md` → "Authorization Cascade by Output Lineage"

### Step 2.5: Adversarial Verification — Verify Authorization Against Actual State

**🚫 CRITICAL: Before trusting any authorization claim, verify it against actual GitHub state. Do NOT rely on cached values, assumed labels, or claimed authorization without direct evidence.**

→ **Evidence format and three-tier classification:** See `enforcement/adversarial-verification.md`

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
| -- | -- | -- | -- |
| Authorization from bot/agent | CONFLICTING | flag-for-review | Reject as authorization source |
| Authorization scoped to different issue | CONFLICTING | flag-for-review | Reject — not scoped to current issue |
| Authorization superseded by revision | STRUCTURE-VIOLATION | auto-fix | Mark authorization as stale, require re-approval |

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

## Critical: Explicit Authorization Priority

When user provides explicit authorization, it **OVERRIDES** the needs-approval label.

| Scenario | Action |
| -- | -- |
| "approved" AND label present | PROCEED - explicit auth wins |
| "approved" AND no label | PROCEED |
| NO auth AND label present | HALT - wait for authorization |
| NO auth AND no label | Check other blockers |

### Step 4: Record Authorization Scope

Authorization applies to:

- Specific issue only
- Current phase/task only
- This session only (no carryover)

### Step 4.5: Verify Item Decomposition and Behavioral Test Coverage

Before implementation proceeds, verify that the plan includes item-level decomposition AND that items which change agent behavior (rule/guideline changes) have behavioral enforcement test coverage.

→ **Full procedure:** See `tasks/verify-authorization/item-decomposition-check.md`

In addition to the decomposition checks in the sub-task file, this step verifies:

- **For each plan item that changes a rule governing agent behavior** (guideline text, skill enforcement, critical violation, agent behavior rule): The item's TDD cycle MUST include a behavioral enforcement test in the RED phase, not just a content-verification test. A plan item for a rule change that only specifies a content-verification grep test in its TDD cycle is INCOMPLETE — it must also specify a behavioral test that verifies the agent actually follows the changed rule.
- **Behavioral test coverage check:** For each rule-changing item in the plan, confirm that the TDD step block includes a behavioral RED phase (write behavioral test expecting agent NOT to follow rule) and a behavioral GREEN phase (make rule change, verify agent NOW follows rule). Items missing behavioral TDD for rule changes are flagged as STRUCTURE-VIOLATION.

### Step 4.6: Verify SC-to-Test Traceability, Behavioral Test Assertions, and RED-Phase Ordering

Before implementation proceeds, verify that the corresponding spec's success criteria have enforcement test assertions (BOTH content-verification AND behavioral where applicable) and that RED-phase ordering was followed.

→ **Full procedure:** See `tasks/verify-authorization/sc-traceability-check.md`

In addition to the content-verification checks in the sub-task file, this step verifies:

- **For each SC that changes agent behavior** (rule-changing, enforcement, behavioral SCs): The spec's success criteria MUST include at least one behavioral assertion describing the RED state (agent behavior without the rule) and GREEN state (agent behavior with the rule). SCs that only have content-verification grep commands are INCOMPLETE for behavioral rule changes.
- **Behavioral test assertions distinguish content from behavior:** A content-verification assertion checks that text exists in a file (e.g., `grep -c 'pattern' file.md`). A behavioral assertion checks that the agent actually follows the rule (e.g., `assert_tool_calls_made` to verify the agent makes verification calls, or `assert_forbidden_pattern_absent` to verify the agent does not bypass a gate). For rule-changing SCs, behavioral assertions are PRIMARY — content-verification is secondary.
- **Behavioral RED state confirmation:** For each rule-changing SC, confirm that a behavioral enforcement test exists in `.opencode/tests/behaviors/` that was verified in RED state (test sends a prompt and confirms the agent does NOT follow the new rule yet). If only content-verification (grep) tests exist for a behavioral SC, flag as MISSING-TRACEABILITY.

### Step 5: Verify Sub-Issue Structure (for Plan Approval)

**This gate is the SINGLE AUTHORITATIVE verification point for sub-issue readiness.** The `issue-operations` `link-sub-issue` task's verification logic is superseded — all sub-issue verification logic lives here.

→ **Full procedure:** See `tasks/verify-authorization/sub-issue-verification.md`

→ **Phase-count cross-reference algorithm:** See `enforcement/sub-issue-graph-traversal.md`
→ **Closed-issue verification procedure:** See `enforcement/closed-issue-verification.md`

### Step 5b: Spec-to-Plan Approval Cascade

When a spec is approved and a plan already exists for that spec, the plan inherits the spec's approval status.

→ **Full procedure:** See `tasks/verify-authorization/spec-to-plan-cascade.md`

### Step 5b.5: Gap-Fill Precedence Principle

**Before evaluating any blocking gate in Steps 5 through 5c, the agent MUST apply this precedence principle:**

> When `authorization_scope`'s gap-fill actions cover a missing artifact requirement, that requirement is a gap-fill trigger, not a blocking gate. Hard gates only apply to artifacts outside the scope's gap-fill coverage.

→ **Full gap-fill procedure and precedence examples:** See `tasks/verify-authorization/gap-fill-cascade.md`

### Step 5c: Scope-Aware Gap-Fill Cascade

When `authorization_scope` from Step 2.0 is >= `for_plan`, missing intermediate artifacts are gap-filled automatically.

→ **Full procedure including PR strategy derivation:** See `tasks/verify-authorization/gap-fill-cascade.md`

→ **Scope-dependent routing table:** See `enforcement/auto-dispatch-table.md`

### Step 6: Scope-Aware Auto-Dispatch After Successful Verification

**🚫 CRITICAL: This step runs ONLY when ALL prior verification gates (Steps 1-5) pass. If ANY gate fails, HALT — do NOT dispatch.**

→ **Full procedure including auto-dispatch context differentiation, spec revision revocation detection, and edge cases:** See `tasks/verify-authorization/auto-dispatch.md`

**🚫 HARD HALT AT SCOPE BOUNDARY:** The agent MUST NOT proceed past the pipeline stage specified by `halt_at`. If the dispatch chain reaches the `halt_at` stage, the agent reports completion and STOPS. Proceeding past `halt_at` without re-authorization is a CRITICAL GUIDELINE VIOLATION.

## Context Required

- Related tasks: `verify-sub-issues` (delegated sub-issue verification detail), `verify-codebase`
- Sub-issue verification gate: This task (Step 5) is the SINGLE AUTHORITATIVE verification point. `issue-operations` `link-sub-issue` verification logic is superseded by this gate.
- Auto-dispatch targets: `writing-plans` (spec approval), `executing-plans` (plan approval)
- Dispatch context for plan approval: pass `plan_issue=#N` and `spec_issue=#M` (extracted from plan body)
- Label state machine: `141-planning-status-tracking.md §10` (remove `needs-approval`, add `in-progress` on approval)
- Adversarial verification model: `spec-auditor --task ground-truth` (finding classification and evidence artifacts)

## Sub-Task Files

This task delegates detailed procedures to sub-task files:

| Sub-Task File | Purpose |
| -- | -- |
| `verify-authorization/scope-auto-resolve.md` | Step 0.5: Scope auto-resolve from authorization phrase |
| `verify-authorization/item-decomposition-check.md` | Step 4.5: Verify item decomposition in plan |
| `verify-authorization/sc-traceability-check.md` | Step 4.6: SC-to-test traceability and RED-phase ordering |
| `verify-authorization/sub-issue-verification.md` | Step 5: Verify sub-issue structure (authoritative gate) |
| `verify-authorization/spec-to-plan-cascade.md` | Step 5b: Spec-to-plan approval cascade |
| `verify-authorization/gap-fill-cascade.md` | Step 5b.5 + 5c: Gap-fill precedence and cascade execution |
| `verify-authorization/auto-dispatch.md` | Step 6: Scope-aware auto-dispatch after verification |

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`