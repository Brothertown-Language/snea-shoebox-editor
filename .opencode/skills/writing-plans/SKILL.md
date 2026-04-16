---
name: writing-plans
description: Use when creating an implementation plan from an approved spec. Triggers on: write plan, create plan, implementation plan, plan spec, approved plan, plan creation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: writing-plans

## Overview

Plan creation workflow that transforms approved specs into actionable implementation plans using a hybrid structure: **phases** for sub-issue tracking and cross-phase visibility, **TDD steps** within each task for granular execution guidance. Every step is one action (2-5 minutes) with exact code and commands. Placeholders are forbidden in plans.

**Source attribution:** TDD step granularity, no-placeholders rule, plan document header, file structure section, and self-review checklist adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

## Plan Issue Model

Plans are either separate GitHub Issues or combined into the spec issue body, depending on agent intelligence evaluation of spec complexity. The hierarchy is:

**Separate plan (multi-task or agent-determined):**

```
Spec #N (approved)
  → [PLAN] #M (linked reference via body text "Spec: #N")
       ├── Task #P1: [Task: #M] Phase 1
       ├── Task #P2: [Task: #M] Phase 2
       └── Task #P3: [Task: #M] Phase 3
```

**Combined spec+plan (single-task, agent-determined):**

```
Spec #N (approved)
  → Body contains spec content
       └── ## Implementation Plan (appended section with header, file structure, TDD tasks)
```

**Plan issue properties (separate):**
- Title prefix: `[PLAN]`
- Labels: `plan` + `needs-approval`
- Body contains spec reference as prose (e.g., `Spec: #784`)
- Sub-issues are children of the plan, NOT the spec
- The plan references the spec via body text (linked reference), not via GitHub sub-issue link

**Combined spec+plan properties:**
- Title prefix: `[SPEC]` (retained, not changed to `[PLAN]`)
- Labels: existing spec labels (no `plan` label added)
- Plan content appended under `## Implementation Plan` heading in spec body
- No sub-issues (single-task by definition)
- Approval follows spec approval status (no separate plan approval needed)

## Combined Spec+Plan (Single-Task Specs)

When a spec is single-task with simple implementation, the plan may be combined into the spec issue body instead of creating a separate [PLAN] issue. The decision is made at the Step 1.5 decision gate in `tasks/create.md`.

### When to Combine vs Keep Separate

| Condition | Recommendation |
|-----------|---------------|
| Single-task, ≤ few TDD steps, plan content flows naturally after spec | **Combine** — one document aids review |
| Single-task, many TDD steps, or spec body already long/dense | **Separate** — readability degrades with combined content |
| Multi-task (multiple phases, mixed concerns) | **Always separate** — sub-issue tracking required |

### Combined Document Structure

When combined, the spec issue body has this structure:

```
[Existing spec content: objectives, requirements, success criteria, etc.]

---

## Implementation Plan

**Goal:** <one-line goal>
**Architecture:** <architectural approach>
**Tech Stack:** <technologies used>

### File Structure
- `path/to/file1.py` — <responsibility>
- `path/to/file2.py` — <responsibility>

### Phase 1: [Concern Name]
#### Task 1: [Component Name]
- Step 1: Write the failing test
- Step 2: Run test to verify it fails
- Step 3: Write minimal implementation
- Step 4: Run test to verify it passes
- Step 5: Commit
```

### Approval Cascade

The spec-to-plan approval cascade still applies to combined plans:

- If the spec was already approved when the plan is appended, the combined plan inherits the spec's approval
- No separate plan approval is needed — the plan content is part of the already-approved spec
- If the spec has not been approved, the combined plan requires the spec to be approved (single approval covers both)
- Spec revision invalidates the `## Implementation Plan` section — see Spec Revision Revocation below

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `create` | Create plan from approved spec; report in chat | ~800 |
| `validate` | Check for placeholders and completeness | ~500 |
| `retroactive` | Create plan for existing spec | ~600 |
| `clean-room` | Generate independent plan from problem statement only | ~500 |

## Invocation

- `/skill writing-plans` — Overview only
- `/skill writing-plans --task create` — Create plan from current spec
- `/skill writing-plans --task validate` — Validate existing plan
- `/skill writing-plans --task retroactive` — Create plan for existing spec
- `/skill writing-plans --task clean-room` — Generate clean-room plan (for comparison by spec-auditor)

## Hybrid Structure: Phases + TDD Steps

Plans use **phases** (for sub-issue tracking) with **TDD step granularity** within each task:

```
Phase 1: [Concern Name]
  Task 1: [Component Name]
    Step 1: Write the failing test
    Step 2: Run test to verify it fails
    Step 3: Write minimal implementation
    Step 4: Run test to verify it passes
    Step 5: Commit
```

Phase-level sections are prose (agent decides content). Task-level steps are TDD-granular with exact code and commands.

## No-Placeholders Rule (CRITICAL)

