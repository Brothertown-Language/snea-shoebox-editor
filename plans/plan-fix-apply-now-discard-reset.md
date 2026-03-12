# Plan: Fix Apply Now Ignoring Discard Selection

**Status:** 🔄 Pending  
**Created:** 2026-03-11  
**Scope:** `src/frontend/pages/upload_mdf.py`

---

## Root Cause

The cache-invalidation block at lines 834–836 clears the user's explicit dropdown
selection whenever the widget's cached label doesn't match `current_status` (derived
from `row.status`). This is too broad — it fires whenever DB status ≠ widget value,
including after the user has deliberately set the dropdown to `'discard'` and an
external event (e.g., re-match) subsequently changes `row.status`. The user's
`'discard'` selection is silently lost, the selectbox resets to the DB default
(e.g., `'matched'`), and Apply Now fires with `override_status='matched'` — updating
a record that should have been discarded.

---

## Fix

Replace the broad cache-invalidation check with a last-known-DB-status tracker.
Only clear the widget cache when `row.status` changed from what was last recorded —
indicating an external event changed the DB, not the user's own dropdown interaction.

---

## Steps

### 1. Replace cache-invalidation logic in `upload_mdf.py` (lines 834–836)

**Replace:**
```python
cached_label = st.session_state.get(f"status_{row.id}")
if cached_label and status_map.get(cached_label) != current_status:
    st.session_state.pop(f"status_{row.id}", None)
```

**With:**
```python
db_status_key = f"db_status_{row.id}"
last_known_db = st.session_state.get(db_status_key)
if last_known_db is not None and last_known_db != row.status:
    # DB status changed externally (e.g., re-match override) — reset widget
    st.session_state.pop(f"status_{row.id}", None)
st.session_state[db_status_key] = row.status
```

### 2. Lint verify

### 3. Update and archive plan
