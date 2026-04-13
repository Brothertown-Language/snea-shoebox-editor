---
name: approval-gate
description: Use when user says "approved", "go", or any implementation instruction, or when authorization needs verification. Triggers on: approval, authorized, implement, start work, go ahead, needs-approval label, batch approval, multiple issues approved, interdependency analysis.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: approval-gate

## Overview

Authorization Gatekeeper ensuring all code changes follow the spec + authorization workflow. The agent MUST invoke this skill before implementation begins.

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
| `verify-fix-spec` | For bug reports, verify fix spec sub-issue exists before closure | ~250 |
| `pre-implementation-analysis` | Analyze interdependencies and expand sub-issues for all approved issues (single or batch), producing flat item list for assemble-batch | ~500 |
| `post-implementation` | Push branch, generate compare URL, HALT | ~480 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~150 |

## Invocation

- `/skill approval-gate --task verify-authorization` - Check auth before work
- `/skill approval-gate --task verify-sub-issues` - Check sub-issue structure
- `/skill approval-gate --task verify-codebase` - Check codebase state
- `/skill approval-gate --task verify-already-implemented` - Check if spec already implemented
- `/skill approval-gate --task verify-blockers` - Check for blockers
- `/skill approval-gate --task verify-open-questions` - Check for unresolved questions
- `/skill approval-gate --task verify-fix-spec` - Verify fix spec exists for bug reports
- `/skill approval-gate --task pre-implementation-analysis` - Analyze interdependencies and expand sub-issues for all approved issues, then yield to assemble-batch
- `/skill approval-gate --task post-implementation` - After implementation done
- `/skill approval-gate --task completion` - Invoke when workflow halts at any point
- `/skill approval-gate` - Overview only

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (authorization result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke approval-gate when it encounters `approved`/`go`, authorization questions, or implementation start. Never prompt for invocation — just invoke the skill.
2. **Two-gate authorization model:** Spec approval → plan creation. Plan approval → implementation. Each gate requires explicit authorization.
3. **Pre-Implementation Verification:** Verify spec or plan exists as GitHub Issue, verify authorization, verify sub-issues under plan (multi-task), check for blockers.
4. **Multi-task cascade:** When plan has sub-issues, authorization cascades from plan to ALL sub-issues. Complete ALL phases, report ONCE, HALT ONCE.
5. **Spec revision revocation:** If a spec is revised (status changed to REVISED - NEEDS APPROVAL), find linked plan issues by searching for `[PLAN]` issues referencing the spec number in their body and mark them for audit. Revision of a spec revokes approval on its linked plan.
6. **Auto-dispatch after verification:** When all verification gates pass, auto-dispatch to the next skill in the chain. See Dispatch Order below.

## Dispatch Order

After `verify-authorization` completes successfully (all gates pass), the skill auto-dispatches based on approval context:

```
Spec approved
  → verify-authorization (all gates pass)
  → writing-plans --task create (auto-dispatched to create plan issue)

Plan approved
  → verify-authorization (all gates pass)
  → sub-issue verification (if multi-phase)
  → pre-implementation-analysis (expand sub-issues, classify, build flat item list)
  → divide-and-conquer/assemble-batch (dispatch sub-agents, squash-merge into batch branch)
  → verification-before-completion
  → finishing-a-development-branch
  → git-workflow/review-prep

Already implemented
  → verify-authorization (all gates pass)
  → verify-already-implemented (detects implementation)
  → Auto-close (no dispatch)
```

**Spec approval dispatches to plan creation, NOT implementation.** The plan then requires its own approval before implementation begins.

**Dispatch context detection:**
- Spec approval: Issue title contains `[SPEC` or has `spec` label
- Plan approval: Issue has `plan` label or `[PLAN]` prefix in title
- See `verify-authorization.md` Step 5 for full procedure

**Circular dispatch prevention:** Spec approval dispatches to `writing-plans`, which creates a plan. Plan approval dispatches to `executing-plans`. The plan requires its own approval before `executing-plans` can run.

## Authorization Requirements

| Requirement | Description |
|-------------|-------------|
| **Spec or Plan exists as GitHub Issue** | No local fallback — GitHub Issues only |
| **Two-gate authorization** | Spec approval → plan creation; Plan approval → implementation |
| **Explicit authorization** | User says `approved`, `go`, or `approved: N.M` — OVERRIDES `needs-approval` label |
| **Open questions resolved** | No unresolved items in spec or plan |
| **Sub-issues verified under plan** | Multi-task plans require phase-level sub-issues |
| **Fix spec for bug reports** | Bug reports must have a fix spec sub-issue before closure (per `000-critical-rules.md`) |
| **Implementation includes** | All file modifications that alter behavior: source code, skill files, guideline files, config files, test files, TypeScript plugins |

## Fix Spec Verification for Bug Reports

Bug reports require a fix spec sub-issue before they can be considered complete. This verification is performed by the `verify-fix-spec` task.

| Check | Action |
|-------|--------|
| Bug report has fix spec sub-issue with `[SPEC] Fix:` title | ✅ Pass — fix spec exists |
| Bug report has fix spec sub-issue via `spec` label | ✅ Pass — fix spec exists |
| Bug report has NO fix spec sub-issue | ❌ Fail — invoke `issue-review --task analyze-and-spec` to create one |
| Bug report is NOT a bug report | ⏭️ Skip — this check does not apply |

This check is invoked:
- During `verify-already-implemented` for bug reports
- During `issue-review --task analyze-and-spec` already-handled path
- Before closing any issue that has `bug` label or bug report language

## Authorization Scope Rules

| Rule | Scope |
|------|-------|
| **Issue-bound** | Authorization applies ONLY to the specific issue |
| **Session-bound** | New session = new authorization required |
| **Single-use** | Authorization for current phase/task only |
| **Plan-bound** | Changes to plan invalidate authorization |
| **External input invalidates** | Bug reports, PR feedback require re-authorization |
| **Revision ≠ implementation** | Spec updates don't authorize code changes |
| **Reference ≠ cascade** | Issue mentions in body/comments do NOT cascade |
| **Confirmation ≠ authorization** | Confirming an observation does NOT authorize implementation |
| **Discussion conclusion ≠ authorization** | Verbal agreement, consensus, or opinion expressed in discussion does NOT constitute explicit authorization — see `020-go-prohibitions.md` §1 |
| **Batch carry-forward** | Authorization carries forward within a batch via persisted batch state file; no re-authorization needed between issues |

## Post-Implementation Workflow

1. Push feature branch to remote
2. Generate compare URL for review
3. Report completion to issue (NO URL) and URL in chat
4. HALT — do NOT create PR without explicit instruction
5. WAIT for "create a PR" instruction

## Sub-Agent Spawning

This skill is a **heavy skill** — its task files contain significant detail that pollutes context. When the main agent needs authorization verification with re-evaluation, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~597 words)
2. Main agent identifies the needed task
3. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use approval-gate skill --task <task-name> with context: issue=#N, <session-context>")`
4. Sub-agent loads: this SKILL.md + relevant task file + required guidelines
5. Sub-agent executes verification in isolation, returns authorization result
6. Main agent receives result — no full approval-gate content in main context

