# Approval Gate

> **See `approval-gate` skill for complete procedural workflow including:**
>
> - Spec + authorization requirements
> - Plan approval gate
> - Sub-issue verification gate (under plan) — consolidated into `approval-gate --task verify-authorization` Step 5
> - Single-task exemption
> - Re-evaluation checklist
> - Bug report response

## Tier 0: Zero Tolerance Rules

**These rules are inviolable. Violation is a protocol breach.**

### Mandatory Requirements

| Requirement | Rule |
| -- | -- |
| **Spec before code** | NO code/guideline changes WITHOUT approved spec |
| **Plan before implementation** | NO implementation WITHOUT approved plan (spec approval → plan creation, plan approval → implementation) |
| **Authorization required** | NO implementation WITHOUT explicit `"approved"` or `"go"` |
| **Explicit auth overrides label** | When user says `approved`/`go`, proceed REGARDLESS of `needs-approval` label |
| **Branch first** | Create feature branch BEFORE any file modification |
| **Human-only merge** | Agents MUST NEVER merge PRs |
| **MCP tools** | Use appropriate tools per five-tier hierarchy (see `mcp-tool-usage` skill) |
| **Silent halt** | HALT after completion, after PR creation — no prompts |
| **Search before halt** | When no spec/plan exists for an implementation request, search GitHub Issues for existing candidates (label filters: `[SPEC]`, `[PLAN]`, `[SPEC-FIX]`; keyword matching against request target), present candidates with URLs, offer create-or-select before halting — see `000-critical-rules.md` §Silent Halt Without Prompt |
| **PR timing** | PRs require explicit `"create a PR"` instruction |
| **Issue closure** | Close issues ONLY after PR merge confirmed |
| **Spec-to-Plan cascade** | When a spec is approved and a plan already exists, the plan is automatically approved. Manual plan approval is only required when no plan exists at the time of spec approval |

### Spec-to-Plan Approval Cascade (Critical)

**When a spec is approved and a plan already exists, the plan is automatically approved.** This eliminates redundant manual approval when the implementation plan was already created and is faithful to the approved spec.

**The two-gate model still applies when no plan exists at the time of spec approval:** spec approval → plan creation → plan approval → implementation.

#### Edge Cases

| Edge Case | Resolution |
| -- | -- |
| **Plan not faithful** | If the plan deviates from the spec, the plan-fidelity-auditor catches this during implementation. The plan must be revised to match the spec, and the revised plan requires fresh approval. |
| **Spec revised after cascade** | Spec revision revokes ALL linked plan approvals (existing behavior per "Revision Revokes Approval"). The cascade does not override revision-based revocation. |
| **No plan exists at spec approval** | Normal two-gate flow applies. The cascade only activates when a plan already exists. Spec approval authorizes plan creation via `writing-plans` skill, then plan approval is required before implementation. |
| **Multiple plans exist** | When a spec has multiple linked plans, the most recent approved plan takes precedence. Older plans are superseded and treated as stale per "Implementing Stale or Superseded Specs" rules. |

### Mandate Tiering Interaction (Critical)

**The contradiction between zero-tolerance mandates and explicit authorization is resolved through mandate tiering.** See `000-critical-rules.md` → "Mandate Tiering" for the complete classification.

The interaction between developer authorization and process mandates follows these rules:

| Scenario | Resolution | Rationale |
| -- | -- | -- |
| Developer authorization + Tier 2 process mandate | Developer authorization wins | The developer has accepted the risk of skipping process; the work is authorized |
| Developer authorization + Tier 1 safety mandate | Safety mandate wins | Worktree and branch protection protect repository integrity regardless of authorization |
| No developer authorization + any mandate | Mandate holds | Authorization is always required for implementation |

**For clearly simple work** (documentation, runbooks, minor configuration edits, single-file non-behavioral changes), developer authorization IS sufficient process — no separate spec/plan is required. The developer's explicit "approved" or "go" serves as both the authorization and the process justification.

**For complex work** (new features, behavioral changes, multi-file modifications), developer authorization means "you may begin the process." The spec/plan workflow still produces value (traceability, review trail, edge case discovery) even when authorization exists. The agent should proceed through spec/plan creation as part of the authorized work.

