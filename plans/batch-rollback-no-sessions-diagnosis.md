# Batch Rollback — No Sessions Shown: Diagnosis & Mitigation Plan

**Status:** 🔄 Pending

---

## Overview

**WHAT**: Fix `get_recent_sessions()` in `batch_rollback.py` so it returns batch-eligible sessions.

**WHY**: The query orders all sessions by `min(timestamp) DESC` with `LIMIT 50`, returning the 50 most recently started sessions. All 17 multi-record (batch-eligible) sessions rank 1,062–1,079 out of 1,079 — below the LIMIT 50 window — because they were uploaded weeks ago while the top 50 slots are occupied by single-record manual edits. The `total_count <= 1` filter then eliminates every session in the window, leaving `available_sessions = []`.

---

## Root Cause

The `get_recent_sessions()` query in `src/frontend/pages/batch_rollback.py` (line 13–30)
orders all sessions by `min(timestamp) DESC` and applies `LIMIT 50`. This returns the 50
most *recently started* sessions.

The local dev DB has **1,079 sessions** with non-deleted records. All **17 multi-record
sessions** (the only ones eligible for batch rollback) rank **1,062–1,079** — the very
bottom of the list — because they were uploaded weeks ago (Feb–Mar 1–6) while the top 50
slots are occupied by 1,029 single-record manual edits made more recently (last 5 entries
all from 2026-03-08).

The `total_count <= 1` filter (step 2) then eliminates every session in the top-50 window,
leaving `available_sessions = []`.

### Evidence

| Session (short) | Rank / 1079 | Reversible records |
|-----------------|-------------|-------------------|
| dad030e5        | 1062        | 463               |
| d525b4a2        | 1064        | 4490              |
| ddb9975e        | 1065        | 1105              |
| f36e2ff3        | 1066        | 339               |
| ccae2ea4        | 1067        | 24                |
| (12 more…)      | 1068–1079   | various           |

---

## Mitigation Options

### Option A — Pre-filter to multi-record sessions before LIMIT (recommended)

Change the step-1 query to only include sessions that touched **more than 1 distinct
record**, then apply `LIMIT 50`. This ensures the window always contains batch-eligible
sessions.

```sql
SELECT session_id, min(timestamp) as earliest_ts,
       min(user_email) as user_email, min(source_name) as source_name,
       min(full_name) as full_name
FROM (
    SELECT eh.session_id, eh.timestamp, eh.user_email,
           s.name as source_name, u.full_name
    FROM edit_history eh
    JOIN records r ON r.id = eh.record_id
    JOIN sources s ON s.id = r.source_id
    LEFT JOIN users u ON u.email = eh.user_email
    WHERE r.is_deleted = False
) AS history
WHERE session_id IS NOT NULL
GROUP BY session_id
HAVING count(DISTINCT record_id) > 1
ORDER BY earliest_ts DESC
LIMIT 50;
```

The `total_count <= 1` step-2 check becomes redundant but can remain as a safety guard.

**Pros:** Minimal change, single query fix, no schema change.
**Cons:** None.

### Option B — Remove LIMIT entirely

Drop `LIMIT 50` and paginate in Python (already done via `rollback_page_idx`).

**Pros:** Shows all eligible sessions.
**Cons:** Slightly more DB work on large datasets; acceptable given batch sessions are rare.

### Option C — Combine A + B

Apply `HAVING count(DISTINCT record_id) > 1` AND remove `LIMIT 50` (rely on Python
pagination). Most correct long-term.

---

## Recommended Fix

**Option A** — add `HAVING count(DISTINCT record_id) > 1` to the step-1 query.
This is the minimal, targeted fix. The `LIMIT 50` remains as a safety cap on the
(now already-filtered) batch sessions.

### Files to change

- `src/frontend/pages/batch_rollback.py` — lines 13–30 (step-1 query only)

---

## Steps

1. 🔄 Add `HAVING count(DISTINCT record_id) > 1` to step-1 query in `get_recent_sessions()`
2. 🔄 Verify `get_recent_sessions()` returns the expected sessions via `tmp/` script
3. 🔄 Manual smoke-test in running app (optional)
4. 🔄 Update this plan to reflect actual progress and declare completion if all steps are done
