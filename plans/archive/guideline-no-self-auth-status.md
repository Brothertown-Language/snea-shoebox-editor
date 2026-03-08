# REVIEW PLAN: Prohibit Self-Authorization Status Labels

## Problem

Plan files (and responses) must not contain status labels like `Status: AWAITING GO` or
`Status: READY TO PROCEED`. These phrases mimic approval-gate language and could be
misread as self-authorization tokens or mislead the agent into treating them as gate state.
The existing rule in `01-approval-gate.md` already forbids approval tokens in plan *delivery*
text, but does not explicitly cover status header fields in plan *files*.

## Proposed Changes

### 1. `guidelines/01-approval-gate.md` — add explicit prohibition

Under the **Plan delivery MUST NOT contain approval tokens** bullet, append a new sub-rule:

> **Plan files MUST NOT contain status fields that echo approval-gate language.**
> Labels such as `Status: AWAITING GO`, `Status: READY TO PROCEED`, `Status: PENDING GO`,
> or any variant that embeds an approval token (GO, Proceed, Approved) in a status header
> are forbidden in plan files, responses, reviews, or any agent-authored artifact.
> Use `🔄 Pending` / `🏗️ In-Progress` / `✔️ Completed` status icons only (per plan_standards.md).

### 2. `plans/record-match-hm-nt-scoring-fix.md` — remove offending line

Line 3 currently reads `## Status: AWAITING GO`. Remove it. The plan's pending state is
conveyed by the absence of `✔️` markers on its steps — no status header is needed.

## Files to Change

- `.junie/guidelines/01-approval-gate.md`
- `plans/record-match-hm-nt-scoring-fix.md`

## Steps

1. ✔️ Add prohibition sub-rule to `.junie/guidelines/01-approval-gate.md`
2. ✔️ Remove `## Status: AWAITING GO` from `plans/record-match-hm-nt-scoring-fix.md`
