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

### Step 3: Gate Evidence Audit (MANDATORY)

**🚫 CRITICAL — STRUCTURAL CHECKPOINT: Before deciding autoclose vs implementation, verify that Gate 1 (sub-issue enumeration) and Gate 2 (success criteria verification) were actually EXECUTED — not just read. This step is the same evidence audit pattern from `pre-implementation-analysis` Step 0.5.**

#### VAI-1: Verify Gate 1 Evidence

1. Did you call `github_issue_read(method=get_sub_issues, issue_number=<candidate>)`? If NO → STOP. Run Gate 1 now.
2. For EACH sub-issue, did you produce a tool-call artifact verifying its state? If NO → STOP. Run Gate 1 verification now.
3. For each closed sub-issue, did you search for merged PR evidence? If NO → STOP. Run closure legitimacy check now.

#### VAI-2: Verify Gate 2 Evidence

1. Did you extract every success criterion from the issue body? If NO → STOP. Run Gate 2 now.
2. For each success criterion, did you perform a direct verification action against the codebase? If NO → STOP. Run Gate 2 verification now.
3. For each criterion, is there a tool-call artifact? If NO → STOP. Re-run with evidence collection.

#### VAI-3: Produce Gate Evidence Audit Table

```markdown
## Gate Evidence Audit Table

| Issue # | Sub-issues Enumerated? | All Sub-issues Verified? | Closure Legitimacy Verified? | Success Criteria Extracted? | All Criteria Verified? | Final Classification |
|---------|------------------------|--------------------------|-------------------------------|-----------------------------|------------------------|---------------------|
| #N | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | already-implemented / NOT already-implemented |
```

**If ANY row has ❌:** The issue CANNOT be autoclosed. Proceed to normal implementation (Step 5).

### Step 4: Decision

| All criteria PASS? | Action |
|--------------------|--------|
| YES — ALL pass + Gate Evidence Audit Table all ✅ | Proceed to Step 5 (autoclose) |
| NO — ANY fail OR Gate Evidence Audit Table has ❌ | Proceed to normal implementation |

**If ANY criterion fails, do NOT autoclose.** Proceed to the standard implementation workflow. A partially-implemented spec requires implementation, not autoclose.

### Step 5: Autoclose Already-Implemented Issue

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

## Pre-Autoclose Sub-Issue Verification

**🚫 CRITICAL: Before autoclosing an issue as "already implemented," verify that ALL sub-issues (if any) are also legitimately closed. A parent issue cannot be autoclosed if any sub-issue was closed without a merged PR.**

### Step AC-1: Check for Sub-Issues

```
sub_issues = github_issue_read(method="get_sub_issues", issue_number=issue_number)

if sub_issues:
    # Parent has sub-issues — each must be verified before autoclose
    for sub_issue in sub_issues:
        verify sub_issue is legitimately closed (see Step AC-2)
else:
    # No sub-issues — proceed to standard autoclose verification
    PROCEED to Step 4
```

### Step AC-2: Verify Each Sub-Issue Closure Reason

```
For each sub-issue:
  child = github_issue_read(method="get", issue_number=sub_issue_number)

  if child.state == "closed":
    state_reason = child.get("state_reason", "")

    if state_reason == "not_planned":
      # Sub-issue was intentionally not implemented
      # Parent CANNOT be autoclosed — some work was deliberately skipped
      VERIFICATION-GAP — flag-for-review
      HALT autoclose

    elif state_reason == "completed":
      # Verify a merged PR exists for this sub-issue
      prs = github_search_pull_requests(query=f"Fixes #{sub_issue_number} repo:{GIT_OWNER}/{GIT_REPO}")
      merged_pr_found = False
      for pr in prs:
        pr_detail = github_pull_request_read(method="get", owner=GIT_OWNER, repo=GIT_REPO, pullNumber=pr["number"])
        if pr_detail.get("merged_at") is not None:
          merged_pr_found = True
          break

      if not merged_pr_found:
        # Closed as "completed" but no merged PR — may be premature closure
        VERIFICATION-GAP — flag-for-review
        HALT autoclose

    else:
      # Closed without clear reason
      VERIFICATION-GAP — flag-for-review
      HALT autoclose

  elif child.state == "open":
    # Open sub-issue — parent CANNOT be autoclosed
    MISSING-ELEMENT — proceed to normal implementation
    HALT autoclose
```

### Step AC-3: Verify Cross-References

```
For each sub-issue verified as legitimately closed:
  # Verify the sub-issue's scope is covered by the parent's success criteria
  child_body = github_issue_read(method="get", issue_number=sub_issue_number)["body"]
  parent_body = github_issue_read(method="get", issue_number=issue_number)["body"]

  # If sub-issue covers scope not in parent's success criteria:
  #   The parent may be "implemented" but the sub-issue's specific concern was not addressed
  #   This is unlikely for autoclose scenarios but should be flagged if detected
```

### Pre-Autoclose Verification Finding Classification

| Finding | Problem Class | Classification | Action |
|---------|---------------|----------------|--------|
| All sub-issues closed via merged PR | VERIFIED | auto-proceed | Proceed to autoclose |
| Sub-issue closed as "not_planned" | VERIFICATION-GAP | flag-for-review | Do NOT autoclose parent — work was intentionally skipped |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Do NOT autoclose — may be premature closure |
| Sub-issue still open | MISSING-ELEMENT | conditional | Do NOT autoclose — open sub-issues mean parent is not complete |
| Sub-issue 404 | MISSING-TRACEABILITY | flag-for-review | Developer must resolve missing sub-issue |

**Only proceed to Step 4 (autoclose) when ALL sub-issues are verified as legitimately closed via merged PR.**

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