Every step must contain actual content. These are **plan failures**: `TBD`, `TODO`, `[to be determined]`, `[needs investigation]`, `[placeholder]`, `[requires research]`, `implement later`, `fill in details`, `Add appropriate error handling`, `Add validation`, `Write tests for the above`, `Similar to Task N`, or steps describing what to do without showing how.

## Self-Review Checklist

After writing the complete plan, check:

1. **Spec coverage:** Can you point to a task for each spec requirement?
2. **Placeholder scan:** Search for red-flag patterns. Fix them.
3. **Type consistency:** Do types/signatures used in later tasks match earlier definitions?

## Auto-Dispatch Entry

This skill can be invoked automatically by `approval-gate` after successful verification of a spec approval. The auto-dispatch chain:

```
approval-gate --task verify-authorization (all gates pass for spec approval)
  → writing-plans --task create (auto-dispatched)
    → github-sub-issues --task create-sub-issue (sub-issues under plan, not spec)
```

**Auto-dispatch context passed from approval-gate:**

| Parameter | Source | Purpose |
|-----------|--------|---------|
| `spec_issue` | Issue number from `verify-authorization` | Identifies the approved spec to plan from |
| `single_task_determination` | From `github-issue-creation/tasks/post-creation` (via `single-task-check`) | Informs combined vs separate plan decision (`single-task` or `multi-task`) |
| `single_task` | Boolean from `github-issue-creation/tasks/post-creation` (via `single-task-check`) | `true` for single-task, `false` for multi-task — shorthand for decision gate |
| `GIT_OWNER` | Session init | Repository owner for API calls |
| `GIT_REPO` | Session init | Repository name for API calls |
| `WORKTREE_PATH` | Session / worktree setup | Base directory for file operations |

**Spec-to-plan approval cascade:** When `writing-plans --task create` is invoked for a spec that is already approved, the newly created plan inherits the spec's approval status. The `needs-approval` label is removed from the plan and a comment documents the cascade — see Step 11 in `tasks/create.md` for the complete post-creation cascade procedure. This handles the case where plan creation happens AFTER spec approval in the same session.

**Manual invocation still works:** `writing-plans --task create` can be invoked directly at any time. Auto-dispatch is additive — it eliminates the silent gap between approval and plan creation, but does not replace manual invocation.

**No circular dispatch:** `writing-plans` never dispatches back to `approval-gate`. After plan creation, the plan requires its own approval (user says "approved"), which triggers `approval-gate` → `executing-plans` (not `writing-plans`).

## Spec Revision Revocation

When the spec referenced by a plan is revised, all linked plans must be re-approved:

**For separate plans:**

1. **Find linked plans:** Search GitHub Issues with `plan` label for body text matching `Spec: #N` (where N is the revised spec number)
2. **Re-apply `needs-approval` label** to each found plan
3. **Add audit comment** on each plan: `Spec #N has been revised. Plan requires re-approval before implementation.`
4. **HALT** — do not proceed with implementation from any plan linked to the revised spec until re-approved

**For combined spec+plan:**

1. **The `## Implementation Plan` section is invalidated** by the spec revision
2. **Add a comment** on the spec issue: `Spec revised — the `## Implementation Plan` section requires re-evaluation.`
3. **The agent re-evaluates** whether the combined plan still matches the revised spec, or whether it needs to be rewritten/separated
4. **HALT** — do not proceed with implementation from the combined plan until re-evaluated

This replaces the previous model where plan content lived in the spec body and revision automatically invalidated it. With the plan-bridge model, revision affects the spec but plans are tracked artifacts that must be explicitly re-reviewed — whether they are separate issues or combined sections.

## Re-Implementation

When a new plan is needed under the same spec (e.g., previous plan was rejected or superseded):

**For separate plans:**

1. **Create new `[PLAN]` issue** following standard plan creation procedure
2. **Close old plan** with comment: `Superseded by #N` (where N is the new plan number)
3. **Update old plan labels:** Remove `needs-approval`, add `wontfix` or close outright
4. **Sub-issues of old plan** remain linked to the old plan (not the spec) — they are closed along with the old plan or re-created under the new plan as appropriate

**For combined spec+plan:**

1. **Remove the `## Implementation Plan` section** from the spec issue body (edit the issue body to remove the appended plan content)
2. **If replacing with a new combined plan:** Append the new `## Implementation Plan` section to the spec issue body
3. **If replacing with a separate plan:** Create a new `[PLAN]` issue following standard procedure; no plan content remains in the spec body

The spec itself is the stable reference. Whether the plan is combined or separate, re-implementation modifies the plan artifact, not the spec content above the `## Implementation Plan` marker.

## Operating Protocol

