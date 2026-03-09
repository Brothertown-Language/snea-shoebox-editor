# Plan: Fix record_id Undefined Column in HAVING Clause

**Status:** ✅ Complete
**Created:** 2026-03-09

---

## Overview

**WHAT**: Fix a SQL error where `record_id` is referenced in a `HAVING` clause but is not available at that scope.

**WHY**: The `HAVING count(DISTINCT record_id) > 1` fix introduced in `batch-rollback-no-sessions-diagnosis.md` may reference `record_id` outside the subquery scope where it is defined, causing a database error. This plan tracks the targeted fix.

---

## Scope

- `src/frontend/pages/batch_rollback.py` — step-1 query in `get_recent_sessions()` only

---

## Steps

1. ✔️ Identify the exact column reference error in the HAVING clause
2. ✔️ Fix the query so `record_id` is correctly scoped (alias or move reference into subquery)
3. ✔️ Verify fix via `tmp/` script against local DB
4. ✔️ Update this plan to reflect actual progress and declare completion if all steps are done
