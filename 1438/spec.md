# Spec — re-anchor semantic flow-suite zero-result probes to post-#1413 empty-path behavior (#1438, sub-issue of #1436)

## Problem

The #1385 semantic flow suite (`test/ui/test_semantic_search_ui_flow_e2e.py`) fails three tests under live E2E: `test_pagination_order_stability`, `test_empty_states_clean`, `test_ui_override_reaches_seam`. Triage (2026-10-12, #1436 comment) root-caused a spec-vs-spec conflict: #1413 (commit 2fa1a36) deliberately moved pagination out of the sidebar into the main panel's twin navigation rows (records.py:383-411, R-1 comment at records.py:594-596) and removed the pager from empty/zero-result paths (records.py:866-875 — the zero-results branch renders only `st.info`, no pagination row; #1413's SC-8 test `test_records_pagination_empty_sc8.py` asserts NO pager on empty paths and AST-pins the call sites).

The flow suite still asserts the pre-#1413 pager behavior in three places:

1. `_click_next`/`_click_prev` (lines 340-353) scope their button locators to `[data-testid="stSidebar"]` — the Next/Prev buttons no longer exist there, so `test_pagination_order_stability` fails at the click helper ("Next pagination button not found") even on a result-rich search.
2. `_sc6_flow` line 531 probes responsiveness after a zero-result search via `_page_label(page)` — unsatisfiable: no pager is rendered on the zero-result path post-#1413.
3. `_sc10_flow` line 590 probes responsiveness after the zero-result threshold-ceiling search via `_page_label(page)` — same unsatisfiable probe.

Not a flake, not load, not #1431/#1434: green screenshots pre-Oct 5 (`tmp/issue-1385`, `tmp/1400`) confirm the suite passed against pre-#1413 app behavior.

## Design direction (from #1436 triage, 2026-10-12)

Test-side re-anchor only — the app behavior is correct (it is #1413's specified, tested behavior):

1. **Click helpers:** `_click_next`/`_click_prev` drop the `stSidebar` scoping and locate the Prev/Next buttons in the main panel (the #1413 twin navigation rows).
2. **Zero-result responsiveness probes:** the two `_page_label` probes after zero-result searches (sc6, sc10) are replaced by a probe of the zero-result `st.info` ("No records scored above the semantic threshold") — already asserted and passing at line 528 before line 531 fails. Rendering of the info block is the responsiveness evidence; no pager assertion remains on empty paths.

No change to the app (`src/`), no change to assertions' semantics beyond re-anchoring to post-#1413 behavior, no coverage loss — every probe keeps a real DOM element as its subject.

## Requirements

- **SC-1 (behavioral):** under `SNEA_E2E=1` against the warmed live app on :8501 (freshly synced database), all three formerly failing tests in `test/ui/test_semantic_search_ui_flow_e2e.py` pass; the file's other tests keep their current outcomes.
- **SC-2 (structural):** the click helpers locate Prev/Next buttons without `stSidebar` scoping, and no responsiveness probe on a zero-result path references the pager; the change is confined to `test/ui/test_semantic_search_ui_flow_e2e.py`.
- **SC-3 (behavioral; no app change):** `test_records_pagination_empty_sc8.py` (the #1413 pin) still passes serverless — the re-anchor does not contradict #1413's spec.

## Verification instruments

Per the regression protocol, `bash scripts/sync_prod_to_local.sh` runs before the verification cycle, on the feature branch under test.

- **SC-1:** executed `SNEA_E2E=1` run of `test/ui/test_semantic_search_ui_flow_e2e.py` against the live app; the three nodeids green; output recorded under `tmp/1436/artifacts/`.
- **SC-2:** fact-decidable inspection of the diff (locator scope; probe replacements; path scope).
- **SC-3:** executed serverless run of `test/test_records_pagination_empty_sc8.py`; green.

## Out of scope

- Any app-side change (the empty-path pager removal is #1413's specified behavior).
- The API-class bolt-warmup race — parent issue #1436's scope.
- Marker alignment, assertions, thresholds, or coverage beyond the three probes named above.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