1. Read approved spec from GitHub Issue
2. **Decision gate:** Evaluate combined vs separate plan using `single_task_determination` and `single_task` inputs — see `tasks/create.md` Step 1.5
3. Map file structure (all files to create/modify with responsibilities)
4. Plan phase structure by judgment (prose-driven)
5. Define tasks within each phase using TDD step structure
6. Write plan document header (Goal, Architecture, Tech Stack)
7. Store plan document: if combined, append `## Implementation Plan` to spec issue body; if separate, create `[PLAN]` GitHub Issue with sub-issues via `github-sub-issues` skill
8. Self-review (coverage, placeholders, type consistency)
9. Validate (no placeholders, TDD structure, actionable steps)
10. Chat output with URL — Report plan creation (combined or separate) using exec summary + URL + byline format per `000-critical-rules.md`

## Enforcement

- No plan → CREATE plan (writing-plans skill) as `[PLAN]` GitHub Issue or combined into spec body per decision gate
- Plan exists but unapproved → HALT, wait for plan approval (not spec approval of plan content)
- Plan approved but has placeholders → REJECT plan
- Plan approved but missing TDD steps → REJECT plan
- Plan approved and complete → PROCEED to implementation
- Combined spec+plan → plan inherits spec approval status; no separate plan approval needed

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `brainstorming` in Cross-References section | File exists at `.opencode/skills/brainstorming/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References and Auto-Dispatch Entry | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `executing-plans` in Cross-References section | File exists at `.opencode/skills/executing-plans/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` in Cross-References section | File exists at `.opencode/skills/spec-auditor/SKILL.md` | MISSING-TRACEABILITY if missing |
| `github-sub-issues` in Cross-References and Auto-Dispatch Entry | File exists at `.opencode/skills/github-sub-issues/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-creation` in Cross-References section | File exists at `.opencode/skills/spec-creation/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `create` | File exists at `.opencode/skills/writing-plans/tasks/create.md` | MISSING-TRACEABILITY if missing |
| Task table entry `validate` | File exists at `.opencode/skills/writing-plans/tasks/validate.md` | MISSING-TRACEABILITY if missing |
| Task table entry `retroactive` | File exists at `.opencode/skills/writing-plans/tasks/retroactive.md` | MISSING-TRACEABILITY if missing |
| Task table entry `clean-room` | File exists at `.opencode/skills/writing-plans/tasks/clean-room.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` auto-dispatch behavior | Matches actual SKILL.md: `verify-authorization` dispatches to `writing-plans` | CONFLICTING if mismatched |
| `github-sub-issues` dispatch behavior | Matches actual SKILL.md: `create-sub-issue` task for sub-issue linking | CONFLICTING if mismatched |
| `spec-auditor` clean-room invocation | Matches actual SKILL.md: `fidelity` subtask invokes `writing-plans --task clean-room` | CONFLICTING if mismatched |

**Verification Procedure:**

Before invoking any cross-referenced skill:
1. `ls .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: file exists or MISSING-TRACEABILITY
2. `grep -c "<task-name>" .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: task referenced or MISSING-TRACEABILITY
3. Compare described behavior with actual content → EVIDENCE: match or CONFLICTING

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced skill file missing | MISSING-TRACEABILITY | flag-for-review | Cannot verify cross-reference |
| Referenced task file missing | MISSING-TRACEABILITY | flag-for-review | Task may have been renamed |
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |
| Invocation mismatch | CONFLICTING | flag-for-review | Skill may have been updated |

## Live Verification: Spec State (MANDATORY)

**🚫 CRITICAL: When this skill reads spec metadata (approval status, revision state, content), it MUST verify against live GitHub state. Trusting cached or claimed spec state is a VERIFICATION-GAP finding per `065-verification-honesty.md`.**

| Metadata Trust Point | Verification Action | Tool Call | Problem Class |
|---------------------|-------------------|-----------|---------------|
| Spec claimed as "approved" | Verify `needs-approval` label is absent AND authorization comment exists from a developer | `github_issue_read(method=get_labels)` + `github_issue_read(method=get_comments)` | CONFLICTING |
| Spec content used for planning | Verify spec body matches current issue state, not a cached version | `github_issue_read(method=get, issue_number=N)` → read body fresh | VERIFICATION-GAP |
| Spec claimed as "not revised since approval" | Verify no revision comments or STATUS changes after authorization comment | `github_issue_read(method=get_comments)` → compare timestamps | CONFLICTING |
| Spec-to-plan cascade eligibility | Verify spec approval actually exists (not just assumed) before auto-approving plan | `github_issue_read(method=get_comments)` → find explicit authorization comment | VERIFICATION-GAP |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Spec lacks approval but plan created | CONFLICTING | flag-for-review | HALT — plan requires separate approval |
| Spec content stale vs live | VERIFICATION-GAP | auto-fix | Re-read spec, regenerate plan |
| Spec revised after authorization | CONFLICTING | conditional | Verify plan still matches revised spec |
| Cascade assumed without evidence | VERIFICATION-GAP | conditional | Collect authorization evidence before proceeding |

## Cross-References

- Related skills: `brainstorming` (pre-spec), `approval-gate` (authorization), `executing-plans` (implementation), `spec-auditor` (fidelity subtask uses clean-room), `github-sub-issues` (sub-issue creation under plan), `spec-creation` (spec creation discipline)
- Source: adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)
