---
name: executing-plans
description: Use when executing an approved plan step-by-step or moving through implementation gates sequentially. Triggers on: execute plan, next step, continue implementation, plan approved, start implementation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: executing-plans

## Overview

Plan execution skill that dispatches to `divide-and-conquer/assemble-work` for implementation. This skill is a thin dispatch layer — all implementation logic flows through the unified work workflow. It receives plan context from `approval-gate` after plan approval.

**Every approval follows one path:** `executing-plans` → `divide-and-conquer/assemble-work` → work branch → pr-creation → one PR.

**There is no single-issue bypass.** Single issue = work of one = one sub-agent.

## Received Context

When dispatched from `approval-gate` after plan approval, the following context is available:

```yaml
plan_issue: <number>
spec_issue: <number, extracted from plan body>
github.owner: "<from-session>"
github.repo: "<from-session>"
worktree.path: "<worktree path>"
phase_progress:
  completed_phases: "<prose listing of completed phases by concern name, from Plan STATUS>"
  concern_boundaries_crossed: "<prose description of architectural concern transitions from plan>"
  verification_evidence: "<prose summary of what was verified and outcomes>"
```

**Verification:** If `plan_issue` is not present in the dispatch context, HALT — this skill requires plan context to track progress against the correct issue.

**Phase progress composition:** Before dispatching to `divide-and-conquer`, `executing-plans` reads the Plan STATUS marker and concern boundary annotations to compose the initial `phase_progress`. If no phases are complete yet, the field notes that explicitly. The `assemble-work` task then maintains and extends phase progress as each sub-agent completes.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `start` | Dispatch to divide-and-conquer/assemble-work for implementation | ≈200 |
| `step` | Legacy — redirects to divide-and-conquer/orchestrate | ≈100 |
| `progress` | Legacy — redirects to divide-and-conquer/orchestrate | ≈100 |
| `verify` | Redirects to verification-before-completion | ≈100 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Invocation

- `/skill executing-plans` — Overview only
- `/skill executing-plans --task start` — Dispatch to divide-and-conquer/assemble-work
- `/skill executing-plans --task step` — Redirects to divide-and-conquer/orchestrate
- `/skill executing-plans --task progress` — Redirects to divide-and-conquer/orchestrate
- `/skill executing-plans --task verify` — Redirects to verification-before-completion
- `/skill executing-plans --task completion` — Invoke when workflow halts at any point

## Operating Protocol

1. **Verify plan context:** Before dispatching, confirm `plan_issue` is present in received context. If missing, HALT and report.

2. **Dispatch to divide-and-conquer:** The `start` task invokes `divide-and-conquer --task assemble-work` which handles all implementation — single issue or work — through the unified workflow. Pass `plan_issue` in the dispatch context.

3. **No direct implementation:** This skill does not implement directly. It dispatches.

4. **Single issue = work of one:** There is no separate path for single issues. The `assemble-work` task handles single-issue dispatch as the default code path.

5. **Progress reports against plan:** All progress tracking references the plan issue (not the spec issue). The plan is the implementation tracking artifact; the spec is the requirements artifact.

## Dispatch Order

```
Plan approved (approval-gate)
  → executing-plans --task start
  → divide-and-conquer --task assemble-work
  → verification-before-completion
  → finishing-a-development-branch
  → git-workflow/review-prep
```

**Progress is tracked against the plan issue.** The plan references the spec via body text (linked reference), not via GitHub sub-issue link.

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `divide-and-conquer` in Cross-References and Dispatch Order | File exists at `.opencode/skills/divide-and-conquer/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References and Dispatch Order | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `verification-before-completion` in Cross-References and Dispatch Order | File exists at `.opencode/skills/verification-before-completion/SKILL.md` | MISSING-TRACEABILITY if missing |
| `finishing-a-development-branch` in Cross-References and Dispatch Order | File exists at `.opencode/skills/finishing-a-development-branch/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` in Cross-References and Dispatch Order | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `writing-plans` in Received Context | File exists at `.opencode/skills/writing-plans/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `start` | File exists at `.opencode/skills/executing-plans/tasks/start.md` | MISSING-TRACEABILITY if missing |
| Task table entry `step` | File exists at `.opencode/skills/executing-plans/tasks/step.md` | MISSING-TRACEABILITY if missing |
| Task table entry `progress` | File exists at `.opencode/skills/executing-plans/tasks/progress.md` | MISSING-TRACEABILITY if missing |
| Task table entry `verify` | File exists at `.opencode/skills/executing-plans/tasks/verify.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/executing-plans/tasks/completion.md` | MISSING-TRACEABILITY if missing |
| `divide-and-conquer` dispatch behavior | Matches actual SKILL.md: `assemble-work` task handles implementation | CONFLICTING if mismatched |
| `approval-gate` dispatch behavior | Matches actual SKILL.md: `verify-authorization` dispatches to `executing-plans` | CONFLICTING if mismatched |
| `verification-before-completion` redirect | Matches actual SKILL.md: `verify` task exists and redirects | CONFLICTING if mismatched |

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

## Cross-References

- Related skills: `divide-and-conquer` (implementation orchestration), `approval-gate` (authorization), `verification-before-completion` (evidence), `finishing-a-development-branch` (branch readiness), `git-workflow` (branch/PR/cleanup), `writing-plans` (plan creation)

Co-authored with AI: <AgentName> (<ModelId>)

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.