**This resolves the contradiction identified in #912:** "NO code WITHOUT approved spec" is a Tier 2 mandate that yields to explicit developer authorization, while "create worktree before editing" is a Tier 1 mandate that never yields.

### Explicit Authorization Priority (Critical)

**⚠️ When user provides explicit authorization (`approved`, `go`, `#123 approved`), proceed with implementation even if the `needs-approval` label is present.**

The `needs-approval` label is a **tracking tool**, not a permanent gate. Its purpose is:

- Indicate "awaiting approval" visually
- Remind reviewers that approval hasn't been given yet
- Block agents from proceeding **until** explicit authorization is received

**The label does NOT override explicit user authorization.**

| Scenario | Action |
| -- | -- |
| User says `approved` AND label present | ✅ **PROCEED** - explicit auth wins |
| User says `#123 approved` AND label present | ✅ **PROCEED** - explicit auth wins |
| User says `go` AND label present | ✅ **PROCEED** - explicit auth wins |
| NO user authorization AND label present | ⛔ **HALT** - wait for authorization |
| Label removed by user | ✅ **Proceed if authorized** - no issue |

### Authorization Scope

- **Issue-bound**: Authorization applies ONLY to the specific issue where it was given
- **Session-bound**: New session = new authorization required (no carryover from previous sessions)
- **Single-use**: Authorization for current phase/task only within that issue
- **External input invalidates**: Bug reports require re-authorization
- **Revision ≠ implementation**: Spec updates don't authorize code changes; spec revision revokes linked plan approvals
- **Reference ≠ authorization cascade**: Issue mentions in body/comments do NOT cascade authorization; spec references plan via body text, not sub-issue link
- **Confirmation ≠ authorization**: Confirming an observation does NOT authorize implementation

**🚫 CRITICAL: Old authorizations do NOT apply:**

- "Approved #332" in previous session → NOT VALID for new session
- Previous session authorization → NOT VALID for new issue/spec
- Authorization is ZERO-BASED — every task needs NEW authorization

### Multi-Task Plan Authorization (CRITICAL)

**When a plan has sub-issues:** plan approval cascades authorization to ALL sub-issues under the plan.

**See `approval-gate` skill → "Multi-Task Plan Authorization" for the complete authorization cascade workflow and enforcement matrix.**

The plan-bridge hierarchy: Spec → (body linked reference) → Plan → Sub-issues. Sub-issues are children of the plan, NOT the spec.

Key rules:

- 🚫 DO NOT halt after each phase of multi-task plan
- 🚫 DO NOT ask for re-authorization between phases
- 🚫 DO NOT treat sub-issues as separate authorization units
- ✅ Complete ALL phases, then report ONCE and HALT ONCE

**Exception:** User explicitly names a phase (e.g., "approved: 1.2" or "Phase 2 only") → complete that phase ONLY, then HALT.

### Batch Authorization Carry-Forward

**When multiple issues are approved together:** authorization carries forward within the batch via the persisted batch state file.

**See `divide-and-conquer` skill `--task assemble-batch` for the complete batch orchestration workflow.**

Key rules:

- 🚫 DO NOT re-authorize between issues in a batch
- 🚫 DO NOT HALT between issues in a batch
- ✅ Batch state file (`.opencode/tmp/batch-<timestamp>.md`) carries authorization context forward
- ✅ Each sub-agent receives `prior_results` from preceding issues
- ✅ Authorization is issue-bound but batch-carries-forward within the same approval

**This replaces the old "session-bound" limitation for batch approvals.** Within a batch, authorization persists via the batch state file, not via ephemeral chat context.

### Revision Revokes Approval (MANDATORY)

**Any modification to a spec or plan document MUST immediately revoke approval.** Spec revision revokes approval of any linked plan (referenced via body text). Plan revision revokes implementation authorization for its sub-issues.

**See `approval-gate` skill for revision status transition rules, mandatory actions, and exemption categories.**

Key rule: Revision = `STATUS: X.Y (REVISED - NEEDS APPROVAL)` + `needs-approval` label + chat output + HALT.

Exempt from approval revocation:

- STATUS marker updates (`☐ → ☑`, `1.1 → 1.2`)
- Bug report additions (separate from spec content changes)

