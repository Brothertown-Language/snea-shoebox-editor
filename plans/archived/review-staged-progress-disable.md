# Plan: Review Staged Entries — Progress Indicator Up Top + Disable UI During Bulk Actions

**File:** `src/frontend/pages/upload_mdf.py` (only)

## Overview
The "Review Staged Entries" view has four bulk action buttons (Approve All as New Records,
Approve All Matched, Approve Non-Matches as New, Discard All Marked) that each run inline with
`st.status` + `st.progress` buried in the sidebar. Apply the same pattern as Stage & Match:
move the progress bar to the top of the main panel and disable all controls during the operation
(except a Cancel button).

## Approach
Use a `review_bulk_in_progress` session state flag (with a `review_bulk_label` for the message).
On button click: set the flag + label + which action to run, then `st.rerun()`. On the next render
(flag is set): show progress bar up top, disable all controls, execute the action, clear the flag,
rerun. Add a Cancel button in the sidebar as the only enabled control.

---

## Steps

1. **Add `review_bulk_in_progress` flag** — In `_render_review_view`, read the flag at the top.
   Each bulk button sets `review_bulk_in_progress=True`, `review_bulk_label=<action name>`,
   `review_bulk_action=<key>`, then calls `st.rerun()`. Clear on completion, error, or cancel.

2. **Render progress bar "up top" in main panel** — At the top of `_render_review_table` (before
   the per-entry loop), when `review_bulk_in_progress` is set, render `st.info(label)` +
   `st.progress(value)`. Store the bar so the `update_progress` callback can update it.

3. **Disable sidebar controls during bulk** — Add `disabled=review_bulk_in_progress` to:
   - Previous / Next page buttons
   - Approve All as New Records button
   - Approve All Matched button
   - Approve Non-Matches as New button
   - Discard All Marked button
   - Discard All Locked Conflicts button
   - Download Locked Conflicts download_button
   - Records per page selectbox
   - Re-Match button (in `_render_review_view`)
   - Back to MDF Upload button (in `_render_review_view`)

4. **Disable main panel controls during bulk** — Add `disabled=review_bulk_in_progress` to:
   - Per-entry Status selectbox (`status_{row.id}`)
   - Apply Now button (`apply_{row.id}`)
   - Change match text_input (`match_search_{row.id}`)
   - Match selectbox (`match_select_{row.id}`)
   - Confirm Override button (`match_confirm_{row.id}`)

5. **Add Cancel button** — In `_render_review_view` sidebar, when `review_bulk_in_progress` is
   True, show `st.button("Cancel", icon="✖️", key="review_bulk_cancel")` that clears the flag
   and calls `st.rerun()`. This is the only enabled control during a bulk operation.

6. **Execute bulk action on second render** — In `_render_review_table`, when
   `review_bulk_in_progress` is set and the progress bar is rendered, dispatch to the correct
   service call based on `review_bulk_action`. Wire `update_progress` to the top-level bar.
   Keep `st.status(...)` for the text log only (no nested progress bar).

---

## Files Changed
- `src/frontend/pages/upload_mdf.py`

## Status: IMPLEMENTED
