---
name: approval-gate
description: Use when user says "approved", "go", or any implementation instruction, or when authorization needs verification. Triggers on: approval, authorized, implement, start work, go ahead, needs-approval label.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: approval-gate

## Overview

Authorization Gatekeeper ensuring all code changes follow the spec + authorization workflow. Invoked automatically before implementation begins.

## Persona

You are an Authorization Gatekeeper. Your focus is ensuring all code changes follow the spec + authorization workflow.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify-qa-mode` | Detect spec-less implementation requests, switch to Q/A mode | ~800 |
| `verify-authorization` | Check explicit auth and needs-approval label; delegates branch creation to `git-workflow --task pre-work` | ~400 |
| `verify-sub-issues` | Verify sub-issue structure for multi-task specs | ~480 |
| `verify-codebase` | Re-evaluate codebase state, detect staleness | ~400 |
| `verify-already-implemented` | Check if all success criteria are already met; autoclose if so | ~400 |
| `verify-blockers` | Check for blocking issues/dependencies | ~320 |
| `verify-open-questions` | Check for unresolved questions in spec | ~370 |
| `post-implementation` | Push branch, generate compare URL, HALT | ~480 |

## Invocation

- `/skill approval-gate --task verify-authorization` - Check auth before work
- `/skill approval-gate --task verify-sub-issues` - Check sub-issue structure
- `/skill approval-gate --task verify-codebase` - Check codebase state
- `/skill approval-gate --task verify-already-implemented` - Check if spec already implemented
- `/skill approval-gate --task verify-blockers` - Check for blockers
- `/skill approval-gate --task verify-open-questions` - Check for unresolved questions
- `/skill approval-gate --task post-implementation` - After implementation done
- `/skill approval-gate` - Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is referenced when:
   - User says `approved`, `go`, or similar authorization
   - User asks about approval workflow
   - Implementation is about to begin
   - DO NOT prompt for invocation - the skill is triggered automatically

2. **Pre-Implementation Verification:**
   - Verify spec exists as GitHub Issue
   - Verify spec has received explicit authorization
   - Verify sub-issues structure (multi-task only)
   - Check for blocking issues/updates

3. **Implementation Scope:**
   - Authorization grants ONLY the specified phase/task
   - HALT after completing authorized work
   - Wait for explicit authorization for next phase/task

## Authorization Requirements

### Mandatory Before ANY Code Change

| Requirement | Description |
|-------------|-------------|
| **Spec exists as GitHub Issue** | No local fallback - GitHub Issues only |
| **Explicit authorization** | User says `approved`, `go`, or `approved: N.M` — **OVERRIDES `needs-approval` label** |
| **Open questions resolved** | No unresolved items in spec |
| **Sub-issues verified** | Multi-task specs require phase-level sub-issues |

### Authorization Does NOT Authorize

- Creating a spec does NOT authorize implementation
- Analyzing/investigating is NOT authorization
- Answering questions is NOT authorization
- `"Should I do X?"` is seeking permission, not receiving it

## Authorization Scope Rules

| Rule | Scope |
|------|-------|
| **Issue-bound** | Authorization applies ONLY to the specific issue where it was given |
| **Single-use** | Authorization for current phase/task only within that issue |
| **Session-bound** | New session = new authorization required (no carryover) |
| **Plan-bound** | Changes to plan invalidate authorization |
| **External input invalidates** | Bug reports, PR feedback require re-authorization |
| **Revision ≠ implementation** | Spec updates don't authorize code changes |

## Multi-Task Spec Authorization (CRITICAL)

**When parent issue has sub-issues:** Authorization cascades to ALL sub-issues.

| Authorization | Scope | Behavior |
|---------------|-------|----------|
| `#34 approved` (parent with sub-issues) | ALL sub-issues authorized | Complete ALL phases in sequence, HALT once at end |
| `#39 approved` (single sub-issue) | That sub-issue only | Complete that phase, HALT after completion |
| `approved: 1.2` (specific phase) | That phase only | Complete that phase, HALT after completion |

**⚠️ PROHIBITED (Common Misinterpretation):**
- 🚫 DO NOT halt after each phase of multi-task spec
- 🚫 DO NOT ask for re-authorization between phases
- 🚫 DO NOT treat sub-issues as separate authorization units

