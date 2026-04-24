# Task: create

## Purpose

Create an implementation plan from an approved spec. For single-task specs the agent may combine the plan into the spec issue body instead of creating a separate [PLAN] issue.

## Prerequisites

1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)
4. (Optional) `authorization_scope` from verify-authorization — if scope >= `for_plan`, plan auto-approval triggers

## Operating Protocol

1. **Verification first:** Must run verification-enforcement --task verify before reading spec
2. **Combined or separate decision:** Early evaluation whether to append to spec or create separate issue
3. **Item decomposition mandatory:** Plan must enumerate items, order dependencies, specify acceptance criteria
4. **RED checkpoint mandatory:** Every TDD task must include explicit Step 2 checkpoint
5. **Approval cascade auto-approve:** Pipeline scope (`for_plan+`) auto-approves plan

## Entry Criteria

- Spec is approved and stored as GitHub Issue
- `authorization_scope` received from approval-gate (for cascade)

## Exit Criteria

- Plan created (combined into spec issue OR separate [PLAN] issue)
- All validation passed
- Plan reported in chat with URL
- Approval cascade applied (or `needs-approval` retained)

## Procedure

### Steps 0-5: Plan Structure Definition

**Route to:** `create/plan-structure`

Runs verification gate, makes combined/separate decision, checks for duplicate plans, maps file structure, defines phase structure, and creates TDD tasks with mandatory RED checkpoints.

### Steps 6-13: Plan Creation and Approval Cascade

**Route to:** `create/create-and-validate`

Writes plan header, stores as combined section or separate issue, creates sub-issues (for separate), runs self-review and validation, revisits verification, cross-references skills, and applies approval cascade with scope-aware auto-approval.

## Sub-Task Files

| Sub-Task | Purpose | Words |
| -- | -- | -- |
| `create/plan-structure` | Verification, combined/separate decision, file mapping, TDD definition | ≈750 |
| `create/create-and-validate` | Document writing, issue creation, validation, approval cascade | ≈650 |

## Plan Phase Structure Requirements

Each phase MUST include (prose-driven, not rigid headers):
- **Why this phase exists** — concern it addresses and place in overall design
- **What it must accomplish** — tasks, deliverables, behavioral requirements
- **How to verify completion** — success criteria and testable outcomes
- **What could go wrong** — edge cases, known risks, failure modes
- **What must be done first** — dependencies on prior phases or external prerequisites

## Concern Boundary Annotations

When transitioning between architectural concerns, describe:
- What concern being left (prior scope)
- What concern being entered (new scope)
- What information the new concern needs from prior (handoff point)

## Combined Plan Format

When combined into spec:
- Append under `## Implementation Plan` section
- Retain `[SPEC]` title prefix
- **Do NOT link sub-issues** — single-task by definition

## Separate Plan Format

When separate [PLAN] issue:
- Title: `[PLAN] <Feature Name>`
- Labels: `plan`, `needs-approval` (unless auto-approved)
- Body: `Spec: #<N>` reference, then plan header, file structure, phases
- Sub-issues linked under the plan (not the spec)

## Approval Cascade Matrix

| Scope | Plan Creation | Plan Approval | Implementation |
| -- | -- | -- | -- |
| `standard` | Yes | Separate approval required | Separate approval required |
| `for_spec` | No | N/A | N/A |
| `for_plan` | Yes | Auto-approved | Separate approval required |
| `for_implementation` | Yes | Auto-approved | Auto-approved |
| `for_pr` | Yes | Auto-approved | Auto-approved |
| `pr_only` | N/A (skip) | N/A | N/A |

## Context Required

- Related skills: `verification-enforcement`, `issue-operations`, `spec-creation`
- Related tasks: `create/plan-structure`, `create/create-and-validate`