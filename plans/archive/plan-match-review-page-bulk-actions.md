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

### 1. ✔️ Completed — Add `queue_ids` filter to bulk service methods

Added `queue_ids: list[int] | None = None` to the following four methods in `UploadService`.
When `queue_ids` is provided, restrict all DB queries to those IDs (in addition to `batch_id`).
When `None`, behaviour is unchanged (whole-batch scope).

Methods updated:
- `approve_all_new_source` (line 904)
- `approve_all_by_record_match` (line 964)
- `approve_non_matches_as_new` (line 1038)
- `discard_marked` (line 1423)

### 2. ✔️ Completed — Add bottom bulk-action block to `_render_review_table`

After the `for row in page_rows:` loop, added a new block conditioned on `len(page_rows) >= 2`
and `not review_bulk_in_progress`. Mirrors sidebar button logic (`is_new_source` branch).
Stores `page_queue_ids` in `st.session_state["review_bulk_page_ids"]` before rerun.
Distinct widget keys (`page_bulk_*`) avoid collisions with sidebar.

### 3. ✔️ Completed — Wire page-scoped IDs into bulk execution block

Reads `st.session_state.pop("review_bulk_page_ids", None)` as `bulk_page_ids` at the top of
the execution block. Passes `queue_ids=bulk_page_ids` to all four service calls.
Sidebar-triggered actions (`bulk_page_ids=None`) retain whole-batch behaviour unchanged.

Also consolidated `session_id` generation to a single `_bulk_session_id = str(uuid4())` per
bulk invocation — all records in a page-scoped action share one session_id, ensuring the action
appears as a single rollback-eligible session in the rollback view.

**Rollback compatibility verified**: rollback view queries `edit_history` by `session_id` where
`count(DISTINCT record_id) > 1`; page-scoped actions touching 2+ records satisfy this automatically.

### 4. ✔️ Completed — Verify and update plan

- Both files lint clean (no errors).
- 33 pre-existing test failures confirmed identical before and after changes; zero regressions introduced.