**✅ REQUIRED Behavior:**
1. User authorizes parent issue
2. Verify: parent has sub-issues? → ALL sub-issues authorized (cascade)
3. Complete Phase 2 (or resume from current phase)
4. Continue to Phase 3, Phase 4, Phase 5, Phase 6
5. Report ONCE at the end
6. HALT ONCE after ALL phases complete

**Exception: User explicitly names a phase**
- If user says "Phase 2 only" or "approved: 1.2" → complete that phase ONLY, then HALT
- The explicit phase restriction OVERRIDES the cascade

**Rationale:**
- Sub-issues exist for **tracking visibility**, not authorization gates
- GitHub sub-issue view shows progress across all phases
- Developer already approved the entire spec—redundant per-phase HALTs waste time
- Sub-issue database IDs link phases to parent for GitHub's hierarchy view

## Sub-Issue Creation Authorization

**When a multi-task spec is approved and has no sub-issues yet, the authorization cascade covers sub-issue creation as a pre-implementation setup step. No separate authorization is needed.**

### Authorization Cascade Table (Extended)

| Authorization | Sub-issues Exist? | Action |
|---------------|-------------------|--------|
| `#34 approved` (parent) | Yes | Cascade to all, proceed with implementation |
| `#34 approved` (parent) | No | Auto-create sub-issues, then cascade, then proceed with implementation |
| `#39 approved` (single sub-issue) | N/A | That sub-issue only, complete and HALT |
| `approved: 1.2` (specific phase) | N/A | That phase only, complete and HALT |

**Sub-issue creation is NOT an implementation action.** It is a tracking/setup action that falls under the existing authorization scope. Creating GitHub Issues for phase tracking does not modify the codebase, does not change files, and does not require separate human approval.

### Pre-Implementation Setup Steps (No Separate Authorization Required)

| Step | Requires Separate Auth? | Why |
|------|------------------------|-----|
| Auto-creating sub-issues | ❌ NO | Tracking/setup action, covered by parent authorization |
| Linking sub-issues to parent | ❌ NO | Part of sub-issue creation workflow |
| Proceeding to implementation after auto-creation | ❌ NO | Parent authorization continues to implementation |

### Prohibited Halts

- 🚫 PROHIBITED: Halting after authorization to ask for separate permission to create sub-issues. Sub-issue creation is a setup step, not an implementation action requiring separate authorization.
- 🚫 PROHIBITED: Treating 'empty sub-issues' as a blocking gate that requires human intervention. The auto-create workflow resolves empty sub-issues without human involvement.
- ✅ REQUIRED: When `get_sub_issues` returns empty for an approved multi-task spec, auto-create sub-issues and proceed to implementation in the same session.

## Post-Implementation Workflow

### After Implementation Completes

1. Push feature branch to remote
2. Generate compare URL for review
3. Report completion to issue (NO URL) and URL in chat
4. HALT — do NOT create PR without explicit instruction
5. WAIT for "create a PR" instruction

## Exceptions (No Authorization Required)

| Action | Authorization Needed? |
|--------|----------------------|
| Writing to `./tmp/` | NO - scratchpad exempt |
| Creating/updating spec issues | NO - spec work exempt |
| Updating STATUS markers | NO - tracking exempt |
| Analyzing code (read-only) | NO - investigation exempt |

## Skill Enforcement Mechanism

**⚠️ CRITICAL: Skills MUST enforce authorization — guidelines alone are insufficient.**

### Why Skills Must Enforce

- **Guidelines document** what agents should do
- **Skills contain code** that actually executes
- Agents have proven to bypass documented guidelines
- Enforcement in code prevents bypass

### Which Skills MUST Enforce

| Skill | Authorization Check Required |
|-------|------------------------------|
| `git-workflow` `--task pre-work` | ✅ YES - Check explicit "approved"/"go" before branch creation |
| `git-workflow` `--task pr-creation` | ✅ YES - Check explicit "create a PR" before PR creation |
| `git-workflow` `--task review-prep` | ❌ NO - Automatic after implementation |
| `git-workflow` `--task cleanup` | ❌ NO - Automatic after PR merge confirmed |
| All other skills | ❌ NO - Not git operation related |

### What Skills MUST Check

