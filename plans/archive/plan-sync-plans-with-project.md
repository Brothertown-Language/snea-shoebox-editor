# REVIEW PLAN: Sync Plans with Project
**Status:** ✅ Complete
**Created:** 2026-03-09

---

## Overview

Several plans in `plans/` are marked 🔄 Pending but their code is already implemented (committed in HEAD or in the working tree). This plan updates each plan's status to reflect actual project state.

---

## Findings

| Plan file | Current status | Actual state | Action |
|-----------|---------------|--------------|--------|
| `plan-sync-prod-local-pgserver-connect.md` | step shows ✔️ in working tree | Step 1 implemented (working tree) | Mark overall plan ✅ Complete |
| `plan-revision-history-exclude-current.md` | 🔄 Pending | Superseded by v2; v2 is implemented | Mark ✅ Complete (superseded) |
| `plan-revision-history-exclude-current-v2.md` | 🔄 Pending | Implemented in HEAD commit d4de0df | Mark ✅ Complete |
| `plan-revision-history-diff-rollback.md` | 🔄 Pending | All phases implemented in HEAD commit d4de0df | Mark ✅ Complete |
| `batch-rollback-no-sessions-diagnosis.md` | 🔄 Pending | HAVING + record_id fix implemented in HEAD | Mark ✅ Complete |
| `batch-rollback-sql-fix.md` | 🔄 Pending | record_id scoping fix implemented in HEAD | Mark ✅ Complete |
| `record-match-hm-nt-scoring-fix.md` | 🔄 Pending | candidate_mdf_map extended for base-form candidates; test passes | Mark ✅ Complete |
| `plan-sync-prod-verify-docs.md` | 🔄 Pending | Documentation-only work not yet done | Leave 🔄 Pending |

---

## Steps (flat plan)

1. ✔️ `plan-sync-prod-local-pgserver-connect.md` — add `**Status:** ✅ Complete` header; mark Step 1 ✔️ Completed; mark Phase 2 completion step ✔️ Completed.
2. ✔️ `plan-revision-history-exclude-current.md` — set status to ✅ Complete; add note "Superseded by v2; v2 implemented in commit d4de0df."
3. ✔️ `plan-revision-history-exclude-current-v2.md` — set status to ✅ Complete; mark all steps ✔️ Completed.
4. ✔️ `plan-revision-history-diff-rollback.md` — set status to ✅ Complete; mark all phase steps ✔️ Completed.
5. ✔️ `batch-rollback-no-sessions-diagnosis.md` — set status to ✅ Complete; mark all steps ✔️ Completed.
6. ✔️ `batch-rollback-sql-fix.md` — set status to ✅ Complete; mark all steps ✔️ Completed.
7. ✔️ `record-match-hm-nt-scoring-fix.md` — set status to ✅ Complete; mark all steps ✔️ Completed.

`plan-sync-prod-verify-docs.md` — no change (genuinely pending).

---

## Out of Scope

- No code changes.
- No archiving of completed plans (not requested).