**Sub-agent context parameters:** Pass issue number, `WORKTREE_PATH`, `GIT_OWNER`, `GIT_REPO` from session init. When `WORKTREE_PATH` is set, sub-agents MUST receive it and use it as the base directory for all file operations and git commands.

## Cross-References

- Related skills: `git-workflow` (branch operations, cleanup), `pr-creation-workflow` (PR timing), `issue-review` (authorization status)
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`
- Related skill tasks: `approval-gate --task verify-sub-issues` (sub-issue verification), `git-workflow --task cleanup` (post-merge closure)
- Label state machine: `141-planning-status-tracking.md §10` (label add/remove actions for this skill)

```yaml+symbolic
schema_version: "1.0"
last_updated: "2026-04-12T12:00:00Z"
rules:
  - id: approval-gate-skill-001
    title: "Pre-implementation authorization verification"
    conditions:
      all:
        - "spec_exists == true"
        - "user_authorized == false"
    actions:
      - HALT
    conflicts_with: []
    requires: [approval-gate-001]
    triggers: [git-workflow]
    source: "approval-gate/SKILL.md §Authorization Requirements"

  - id: approval-gate-skill-002
    title: "Multi-task cascade: authorization extends from plan to all sub-issues"
    conditions:
      all:
        - "plan_has_sub_issues == true"
        - "user_authorized == true"
    actions:
      - PROCEED
    conflicts_with: []
    requires: [approval-gate-002]
    triggers: [divide-and-conquer, executing-plans]
    source: "approval-gate/SKILL.md §Multi-task cascade"

  - id: approval-gate-skill-003
    title: "Post-implementation: push then halt"
    conditions:
      all:
        - "implementation_complete == true"
        - "pr_not_created == true"
    actions:
      - INVOKE(git-workflow)
      - HALT
    conflicts_with: []
    requires: []
    triggers: [git-workflow]
    source: "approval-gate/SKILL.md §Post-Implementation Workflow"
```