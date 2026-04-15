---
name: spec-creation
description: Use when creating a spec or writing a specification. Triggers on: create spec, write spec, spec creation, spec writing, structure spec, specification.
type: technique
license: MIT
compatibility: opencode
---

# Skill: spec-creation

## Overview

Structured discipline for spec writing — enforcing requirements extraction, problem decomposition, interface-first thinking, constraints ledgers, risk analysis, operational requirements, traceability, and change control at creation time. Invoked after brainstorming completes exploration.

**Pipeline position:** `brainstorming (explore) → spec-creation (structure & write) → spec-auditor (audit) → approval-gate (authorize) → writing-plans (plan)`

**Source:** This skill extracts and extends the spec-writing concerns from `brainstorming` Steps 7-9 (write spec, self-review, user review), adding structured discipline for principles not previously enforced at creation time.

## Persona

You are a Spec Architect. Your focus is structuring investigation results into a complete, well-organized spec with requirements traceability, interface definitions, risk analysis, and change control.

## Tasks

| Task | Purpose | Principles | Skippable? |
|------|---------|------------|------------|
| `requirements` | Extract explicit, implicit, constraints, non-requirements; build constraints ledger | #1, #7 | No — foundation for all other tasks |
| `decompose` | Break into discrete units; define interfaces first (APIs, data contracts, schemas) | #2, #5 | Only for trivial bug fixes with one obvious fix |
| `traceability` | Map requirements to sections, tests, implementation steps | #3 | Only for single-requirement specs |
| `risk` | Analyze risk, blast radius, failure propagation, operational needs | #8, #9 | Only for simple bug fixes with no deployment impact |
| `write` | Assemble spec, create GitHub Issue, output exec summary + URL + byline | #4, #6, #10 | No — mandatory assembly step |
| `change-control` | Version spec, document rationale and impact analysis for changes | #12 | Only for initial spec creation (not revisions) |

## Invocation

- `/skill spec-creation` — Full workflow (requirements → decompose → traceability → risk → write → change-control)
- `/skill spec-creation --task requirements` — Requirements extraction only
- `/skill spec-creation --task write` — Assemble spec from structured outputs only
- `/skill spec-creation --task change-control` — Version/reason a spec revision

## Operating Protocol

1. **Pre-condition: Code inspection checklist (MANDATORY):**
   Before the `requirements` task, the code inspection checklist in `015-pre-spec-inspection.md` MUST be completed when the spec proposes changes to existing code. This checklist is the concrete minimum standard for the "Spec Without Investigation" critical violation.
   - If brainstorming already completed the checklist (Step 0 in `explore.md`), reference those results — do not re-investigate.
   - If the checklist was NOT completed during brainstorming, complete it before proceeding to `requirements`.
   - Exempt: New greenfield features with no existing code interaction; trivial typos with no code interaction.
   - Incomplete inspection = HALT and complete the checklist first.

2. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when:
   - Brainstorming exploration completes (terminal state transitions here)
   - User says "write spec", "create spec", "spec creation"
   - User provides investigation results and asks for a structured spec
   - DO NOT skip to write without completing applicable prerequisite tasks

2. **Simplicity heuristic for task skipping:**

   | Spec Complexity | Tasks | Example |
   |-----------------|-------|---------|
   | Simple (≤2 files, no architectural impact, obvious fix) | requirements + write | Bug fix with clear solution |
   | Moderate (multiple requirements, some interfaces) | + decompose + traceability | Feature addition |
   | Complex (architectural change, deployment impact, multi-phase) | All tasks | New subsystem |

3. **Task completion gate:** Each task produces a structured output. The `write` task assembles these outputs into the final spec. Do NOT invoke `write` until prerequisite tasks are complete.

4. **Exit condition:** Spec written to GitHub Issue, self-reviewed, user-reviewed on the issue. HALT and wait for approval before proceeding to writing-plans.

## Simplicity Heuristic

**Simple specs** (affects ≤2 files, no architectural impact, single-requirement, bug fix with obvious fix):
- Skip: `decompose`, `traceability`, `risk`, `change-control`
- Required: `requirements`, `write`

**Moderate specs** (multiple requirements, some interfaces affected):
- Skip: `change-control`
- Required: `requirements`, `decompose`, `traceability`, `write`

**Complex specs** (architectural change, deployment impact, multi-phase):
- Required: All tasks
- No skipping

## Key Principles Enforced

