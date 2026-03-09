# Plan: Re-Match Button — Progress Bar & UI Disable

## Problem

The "Re-Match" button in `_render_review_view` (line 428,
`src/frontend/pages/upload_mdf.py`) calls `UploadService.rematch_batch`
synchronously and inline. It does not:

- Set `review_bulk_in_progress = True` to disable the rest of the UI.
- Show a progress bar.
- Use the two-render bulk pattern that all other bulk actions use.

## Root Cause

The button handler (lines 428–437) calls the service directly instead of
setting `review_bulk_in_progress` + `review_bulk_action` and deferring
execution to the second render (the block at lines 688–755).

## File to Change

`src/frontend/pages/upload_mdf.py`

### Change 1 — Re-Match button click handler (lines 428–437)

Replace the inline service call with the same deferred pattern used by
all other bulk actions:

```python
# C-6b: Re-Match button
if st.button("Re-Match", key="rematch_btn", disabled=review_bulk_in_progress):
    st.session_state["review_bulk_in_progress"] = True
    st.session_state["review_bulk_label"] = "Re-matching entries…"
    st.session_state["review_bulk_action"] = "rematch"
    st.rerun()
```

### Change 2 — Bulk action handler block (after line 746, inside the `elif` chain)

Add a new `elif` branch for `"rematch"` inside the bulk action block
(lines 698–755), after the existing `elif bulk_action == "discard_marked":` branch:

```python
elif bulk_action == "rematch":
    with st.status(bulk_label, expanded=True) as status:
        match_results = UploadService.rematch_batch(batch_id, progress_callback=update_progress)
        matched_count = sum(1 for m in match_results if m.get('suggested_record_id') is not None)
        status.update(label=f"Re-matched. {matched_count} match(es) found.", state="complete", expanded=False)
        st.session_state["bulk_flash"] = ("success", f"Re-matched batch. {matched_count} match(es) found.")
```

### Change 3 — `rematch_batch` signature

`rematch_batch` currently does not accept a `progress_callback` parameter.
It calls `suggest_matches(batch_id)` without forwarding one. Add the
parameter and forward it:

```python
@staticmethod
def rematch_batch(batch_id: str, progress_callback: Optional[callable] = None) -> list[dict]:
    ...
    return UploadService.suggest_matches(batch_id, progress_callback=progress_callback)
```

## Verification

```
uv run python -m pytest tests/services/test_upload_service.py -v --tb=short
```

Manual: trigger Re-Match in the UI — confirm progress bar appears, UI is
disabled during processing, and success flash appears after completion.

---

**Status**: ✅ COMPLETE
