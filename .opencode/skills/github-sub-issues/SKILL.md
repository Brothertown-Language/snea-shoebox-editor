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

## Sub-Issue Verification Gate (MANDATORY Before Implementation)

1. Call `github_issue_read method=get_sub_issues` on the **plan** issue (not the spec)
2. **If empty AND multi-task:** AUTO-CREATE sub-issues under the plan immediately, then proceed — no separate authorization needed
3. **If sub-issues exist:** Verify phase being implemented is among them, proceed

**Authorization for the parent plan covers sub-issue creation.** When `get_sub_issues` returns empty for an approved multi-task plan, auto-create and proceed.

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

Before implementing ANY subtask: get parent STATUS, extract authorized subtask, verify match, report decision to user. STATUS format: `STATUS: X.Y` where X = phase, Y = subtask within phase.

## Prohibited Halts

- Halting to ask "should I create sub-issues?" when the plan is already approved
- Treating sub-issue creation as a separate implementation phase
- Implementing a phase that exists only as text in plan issue body

## Cross-References

- Related skills: `git-workflow` (before starting implementation), `approval-gate` (pre-implementation check)
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`
- Issue format: See `143-planning-spec-templates.md` for spec structure and `144-planning-spec-examples.md` for examples