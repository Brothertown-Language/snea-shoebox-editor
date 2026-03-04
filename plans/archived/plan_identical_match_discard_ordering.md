# Plan: Fix Identical-Match Records Not Being Auto-Discarded

## Status: ✅ IMPLEMENTED

---

## Problem

When an uploaded record is content-identical to an existing record (after stripping
`\nt Record:` lines), the queue row is set to `status='matched'` instead of
`status='discard'`.

**Example:**

Existing record in DB:
```
\lx *|achm∞wonk|, vbl. n. `news'    C.
\cf aunchem∞kau
\nt Record: 5253
```

Uploaded record (no `\nt Record:` line):
```
\lx *|achm∞wonk|, vbl. n. `news'    C.
\cf aunchem∞kau
```

Expected: `status='discard'` (identical content, ignoring `\nt Record:`)
Actual: `status='matched'`

---

## Root Cause: Order Dependency in `suggest_matches`

In `src/services/upload_service.py`, `suggest_matches` (line ~246) filters to
`status='pending'` rows only. The UI page (`upload_mdf.py`, line ~843) triggers
`UploadService.confirm_match(row.id)` on **every render** for any row where
`selected_status != row.status` — which happens because the selectbox defaults to
`'matched'` (line 787–790) for any row with `has_suggestion=True`, even before the
user acts.

This creates the ordering problem:

1. `suggest_matches` runs → sets `row.status='discard'` for identical rows ✓
2. UI renders → selectbox defaults to `'matched'` for rows with `suggested_record_id`
   (line 787–790 does NOT check `match_type='identical'`)
3. `selected_status ('matched') != row.status ('discard')` → triggers
   `confirm_match(row.id)` → sets `row.status='matched'` ✗

The identity check result (`match_type='identical'`, `status='discard'`) is
**overwritten by the UI render loop**.

### Secondary Issue: `suggest_matches` skips non-pending rows

If re-match is triggered after the UI has already changed a row's status away from
`'pending'`, `suggest_matches` skips that row entirely (line 248 filter). The
identity check never re-runs.

---

## Files to Change

| File | Location | Change |
|------|----------|--------|
| `src/frontend/pages/upload_mdf.py` | line ~783–792 | Fix `current_status` derivation to respect `match_type='identical'` |
| `src/services/upload_service.py` | line ~246–248 | Expand `suggest_matches` filter to include `'matched'` rows for re-match |

---

## Changes

### Fix 1 — `upload_mdf.py`: Respect `match_type='identical'` in `current_status`

**Location:** lines ~783–792 (the `current_status` derivation block)

**Current logic:**
```python
if row.status not in ('pending',):
    current_status = row.status
elif record_id_conflict:
    current_status = 'create_new'
elif has_suggestion and match_type == 'exact':
    current_status = 'matched'
elif has_suggestion and match_type == 'base_form':
    current_status = 'matched'
else:
    current_status = 'create_new'
```

**Problem:** When `row.status='pending'` and `match_type='identical'`, the code falls
through to `current_status='matched'` (because `has_suggestion=True`). The
`match_type='identical'` case is never handled.

**Fix:** Add an explicit guard for `match_type='identical'` before the `'exact'`/
`'base_form'` branches:

```python
if row.status not in ('pending',):
    current_status = row.status
elif record_id_conflict:
    current_status = 'create_new'
elif has_suggestion and match_type == 'identical':
    current_status = 'discard'
elif has_suggestion and match_type == 'exact':
    current_status = 'matched'
elif has_suggestion and match_type == 'base_form':
    current_status = 'matched'
else:
    current_status = 'create_new'
```

This prevents the selectbox from defaulting to `'matched'` for identical rows,
which prevents the spurious `confirm_match` call on render.

### Fix 2 — `upload_service.py`: `suggest_matches` must also process `'matched'` rows on re-match

**Location:** line ~246–248

**Current:**
```python
pending_rows = (
    session.query(MatchupQueue)
    .filter_by(batch_id=batch_id, status='pending')
    ...
)
```

**Problem:** Re-match skips rows already set to `'matched'` by the UI. If a row was
incorrectly set to `'matched'` (due to Fix 1 not yet applied, or a race), re-match
cannot correct it.

**Fix:** Expand the filter to include `'matched'` rows:

```python
pending_rows = (
    session.query(MatchupQueue)
    .filter_by(batch_id=batch_id)
    .filter(MatchupQueue.status.in_(['pending', 'matched']))
    ...
)
```

This ensures re-match can re-evaluate and correct rows that were incorrectly promoted
to `'matched'`.

---

## Verification

```
uv run python -m pytest tests/ -k "identical or discard or suggest_match" -v --tb=short
```

Also: manual upload of the example records from the issue to confirm the queue row
shows `status='discard'` after `suggest_matches` runs.

---

## Notes

- Fix 1 is the primary mitigation (prevents the UI from overwriting `discard`).
- Fix 2 is a defensive hardening (ensures re-match can correct any rows that slipped
  through before Fix 1 was applied).
- `auto_remove_exact_duplicates` uses a different normalization (`_strip_nt_record_lines`
  only, no blank-line stripping) vs step F in `suggest_matches` (`_normalize` which
  also strips blank lines). These should be unified in a follow-up.
