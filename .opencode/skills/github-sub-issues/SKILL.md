---
name: github-sub-issues
description: Use when a multi-task spec needs phase-level sub-issues created or linked. Triggers on: sub-issue, phase issue, multi-task, create sub issue, link issue, task breakdown, subtask, parent issue.
type: technique
license: MIT
compatibility: opencode
---

# GitHub Sub-Issues Workflow

## Overview

Ensures multi-task plans have proper sub-issue structure before implementation begins. Sub-issues track phases as separate GitHub Issues linked to the parent **plan** (not the spec), providing state tracking, progress visibility, and proper parent-child relationships.

The hierarchy is: **Spec → (linked reference) → Plan → Sub-issues**. Sub-issues are children of the plan issue, NOT the spec.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `create-sub-issue` | Create and link a single sub-issue to parent | ~300 |
| `link-sub-issue` | Link an existing issue as sub-issue to parent | ~200 |
| `track-hierarchy` | Verify and manage parent-child relationships | ~250 |

## Invocation

- `/skill github-sub-issues --task create-sub-issue` - Create a phase-level sub-issue
- `/skill github-sub-issues --task link-sub-issue` - Link existing issue as sub-issue
- `/skill github-sub-issues --task track-hierarchy` - Verify hierarchy structure
- `/skill github-sub-issues` - Overview only

## Single-Task Exemption

Single-task plans do NOT require sub-issues. A plan is "single-task" if it has exactly ONE implementation task/phase with no decomposition needed. If single-task: proceed without sub-issue verification. If multi-task: sub-issues are MANDATORY.

## Sub-Issue Verification Gate (SUPERSEDED — Use `approval-gate --task verify-authorization`)

**⚠️ This verification gate is SUPERSEDED.** Sub-issue verification is now consolidated into `approval-gate --task verify-authorization` (Step 5) as the single authoritative readiness check. The content below is retained for reference only.

**Authoritative check:** `approval-gate --task verify-authorization` Step 5 handles:
- Verifying sub-issues exist under the Plan
- Verifying sub-issue structure matches Plan phases
- Verifying sub-issue bodies contain phase context (leveraging Phase 1 enrichment)
- Adversarial verification of sub-issue state (open/closed, labels, parent linkage)
- Auto-creating sub-issues under the plan when missing

**This skill (`github-sub-issues`) remains the authoritative source for:**
- Sub-issue creation (`create-sub-issue` task)
- Sub-issue linking (`link-sub-issue` task)
- Hierarchy tracking (`track-hierarchy` task)

---

<details>
<summary>Historical verification gate content (reference only — do NOT invoke this gate directly)</summary>

1. Call `github_issue_read method=get_sub_issues` on the **plan** issue (not the spec)
2. **If empty AND multi-task:** AUTO-CREATE sub-issues under the plan immediately, then proceed — no separate authorization needed
3. **If sub-issues exist:** Verify phase being implemented is among them, proceed

**Authorization for the parent plan covers sub-issue creation.** When `get_sub_issues` returns empty for an approved multi-task plan, auto-create and proceed.

</details>

## Phase-Level vs Step-Level

Sub-issues = PHASES, not steps. Phases are approval units; steps are implementation details within phases.

```
✅ CORRECT: Phase-level sub-issues under plan
PLAN #200: [PLAN] Feature Name
├── Task #201: [Task: #200] Create database schema
├── Task #202: [Task: #200] Implement API endpoints
└── Task #203: [Task: #200] Build UI components

❌ WRONG: Step-level sub-issues (too granular)
├── Task #201: Step 1.1 - Create table
├── Task #202: Step 1.2 - Add index
```

## Title Format

Format: `[Task: #<plan-number>] <descriptive-title>`

Titles MUST describe WHAT the task accomplishes, not just the phase type. "Phase 1 - Implementation" is PROHIBITED. "[Task: #200] Add OAuth2 authentication" is correct.

## Context Efficiency (CRITICAL)

API responses from `github_issue_write` and `github_sub_issue_write` contain full plan issue body (~8KB each). Creating + linking 8 sub-issues produces ~128KB of context — enough to block implementation.

**MANDATORY:** Extract ONLY issue number and database ID from API responses. Discard full response body immediately.

## Database ID Requirement

Use the `.id` field from response (e.g., `4129879155`), NOT the issue number (e.g., `10`). Get via `github_issue_read method=get` response.

## STATUS Gate Verification

Before implementing ANY subtask: get parent STATUS, extract authorized subtask, verify match, report decision to user.

**STATUS format recognition (prose-driven, backward-compatible):**

| Format | Example | Meaning |
|--------|---------|---------|
| `in progress — {concern}, Step {N}` | `in progress — Authorization Gate, Step 1` | Working on a specific step (prose-driven, recommended) |
| `completed — {concern}` | `completed — Authorization Gate` | Phase/concern done (prose-driven, recommended) |
| `{concern} — {task description}` | `Authorization Gate — verify label state` | Active task within concern (prose-driven, recommended) |
| `X.Y` | `1.2` | Phase 1, step 2 (numeric, backward-compatible) |
| `completed` | `completed` | All work done (both formats) |
| `X.Y (REVISED - NEEDS APPROVAL)` | `1.2 (REVISED - NEEDS APPROVAL)` | Spec was modified (numeric, backward-compatible) |
| `{concern} (REVISED - NEEDS APPROVAL)` | `Authorization Gate (REVISED - NEEDS APPROVAL)` | Spec was modified (prose-driven) |

