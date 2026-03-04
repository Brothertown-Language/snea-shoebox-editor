# Plan: Stage & Match — Progress Indicator Up Top + Disable UI During Staging

## Overview
During the "Stage & Match" operation on the Upload MDF page, the progress bar is buried inside
an `st.status()` widget. The issue requires: (1) moving the progress indicator to the top of the
main panel, and (2) disabling all interactive elements in both the sidebar and main view while
staging is in progress (except a Cancel button).

## Approach
Use a `st.session_state` flag `staging_in_progress` to gate all UI elements. Render a
`st.progress()` bar at the very top of the main panel when the flag is set. Add a Cancel button
(sidebar) that clears the flag and reruns. Pass the top-level progress bar into the staging
callback.

---

## Steps

1. 🔄 **Add `staging_in_progress` flag** — Set to `True` immediately when Stage & Match button
   is clicked (before any service calls); clear it on completion, error, or cancel.

2. 🔄 **Render progress bar "up top"** — At the top of the main panel (before pending batches,
   preview, dataframe), check `staging_in_progress`; if set, render `st.progress()` and a status
   message. Store the progress bar object in `st.session_state["_staging_progress_bar"]` so the
   `update_progress` callback can update it.

3. 🔄 **Disable sidebar controls during staging** — Pass `disabled=st.session_state.get("staging_in_progress", False)`
   to: `st.file_uploader`, `st.selectbox` (source), `st.text_input` (new source name/description),
   `st.button("Create Source")`, `st.button("Back to Main Menu")`.

4. 🔄 **Disable main panel controls during staging** — Pass `disabled=staging_in_progress` to:
   Review/Download/Discard buttons on pending batches, the Stage & Match button itself.

5. 🔄 **Add Cancel button** — In the sidebar, when `staging_in_progress` is True, show a
   `st.button("Cancel", icon="✖️")` that clears `staging_in_progress` from session state and
   calls `st.rerun()`. This is the only enabled control during staging.

6. 🔄 **Wire progress callback to top-level bar** — Replace the `st.progress()` inside
   `st.status(...)` with the top-level bar; keep `st.status(...)` for the text log only
   (no nested progress bar).

## Files Changed
- `src/frontend/pages/upload_mdf.py` — only file modified.

## Tests
- Existing test class `TestStageAndMatch` in `tests/frontend/test_upload_mdf_page.py` covers
  the staging call path; verify it still passes after changes.
- Existing `TestStageAndMatchDisable` in `tests/frontend/test_upload_review_d1.py` covers
  disable behavior; verify it still passes.