**Exception: Needs-Approval State** — When an issue is already in `needs-approval` state (no approval has been granted), spec revision does NOT constitute "revoking approval" — there is nothing to revoke. The `needs-approval` label is preserved and the revision is documented in Revision Notes. This is the common case: most spec updates happen before approval.

### Re-implementation Workflow

When a spec is revised after a linked plan was already approved:

1. Spec revision revokes the linked plan's approval
2. The old plan is closed with a comment referencing the spec revision
3. A new plan is created under the same spec (using `writing-plans` skill)
4. The new plan requires fresh approval before implementation proceeds

### Label Handling

**The `needs-approval` label is informational when explicit authorization is present.**

**See `approval-gate` skill for the complete label handling enforcement matrix.**

Key rule: Explicit authorization (`approved`/`go`) OVERRIDES the `needs-approval` label.

### Bug Report Response

**See `approval-gate` skill for the complete bug report response protocol.**

Key rule: Bug reports requiring code changes → add `needs-approval` label → HALT → wait for explicit authorization.

### Audit Auto-Fix Exemption

**Spec-auditor auto-fixes applied to GitHub Issues are exempt from the "no implementation without authorization" rule** when ALL conditions below are met. This exemption exists because audit auto-fixes are analogous to linter auto-fixes (`ruff --fix`) — they correct mechanical issues without changing semantics.

**Conditions for exemption (ALL must be true):**

| Condition | Requirement |
| -- | -- |
| Deliberate invocation | Audit was user-triggered (`spec-auditor --issue N`) or pipeline-triggered |
| Classification | Finding is classified as `auto-fix` by spec-auditor's three-tier model |
| Target | Fix is applied to a GitHub Issue body only (not source code, not skill files, not guideline files, not configuration) |
| Non-substantive | Fix is structural/mechanical: STATUS headers, numbering, markers, boilerplate additions, trace links, approach differences, concern separation, inline context replacement |
| No scope change | Fix does not add/remove phases, requirements, success criteria, or alter scope |

**Conditional fixes are NOT exempt.** They require separate authorization ("approved"/"go") before application, even when the audit itself was deliberately invoked. The safety check in the conditional tier assesses whether the fix could break dependencies — it does NOT substitute for authorization.

**Flag-for-review findings are never applied.** They are reported in the executive summary for developer action.

**When any condition is NOT met**, the action reverts to the standard approval-gate rule: no implementation without explicit authorization.

**See `000-critical-rules.md` → "Implementation Without Spec" table for the auto-fix exemption row, and `spec-auditor` skill → "Auto-Fix Model" for the three-tier classification.**

### Bug Discovery Protocol (CRITICAL)

**⚠️ Finding a bug during analysis or any other activity does NOT authorize fixing it.**

**See `000-critical-rules.md` → "Bug Discovery Does NOT Authorize Bug Fixing" for the complete authorization matrix, self-correction protocol, and enforcement details.**

Key rules:

- 🚫 NEVER edit source code after discovering a bug without an approved spec
- 🚫 NEVER create a branch for a bug fix without authorization
- ✅ ALWAYS create a bug report issue (permitted without authorization)
- ✅ ALWAYS perform read-only analysis (permitted without authorization)
- ✅ ALWAYS HALT and wait for explicit authorization before any code changes
- ✅ If you catch yourself editing code without a spec, immediately `git checkout` and HALT

**Bug discovery is a reporting action, NOT an implementation authorization.**

### Action Authorization Classification

**The single source for determining whether an action requires authorization.** When in doubt, check this table before checking other files.

