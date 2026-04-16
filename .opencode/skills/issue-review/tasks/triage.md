# Task: triage

## Purpose

Classify the review path based on content analysis, not label conventions. Two-pass approach: pattern signals first, then AI content verification.

## Entry Criteria

- Gathered data from `gather` task available
- Issue body and comments have been read

## Exit Criteria

- Triage path selected (audit, qa, just-review, or already-handled)
- Confidence level assigned (high, medium, low)
- Reasoning documented

## Triage Paths

| Path | When |
|------|------|
| `audit` | Content looks like a spec (phases/steps, success criteria, edge cases) |
| `analyze-and-spec` | Bug report (crash, error, broken, steps to reproduce, unexpected behavior) |
| `qa` | Feature idea, unclear request, or issue needing clarification (not a bug) |
| `just-review` | Already-audited spec with no new relevant comments |
| `already-handled` | Issue appears complete (approved + implemented) |

## Procedure

### Pass 1 — Pattern Signals (Fast Classification)

Scan gathered data for these signals:

| Signal | Points Toward |
|--------|---------------|
| Body contains "Phase 1:", "Phase 2:", etc. | `audit` |
| Body has "Success Criteria" section | `audit` |
| Body has "Edge Cases" section | `audit` |
| Body has "Affected Files" table | `audit` |
| Body has "Risk Assessment" table | `audit` |
| Comments contain "approved" or "go" | Check if also implemented AND sub-issues verified closed AND cross-references resolved → `already-handled` |
| Comments contain audit finding patterns | `just-review` (if no new non-audit comments) |
| `needs-approval` label present, no explicit auth | `just-review` (report auth status) |
| Body uses bug report language ("crash", "error", "broken") | `analyze-and-spec` |
| Body contains "steps to reproduce" | `analyze-and-spec` |
| Body describes unexpected behavior or regression | `analyze-and-spec` |
| `bug` label present | `analyze-and-spec` (unless content clearly is not a bug) |
| Issue is closed AND PR merged AND sub-issues verified closed AND cross-references resolved | `already-handled` |
| Body is unclear, vague, or request for information (not a bug) | `qa` |
| Title has `[SPEC]` but body is a bug report | `analyze-and-spec` (content over prefix) |

**IMPORTANT:** Do NOT use the `[SPEC]` prefix or any label as the sole classification signal. Content analysis is the authoritative classifier.

### Pass 2 — AI Content Verification (Confirm or Redirect)

Read the body and comments. Ask: **"Does the Pass 1 classification match what the content actually describes?"**

Redirection examples:

| Pass 1 Result | Pass 2 Observation | Redirect To |
|----------------|--------------------|-------------| 
| `audit` (based on checkboxes) | Content is really a bug report | `analyze-and-spec` |
| `just-review` | Body has no formal sections but describes a clear feature spec | `audit` |
| `audit` | Comments contain audit findings AND unanswered questions | `audit` + flag for `qa` afterward |
| `already-handled` | Only partially implemented | `audit` (spec still active) |
| `just-review` | New scope-relevant comments since last audit | `audit` |
| `qa` | Bug language detected on closer inspection | `analyze-and-spec` |
| `analyze-and-spec` | Content is actually a feature request, not a bug | `qa` |

### Output Format

State results in this format:

```
Triage: <path> (<confidence>)
Reason: <one sentence explaining why>
Verification: <one sentence confirming or noting redirect from Pass 1>
```

Examples:

```
Triage: analyze-and-spec (high confidence)
Reason: Body describes a crash with steps to reproduce and expected vs actual behavior.
Verification: Bug report language confirmed — routed to analyze-and-spec for root cause analysis.

Triage: audit (high confidence)
Reason: Body contains 6 phases with success criteria and edge cases.
Verification: Content describes a structured feature spec — confirmed audit path.

Triage: qa (medium confidence)
Reason: Body appears to be a spec but actually describes an error condition with no structured phases.
Verification: Redirected from audit — title says [SPEC] but content is a bug report.

Triage: analyze-and-spec (medium confidence)
Reason: Body uses error terminology but lacks clear reproduction steps.
Verification: Bug language detected, but root cause unclear — may need clarification before fix spec.
```

### Sub-issue Triage

Each sub-issue gets its own independent triage decision. A parent may be `audit` while a sub-issue is `qa`.

## Closed Issue Verification in Triage

**Before classifying any closed issue as `already-handled`, verify:**

1. **Sub-issues resolved:** `github_issue_read(method="get_sub_issues", issue_number=N)` — all sub-issues must be closed
2. **Cross-references resolved:** Spec → plan chain must be complete (plan closed, all sub-issues under plan closed)
3. **Closure correctness:** `state_reason == "completed"` AND merged PR exists (search PRs referencing the issue)

If any verification fails, do NOT classify as `already-handled`. Instead:
- Route to `analyze-and-spec` (if bug report with open fix spec)
- Route to `audit` (if spec with open sub-issues)
- Report as `flag-for-review` with specific verification failures

## Confidence Levels

| Level | Meaning |
|-------|---------|
| High | Clear match between signals and content; no ambiguity |
| Medium | Signals point one way but content has some ambiguity |
| Low | Conflicting signals; agent should proceed cautiously and note uncertainty |

## Edge Cases

| Case | Handling |
|------|----------|
| No comments, no phases, no bug language | `qa` (unclear intent, ask for clarification) |
| No comments, but bug language present | `analyze-and-spec` (bug language is sufficient) |
| Issue is closed | Verify sub-issues closed, cross-references resolved, closure correctness → then classify as `already-handled` or `stale` |
| Mixed signals (phases + bug language) | AI verification breaks tie; document reasoning |
| Title says spec but body is bug | Redirect to `analyze-and-spec` |
| Body lacks formal sections but clear feature | Redirect to `audit` |
| Bug language present but actually a feature request | Redirect to `qa` |

## Live Verification: Triage Classification Claims (MANDATORY)

**Before trusting a triage classification, verify key claims against actual GitHub state. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Issue is a bug report" | Verify bug language in body | `github_issue_read(method=get)` → scan for bug patterns | CONFLICTING |
| "Issue is already handled" | Verify sub-issues closed + merged PR | `github_issue_read(method=get_sub_issues)` + PR search | VERIFICATION-GAP |
| "Issue has been audited before" | Verify audit comments exist | `github_issue_read(method=get_comments)` → search for audit patterns | VERIFICATION-GAP |
| "Authorization exists" | Verify auth comment from developer | `github_issue_read(method=get_comments)` → check `author_association` | CONFLICTING |
| "`[SPEC]` prefix is accurate" | Verify content matches prefix (content over label) | `github_issue_read(method=get)` → body analysis vs title | STRUCTURE-VIOLATION |
| "Sub-issues are all closed" | Verify each sub-issue state via API | `github_issue_read(method=get, issue_number=N)` per child | VERIFICATION-GAP |

**Evidence artifact:** Tool call results for each claim verified during triage.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| `[SPEC]` prefix on bug report | STRUCTURE-VIOLATION | auto-fix | Re-triage to `analyze-and-spec` |
| `already-handled` but no merged PR | VERIFICATION-GAP | flag-for-review | Re-classify as `audit` or `just-review` |
| Authorization from bot/agent | CONFLICTING | flag-for-review | Require human authorization |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Investigate closure reason |