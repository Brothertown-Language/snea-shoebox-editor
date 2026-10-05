> **Full spec and artifacts: [`.issues/1413/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1413)** — authoritative spec record for Issue #1413; the GitHub issue body is a condensed exec summary.

# Spec: Records page pagination — relocate page navigation from sidebar to twin navigation rows in the main panel

## 1. Intent and Executive Summary

- **Problem Statement:** The Records page (`src/frontend/pages/records.py`) renders page-level pagination — Prev/Next buttons and the "Page N of M" / "Showing X-Y of Z" captions — only in the sidebar. The main content area has no navigation above the first record or after the last record, so the pager is visually distant from the records it controls, most acutely in single-record view (page size 1).
- **Root Cause / Motivation:** The pager was implemented sidebar-first when the page was built, before the main panel became the primary scroll surface for record review. The page-change/auto-save logic it carries is duplicated once per button, a latent divergence risk. Relocation is requested now because the stakeholder confirmed the awkwardness and a brainstorming session produced binding layout decisions (D1-D7).
- **Approach Chosen:** Remove the sidebar pager block; introduce one shared, key-namespaced helper that renders a full-form navigation row; invoke it twice in the main panel's non-empty records branch — once immediately before the first record card and once immediately after the last card — so the page-change and auto-save-on-page-change logic exists exactly once.
- **Alternatives Considered & Why Discarded:** Keeping the sidebar pager and adding main-panel rows was discarded — it retains duplicated page-change logic and two competing pager surfaces, contrary to decision D1. A sticky/floating pagination bar was discarded — the records-page convention requires theme-aware native elements, and the stakeholder selected in-flow twin rows (D2). A jump-to-page input was discarded — new pagination features are explicitly out of scope.
- **Key Design Decisions:** D1 — remove the sidebar pager entirely (tradeoff: no fallback pager, so main-panel rows must be correct before removal). D2 — twin full-form rows inside the main panel's scroll container (tradeoff: vertical space consumed versus always-adjacent navigation). D3 — one shared helper with position-namespaced widget keys (tradeoff: slight key-naming complexity versus eliminating the duplicated auto-save block). D4 — boundary disabling parity in both rows. D5 — Results-per-page selectbox and edit-mode controls stay in the sidebar. D6 — empty-results path renders no navigation rows. D7 — layout fit is verified with Playwright captures under vision review.
- **User Intent / Original Prompt:** Stakeholder issue #1413 requesting that page navigation move from the sidebar to the main panel; the brainstorming handoff (`tmp/discussion-records-nav/artifacts/preliminary/handoff.yaml`, decisions D1-D7) is the binding requirements source consumed by this spec.

## 2. Not Included

- **Search/filter controls and logic** — the sidebar filter surface and all search modes are untouched; this spec changes pagination placement only.
- **Results-per-page behavior** — the selectbox stays in the sidebar with unchanged values and preference persistence (decision D5).
- **Edit-mode controls** — Enter Edit Mode / Cancel All / Save All stay in the sidebar with unchanged semantics (decision D5).
- **New pagination features** — no jump-to-page input, no page-size control in the main panel, no infinite scroll.
- **Backend, service, schema, or API changes** — the change is UI-layout-only; the record update path is called with identical semantics, never modified.
- **Record card rendering internals** — card content is untouched; only the rows immediately surrounding the card loop are added.

## 3. Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|----------------------|
| SC-1 | On the Records page, the sidebar renders no page-level Prev/Next navigation buttons and no "Page N of M" / "Showing X-Y of Z" captions, while the Results-per-page selectbox and the edit-mode controls (Enter Edit Mode / Cancel All / Save All) still render in the sidebar. | behavioral | Playwright real-browser check of the sidebar region (no pager buttons, no captions, selectbox and edit controls present), accompanied by a source-absence assertion on the removed block in `src/frontend/pages/records.py` as supplementary evidence. | `docs/development/ui_testing_standard.md`; `src/frontend/pages/records.py`; `test/ui/` existing e2e modules |
| SC-2 | In the main panel, a full-form navigation row — [Prev] with the "Page N of M" caption and the "Showing X-Y of Z" caption, then [Next] — renders immediately before the first bordered record container, displaying the live page, showing-range, and total values. | behavioral | Playwright capture of the top of the record list asserting the row's presence, order, and live caption values, with vision review of the capture for layout fit (decision D7). | `docs/development/ui_testing_standard.md`; `src/frontend/pages/records.py`; baseline captures under `tmp/discussion-records-nav/artifacts/` |
| SC-3 | In the main panel, an identical full-form navigation row renders immediately after the last record card (after all per-record content including revision-history expanders), displaying the same live values as the top row for the same page. | behavioral | Playwright capture of the bottom of the record list asserting the row's presence, order, and value parity with the top row, with vision review for layout fit. | `docs/development/ui_testing_standard.md`; `src/frontend/pages/records.py` |
| SC-4 | Clicking Next in the top row advances the page and clicking Prev in the bottom row returns to the previous page, with captions updating in both rows; with global edit mode active and pending edits present, a page change from either row persists each pending edit exactly once through the existing record-update path (same change summary as today) and clears the pending-edit state; at page 1 Prev is disabled in both rows and at the last page Next is disabled in both rows. | behavioral | Playwright end-to-end click-through module in `test/ui/` (playwright_e2e marker with SNEA_E2E gating) asserting navigation, caption parity, observable auto-save effect (revision-history entry / cleared pending state, not mocked), and boundary disabling in both rows. | `docs/development/ui_testing_standard.md`; `src/frontend/pages/records.py`; `test/ui/` conventions |
| SC-5 | On the empty-results path (no records batch, including all semantic-status empty states), the main panel renders only the empty-state message — no navigation rows, no "Page 1 of 1", and no "Showing 1-0 of 0" artifacts anywhere. | behavioral | Playwright empty-results capture asserting zero pagination artifacts, with a supplementary source assertion that both row call sites sit inside the non-empty records branch (supplementary only, never a substitute for the behavioral verdict). | `docs/development/ui_testing_standard.md`; `src/frontend/pages/records.py` |
| SC-6 | The page-change and auto-save-on-page-change logic exists exactly once in the source, inside a shared pagination-row helper that is referenced by exactly two call sites (top and bottom) using position-distinct widget keys. | structural | Source inspection of `src/frontend/pages/records.py`: occurrence count of the auto-save-on-page-change block (exactly one), helper definition present, and exactly two call sites with namespaced keys. | `src/frontend/pages/records.py` |

## 4. Requirements

- R-1. The Records page sidebar SHALL NOT render page-level Prev/Next navigation buttons or the "Page N of M" / "Showing X-Y of Z" captions.
- R-2. The Records page sidebar SHALL retain the Results-per-page selectbox with its current values and preference persistence.
- R-3. The Records page sidebar SHALL retain the edit-mode controls (Enter Edit Mode / Cancel All / Save All) with their current semantics.
- R-4. The main panel SHALL render a full-form navigation row — [Prev] button, "Page N of M" caption, "Showing X-Y of Z" caption, [Next] button — immediately before the first bordered record container, inside the main panel's scroll container.
- R-5. The main panel SHALL render an identical full-form navigation row immediately after the last record card, including all per-record revision-history content.
- R-6. Both navigation rows SHALL display live pagination values: the current page against total pages, and the showing range clamped to the records actually returned, against the total count.
- R-7. A page change triggered from either navigation row SHALL behave identically to the removed sidebar pager: the current page increments or decrements by one with the existing bounds clamping preserved, and the corresponding button SHALL be disabled at the boundary (Prev at page 1, Next at the last page) in both rows.
- R-8. On a page change from either row, when global edit mode is active and pending edits exist, the system SHALL persist each pending edit exactly once through the existing record-update path with the same change summary as today and SHALL clear the pending-edit state after the save pass; when the guard does not hold, the page change SHALL proceed without saving.
- R-9. The page-change and auto-save-on-page-change logic SHALL exist exactly once in the source, inside a shared pagination-row helper invoked by both the top and bottom rows.
- R-10. The navigation-row widgets SHALL use position-namespaced keys so the top and bottom rows are distinct widget instances and no duplicate-key conflict can occur.
- R-11. On the empty-results path — including all semantic-status empty states — the main panel SHALL render no navigation rows and no pagination artifacts.
- R-12. Layout fit SHALL be verified with Playwright captures under vision review, confirming the whitespace gap above the first record card and the dead space after the last card absorb the navigation rows without crowding (decision D7).

### Implementation Constraints

- C-1. Implementation SHALL confine production-code changes to `src/frontend/pages/records.py`; new test modules under `test/ui/` are the only other additions. Enforced by the blast-radius artifact and item scoping.
- C-2. No backend, service, persistence, schema, or public API changes SHALL be made. Enforced by the blast-radius and interface-compatibility artifacts.
- C-3. Behavioral success criteria SHALL be verified with behavioral evidence; structural or string substitutes SHALL NOT satisfy them. Enforced by the Evidence Type column of the SC table.
- C-4. Within the implementation branch, the main-panel navigation rows SHALL be wired before the sidebar pager block is removed, so pagination is never lost mid-branch. Enforced by the item dependency order in the Items section.

## 5. Items

### Item 1 (SC-6): Shared key-namespaced pagination-row helper with single page-change/auto-save logic

- RED: Source inspection fails — the shared helper is absent and the auto-save-on-page-change block occurs more than once in `src/frontend/pages/records.py`.
- GREEN: The helper exists and renders a full-form row for a position parameter ("top"/"bottom") with namespaced widget keys and boundary disabling; the auto-save-on-page-change block occurs exactly once, inside the helper; an invalid position value fails fast rather than silently defaulting.
- verify: Source-inspection occurrence count of the auto-save block equals one; helper is referenced by zero call sites at this item (no user-visible change yet).
- commit: Refactor commit adding the helper with no call sites.

### Item 2 (SC-2): Wire the top navigation row immediately before the first record card

- RED: Playwright capture plus source assertion show no navigation row above the first bordered record container in the main panel.
- GREEN: The full-form row renders immediately above the first bordered record container, with live captions, invoked inside the non-empty records branch just before the record loop.
- verify: Playwright capture with vision review (D7) confirming the whitespace gap above the first card absorbs the row; source assertion confirms the call site is inside the non-empty branch.
- commit: Feature commit wiring the top row.

### Item 3 (SC-3): Wire the bottom navigation row immediately after the last record card

- RED: Playwright capture plus source assertion show no navigation row after the last record card.
- GREEN: An identical row renders immediately after the record loop completes (after all per-record content including revision-history expanders), still inside the non-empty records branch, with the same live values as the top row.
- verify: Playwright capture with vision review (D7) confirming the dead space after the last card absorbs the row; caption parity with the top row for the same page.
- commit: Feature commit wiring the bottom row.

### Item 4 (SC-1): Remove the sidebar pager block; selectbox and edit-mode controls remain

- RED: Playwright check shows the sidebar still rendering Prev/Next page buttons and the Page/Showing captions.
- GREEN: The sidebar pager block is deleted; the Results-per-page selectbox and the edit-mode controls still render and function; no orphan references to the removed widgets remain; all other current-page/page-size state management is untouched.
- verify: Playwright sidebar check plus source-absence assertion of the removed block; preserved-control assertions pass.
- commit: Feature commit removing the sidebar pager (pagination now lives in the main-panel twin rows). Depends on Items 2 and 3 (constraint C-4).

### Item 5 (SC-4): End-to-end behavioral test module — click-through, auto-save, boundaries from either row

- RED: Enforcement-test gap — no behavioral test exists for the twin-row click-through contract (the target test module is absent), following the repository's red-test convention.
- GREEN: The Playwright e2e module in `test/ui/` (playwright_e2e marker with SNEA_E2E gating) passes against the implemented twin rows: top-row Next advances, bottom-row Prev returns, captions update in both rows, auto-save-on-page-change persists pending edits exactly once with the observable persisted effect verified (not mocked) and pending state cleared, and boundary disabling holds in both rows.
- verify: Test module runs gated (skips without the E2E environment variable, and a skip is never reported as a pass); all four assertion groups pass when gated on.
- commit: Test commit adding the SC-4 e2e module. Depends on Item 4.

### Item 6 (SC-5): Empty-results suppression — behavioral empty-state check with supplementary source placement assertion

- RED: Enforcement-test gap — no test asserts empty-path suppression (the target test module is absent).
- GREEN: The behavioral check passes — on the empty-results path the main panel renders only the empty-state message with zero pagination artifacts — and a supplementary source assertion confirms both row call sites sit inside the non-empty records branch.
- verify: Empty-path Playwright capture shows no nav rows, no "Page 1 of 1", no "Showing 1-0 of 0"; suppression holds across all empty-state branches; the structural check remains supplementary to the behavioral verdict (constraint C-3).
- commit: Test commit adding the SC-5 suppression guard. Depends on Items 2 and 3.

## 6. Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Brainstorm handoff decisions D1-D7 (`tmp/discussion-records-nav/artifacts/preliminary/handoff.yaml`) | Binding requirements source — consumed during requirements extraction | Satisfied |
| GitHub Issue #1413 (stakeholder request and draft discussion) | Source of intent this spec formalizes | Satisfied |
| `docs/development/ui_testing_standard.md` | MUST be read before writing or running any UI test — Playwright real-browser tests are the standard of record | Satisfied (exists) |
| `test/ui/` Playwright conventions (playwright_e2e marker + SNEA_E2E skip guards) | Implementation of Items 5 and 6 MUST follow these conventions | Satisfied (exists) |
| Current `src/frontend/pages/records.py` implementation (sidebar pager block, record render loop, empty-state branches) | Removal and wiring targets; anchors verified by direct reads during pre-spec inspection | Satisfied |
| Baseline captures (6 PNGs under `tmp/discussion-records-nav/artifacts/`) | Pre-change evidence baseline for layout-fit vision review (D7) | Satisfied |

## 7. Traceability

| Requirement | SC(s) | Item(s) |
|-------------|-------|---------|
| R-1 | SC-1 | Item 4 |
| R-2 | SC-1 | Item 4 |
| R-3 | SC-1 | Item 4 |
| R-4 | SC-2 | Item 2 |
| R-5 | SC-3 | Item 3 |
| R-6 | SC-2, SC-3 | Items 2, 3 |
| R-7 | SC-4 | Items 1, 5 |
| R-8 | SC-4 | Items 1, 5 |
| R-9 | SC-6 | Item 1 |
| R-10 | SC-6 | Item 1 |
| R-11 | SC-5 | Item 6 |
| R-12 | SC-2, SC-3 | Items 2, 3 |
| C-1 | SC-1 through SC-6 (all) | All items |
| C-2 | SC-1 through SC-6 (all) | All items |
| C-3 | SC-1, SC-2, SC-3, SC-4, SC-5 | Items 2-6 |
| C-4 | SC-1, SC-2, SC-3 | Items 2, 3, 4 |

## 8. Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| Records page implementation | code | `src/frontend/pages/records.py` | Direct reads of bounded windows during pre-spec inspection (sidebar pager block, selectbox, edit controls, empty-state branches, record loop) — anchors re-verified by the create task this session |
| UI testing standard of record | doc | `docs/development/ui_testing_standard.md` | Referenced by repository guidelines as the Playwright standard; consulted during testability assessment |
| Playwright e2e conventions | code | `test/ui/` (existing gated modules) | Pattern inspection during pre-spec inspection |
| Source-inspection red-test conventions | code | `test/` (existing `test_records_*_red.py` modules) | Pattern inspection during pre-spec inspection |
| Brainstorm handoff (decisions D1-D7) | analysis artifact | `tmp/discussion-records-nav/artifacts/preliminary/handoff.yaml` | Consumed as the primary input of requirements extraction |
| Baseline layout captures | evidence artifact | `tmp/discussion-records-nav/artifacts/` (6 PNGs, 1280px) | Vision-reviewed during the discussion phase |
| Record-update service path | code | `src/services/linguistic_service.py` | Read-only reference — called unchanged by auto-save (path corrected and verified 2026-10-05) |
| Preference service path | code | `src/services/preference_service.py` | Read-only reference — page-size persistence unchanged (path corrected and verified 2026-10-05) |

## 9. Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## 10. Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Running the Playwright sidebar-absence check costs minutes of execution time — the defect (pager removed without relocation, or over-deletion into the selectbox or edit controls) is caught at the gate. Skipping costs a full post-merge regression cycle — a destroyed selectbox or lost pagination surfaces on the live Records page and costs a diagnose-fix-re-review-redeploy round trip.
- **SC-2:** Capturing the top-row render costs minutes of execution time. Skipping costs a broken pagination surface discovered by stakeholders — the row may be absent, misplaced, or show stale captions, and the fix arrives after review cycles instead of before the commit.
- **SC-3:** Capturing the bottom-row render costs minutes of execution time. Skipping costs the same discovery latency as SC-2 — the bottom row is the one users reach after scrolling a full page of records, so its absence is the most visible failure of the relocation.
- **SC-4:** Running the click-through e2e (navigation, auto-save, boundaries) costs minutes of execution time. Skipping costs a data-integrity defect shipping to production — a silently dropped user edit or a divergent page-change path is discovered by the stakeholder's own edits, and data loss costs more than every test in this spec combined.
- **SC-5:** Running the empty-path capture costs minutes of execution time. Skipping costs a "Page 1 of 1" / "Showing 1-0 of 0" artifact rendering on every empty search — a defect visible on the page's most frequent degenerate state, caught only after stakeholder reports.
- **SC-6:** Counting the auto-save block occurrences costs one source-inspection run of seconds. Skipping costs silent divergence — duplicated save logic drifts apart on the first future edit to either copy, and the desynchronization ships undetected until a save behaves differently depending on which row triggered it.

## 11. Edge Cases

- **Condition:** Single-record view (page size 1) — the motivating case. **Expected behavior:** The twin rows flank the single record card; both rows show identical live captions; boundary disabling applies at page 1 and the last page in both rows. **Resolution:** Covered by SC-2/SC-3/SC-4 verification at page size 1.
- **Condition:** Partial last page — the record batch is shorter than the page size (e.g., page size 25 with 7 remaining records). **Expected behavior:** The showing range clamps to the records actually returned, against the total count; Next is disabled at the last page in both rows. **Resolution:** Live-caption derivation reuses the existing clamped computation (R-6).
- **Condition:** Zero total records — the empty-results path, including every semantic-status empty state. **Expected behavior:** No navigation rows and no pagination artifacts render in the main panel; the sidebar selectbox remains functional. **Resolution:** Suppression by construction — both call sites sit inside the non-empty records branch (SC-5).
- **Condition:** Page change while global edit mode is active with no pending edits. **Expected behavior:** The auto-save guard short-circuits and the page changes without any save. **Resolution:** Guard parity with the removed sidebar logic (R-8).
- **Condition:** Page change while global edit mode is active with pending edits present. **Expected behavior:** Each pending edit is persisted exactly once through the existing update path with the same change summary, pending state is cleared, then the page changes. **Resolution:** Auto-save semantics preserved verbatim (R-8, SC-4).
- **Condition:** Invalid position value passed to the shared helper. **Expected behavior:** Immediate fail-fast error rather than silent default rendering. **Resolution:** Explicit position validation in the helper (fail-fast per data-integrity rules).
- **Condition:** Duplicate widget keys across the two rows. **Expected behavior:** The framework raises a duplicate-widget error on render. **Resolution:** Position-namespaced keys prevent the collision by construction (R-10); SC-6 verifies the namespacing exists.
- **Condition:** Record-update failure during the auto-save pass. **Expected behavior:** The existing error behavior of the update path applies unchanged — no new swallowing, no new suppression. **Resolution:** Out of scope to change; semantics preserved (constraint C-2, requirement R-8).
- **Condition:** Both rows' buttons clicked within one interaction cycle. **Expected behavior:** The framework executes exactly one interaction per rerun, so both handlers cannot fire in a single pass; a single page change results. **Resolution:** Framework rerun model; asserted in the SC-4 e2e module's double-save failure-mode check.
- **Condition:** Filter, search-term, or page-size change while viewing a non-first page. **Expected behavior:** The current page resets to 1 exactly as today. **Resolution:** Untouched state management — the relocation changes where page-change buttons live, not the reset points.