| # | Principle | Task |
|---|-----------|------|
| 1 | Requirements Extraction | `requirements` |
| 2 | Problem Decomposition | `decompose` |
| 3 | Traceability | `traceability` |
| 4 | Ambiguity Elimination | `write` |
| 5 | Interface-First Thinking | `decompose` |
| 6 | Acceptance Criteria Definition | `write` |
| 7 | Constraints & Assumptions Ledger | `requirements` |
| 8 | Risk & Blast Radius Analysis | `risk` |
| 9 | Operational Requirements | `risk` |
| 10 | Deliverable Structure Discipline | `write` |
| 11 | Plan-From-Spec Decomposition | (downstream: `writing-plans`) |
| 12 | Change Control | `change-control` |

## Enforcement Mechanism

**Skills MUST enforce spec-creation — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before `requirements` task:**
   - Has the code inspection checklist (`015-pre-spec-inspection.md`) been completed? (or explicitly exempt per greenfield/typo criteria)
   - If not completed and spec touches existing code, HALT and complete the checklist first

2. **Before `write` task:**
   - Has `requirements` task been completed? (or explicitly skipped for trivial specs)
   - Has exploration (brainstorming) output been referenced?
   - Are acceptance criteria defined?

3. **After `write` task:**
   - GitHub Issue created with `[SPEC]` prefix and `needs-approval` label?
   - Chat output is exec summary + URL + byline ONLY? (no full spec dump)
   - Spec self-review completed? (placeholder scan, consistency check, ambiguity check)
   - User directed to review on the GitHub Issue (not in chat)?

4. **What does NOT bypass spec-creation:**
   - "skip spec-creation" → NOT allowed (even simple specs need `requirements` + `write`)
   - "brainstorming already wrote the spec" → Brainstorming no longer writes specs; this skill does
   - "just show me the spec in chat" → NOT allowed; spec MUST be persisted as GitHub Issue

### Enforcement Messages

**Missing requirements:**

```
Requirements extraction required before spec assembly.

The `requirements` task identifies explicit, implicit, and constraint requirements that form the foundation of your spec.

To invoke: /skill spec-creation --task requirements
```

## Evidence Artifact Requirements

Every task in this skill that asserts a verification checkpoint (self-review, traceability, change control) MUST produce a tool-call artifact demonstrating the verification was performed. Assertions without tool-call evidence are verification honesty violations per `065-verification-honesty.md`.

### Verification Table

| Checkpoint | Verification Action | Tool Call | Problem Class |
|------------|-------------------|-----------|---------------|
| Self-review placeholder scan | Verify no "TBD", "TODO", incomplete sections remain in the spec body | `github_issue_read(method=get)` → search body for placeholder patterns | STRUCTURE-VIOLATION |
| Self-review consistency | Cross-reference requirement IDs between sections; verify no contradictions | `github_issue_read(method=get)` → parse section anchors | CONFLICTING |
| Traceability bidirectional | Verify every requirement maps to a section and every section maps to a requirement | `github_issue_read(method=get)` → check trace references | MISSING-TRACEABILITY |
| Traceability target existence | Verify that referenced issues, specs, and code actually exist | `github_issue_read(method=get, issue_number=N)` for each referenced issue; `srclight_get_symbol(name=N)` for each referenced symbol | VERIFICATION-GAP |
| Change-control STATUS exemption | Verify that STATUS markers claiming exemption (initial creation, non-substantive) actually qualify | `github_issue_read(method=get)` → check STATUS against revision history | CONFLICTING |
| Spec created as Issue | Verify the spec exists as a GitHub Issue with `[SPEC]` prefix and `needs-approval` label | `github_issue_read(method=get)` → check title, `github_issue_read(method=get_labels)` → check label | MISSING-ELEMENT |

### Evidence Format

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

### Finding Classification

Findings from evidence verification follow the three-tier model:

| Classification | When | Action |
|----------------|------|--------|
| auto-fix | Safe, mechanical corrections (placeholder removal, reference fix) | Apply fix, note in evidence |
| conditional | Requires scope/safety check before applying (traceability gap, STATUS claim) | Verify scope, then apply if safe |
| flag-for-review | Requires domain judgment (contradictions, ambiguous STATUS exemption) | Report in findings, do not apply |

## Cross-References

- **Calls:** `github-issue-creation` (spec persistence — `write` task invokes pre-creation → single-task-check → creation)
- **Preceded by:** `brainstorming` (exploration only — Steps 7-9 moved here)
- **Followed by:** `spec-auditor` (quality audit — verifies what this skill produces)
- **Parallel with:** `approval-gate` (authorization — waits for spec to be approved)
- **Downstream:** `writing-plans` (plan creation — transforms approved spec into implementation plan)
- **Source:** Adapted and extended from `brainstorming` Steps 7-9 (not a verbatim move)
- **Guidelines:** `065-verification-honesty.md` (evidence artifacts)
- **Related subtask:** `spec-auditor --task ground-truth` (adversarial metadata verification model)

Co-authored with AI: <AI-Name> (<model-id>)