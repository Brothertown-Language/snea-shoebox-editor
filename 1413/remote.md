---
remote_issue: 1413
remote_url: "https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1413"
last_sync: 2026-10-05T05:14:29Z
source: github.com
---

> Full spec and plan artifacts: https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1413/

## Problem

The Records page (`src/frontend/pages/records.py`) renders page-level navigation — Prev/Next buttons and the "Page N of M" / "Showing X–Y of Z" captions — only in the sidebar, visually distant from the records it controls and most awkward in single-record view; its page-change/auto-save logic is also duplicated once per button. A stakeholder discussion produced binding layout decisions (D1–D7), so the relocation is now ready to be specified and built.

## Scope

- Remove the sidebar pager block (Prev/Next buttons and Page/Showing captions) from the Records page.
- Add twin full-form navigation rows in the main panel — one immediately before the first record card, one immediately after the last card — inside the main panel's scroll container.
- Introduce one shared, key-namespaced helper that renders both rows so the page-change and auto-save-on-page-change logic exists exactly once.
- Preserve boundary behavior: Prev disabled at page 1 and Next disabled at the last page, applied in both rows.
- Suppress the navigation rows entirely on the empty-results path.

**Out of scope:** search/filter logic and modes; Results-per-page selectbox placement and behavior (stays in the sidebar); edit-mode control placement and Save All / Cancel All semantics (stay in the sidebar); new pagination features (jump-to-page, page-size control in the main panel, infinite scroll); backend, service, schema, or API changes; record-card rendering internals.

## Approach

Remove the sidebar pager block from `src/frontend/pages/records.py` and replace it with a shared helper that renders one full-form navigation row parameterized by position (top/bottom) with position-namespaced widget keys. Invoke the helper twice inside the non-empty records branch of the main panel — once before the record loop and once after it — which suppresses the rows by construction on empty results. The helper owns the single copy of the page-change logic, including auto-save-on-page-change that persists pending edits in global edit mode with unchanged semantics. The change is UI-layout-only: no backend, service, schema, or API surface is touched. Verification follows the repository's Playwright standard of record with SNEA_E2E gating, plus one structural source-inspection criterion for the exactly-once logic guarantee.

## Impact

- **Risk: sidebar over-deletion damages the Results-per-page selectbox or edit-mode controls** — mitigated by line-bounded removal targets plus dedicated retention checks (SC-2 selectbox, SC-3 edit-mode controls).
- **Risk: auto-save semantics drift while consolidating the duplicated logic** — mitigated by requiring verbatim guard/change-summary/clearing parity, asserted behaviorally in SC-7.
- **Risk: pagination lost mid-branch during relocation** — mitigated by dependency ordering: the twin rows are wired before the sidebar block is removed, so pagination is never absent.
- **Dependencies:** brainstorm decisions D1–D7 (consumed); Playwright e2e conventions in `test/ui/` and the UI testing standard of record; baseline layout captures for layout-fit vision review.
- **Call to action:** review the full spec and its nine success criteria in the issues-data branch linked above.

🤖 OpenCode (zai-org/GLM-5.3-Flash) created
