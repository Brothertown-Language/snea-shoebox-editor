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
   - Byline: `🤖 <AgentName> (<ModelID>) completed`

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

## Auto-Close Procedure (Post-Merge Verification)

When `verify-already-implemented` identifies issues that were already implemented via a merged PR, the following auto-close procedure MUST be followed:

1. **Verify PR merge via GitHub API** — Use `github_pull_request_read(method=get)` on the referenced PR. Confirm `merged == true` and `state == "closed"`. Do NOT rely on visual inspection or memory.

2. **Close each verified-already-implemented issue** with a comment referencing the merged PR:
   - Use `github_issue_write(method=update, state="closed", state_reason="completed")`
   - Use `github_add_issue_comment` with a reference to the merged PR (e.g., `Closing: implementation verified via merged PR #N`)

3. **Remove `needs-approval` label** if present — Use `github_issue_read(method=get_labels)` to check, then remove via label update if found.

4. **Report closure in chat output** — Include:
   - Which issues were closed
   - The merged PR that verified the implementation
   - Byline: `🤖 <AgentName> (<ModelID>) completed`

**⚠️ CRITICAL:** Do NOT close issues without verifying PR merge via the GitHub API. Assuming a PR was merged without API confirmation is a verification dishonesty violation per `065-verification-honesty.md`.

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

## Adversarial Verification: Implementation State

**Before claiming a spec is "already implemented," verify against actual codebase and git state — not claimed state, not cached results, not visual inspection.**

### Verify Success Criteria Against Live Code

```
For each success criterion:
  - Use actual tool calls: read, grep, srclight_search_symbols, srclight_get_signature
  - Read the relevant file(s) directly — do NOT rely on memory of previous reads
  - If criterion references specific file paths → verify files exist with glob
  - If criterion references specific functions/classes → verify with srclight_get_signature
  - If criterion references specific content → verify with grep or read
  - Record: tool used, file path, line reference, summary of evidence
```

**Evidence artifact:** Tool call results (read, grep, srclight) for each criterion — NOT just "PASS/FAIL" assertions.

### Verify Implementation Source

```
When claiming implementation exists:
  - Check git log for commits referencing the issue number
  git log --oneline --grep="#N" origin/dev
  
  - If commits found → verify they are merged to dev:
    git branch --contains <commit-sha> | grep dev
  
  - If PR references found → verify PR merge via GitHub API:
    github_pull_request_read(method=get, pullNumber=M)
    → confirm merged == true AND state == "closed"
  
  - Do NOT trust "looks implemented" from file reads alone
  - Do NOT trust cached PR merge status from previous sessions
```

**Evidence artifact:** Git log output and/or `github_pull_request_read` response confirming merge status.

### Verify No Stale Implementation Claims

```
If success criteria reference specific code structure:
  - Verify that code structure is CURRENT, not from a previous version
  - If a file was modified after the "already implemented" check → re-verify
  - Use srclight_recent_changes to check if relevant files changed recently
  - If files changed since implementation → VERIFICATION-GAP (re-verify all criteria)
```

**Evidence artifact:** Recent changes output showing file modification dates relative to implementation.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Criterion cannot be verified | VERIFICATION-GAP | flag-for-review | Developer must confirm manually |
| Implementation exists but not merged | VERIFICATION-GAP | flag-for-review | Cannot autoclose — PR must merge first |
| Implementation claim from stale session | STRUCTURE-VIOLATION | conditional | Re-verify all criteria with fresh tool calls |
| Code changed since implementation | VERIFICATION-GAP | flag-for-review | Re-verify affected criteria |
| PR claimed merged but API says open | CONFLICTING | flag-for-review | Do NOT autoclose — verify merge manually |
| File/symbol referenced in criterion does not exist | MISSING-TRACEABILITY | flag-for-review | Criterion may be inapplicable or spec may be stale |

## Context Required

- Preceded by: `verify-authorization`, `verify-codebase`, `verify-blockers`
- Supersedes: None (new task)
- Related: `post-implementation` (used when implementation IS needed)
- Label state machine: `141-planning-status-tracking.md §10` (remove `needs-approval` on autoclose)