**For `pre-work` task:**
1. Get issue context (issue number)
2. Query GitHub Issue for labels and comments
3. Check for explicit authorization in comments
4. Check for `needs-approval` label
5. Apply enforcement matrix:
   - Explicit auth present → PROCEED
   - Label + no auth → HALT
   - No label + no auth → HALT
   - Conditional phrase → HALT (not explicit)

**For `pr-creation` task:**
1. Check if user said an explicit PR creation phrase ("create a PR", "make a PR", "push and create PR", "let's get a PR up", "create a pull request", "PR", "PR #NNN")
2. Apply enforcement matrix:
   - Explicit PR phrase present → PROCEED
   - "approved" only → HALT (auth for implementation, not PR)
   - Implementation complete → HALT (need explicit PR instruction)

### What Does NOT Authorize

| Phrase | Why NOT Authorization |
|--------|----------------------|
| "continue" | Ambiguous - could mean analysis |
| "if you have next steps" | CONDITIONAL - not explicit |
| "proceed with X" | Ambiguous without "approved"/"go" |
| Implementation complete | NOT instruction to create PR |

### Enforcement Messages

**Missing authorization:**
```
Authorization required before proceeding.

Issue #N has needs-approval label and no explicit 'approved' or 'go' comment.

To authorize: Say 'approved' or 'go' in a comment.
```

**PR not authorized:**
```
PR creation requires explicit instruction.

User said 'approved' which authorizes implementation ONLY, not PR creation.

To create PR: Say 'create a PR', 'make a PR', 'PR', or 'PR #NNN' explicitly.
```

## Analysis → Implementation Authorization Boundary

**Finding a bug during analysis does NOT authorize fixing it.**

**This is a CRITICAL behavioral violation, not a one-off mistake. See `000-critical-rules.md` → "Bug Discovery Does NOT Authorize Bug Fixing" for the complete rule, authorization matrix, and self-correction protocol.**

### Bug Discovery ≠ Bug Fixing Authorization

| Discovery Action | Authorized? | Action Required |
|-----------------|-------------|-----------------|
| Found a bug during analysis | ✅ YES | Create bug report issue |
| Read-only analysis of bug | ✅ YES | Report findings |
| Edit code to fix the bug | 🚫 NO | STOP, create spec, wait for authorization |
| Create branch for fix | 🚫 NO | STOP, wait for authorization |
| Commit fix code | 🚫 NO | STOP, wait for authorization |

### Self-Correction When Catching Unauthorized Edits

1. **STOP** — do not proceed
2. **REVERT** — `git checkout -- <affected-files>`
3. **REPORT** — document as factual observation
4. **HALT** — wait for explicit authorization

## Revision Revokes Approval

**Any modification to a spec or task document MUST immediately revoke approval.**

### Status Transition

When a spec is modified:
1. **Status transitions to pending**: `STATUS: X.Y` → `STATUS: X.Y (REVISED - NEEDS APPROVAL)`
2. **Label applied**: Add `needs-approval` label to the issue
3. **Agent MUST HALT**: Do NOT proceed with implementation
4. **Fresh authorization required**: New explicit approval needed before implementation

### Exempt from Approval Revocation

- STATUS marker updates (`☐ → ☑`, `1.1 → 1.2`)
- Progress comments added to issue
- Bug report additions (separate from spec content changes)

## Bug Report Response Protocol

When a bug report requires code changes:

1. Add `needs-approval` label to the issue
2. Post additional spec comment documenting the bug
3. HALT immediately — do NOT implement
4. Wait for explicit `go` or `approved`

## Cross-References

- Related skills: `git-workflow` (branch operations, cleanup with parent closure check), `pr-creation-workflow` (PR timing), `issue-review` (reads authorization status in gather task)
- Related guidelines: `010-approval-gate.md`, `120-github-issue-first.md`, `000-critical-rules.md`, `124-github-archive-workflow.md` (parent closure pre-check)

## Parent Closure Pre-Check Reference

Parent/child issue closure verification is handled in:
- **`git-workflow` skill** → `cleanup` task → Sub-issue double-check
- **`124-github-archive-workflow.md`** → "Parent Closure Pre-Check" section

The approval-gate verifies **pre-implementation** authorization. Parent closure verification happens **post-merge** during cleanup.