> **Full spec and artifacts: [`.issues/1401/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1401/)** — authoritative artifacts live in the `issues-data` branch.

# [SPEC] Search-match highlighting in Records view

## Intent and Executive Summary

**Problem Statement:** When a search returns records in the Records view, the rendered MDF block gives no indication of which text matched the query, forcing manual scanning of every rendered entry to locate the match. The system SHALL visually highlight matched terms inside the rendered MDF block in View mode for all search modes (Lexeme, Headword, Gloss, FTS, Semantic Gloss, Semantic All).

**Root Cause / Motivation:** The search pipeline stops at returning records — no matched-term data flows from the service layer to the renderer, and the renderer has no highlight mechanism for search matches. The existing diagnostics mechanism (`mark.diff-token` spans) proves the markup path is viable, but no search-side span data exists. Highlighting is needed now because search quality verification on real Algonquian corpus data (diacritics, IPA characters, infinity symbols) is a daily user activity and unlocatable matches erode trust in the search modes.

**Approach Chosen:** A three-layer additive design: a new pure span-computation module (stored-term verbatim find plus FTS normalized query-token scan) produces per-line offsets; the service search layer collects matched raw terms per record during the existing paginated query (query tokens for FTS, matched source-field terms for the semantic modes via the semantic search layer) and returns them in an additive optional field; the MDF block renderer accepts default-off highlight parameters and wraps matches in `mark.search-token` elements, with the Records page threading spans into the single View-mode render call.

**Alternatives Considered & Why Discarded:**
- *PostgreSQL `ts_headline` for FTS highlighting* — discarded: the FTS table stores only the tsvector of fully-normalized text, with no raw document and no positions, so `ts_headline` cannot mark raw rendered text (normalized positions refer to a string that is not stored).
- *Highlighting inside the MDF parser/formatter* — discarded: it would couple presentation state into the read-path parser, touching a surface the scope explicitly excludes, and would leak highlight concerns into revision-history and diff call sites that must stay untouched.
- *Semantic-mode highlighting via embedding similarity scores* — discarded by design decision: approximate/fuzzy highlighting is prohibited by the data-integrity mandate; the confirmed design instead anchors semantic highlights on the matched source-field term returned by the semantic search layer (deterministic verbatim span computation), not on similarity scores.

**Key Design Decisions:**
- *Whole-term granularity over sub-word spans* — tradeoff: simpler, deterministic spans that match user expectation of "the term lit up" at the cost of not pinpointing the exact sub-word character range.
- *Pure span-computation module separate from the renderer* — tradeoff: one new file and an import of the normalizer into presentation-adjacent code, in exchange for unit-testability without Streamlit or database and an additive-only renderer.
- *Single normalizer reuse (`generate_sort_lx`) for the FTS scan* — tradeoff: a service-layer dependency in presentation code, in exchange for guaranteed normalization parity between what FTS indexes and what gets highlighted (infinity→oozzz mapping preserved).
- *Additive optional `matched_terms` field defaulting to None* — tradeoff: a nullable field threading through the result contract, in exchange for zero breakage of existing construction sites and the semantic seam mirror; FTS leaves the field None, while Semantic modes populate it from the matched source-field term of the matched `SemanticSearchEntry` (`SemanticSearchResult` returns record_id, entry_type, term, similarity).
- *Ignore-not-clamp for malformed spans* — tradeoff: a highlight span whose offsets are invalid is dropped rather than clamped to the line boundary, in exchange for never highlighting text the span did not intend (clamping can fabricate a highlight over unintended characters, violating the data-integrity posture); the render always completes.
- *Measured styling criteria over quality adjectives* — tradeoff: the spec pins a WCAG 2.1 AA contrast ratio of at least 4.5:1 and computed-color distinctness instead of the unverifiable terms "reasonable contrast" and "visually distinct", in exchange for mechanically verifiable CSS targets in both theme variants.
- *Diff-token precedence in the coexistence rule* — tradeoff: where a highlight span overlaps a diagnostics diff-token span, the diff-token span wins and the overlapping search-token mark is omitted, in exchange for guaranteed behavioral stability of diagnostics rendering as mandated by R-16.

**User Intent / Original Prompt:** Stakeholder request: search matches should be highlighted in the rendered record so users can see where their search term occurs; brainstorming session confirmed whole-term granularity, teal/cyan styling, all-modes coverage (semantic modes anchored on matched source-field terms), View-mode-only application, and no highlight when the search box is empty (design approved; handoff artifacts under `tmp/issue-1401/artifacts/preliminary/`).

## Not Included

- **Approximate or fuzzy semantic highlighting** — similarity scores remain the semantic relevance surface; semantic highlighting anchors only on the matched source-field term returned by the semantic search layer, never on similarity-derived approximations (data-integrity mandate).
- **Edit-mode highlighting** — the Streamlit textarea cannot render rich markup; highlighting there is technically impossible without replacing the editor.
- **Revision history and import diff views** — their renderer call sites stay untouched via default-off parameters; highlighting there was not requested and would couple diff semantics to search state.
- **Sub-word / partial-term spans** — developer decision: whole-term granularity only; partial spans add complexity without user value.
- **Fuzzy or approximate matching** — absent terms degrade to a no-op; fabricating approximate matches violates the data-integrity mandate.
- **Database schema changes, migrations, new endpoints** — search tables already store raw `term` values verbatim; `fts_entries` is untouched.
- **`ts_headline` usage** — not viable against stored data (no raw document, no positions).
- **New session-state keys, preference toggle, caching layer** — highlighting activates automatically with an active-mode query; span computation is cheap enough per page render that caching adds state without need.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|-----------------------|
| SC-1 | A pure stored-term span helper returns a whole-term (start, end) offset pair for every verbatim occurrence of every provided stored raw term in a rendered line, scanning deterministically left-to-right. | behavioral | pytest unit execution over verbatim, NFD-diacritic, IPA, infinity-symbol, and overlapping-term samples with output inspection | `src/frontend/search_highlight.py` (new); `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` |
| SC-2 | The pure stored-term span helper returns an empty span list when a provided term does not occur in the rendered line, when the term list is empty, or when the rendered line is empty. | behavioral | pytest unit execution over absent-term, empty-term-list, and empty-line samples with output inspection | `src/frontend/search_highlight.py` (new); `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` |
| SC-3 | The pure FTS span helper emits a whole-word span for every rendered-line word whose normalized form matches any query token, where query tokens are produced by the service normalizer with the FTS strategy's tsquery-unsafe stripping and `:*` prefix semantics. | behavioral | pytest unit execution with output inspection over normalization-parity, prefix-semantics, multi-token, and Unicode edge samples | `src/services/linguistic_service.py` (normalizer and FTS strategy); `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` |
| SC-4 | The pure FTS span helper returns an empty span list when the query yields no tokens (including queries containing only tsquery-unsafe characters) or when no rendered-line word matches a query token. | behavioral | pytest unit execution over token-free query, empty query, and no-match samples with output inspection | `src/services/linguistic_service.py` (normalizer and FTS strategy); `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` |
| SC-5 | The service search result container gains an additive optional matched-terms field defaulting to None such that all existing construction sites remain source-compatible. | behavioral | pytest integration execution against the test database with output inspection (field default value, construction-site compatibility) | `src/services/linguistic_service.py` |
| SC-6 | The page-local mirror container carries the same optional matched-terms field such that semantic seam construction completes without raising. | behavioral | pytest integration execution constructing the mirror container with the new field and output inspection | `src/frontend/pages/records.py` (mirror container) |
| SC-7 | The service search method collects the deduplicated set of matched raw term values grouped by record identifier for Lexeme, Headword, and Gloss modes within the existing paginated query pass. | behavioral | pytest integration execution against the test database with output inspection (per-mode collection, per-record dedup, bounded to the paginated window) | `src/services/linguistic_service.py` |
| SC-8 | FTS mode searches return the matched-terms field as None (no raw-term anchor); Semantic mode searches (Semantic Gloss, Semantic All) populate matched-terms from the matched source-field terms of the semantic search layer (`SemanticSearchResult` term values), grouped and deduplicated per record identifier. | behavioral | pytest integration execution with output inspection (None for FTS; per-record deduplicated source-field terms for Semantic strategies) | `src/services/linguistic_service.py` |
| SC-9 | Every MDF block renderer call site that does not supply the new optional highlight span parameters renders markup-identically to its current output — identical rendered markup for identical inputs, with CSS styling blocks excluded from the comparison (styling is separately governed by SC-14 through SC-16). | behavioral | pytest/AppTest smoke execution plus markup comparison (CSS excluded) confirming the revision-history and import-diff call sites are unchanged | `src/frontend/ui_utils.py` |
| SC-10 | When highlight spans are supplied, the renderer wraps each span's covered text range in `mark.search-token` elements with output escaping preserved. | behavioral | pytest/AppTest smoke execution for markup structure plus Playwright DOM assertions on rendered output | `src/frontend/ui_utils.py` |
| SC-11 | Highlight spans that are malformed or out of range (negative offsets, start greater than or equal to end, or end beyond the line length) are ignored by the renderer — dropped without raising — and rendering of all other content is unaffected. | behavioral | pytest/AppTest smoke execution feeding malformed and out-of-range span samples and asserting no exception and no mark for dropped spans | `src/frontend/ui_utils.py` |
| SC-12 | The renderer applies the defined precedence rule: where a highlight span overlaps a diff-token span, the diff-token span renders unchanged and the overlapping search-token mark is omitted. | behavioral | pytest/AppTest smoke execution plus Playwright DOM assertions with overlapping span samples | `src/frontend/ui_utils.py` |
| SC-13 | Status line tints render unchanged when search-token highlighting is active. | behavioral | Playwright DOM and computed-style assertions comparing status tint output with and without active highlighting | `src/frontend/ui_utils.py` |
| SC-14 | Search-token marks render with the defined teal/cyan background tint and bold font weight. | behavioral | Playwright computed-style assertions on rendered marks | `src/frontend/ui_utils.py` (CSS block) |
| SC-15 | The computed background-color of search-token marks differs from the computed background-colors of diff-token marks and of status line tints in both the light and dark theme variants. | behavioral | Playwright computed-style comparison across both theme variants with screenshots archived | `src/frontend/ui_utils.py` (CSS block); `docs/development/ui_testing_standard.md` |
| SC-16 | The contrast ratio between the search-token mark's text color and the underlying block background is at least 4.5:1 (WCAG 2.1 AA normal-text threshold) in both the light and dark theme variants. | behavioral | Playwright computed-style contrast-ratio computation in both theme variants with screenshots archived | `src/frontend/ui_utils.py` (CSS block); `docs/development/ui_testing_standard.md` |
| SC-17 | The Records page supplies highlight context (query, mode, and computed spans) only to the View-mode render call. | behavioral | Playwright real-browser behavioral execution confirming revision-history and diff renders receive no highlight parameters | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-18 | With a lexical-mode query active, highlighting activates automatically in the rendered block in a fresh session, without any preference toggle or prior configuration. | behavioral | Playwright real-browser behavioral execution across Lexeme, Headword, Gloss, and FTS modes from a fresh session state | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-19 | With an empty search query, the rendered block contains no search-token marks. | behavioral | Playwright real-browser behavioral execution on empty-query searches with DOM assertions | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-20 | In Semantic Gloss and Semantic All modes with an active query, the rendered block highlights the matched source-field terms using the same verbatim whole-term span computation (`compute_term_spans`) used for stored terms; no approximate or fabricated spans. | behavioral | Playwright real-browser behavioral execution across both semantic modes with DOM assertions on matched-term marks | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-21 | The gated end-to-end suite on the live local app verifies that a search in each lexical mode highlights matches in the rendered block. | behavioral | Playwright E2E execution gated by `SNEA_E2E=1` plus live app on port 8501, with screenshots archived under the issue's artifact directory; gate-skipping is by design and never silently treated as a pass | `test/ui/` (Playwright suite); `docs/development/ui_testing_standard.md` |
| SC-22 | The gated end-to-end suite on the live local app verifies that Semantic modes with an active query produce search-token marks containing the matched source-field term; absence of marks is verified only when no term matches or the query is empty. | behavioral | Playwright E2E execution gated by `SNEA_E2E=1` plus live app on port 8501; gate-skipping is by design and never silently treated as a pass | `test/ui/` (Playwright suite); `docs/development/ui_testing_standard.md` |
| SC-23 | The gated end-to-end suite on the live local app verifies the absence of search-token marks on an empty query. | behavioral | Playwright E2E execution gated by `SNEA_E2E=1` plus live app on port 8501; gate-skipping is by design and never silently treated as a pass | `test/ui/` (Playwright suite); `docs/development/ui_testing_standard.md` |

## Requirements

R-1. The system SHALL visually highlight matched terms inside the rendered MDF block in Records View mode when a search query is active in any search mode.
R-2. The system SHALL apply highlighting at whole-term granularity: any term containing a match SHALL highlight in full, never as a sub-word span.
R-3. The system SHALL apply highlighting in all search modes: Lexeme, Headword, and Gloss via stored raw-term verbatim find; FTS via query-token normalized scan; and Semantic Gloss and Semantic All via the matched source-field term returned by the semantic search layer (`SemanticSearchEntry`/`SemanticSearchResult`), anchored with the same whole-term verbatim span computation used for stored terms.
R-4. The system SHALL locate stored raw terms verbatim in rendered text for ILIKE modes (Lexeme, Headword, Gloss) using a plain substring find of the whole term string.
R-5. The system SHALL, for FTS mode, normalize the query tokens the same way the FTS search strategy does and perform a Unicode-aware normalized scan of rendered lines, honoring prefix semantics for `:*` and multi-token queries.
R-6. The system SHALL degrade gracefully when a matched term cannot be located in rendered text: it SHALL yield no highlight span for that term and SHALL NOT use fuzzy or approximate matching.
R-7. The system SHALL expose matched terms through an additive optional field on the service search result container that defaults to None, and the page-local mirror container SHALL gain the same optional field so the semantic seam construction remains intact.
R-8. The system SHALL expose highlight rendering through optional default-off parameters on the MDF block renderer, leaving the revision-history and import-diff call sites markup-identical (CSS styling blocks excluded from the comparison) without edits.
R-9. The system SHALL collect matched terms inside the service search method after strategy dispatch, so all ILIKE modes share one implementation; FTS SHALL leave the field as None, and semantic strategies SHALL populate matched terms from their matched source-field entries (`SemanticSearchEntry` term values).
R-10. The Records page SHALL thread search context (query, mode, matched-term spans) from session state and the search result into the View-mode render call only, introducing no new session-state keys and no preference toggle.
R-11. The FTS span scan SHALL reuse the service normalization function as the single normalizer; a second normalizer implementation SHALL NOT be introduced.
R-12. Span computation SHALL be implemented as pure helpers, testable without Streamlit or database dependencies.
R-13. Search-token marks SHALL render with a teal/cyan tint plus bold weight, with a computed background-color that differs from the computed background-colors of the yellow diff-token marks and the status line tints, with defined styles for both light and dark theme variants.
R-14. All matching logic SHALL be Unicode-aware: NFD-decomposed diacritics, IPA characters, infinity symbols, and fancy quotes SHALL be handled; ASCII-only character classes SHALL NOT be used; the infinity symbol SHALL map to its normalized form consistently with the service normalizer.
R-15. The change SHALL introduce no database schema change, no migration, no new endpoints, and no modifications to MDF parsing or database write paths (read-path only).
R-16. Search-token marks SHALL NOT alter diagnostics behavior. The coexistence and precedence rule is: where a search-token span would overlap a diff-token span, the diff-token span SHALL render unchanged and the overlapping search-token mark SHALL be omitted; status line tints SHALL render unchanged when search-token highlighting is active. Both rule clauses SHALL be tested.
R-17. Search-token styling SHALL achieve a contrast ratio of at least 4.5:1 (WCAG 2.1 AA normal-text threshold) between the mark's text color and the underlying block background in both the light and dark theme variants.
R-18. Per-rendered-record span computation SHALL remain bounded (linear in lines times terms over the paginated page window), with matched-term collection as a join-side aggregation in the existing paginated query and no new caching layer.
R-19. User-visible highlight behavior SHALL be verified with Playwright real-browser tests per the UI testing standard; AppTest SHALL be smoke-only; end-to-end tests SHALL be gated by `SNEA_E2E=1` plus the live app on port 8501, and gate-skipping SHALL be by design and never silently treated as a pass.
R-20. The renderer SHALL ignore highlight spans that are malformed or out of range (negative offsets, start greater than or equal to end, or end beyond the line length) by dropping them without raising; rendering of all other content SHALL be unaffected.

## Items

### Item 1 (SC-1): Stored-term span helper — occurrence spans

- RED: pytest unit test that fails because the pure stored-term span helper does not exist — samples cover verbatim find, NFD diacritics, IPA characters, infinity symbols, and overlapping/adjacent term occurrences.
- GREEN: implement the pure helper in the new presentation-adjacent module (no Streamlit or database imports): deterministic left-to-right whole-term substring find returning per-line (start, end) offsets for every occurrence of every provided term.
- verify: run the unit suite; confirm the emitted span set matches the defined contract exactly.
- commit: new pure module plus its unit tests.

### Item 2 (SC-2): Stored-term span helper — no-match empty contract

- RED: pytest unit test that fails because the helper does not return empty span lists for no-match inputs — samples cover absent terms, empty term lists, and empty lines.
- GREEN: implement the no-match branches of the pure helper: empty span list whenever no verbatim occurrence exists.
- verify: run the unit suite; confirm empty-span behavior for all no-match samples.
- commit: helper extension plus its unit tests.

### Item 3 (SC-3): FTS query-token span helper — match spans

- RED: pytest unit test that fails because the pure FTS span helper does not exist — samples cover query normalization parity with the FTS strategy (tsquery-unsafe stripping, `:*` prefix semantics, multi-token queries), Unicode-safe line tokenization without ASCII-only classes, and infinity→normalized-form consistency.
- GREEN: implement the pure helper reusing the service normalizer as the sole normalization entry point; scan candidate words, normalize each on the fly, and emit whole-word spans for matches.
- verify: run the unit suite; confirm normalization parity and correct span emission.
- commit: helper extension plus its unit tests.

### Item 4 (SC-4): FTS query-token span helper — no-match empty contract

- RED: pytest unit test that fails because the FTS helper does not return empty span lists for no-match inputs — samples cover token-free queries (only tsquery-unsafe characters), empty queries, and no-match lines.
- GREEN: implement the no-match branches of the FTS helper: empty span list whenever no query token survives cleaning or no line word matches.
- verify: run the unit suite; confirm no-op behavior on all no-match samples.
- commit: helper extension plus its unit tests.

### Item 5 (SC-5): Additive matched-terms field on the service result container

- RED: pytest integration test that fails because the service search result container has no matched-terms field.
- GREEN: add the optional default-None matched-terms field to the service search result container, keeping all existing construction sites source-compatible.
- verify: run the service integration suite; confirm the field defaults to None and existing construction sites still work.
- commit: service container change plus integration tests.

### Item 6 (SC-6): Matched-terms field on the page-local mirror container

- RED: pytest integration test that fails because the page-local mirror container has no matched-terms field.
- GREEN: add the same optional default-None matched-terms field to the page-local mirror container.
- verify: run the service integration suite; confirm the semantic seam construction completes without raising.
- commit: mirror container change plus integration tests.

### Item 7 (SC-7): Matched-term collection for ILIKE modes

- RED: pytest integration test that fails because the service search method does not collect matched raw terms — covers per-mode collection (Lexeme/Headword/Gloss), per-record grouping, and per-record dedup.
- GREEN: implement join-side matched-term aggregation in the service search method within the existing paginated query, grouped and deduplicated per record identifier.
- verify: run the service integration suite; confirm the collected map matches the defined contract.
- commit: service collection logic plus integration tests.

### Item 8 (SC-8): FTS None; Semantic matched source-field terms

- RED: pytest integration test that fails because the FTS strategy does not leave the matched-terms field as None and the Semantic strategies do not populate it with matched source-field terms.
- GREEN: FTS leaves matched-terms as None; Semantic Gloss and Semantic All populate matched-terms from `SemanticSearchResult` term values (the matched source-field term of the matched `SemanticSearchEntry`), grouped and deduplicated per record identifier.
- verify: run the service integration suite; confirm None for FTS and per-record deduplicated source-field terms for both semantic strategies.
- commit: strategy-level guards plus integration tests.

### Item 9 (SC-9): Default-off highlight parameters — markup-identical default rendering

- RED: markup-comparison smoke test that fails because the renderer has no highlight parameters and any parameterless change would alter output. CSS styling blocks are excluded from the comparison.
- GREEN: add optional default-off highlight span parameters to the MDF block renderer; call sites that do not supply them render markup-identically.
- verify: run the smoke tests and markup comparison; confirm the revision-history and import-diff call sites render markup-identically.
- commit: renderer signature change plus comparison tests.

### Item 10 (SC-10): Search-token markup wrapping with escaping preserved

- RED: markup smoke test plus Playwright DOM assertion that fail because the renderer emits no `mark.search-token` elements.
- GREEN: wrap each supplied span's covered text range in `mark.search-token` elements with output escaping preserved.
- verify: run the smoke tests and Playwright DOM assertions; confirm escaping on matched text containing markup-sensitive characters.
- commit: renderer markup change plus tests.

### Item 11 (SC-11): Malformed-span ignore strategy

- RED: smoke test that fails because the renderer raises or misrenders on malformed or out-of-range spans.
- GREEN: drop highlight spans with negative offsets, start greater than or equal to end, or end beyond the line length, without raising; all other content renders unaffected.
- verify: run the smoke tests; confirm no exception and no mark for dropped spans.
- commit: defensive bounds handling plus tests.

### Item 12 (SC-12): Diff-token overlap precedence rule

- RED: smoke test plus Playwright DOM assertion that fail because the precedence rule is not implemented.
- GREEN: implement the defined precedence rule — where a highlight span overlaps a diff-token span, the diff-token span renders unchanged and the overlapping search-token mark is omitted.
- verify: run the smoke tests and DOM assertions with overlapping span samples.
- commit: precedence implementation plus tests.

### Item 13 (SC-13): Status line tint non-interference

- RED: Playwright assertion that fails because search highlighting alters status line tints.
- GREEN: ensure status line tints render unchanged when search-token highlighting is active.
- verify: run the Playwright assertions comparing status tint output with and without active highlighting.
- commit: non-interference guarantee plus tests.

### Item 14 (SC-14): Search-token base styling

- RED: Playwright computed-style assertion that fails because no `mark.search-token` styles exist.
- GREEN: add the CSS block alongside the existing mark styles: teal/cyan background tint plus bold font weight.
- verify: run the Playwright computed-style assertions.
- commit: CSS plus style tests.

### Item 15 (SC-15): Distinctness from diagnostic marks

- RED: Playwright computed-style assertion that fails because the search-token color is not distinct from diff-token marks and status tints.
- GREEN: define theme-variant styles such that the computed background-color of search-token marks differs from the computed background-colors of diff-token marks and status line tints in both themes.
- verify: run the Playwright computed-style comparisons in both themes; archive screenshots.
- commit: CSS refinement plus visual tests.

### Item 16 (SC-16): Contrast threshold verification

- RED: Playwright contrast-ratio assertion that fails because the search-token styling does not meet the 4.5:1 threshold.
- GREEN: adjust the theme-variant styles so the contrast ratio between the mark's text color and the underlying block background is at least 4.5:1 (WCAG 2.1 AA normal-text) in both themes.
- verify: run the Playwright contrast-ratio computation in both themes; archive screenshots.
- commit: CSS refinement plus contrast tests.

### Item 17 (SC-17): View-mode-only highlight threading

- RED: Playwright behavioral test that fails because the View-mode render call does not thread highlight context (or other call sites receive it).
- GREEN: supply query, mode, and computed spans to the View-mode render call only.
- verify: run Playwright behavioral assertions; confirm revision-history and diff renders receive no highlight parameters.
- commit: page wiring plus behavioral tests.

### Item 18 (SC-18): Auto-activation without configuration

- RED: Playwright behavioral test that fails because highlighting does not activate from a lexical-mode query alone in a fresh session.
- GREEN: activate highlighting automatically when a lexical-mode query is present, with no preference toggle or prior configuration.
- verify: run Playwright behavioral assertions across Lexeme, Headword, Gloss, and FTS modes from a fresh session state.
- commit: activation wiring plus behavioral tests.

### Item 19 (SC-19): Empty-query no-highlight boundary

- RED: Playwright behavioral test that fails because an empty query still produces search-token marks.
- GREEN: ensure the empty-query boundary produces no search-token marks in the rendered block.
- verify: run Playwright behavioral assertions on empty-query searches.
- commit: boundary wiring plus behavioral tests.

### Item 20 (SC-20): Semantic-mode source-field-term highlighting

- RED: Playwright behavioral test that fails because Semantic Gloss or Semantic All renders do not highlight the matched source-field terms.
- GREEN: thread the semantic matched source-field terms into the View-mode render and highlight them with the same verbatim whole-term span computation used for stored terms; never approximate or fabricate spans.
- verify: run Playwright behavioral assertions across both semantic modes.
- commit: semantic wiring plus behavioral tests.

### Item 21 (SC-21): Gated E2E — lexical-mode highlight flow

- RED: gated E2E test that fails pre-wiring when enabled (`SNEA_E2E=1` with live app on port 8501).
- GREEN: complete the end-to-end flow: a search in each lexical mode highlights matches in the rendered block.
- verify: run the gated suite; a gate-skipped run is recorded as skipped by design, never as a pass.
- commit: E2E suite plus archived screenshots when executed.

### Item 22 (SC-22): Gated E2E — semantic-mode matched-term presence

- RED: gated E2E assertion that fails because Semantic modes do not show matched-term highlighting when enabled.
- GREEN: verify end-to-end on the live local app that Semantic modes with an active query show search-token marks containing the matched source-field term, and that no marks appear when no term matches or the query is empty.
- verify: run the gated suite; a gate-skipped run is recorded as skipped by design, never as a pass.
- commit: E2E assertions plus archived screenshots when executed.

### Item 23 (SC-23): Gated E2E — empty-query absence

- RED: gated E2E assertion that fails because an empty query shows highlighting when enabled.
- GREEN: verify end-to-end on the live local app that an empty query shows no search-token marks.
- verify: run the gated suite; a gate-skipped run is recorded as skipped by design, never as a pass.
- commit: E2E assertions plus archived screenshots when executed.

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| `docs/development/ui_testing_standard.md` | MUST be read before writing or running any UI test — Playwright real-browser tests are the standard of record for user-visible behavior | exists |
| `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | MUST be read before writing matching/tokenization code — ASCII-based regex destroys linguistic data | exists |
| `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | MUST be read for FTS normalization consistency — infinity is a valid letter mapping to its normalized form | exists |
| Existing service search-result container and page-local mirror (the semantic seam contract) | MUST be preserved additively — the mirror construction SHALL NOT raise after the new field | exists in code |
| Brainstorming handoff artifacts (`tmp/issue-1401/artifacts/preliminary/`) | Design input with developer decisions already approved | complete |
| pytest and Playwright test infrastructure (`test/`, `test/ui/`) | Verification instruments for all SCs | exists |
| Local PostgreSQL test instance and local live app for the gated E2E | Required at verification time; tests never run against production data | available |

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-10, SC-18 | Phase 3 |
| R-2 | SC-1, SC-3 | Phase 1 |
| R-3 | SC-8, SC-18, SC-20, SC-21, SC-22 | Phase 2, Phase 3, Phase 4 |
| R-4 | SC-1 | Phase 1 |
| R-5 | SC-3 | Phase 1 |
| R-6 | SC-2, SC-4, SC-11 | Phase 1, Phase 3 |
| R-7 | SC-5, SC-6 | Phase 2 |
| R-8 | SC-9 | Phase 3 |
| R-9 | SC-7 | Phase 2 |
| R-10 | SC-17, SC-18 | Phase 3 |
| R-11 | SC-3 | Phase 1 |
| R-12 | SC-1, SC-2, SC-3, SC-4 | Phase 1 |
| R-13 | SC-14, SC-15 | Phase 3 |
| R-14 | SC-1, SC-2, SC-3, SC-4 | Phase 1 |
| R-15 | SC-5, SC-9 | Phase 2, Phase 3 |
| R-16 | SC-12, SC-13 | Phase 3 |
| R-17 | SC-16 | Phase 3 |
| R-18 | SC-1, SC-3, SC-7 | Phase 1, Phase 2 |
| R-19 | SC-9, SC-10, SC-11, SC-12, SC-13, SC-14, SC-15, SC-16, SC-17, SC-18, SC-19, SC-20, SC-21, SC-22, SC-23 | Phase 3, Phase 4 |
| R-20 | SC-11 | Phase 3 |

Phases: Phase 1 = pure span helpers (SC-1 through SC-4); Phase 2 = service data layer (SC-5 through SC-8); Phase 3 = renderer, styling, and page wiring (SC-9 through SC-20); Phase 4 = gated end-to-end verification (SC-21 through SC-23). Dependency ordering: SC-1 through SC-4 are mutually independent; SC-5 through SC-8 are mutually independent and independent of Phase 1; SC-9 through SC-13 depend on the span contract of SC-1 and SC-3; SC-14 through SC-16 depend on SC-10; SC-17 through SC-20 depend on SC-9 and SC-7; SC-21 through SC-23 depend on all.

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| Service search layer (strategies, result container, normalizer) | code | `src/services/linguistic_service.py` | bounded line-range reads, 2026-10-02 |
| Records page (search state, semantic seam, View-mode render call) | code | `src/frontend/pages/records.py` | bounded line-range reads, 2026-10-02 |
| MDF block renderer (signature, span markup, CSS, theming) | code | `src/frontend/ui_utils.py` | bounded line-range reads, 2026-10-02 |
| Search data models (raw term plus normalized columns, FTS table) | code | `src/database/models/search.py` | bounded line-range reads, 2026-10-02 |
| Search-table population paths (raw term stored verbatim) | code | `src/services/upload_service.py` | bounded line-range reads, 2026-10-02 |
| MDF formatter (field content preserved verbatim) | code | `src/mdf/parser.py` | bounded line-range reads, 2026-10-02 |
| UI testing standard (Playwright standard of record, E2E gating) | doc | `docs/development/ui_testing_standard.md` | read per AGENTS.md mandate |
| Unicode regex mandate (ASCII regex destroys linguistic data) | doc | `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | read; findings embedded in cross-cutting analysis |
| Infinity-symbol normalization (∞ is a valid letter) | doc | `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | read; mapping verified in normalizer source |
| Existing renderer test coverage gap | code search | `test/` | `rg -n "render_mdf_block" test/` returned zero matches, 2026-10-02 |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- SC-1: Running the stored-term span unit suite costs minutes of execution time — a Unicode defect in verbatim find is caught at the earliest gate with zero downstream cost. Skipping costs the full rework chain — the defect ships and surfaces as wrong or missing highlights on real corpus data, where diagnosis requires reproducing diacritic and infinity-symbol conditions the developer did not anticipate.
- SC-2: Running the no-match contract unit suite costs minutes of execution time — an empty-output defect is caught before integration. Skipping costs days — absent terms crash or misrender only when real corpus drift reaches production.
- SC-3: Running the FTS normalization-parity unit suite costs minutes of execution time — a normalization mismatch is caught before it can spread. Skipping costs days-to-weeks of discovery latency — highlighted spans disagree with indexed matches in production, and each fix cycle re-introduces the same drift because two normalizers disagree.
- SC-4: Running the FTS no-match contract unit suite costs minutes of execution time — a no-op defect is caught before integration. Skipping costs days — token-free queries highlight garbage or raise only when users type unusual queries.
- SC-5: Running the container-field integration suite costs minutes of execution time — a broken additive field is caught at the gate. Skipping costs hours-to-days — a TypeError in an existing construction site surfaces only when a user opens search, requiring data-integrity investigation.
- SC-6: Running the mirror-construction integration suite costs minutes of execution time — a broken semantic seam is caught at the gate. Skipping costs data-integrity investigation when semantic search raises on the new field.
- SC-7: Running the collection integration suite costs minutes of execution time — a collection or dedup defect is caught before UI wiring. Skipping costs days — a silently fabricated or missing matched-terms map propagates wrong highlights into the renderer.
- SC-8: Running the strategy-contract integration suite costs minutes of execution time — a mode-contract defect (an FTS leak into matched-terms, or missing or duplicated semantic source-field terms) is caught at the gate. Skipping ships wrong or missing semantic anchors — highlights that disagree with the semantic search layer's matched terms, a data-integrity violation surfacing as wrong highlighting.
- SC-9: Running the markup-identity smoke suite costs minutes of execution time — a rendering regression is caught before UI review. Skipping costs days — altered diagnostics rendering ships to users, and the regression hunt spans renderer call sites that were supposed to stay markup-identical.
- SC-10: Running the markup smoke plus Playwright DOM assertions costs minutes of execution time — markup or escaping defects are caught before UI review. Skipping costs days — corrupted markup on matched text ships to users.
- SC-11: Running the malformed-span smoke suite costs minutes of execution time — a crash defect is caught before UI review. Skipping costs days — a span defect crashes the record view in production.
- SC-12: Running the precedence-rule assertions costs minutes of execution time — a coexistence defect is caught before UI review. Skipping costs days of regression hunting in diagnostics rendering that was supposed to stay stable.
- SC-13: Running the status-tint assertions costs minutes of execution time — a tint interference defect is caught before UI review. Skipping costs days — altered status rendering ships to users.
- SC-14: Running the base-style computed-style assertions costs minutes of execution time — a style defect is caught with archived screenshots as evidence. Skipping costs days — unstyled or wrong-colored marks ship to users.
- SC-15: Running the distinctness comparisons in both themes costs minutes of execution time — an indistinct-mark defect is caught before review. Skipping costs weeks — confusingly identical colors surface as user complaints that are expensive to reproduce.
- SC-16: Running the contrast-ratio computation in both themes costs minutes of execution time — a contrast defect is caught with archived screenshots as evidence. Skipping costs weeks — dark-theme-only contrast defects survive every light-theme review and surface as user complaints.
- SC-17: Running the View-mode-only behavioral suite costs minutes of execution time — a wrong-call-site wiring defect is caught as behavior. Skipping costs days-to-weeks — highlight appears in revision history or diff views where it was explicitly excluded.
- SC-18: Running the auto-activation behavioral suite costs minutes of execution time — an activation defect is caught as behavior. Skipping costs weeks — dead highlighting ships, eroding trust in the search modes.
- SC-19: Running the empty-query behavioral suite costs minutes of execution time — a boundary leak is caught as behavior. Skipping costs days — stray highlights appear on empty searches.
- SC-20: Running the semantic-mode behavioral suite costs minutes of execution time — a semantic anchoring defect is caught as behavior. Skipping costs weeks — semantic highlights disagree with the matched source-field term or fail to appear, and users lose trust in semantic search feedback.
- SC-21: Running the gated E2E when enabled costs minutes of execution time — the full search-to-highlight flow is verified as users experience it. Skipping the gate is legitimate; silently treating a gate-skip as a pass costs the entire verification chain its meaning — every upstream behavioral claim degrades to structural theater with discovery latency measured in production incidents.
- SC-22: Running the gated semantic-presence E2E when enabled costs minutes of execution time — semantic matched-term highlighting and its no-match/empty-query absence boundary are verified as users experience it. Skipping the gate is legitimate; silently treating a gate-skip as a pass degrades every upstream behavioral claim to structural theater.
- SC-23: Running the gated empty-query-absence E2E when enabled costs minutes of execution time — the empty-query boundary is verified as users experience it. Skipping the gate is legitimate; silently treating a gate-skip as a pass degrades every upstream behavioral claim to structural theater.

## Edge Cases

**Input boundaries:**
- Condition: empty search query. Expected behavior: no highlight parameters are threaded and rendering is identical to today. Resolution: the page computes spans only when a query is present in the active mode.
- Condition: empty term list or empty rendered line. Expected behavior: the span helpers return empty span lists. Resolution: empty input short-circuits to a no-op.
- Condition: a stored term longer than the rendered line or containing line-wrap artifacts. Expected behavior: no span is emitted for that term. Resolution: verbatim find simply does not match; no approximation is attempted.
- Condition: FTS query containing only tsquery-unsafe characters. Expected behavior: no tokens survive cleaning and no spans are emitted. Resolution: mirrors the FTS strategy's own token cleaning, producing a consistent no-op.

**State transitions:**
- Condition: user switches between modes with a query active. Expected behavior: highlight parameters appear in every mode — lexical modes from stored terms or query tokens, semantic modes from the matched source-field term — and disappear when the query is empty. Resolution: mode is part of the threaded context; spans are anchored only on matched terms returned by the active mode's search layer, never fabricated.
- Condition: user clears the search box. Expected behavior: highlighting deactivates entirely. Resolution: the empty-query boundary takes precedence.
- Condition: user paginates through results. Expected behavior: spans are recomputed per rendered page from the per-record matched terms. Resolution: matched-term collection is bounded to the paginated query window; nothing is cached across pages.

**Failure modes:**
- Condition: data drift — a stored term no longer appears verbatim in the rendered text. Expected behavior: that term yields no span and rendering continues normally. Resolution: graceful no-op per the data-integrity mandate; never fuzzy-matched, never fabricated.
- Condition: malformed or out-of-range span offsets reach the renderer. Expected behavior: spans with negative offsets, start greater than or equal to end, or end beyond the line length are ignored — dropped without raising — and all other content renders unchanged. Resolution: the single defined strategy is to drop invalid spans; no clamping, no fabricated highlight over unintended characters.
- Condition: span computation raises unexpectedly. Expected behavior: rendering of the record still completes. Resolution: the renderer treats highlight input as advisory presentation data, never as a correctness dependency of the record display.

**Concurrency:**
- Condition: concurrent user sessions search and render simultaneously. Expected behavior: no shared mutable highlight state exists. Resolution: matched terms and spans are per-request and per-render ephemeral values; no session-state keys, caches, or shared stores are introduced, so no cross-session races are possible.

**Recovery:**
- Condition: any highlight-path failure. Expected behavior: the record renders unhighlighted and the failure is confined to presentation. Resolution: no persistent state is introduced; a page reload or re-query recomputes everything from source data.

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-10-02 | Initial spec draft | — | spec-creation pipeline |
| 2026-10-02 | Split all 7 compound SCs into 23 atomic single-deliverable SCs (1:1 with plan items); fixed SC-4's "clamps or ignores" disjunction to the single ignore strategy (new R-20); replaced SC-5 subjective contrast language with the WCAG 2.1 AA 4.5:1 threshold and a computed-color distinctness criterion; collapsed R-7 "(or tolerate its absence)" to the single mirror-contract path; stated the coexistence/precedence rule content explicitly in R-16; updated Items, Traceability, Cost Frame, and Edge Cases to match | Validation findings: aggregate FAIL on 7 of 25 checks in two clusters — decomposition (compound-sc-detection, decomposition-atomicity, decomposition-single-deliverable, decomposition-binary-verifiability) and determinism/ambiguity (determinism, 1-implementability, 3-completeness, 5-testability) — with the validator's remediation directives | spec-creation validation pipeline (orchestrator-dispatched revision per validator remediation directives) |
| 2026-10-03 | Developer-confirmed revision: ALL search modes produce highlighting. SC-8 revised (FTS leaves matched_terms as None; Semantic modes now populate matched_terms from the matched source-field terms, per-record deduplicated); SC-20 revised (Semantic Gloss and Semantic All highlight the matched source-field terms in the rendered block — never-highlight boundary removed); SC-22 revised (E2E semantic presence: search-token marks contain the matched term; absence boundary only when no term matches or query is empty); R-1, R-3 and R-9 revised to all-modes scope; Problem Statement, Approach, Alternatives, Design Decisions, Not Included, Items 8/20/22, Traceability (R-3 row), Cost Frame (SC-8/20/22) and Edge Cases updated. SC numbering unchanged; all other SCs unchanged | Developer directive (2026-10-03): the spec-creation pipeline missed an explicit prior discussion; confirmed intent is all-modes highlighting anchored on the matched source-field term via the semantic search layer | Developer (Michael Conrad), 2026-10-03 |

## Revision Note — 2026-10-03

**Source of this revision:** developer-confirmed directive. The spec-creation pipeline missed an explicit prior discussion between developer and agent; the confirmed intent is that **ALL search modes produce highlighting** — not only the lexical ones.

**What changed in one paragraph:** The semantic modes (Semantic Gloss, Semantic All) now highlight using the **matched source-field term** from the semantic search layer. `SemanticSearchEntry` stores (record_id, entry_type 'lx'/'va'/'ge'/etc., term, embedding) and `SemanticSearchResult` returns (record_id, entry_type, term, similarity). The matched term is the highlight anchor, applied through the **same verbatim whole-term span computation (`compute_term_spans`) used for stored terms** — no similarity-based or approximate highlighting, preserving the data-integrity mandate.

**Revised items:** SC-8 (FTS keeps matched_terms as None; Semantic modes populate it per-record, deduplicated), SC-20 (semantic modes highlight the matched source-field terms in the rendered block), SC-22 (E2E semantic presence; absence boundary only when no term matches or query is empty), R-1/R-3/R-9 (all-modes scope), plus supporting updates in Problem Statement, Approach, Alternatives, Key Design Decisions, Not Included, Items 8/20/22, Traceability, Cost Frame and Edge Cases.

**Unchanged:** SC numbering (SC-1 through SC-23) and every other success criterion, requirement and item.

*Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)*
