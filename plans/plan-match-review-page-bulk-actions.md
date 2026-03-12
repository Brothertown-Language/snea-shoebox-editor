# Plan: Match Review Page — Bottom Bulk Actions

## Overview

Add a bulk-action button block at the bottom of the MDF match review main panel that mirrors the
sidebar bulk actions but operates only on the records currently displayed on the page (current
page/view). Appears only when two or more records are displayed.

---

## Affected Files

- `src/services/upload_service.py` — add optional `queue_ids` parameter to the four bulk methods
- `src/frontend/pages/upload_mdf.py` — add bottom bulk-action block after the record loop

---

## Steps

### 1. 🔄 Pending — Add `queue_ids` filter to bulk service methods

Add `queue_ids: list[int] | None = None` to the following four methods in `UploadService`.
When `queue_ids` is provided, restrict all DB queries to those IDs (in addition to `batch_id`).
When `None`, behaviour is unchanged (whole-batch scope).

Methods to update:
- `approve_all_new_source` (line 904)
- `approve_all_by_record_match` (line 964)
- `approve_non_matches_as_new` (line 1038)
- `discard_marked` (line 1423)

### 2. 🔄 Pending — Add bottom bulk-action block to `_render_review_table`

After the `for row in page_rows:` loop ends (after line 987), add a new block:

- Condition: `len(page_rows) >= 2` and `not review_bulk_in_progress`
- Collect `page_queue_ids = [r.id for r in page_rows]`
- Render `st.divider()` then `st.markdown("**Page Actions** — applies to displayed records only")`
- Mirror the same conditional button logic as the sidebar:
  - If `is_new_source`: "Approve Page as New Records" → `review_bulk_action = "approve_new"`
  - Else: "Approve Page Matched" → `"approve_matched"` and "Approve Page Non-Matches as New" → `"approve_nonmatch"`
  - Always: "Discard Page Marked" → `"discard_marked"`
- Store `page_queue_ids` in `st.session_state["review_bulk_page_ids"]` before triggering rerun
- Use distinct widget keys (e.g. `"page_bulk_approve_new"`) to avoid key collisions with sidebar

### 3. 🔄 Pending — Wire page-scoped IDs into bulk execution block

In the bulk execution block (lines 668–742), read
`st.session_state.pop("review_bulk_page_ids", None)` as `page_ids`.
Pass `queue_ids=page_ids` to each of the four service method calls.
When `page_ids` is `None` (sidebar-triggered), the whole-batch behaviour is unchanged.

**Rollback compatibility**: The existing bulk execution block already generates a single
`session_id = str(uuid4())` per bulk action invocation and passes it through to every
`apply_single` call, which writes it to `edit_history`. The rollback view (`batch_rollback.py`)
discovers sessions from `edit_history` where `count(DISTINCT record_id) > 1` — so any
page-scoped bulk action touching 2+ records will automatically appear in the rollback view.
No changes to the `session_id` mechanism are required; this constraint is satisfied by design.
The plan step must verify this by confirming `session_id` is forwarded unchanged to all
page-scoped service calls.

### 4. 🔄 Pending — Verify and update plan

Run the existing upload/review tests to confirm no regressions. Confirm lint is clean.
Update plan statuses to reflect actual completion and archive if all steps are done.