When matching STATUS to sub-issues, match the concern name in the STATUS to the sub-issue title/description. Numeric `X.Y` format is still recognized for backward compatibility but prose-driven formats are recommended for new specs and plans.

## Prohibited Halts

- Halting to ask "should I create sub-issues?" when the plan is already approved
- Treating sub-issue creation as a separate implementation phase
- Implementing a phase that exists only as text in plan issue body

## Sub-Agent Tasks

### Execution Mode Table

| Task | Words | Mode |
|------|-------|------|
| `create-sub-issue` | ~300 | inline |
| `link-sub-issue` | ~200 | inline |
| `track-hierarchy` | ~250 | inline |

**Note:** All tasks are under 1,000 words — inline execution. No sub-agent dispatch needed for individual sub-issue operations. However, bulk creation (3+ sub-issues at once) benefits from sub-agent dispatch to keep creation API responses out of main context.

### Dispatch Context Schema (Bulk Creation)

```yaml
parent_plan: <N>
phases: [{title: <str>, body: <str>, labels: [<str>]}]
session_vars:
  GIT_OWNER: <from-session>
  GIT_REPO: <from-session>
  DEV_NAME: <from-session>
  DEV_EMAIL: <from-session>
  WORKTREE_PATH: <from-session>
```

### Result Contract (Bulk Creation)

```yaml
status: DONE
task: create-sub-issues
sub_issues_created: [<N>]
sub_issues_linked: [<N>]
parent_issue: <N>
```

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `git-workflow` in Cross-References section | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References section | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `writing-plans` in auto-dispatch chain | File exists at `.opencode/skills/writing-plans/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `create-sub-issue` | File exists at `.opencode/skills/github-sub-issues/tasks/create-sub-issue.md` | MISSING-TRACEABILITY if missing |
| Task table entry `link-sub-issue` | File exists at `.opencode/skills/github-sub-issues/tasks/link-sub-issue.md` | MISSING-TRACEABILITY if missing |
| Task table entry `track-hierarchy` | File exists at `.opencode/skills/github-sub-issues/tasks/track-hierarchy.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` authorization cascade behavior | Matches actual SKILL.md: plan approval cascades to sub-issues | CONFLICTING if mismatched |
| `git-workflow` cleanup behavior | Matches actual SKILL.md: `cleanup` task handles post-merge closure | CONFLICTING if mismatched |
| `writing-plans` auto-dispatch | Matches actual SKILL.md: `create` task creates plan then dispatches to github-sub-issues | CONFLICTING if mismatched |

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

## Live Verification: Sub-Issue State (MANDATORY)

**🚫 CRITICAL: When this skill reads sub-issue metadata (state, labels, parent linkage), it MUST verify against live GitHub API. Trusting cached sub-issue state is a VERIFICATION-GAP finding per `065-verification-honesty.md`.**

| Metadata Trust Point | Verification Action | Tool Call | Problem Class |
|---------------------|-------------------|-----------|---------------|
| Sub-issue claimed as "open" | Verify actual state via GitHub API | `github_issue_read(method=get, issue_number=N)` → check `state` | CONFLICTING |
| Sub-issue claimed as linked to parent | Verify parent-child relationship exists | `github_issue_read(method=get_sub_issues, issue_number=N)` → check linkage | MISSING-TRACEABILITY |
| Sub-issue body claimed to contain phase context | Verify body actually contains relevant context | `github_issue_read(method=get, issue_number=N)` → check body content | MISSING-ELEMENT |
| Sub-issue labels claimed | Verify labels match expectations | `github_issue_read(method=get_labels, issue_number=N)` → check label set | CONFLICTING |
| Sub-issue database ID claimed | Verify ID is valid for sub-issue write operations | `github_issue_read(method=get)` → verify `.id` field | VERIFICATION-GAP |

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
| Sub-issue closed but claimed open | CONFLICTING | auto-fix | Update tracking to reflect actual state |
| Parent-child link missing | MISSING-TRACEABILITY | conditional | Re-link via `github_sub_issue_write` |
| Sub-issue body empty or missing context | MISSING-ELEMENT | conditional | Re-populate sub-issue body |
| Labels don't match expectations | CONFLICTING | auto-fix | Update labels |
| Database ID invalid | VERIFICATION-GAP | conditional | Re-fetch valid ID |

## Cross-References

- Related skills: `approval-gate` (sub-issue verification gate — the single authoritative readiness check), `git-workflow` (before starting implementation), `writing-plans` (auto-dispatch chain: writing-plans → github-sub-issues)
- Superseded gate: `github-sub-issues` verification gate is superseded by `approval-gate --task verify-authorization` Step 5
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`
- Issue format: See `143-planning-spec-templates.md` for spec structure and `144-planning-spec-examples.md` for examples