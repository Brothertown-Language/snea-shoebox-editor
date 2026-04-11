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
| `qa` | Bug report, unclear request, or issue needing clarification |
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
| Comments contain "approved" or "go" | Check if also implemented → `already-handled` |
| Comments contain audit finding patterns | `just-review` (if no new non-audit comments) |
| `needs-approval` label present, no explicit auth | `just-review` (report auth status) |
| Body uses bug report language ("crash", "error", "broken") | `qa` |
| Issue is closed AND PR merged | `already-handled` |
| Body is unclear, vague, or request for information | `qa` |
| Title has `[SPEC]` but body is a bug report | `qa` (title ≠ content) |

**IMPORTANT:** Do NOT use the `[SPEC]` prefix or any label as the sole classification signal. Content analysis is the authoritative classifier.

### Pass 2 — AI Content Verification (Confirm or Redirect)

Read the body and comments. Ask: **"Does the Pass 1 classification match what the content actually describes?"**

Redirection examples:

| Pass 1 Result | Pass 2 Observation | Redirect To |
|----------------|--------------------|-------------| 
| `audit` (based on checkboxes) | Content is really a bug report | `qa` |
| `just-review` | Body has no formal sections but describes a clear feature spec | `audit` |
| `audit` | Comments contain audit findings AND unanswered questions | `audit` + flag for `qa` afterward |
| `already-handled` | Only partially implemented | `audit` (spec still active) |
| `just-review` | New scope-relevant comments since last audit | `audit` |

### Output Format

State results in this format:

```
Triage: <path> (<confidence>)
Reason: <one sentence explaining why>
Verification: <one sentence confirming or noting redirect from Pass 1>
```

Examples:

```
Triage: audit (high confidence)
Reason: Body contains 6 phases with success criteria and edge cases.
Verification: Content describes a structured feature spec — confirmed audit path.

Triage: qa (medium confidence)
Reason: Body appears to be a spec but actually describes an error condition with no structured phases.
Verification: Redirected from audit — title says [SPEC] but content is a bug report.
```

### Sub-issue Triage

Each sub-issue gets its own independent triage decision. A parent may be `audit` while a sub-issue is `qa`.

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
| Issue is closed | Check if `already-handled` or stale |
| Mixed signals (phases + bug language) | AI verification breaks tie; document reasoning |
| Title says spec but body is bug | Redirect to `qa` |
| Body lacks formal sections but clear feature | Redirect to `audit` |