# Plan: Fix Apply Now Ignoring "Discard" Selection

**File:** `plans/plan-apply-now-discard-bug.md`
**Status:** ✔️ Completed

## Problem

In `src/frontend/pages/upload_mdf.py`, lines 834–836 contained a stale-cache clearing guard:

```python
cached_label = st.session_state.get(f"status_{row.id}")
if cached_label and status_map.get(cached_label) != current_status:
    st.session_state.pop(f"status_{row.id}", None)
```

This fired incorrectly when the user changed the selectbox to "Discard Entry" and immediately
clicked "Apply Now" — because on the button-click rerun, `cached_label` = `"Discard Entry"` but
`current_status` = `"matched"` (old DB value), so the guard popped the key and the selectbox fell
back to `default_idx` ("Matched"), causing an unwanted record update instead of a discard.

## Root Cause

The guard condition was too broad: it could not distinguish user-driven selectbox changes (should
NOT be cleared) from external DB changes via "Confirm Override" (SHOULD be cleared).

## Fix

Used a dedicated `status_override_{row.id}` flag set only by "Confirm Override". The guard fires
only when this flag is set, then clears it atomically.

**Step 1:** ✔️ Completed — Set override flag in "Confirm Override" handler (`upload_mdf.py` ~line 943).

**Step 2:** ✔️ Completed — Replace stale-cache guard with flag-based check (`upload_mdf.py` lines 834–836).

**Step 3:** ✔️ Completed — Ran `test_upload_review_d1.py`; 17 pre-existing failures, no regression.

**Step 4:** ✔️ Completed — Verified fix matches plan.

**Step 5:** ✔️ Completed — Archived.
