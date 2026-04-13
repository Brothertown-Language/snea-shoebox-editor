# Task: verify-already-implemented

## Purpose

Check whether a spec is already fully implemented before starting work. When all success criteria are verifiably met with no file modifications needed, autoclose the issue instead of proceeding to implementation.

## Pre-Conditions

- **Load guideline:** `.opencode/guidelines/065-verification-honesty.md` before proceeding — verification claims must be backed by actual tool calls, not memory

## Entry Criteria

- Authorization verified
- Codebase checked (no staleness)
- No blockers found

## Exit Criteria

- If already implemented: Issue closed with evidence comment, `needs-approval` label removed, HALT
- If not already implemented: Proceed to implementation workflow

## Procedure

### Step 1: Extract Success Criteria

From the spec issue, extract every success criterion:
- List each criterion verbatim
- Number each criterion for traceability
- Note any that are ambiguous or subjective

### Step 2: Verify Each Criterion Against Codebase

For each success criterion:
- Read the relevant file(s) and verify the criterion is met
- Use actual tool calls (read, grep, srclight) — NOT memory
- Record evidence: file path, line number, code/content snippet
- Mark each criterion PASS or FAIL with evidence

**⚠️ CRITICAL: Use tool calls for every verification. Memory recall is NOT evidence. Per `065-verification-honesty.md`, reporting unverified information as verified is a critical violation.**

### Step 3: Decision

| All criteria PASS? | Action |
|--------------------|--------|
| YES — ALL pass | Proceed to Step 4 (autoclose) |
| NO — ANY fail | Proceed to normal implementation |

**If ANY criterion fails, do NOT autoclose.** Proceed to the standard implementation workflow. A partially-implemented spec requires implementation, not autoclose.

### Step 4: Autoclose Already-Implemented Issue

When ALL success criteria are verified as already met:

1. **Post close comment** on the GitHub Issue:

   All success criteria verified as already implemented. No file modifications required.

   <criterion-by-criterion evidence summary>

   Closing as already implemented.

2. **Remove `needs-approval` label** from the issue (if present)

3. **Close the issue** with state `closed` and state_reason `completed`

4. **Post chat output** with executive summary:
   - What happened: Spec #N approved but all success criteria already met
   - Outcome: Issue autoclosed as already implemented
   - Byline: `🤖 OpenCode (ollama-cloud/glm-5.1) completed`

5. **HALT** — no branch, no PR, no implementation needed

## Evidence Requirements

Each criterion verification MUST include:
- **Tool call**: The actual read/grep/srclight tool used
- **File path**: Where the evidence was found
- **Line reference**: Line number or range
- **Summary**: One-sentence statement of why the criterion is met

**Example evidence format:**

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | SKILL.md has task table with new entry | PASS | `approval-gate/SKILL.md:22` shows new task row |
| 2 | Task file exists at correct path | PASS | `tasks/verify-already-implemented.md` verified via read |
| 3 | Guideline section updated | PASS | `000-critical-rules.md:688-713` includes autoclose exemption |

## What This Is NOT

This task does NOT replace:
- `verify-codebase` — That checks staleness (files moved, signatures changed)
- `verify-blockers` — That checks for blocking dependencies
- Bug fix without spec — This requires an approved spec issue first

This task ONLY handles the case where an approved spec describes changes that are already present in the codebase with zero modifications needed.

## Relationship to PR Requirements

Per `000-critical-rules.md` → "Skipping PR for Documentation/Guideline Changes":

| Scenario | PR Required? |
|----------|-------------|
| Files modified during implementation | ✅ YES |
| Zero files modified (already implemented) | ❌ NO |

Autoclose bypasses the PR workflow because no branch, commits, or PR are needed — the work is already done.

## Context Required

- Preceded by: `verify-authorization`, `verify-codebase`, `verify-blockers`
- Supersedes: None (new task)
- Related: `post-implementation` (used when implementation IS needed)
- Label state machine: `141-planning-status-tracking.md §10` (remove `needs-approval` on autoclose)