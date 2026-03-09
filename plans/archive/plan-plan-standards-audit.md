# Plan: Audit & Fix All Plans to Meet plan_standards.md

**Status:** ✅ Complete
**Created:** 2026-03-09

---

## Overview

**WHAT**: Audit all active plan files in `plans/` against `plan_standards.md` and fix every violation found.

**WHY**: Plans are the primary record of authorized work. Non-conforming plans create ambiguity about step status, numbering, and completeness. Consistent formatting ensures the approval gate and progress tracking work correctly.

---

## Violations Found (per file)

### `batch-rollback-no-sessions-diagnosis.md`
- No status icons (✔️/🏗️/🔄) on any steps — uses `[ ]` checkbox syntax instead
- No final "update plan to reflect actual progress" step
- Status line uses free-text ("DIAGNOSIS COMPLETE — awaiting GO for fix"), not a standard icon

### `batch-rollback-sql-fix.md`
- Stub file: no steps, no WHAT+WHY overview, no final update step
- Status icon present (🔄) but content is empty placeholder

### `plan-revision-history-diff-rollback.md`
- Steps numbered globally (1, 2, 3) across phases instead of restarting at 1 per phase
- No final "update plan to reflect actual progress" step
- No status line at top of file

### `plan-revision-history-exclude-current.md`
- Single step inside a phase — no final "update plan" step
- No status line at top of file

### `plan-revision-history-exclude-current-v2.md`
- Single step inside a phase — no final "update plan" step
- No status line at top of file

### `plan-sync-prod-verify-docs.md`
- Steps use `### N.` heading format instead of plain numbered list items (`1.`, `2.`, `3.`)
- No final "update plan to reflect actual progress" step

### `plan-validator-mdf-tag-ordering.md`
- Status says ✅ Complete but all checklist items are `[ ]` unchecked — inconsistent
- Steps use `### Step N` heading format instead of plain numbered list items
- Checklist uses `[ ]` syntax instead of status icons
- No final "update plan" step
- If truly complete, must be archived via `uv run python ai_bin/plan archive`

### `record-match-hm-nt-scoring-fix.md`
- Steps have no status icons (✔️/🏗️/🔄) — plain numbered list with no icon
- No final "update plan to reflect actual progress" step
- No status line at top of file

### `TODO.md`
- Not a REVIEW PLAN — backlog/task list format; exempt from most plan_standards.md rules
- No action needed

---

## Steps

1. ✔️ Fix `batch-rollback-no-sessions-diagnosis.md`: replace `[ ]` with 🔄 icons; add status line; add final update step
2. ✔️ Fix `batch-rollback-sql-fix.md`: add WHAT+WHY overview; add placeholder steps with 🔄 icons; add final update step
3. ✔️ Fix `plan-revision-history-diff-rollback.md`: add status line; renumber steps within phases starting at 1; add final update step
4. ✔️ Fix `plan-revision-history-exclude-current.md`: add status line; add final update step
5. ✔️ Fix `plan-revision-history-exclude-current-v2.md`: add status line; add final update step
6. ✔️ Fix `plan-sync-prod-verify-docs.md`: convert `### N.` step headings to plain numbered list items with icons; add final update step
7. ✔️ Fix `plan-validator-mdf-tag-ordering.md`: convert `### Step N` headings to plain numbered list; replace `[ ]` with status icons; reconcile status; archived
8. ✔️ Fix `record-match-hm-nt-scoring-fix.md`: add status line; add status icons to steps; add final update step
9. ✔️ All steps complete — plan updated to reflect actual progress.
