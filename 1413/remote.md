---
remote_issue: 1413
remote_url: "https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1413"
last_sync: 2026-10-05T04:58:08Z
source: github.com
---

## Problem Statement

The Records page (`src/frontend/pages/records.py`) renders page-level navigation (Prev/Next buttons, "Page N of M" and "Showing X–Y of Z" captions) only in the sidebar. The main content area has no navigation controls above the first record or after the last record, making pagination awkward — the pager is visually distant from the records it controls, especially in single-record view (page_size=1).

## Approach

Relocate page-level pagination from the sidebar to the main panel as twin navigation rows:

- **Remove from sidebar:** Prev/Next page buttons and the Page N of M / Showing X–Y of Z captions (sidebar pager block, `records.py` lines ~538-568).
- **Twin rows in main panel:** full-form rows `[◀️ Prev] Page N of M / Showing X–Y of Z [▶️ Next]` — one row immediately before the first record, one immediately after the last record, inside the main panel's scroll container.
- **Shared helper:** one helper renders both rows with key-namespacing (top/bottom) so the page-change logic — including auto-save-on-page-change of pending edits in edit mode — exists exactly once (currently duplicated at `records.py` ~540-545 and ~549-554).
- **Boundary behavior:** Prev disabled at page 1, Next disabled at last page (matches current sidebar behavior).
- **Stays in sidebar:** Results-per-page selectbox; Enter/Cancel/Save edit-mode controls.
- **Layout fit verified:** Playwright captures under `tmp/discussion-records-nav/artifacts/` (vision-reviewed) show a whitespace gap above the first record card and dead space after the last card absorb the rows without crowding.

## Success Criteria (draft)

- SC-1 (behavioral): Sidebar no longer renders page-level Prev/Next buttons or the Page N of M / Showing captions on the Records page; Results-per-page selectbox and edit-mode controls remain.
- SC-2 (behavioral): A full-form navigation row (Prev | Page N of M / Showing X–Y of Z | Next) renders immediately above the first record card in the main panel.
- SC-3 (behavioral): An identical navigation row renders immediately after the last record card in the main panel.
- SC-4 (behavioral): Clicking Prev/Next in either row performs the same page change as the removed sidebar pager, including auto-save of pending edits in global edit mode; boundary pages disable the corresponding button in both rows.
- SC-5 (behavioral): On the empty-results path, the twin navigation rows are suppressed entirely (no "Page 1 of 1" / "Showing 1-0 of 0" artifacts in the main panel).
- SC-6 (structural): The page-change/auto-save logic exists exactly once in the code (shared helper), referenced by both rows.

## Affected Files

- `src/frontend/pages/records.py` (sidebar pager removal; main-panel twin rows; shared pager helper)

## Notes

- Streamlit reruns the script per interaction; top/bottom row widgets need unique keys sharing one code path.
- Evidence baseline: Playwright full-page and viewport captures at 1280px confirm no main-panel navigation exists today and sidebar-only pagination is the current state.

🤖 Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