| Action | Requires Auth? | Authority Source |
|--------|---------------|-----------------|
| Writing Python/source code | Yes | Tier 0: Spec before code |
| Editing skill files (SKILL.md, task/*.md) | Yes | `000-critical-rules.md` §Implementation Without Spec |
| Editing guideline files | Yes | `000-critical-rules.md` §Implementation Without Spec |
| Editing config (pyproject.toml, .pre-commit) | Yes | `000-critical-rules.md` §Implementation Without Spec |
| Editing test files | Yes | `000-critical-rules.md` §Implementation Without Spec |
| Creating new files of any type | Yes | `000-critical-rules.md` §Implementation Without Spec |
| **Graph reconciliation** | On approval/re-approval, `reconcile-issue-graph` auto-closes verified-complete tickets and reopens verified-incomplete tickets in the reachable issue graph |
| Creating new GitHub Issue (spec/plan) | No auth, but mandatory `github-issue-creation` skill | `github-issue-creation` skill |
| Updating existing issue spec text (revision) | No auth — spec revision ≠ implementation | `010-approval-gate.md` §Revision ≠ Implementation |
| Updating issue spec to match code reality (drift sync) | No auth — administrative sync | `130-authority-source.md` §Documentation Drift Protocol |
| Moving issue labels | No auth | (explicit classification) |
| Running lint/typecheck/format commands | No auth | (existing practice, now explicit) |
| Posting progress comments to GitHub | No auth | `github-comments` skill |
| Creating feature branch | No auth, but mandatory worktree | `git-workflow` skill pre-work |
| Merging PR | Forbidden — human-only | Tier 0: Human-only merge |
| Closing issues | Only after PR merge confirmed | `git-workflow` skill cleanup |
| Spec-auditor auto-fixes on GitHub Issue bodies | Exempt (per conditions) | `010-approval-gate.md` §Audit Auto-Fix Exemption |

**Key invariant**: This table does NOT weaken any existing authorization gate. It only makes existing practice explicit and resolves ambiguous boundary cases.

## Skill Enforcement (CRITICAL)

**⚠️ CRITICAL: Skills MUST enforce authorization — guidelines alone are insufficient.**

**See `approval-gate` skill for the complete enforcement specification including:**

- Which skills MUST check authorization
- What each skill MUST check (pre-work, pr-creation)
- Enforcement matrix (explicit auth, label + no auth, conditionals)
- Conditional phrases that are NOT authorization

## What This Guideline Does NOT Cover

**The skill handles procedural workflow:**

- Spec + approval requirements details
- Re-evaluation checklist
- Pre-implementation verification steps
- Single-task exemption logic
- Authorization scope rules
- Workflow decision tree

**See the skill for complete implementation details.**

## Related Guidelines

| Guideline | Purpose |
| -- | -- |
| `000-critical-rules.md` | Critical violations and auditor enforcement |
| `020-go-prohibitions.md` | GO command restrictions |
| `140-planning-spec-creation.md` | Spec creation and plan-bridge hierarchy |
| `github-sub-issues` skill | Sub-issue creation and hierarchy tracking (verification superseded by `approval-gate --task verify-authorization`) |
| `git-workflow` skill `cleanup` task | Post-merge closure workflow |
| `pr-creation-workflow` skill | PR creation timing |
| `writing-plans` skill | Plan creation from approved spec |
| `executing-plans` skill | Plan execution after plan approval |

```yaml+symbolic
schema_version: "1.0"
last_updated: "2026-04-13T12:00:00Z"
rules:
  - id: approval-gate-001
    title: "No implementation without authorization"
    conditions:
      all:
        - "has_approved_plan == false"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: []
    source: "010-approval-gate.md §Tier0"

  - id: approval-gate-001a
    title: "Spec approval authorizes plan creation, not implementation"
    conditions:
      all:
        - "has_approved_spec == true"
        - "has_approved_plan == false"
        - "has_existing_plan == false"
    actions:
      - INVOKE(writing-plans)
    conflicts_with: []
    requires: [approval-gate-001]
    triggers: [writing-plans]
    source: "010-approval-gate.md §Tier0"

  - id: approval-gate-001a-cascade
    title: "Spec approval cascades to existing faithful plan"
    conditions:
      all:
        - "has_approved_spec == true"
        - "has_existing_plan == true"
        - "plan_is_faithful == true"
    actions:
      - AUTO_APPROVE(plan)
      - PROCEED_TO(implementation)
    conflicts_with: [approval-gate-001a]
    requires: [approval-gate-001]
    triggers: [executing-plans]
    source: "010-approval-gate.md §Spec-to-Plan Approval Cascade"

  - id: approval-gate-001b
    title: "Plan approval authorizes implementation"
    conditions:
      all:
        - "has_approved_plan == true"
    actions:
      - INVOKE(executing-plans)
    conflicts_with: []
    requires: [approval-gate-001a]
    triggers: [executing-plans]
    source: "010-approval-gate.md §Tier0"

  - id: approval-gate-002
    title: "Explicit authorization overrides needs-approval label"
    conditions:
      any:
        - "user_says == 'approved'"
        - "user_says == 'go'"
    actions:
      - PROCEED
    conflicts_with: []
    requires: []
    triggers: [approval-gate, divide-and-conquer]
    source: "010-approval-gate.md §Explicit Authorization Priority"

  - id: approval-gate-003
    title: "No authorization without user input"
    conditions:
      all:
        - "has_authorization == false"
        - "needs_approval_label == true"
    actions:
      - HALT
    conflicts_with: [approval-gate-002]
    requires: []
    triggers: []
    source: "010-approval-gate.md §Explicit Authorization Priority"

  - id: approval-gate-004
    title: "Branch first before any file modification"
    conditions:
      all:
        - "has_feature_branch == false"
    actions:
      - HALT
    conflicts_with: []
    requires: [approval-gate-001]
    triggers: [git-workflow]
    source: "010-approval-gate.md §Mandatory Requirements"

  - id: approval-gate-005
    title: "Agents must never merge PRs"
    conditions:
      all:
        - "is_agent == true"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: []
    source: "010-approval-gate.md §Mandatory Requirements"

  - id: approval-gate-006
    title: "Spec revision revokes linked plan approvals"
    conditions:
      all:
        - "spec_revised == true"
        - "has_linked_plan == true"
    actions:
      - REVOKE(plan_approval)
      - INVOKE(re-implementation-workflow)
    conflicts_with: []
    requires: []
    triggers: [writing-plans]
    source: "010-approval-gate.md §Revision Revokes Approval"

  - id: approval-gate-007
    title: "Sub-issues are under plan, not spec"
    conditions:
      all:
        - "spec_has_sub_issues == true"
        - "plan_has_sub_issues == false"
    actions:
      - RESTRUCTURE(move sub-issues to plan)
    conflicts_with: []
    requires: []
    triggers: [github-sub-issues]
    source: "010-approval-gate.md §Multi-Task Plan Authorization"

  - id: approval-gate-008
    title: "Audit auto-fix exempt from authorization when conditions met"
    conditions:
      all:
        - "audit_deliberately_invoked == true"
        - "finding_classification == 'auto-fix'"
        - "fix_target == 'github-issue-body'"
        - "fix_non_substantive == true"
    actions:
      - PROCEED
    conflicts_with: [approval-gate-001]
    requires: []
    triggers: [spec-auditor]
    source: "010-approval-gate.md §Audit Auto-Fix Exemption"

  - id: approval-gate-009
    title: "Conditional audit fixes require authorization"
    conditions:
      all:
        - "audit_deliberately_invoked == true"
        - "finding_classification == 'conditional'"
    actions:
      - HALT
    conflicts_with: [approval-gate-008]
    requires: []
    triggers: [spec-auditor]
    source: "010-approval-gate.md §Audit Auto-Fix Exemption"

state_machines:
  - id: approval-lifecycle
    states: [draft, spec_approved, plan_created, plan_approved, implementing, pr_created, merged, closed]
    start_state: draft
    transitions:
      - from: draft
        to: spec_approved
        guard: "user_authorizes_spec == true"
        action: INVOKE(writing-plans)
      - from: spec_approved
        to: plan_created
        guard: "plan_exists == true"
        action: PROCEED
      - from: draft
        to: plan_approved
        guard: "user_authorizes_spec == true AND existing_plan_is_faithful == true"
        action: AUTO_APPROVE_PLAN_THEN_IMPLEMENT
      - from: plan_created
        to: plan_approved
        guard: "user_authorizes_plan == true"
        action: INVOKE(executing-plans)
      - from: plan_approved
        to: implementing
        guard: "plan_approved == true"
        action: INVOKE(divide-and-conquer)
      - from: implementing
        to: pr_created
        guard: "implementation_complete == true"
        action: INVOKE(git-workflow)
      - from: pr_created
        to: merged
        guard: "pr_approved == true"
        action: PROCEED
      - from: merged
        to: closed
        guard: "all_plan_sub_issues_closed == true"
        action: PROCEED
```
