> **Full spec and artifacts: [`.issues/1401/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1401/)** — authoritative artifacts live in the `issues-data` branch.

# [SPEC] Search-match highlighting in Records view

## Intent and Executive Summary

**Problem Statement:** When a search returns records in the Records view, the rendered MDF block gives no indication of which text matched the query, forcing manual scanning of every rendered entry to locate the match. The system SHALL visually highlight matched terms inside the rendered MDF block in View mode for the lexical search modes (Lexeme, Headword, Gloss, FTS).

**Root Cause / Motivation:** The search pipeline stops at returning records — no matched-term data flows from the service layer to the renderer, and the renderer has no highlight mechanism for search matches. The existing diagnostics mechanism (`mark.diff-token` spans) proves the markup path is viable, but no search-side span data exists. Highlighting is needed now because search quality verification on real Algonquian corpus data (diacritics, IPA characters, infinity symbols) is a daily user activity and unlocatable matches erode trust in the search modes.

**Approach Chosen:** A three-layer additive design: a new pure span-computation module (stored-term verbatim find plus FTS normalized query-token scan) produces per-line offsets; the service search layer collects matched raw terms per record during the existing paginated query and returns them in an additive optional field; the MDF block renderer accepts default-off highlight parameters and wraps matches in `mark.search-token` elements, with the Records page threading spans into the single View-mode render call.

**Alternatives Considered & Why Discarded:**
- *PostgreSQL `ts_headline` for FTS highlighting* — discarded: the FTS table stores only the tsvector of fully-normalized text, with no raw document and no positions, so `ts_headline` cannot mark raw rendered text (normalized positions refer to a string that is not stored).
- *Highlighting inside the MDF parser/formatter* — discarded: it would couple presentation state into the read-path parser, touching a surface the scope explicitly excludes, and would leak highlight concerns into revision-history and diff call sites that must stay untouched.
- *Semantic-mode highlighting via embedding similarity* — discarded by design decision: similarity scores are already the semantic feedback surface, and approximate/fuzzy highlighting is prohibited by the data-integrity mandate.

**Key Design Decisions:**
- *Whole-term granularity over sub-word spans* — tradeoff: simpler, deterministic spans that match user expectation of "the term lit up" at the cost of not pinpointing the exact sub-word character range.
- *Pure span-computation module separate from the renderer* — tradeoff: one new file and an import of the normalizer into presentation-adjacent code, in exchange for unit-testability without Streamlit or database and an additive-only renderer.
- *Single normalizer reuse (`generate_sort_lx`) for the FTS scan* — tradeoff: a service-layer dependency in presentation code, in exchange for guaranteed normalization parity between what FTS indexes and what gets highlighted (infinity→oozzz mapping preserved).
- *Additive optional `matched_terms` field defaulting to None* — tradeoff: a nullable field threading through the result contract, in exchange for zero breakage of existing construction sites and the semantic seam mirror.

**User Intent / Original Prompt:** Stakeholder request: search matches should be highlighted in the rendered record so users can see where their search term occurs; brainstorming session confirmed whole-term granularity, teal/cyan styling, lexical-modes-only coverage, View-mode-only application, and no highlight when the search box is empty (design approved; handoff artifacts under `tmp/issue-1401/artifacts/preliminary/`).

## Not Included

- **Semantic Gloss / Semantic All highlighting** — similarity scores are already rendered as the semantic feedback surface; approximate highlighting is prohibited (data-integrity mandate).
- **Edit-mode highlighting** — the Streamlit textarea cannot render rich markup; highlighting there is technically impossible without replacing the editor.
- **Revision history and import diff views** — their renderer call sites stay untouched via default-off parameters; highlighting there was not requested and would couple diff semantics to search state.
- **Sub-word / partial-term spans** — developer decision: whole-term granularity only; partial spans add complexity without user value.
- **Fuzzy or approximate matching** — absent terms degrade to a no-op; fabricating approximate matches violates the data-integrity mandate.
- **Database schema changes, migrations, new endpoints** — search tables already store raw `term` values verbatim; `fts_entries` is untouched.
- **`ts_headline` usage** — not viable against stored data (no raw document, no positions).
- **New session-state keys, preference toggle, caching layer** — highlighting activates automatically with a lexical-mode query; span computation is cheap enough per page render that caching adds state without need.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|-----------------------|
| SC-1 | A pure stored-term span helper returns whole-term (start, end) offsets for each verbatim occurrence of each stored raw term in a rendered line via a deterministic left-to-right scan, and returns an empty span list when a term is absent or the term list is empty. | behavioral | pytest unit execution over verbatim, NFD-diacritic, IPA, infinity-symbol, overlapping-term, and absent-term samples with output inspection | `src/frontend/search_highlight.py` (new); `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` |
| SC-2 | A pure FTS span helper normalizes the query with the service normalizer, extracts tokens with tsquery-unsafe stripping and `:*` prefix semantics, tokenizes the rendered line with Unicode-safe word matching (no ASCII-only character classes), and emits whole-word spans for line words whose normalized form matches any query token. | behavioral | pytest unit execution with output inspection over normalization-parity, prefix-semantics, multi-token, and Unicode edge samples | `src/services/linguistic_service.py` (normalizer and FTS strategy); `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` |
| SC-3 | The service search result container gains an additive optional matched-terms field defaulting to None, the page-local mirror container gains the same optional field, and the service collects matched raw term values grouped by record identifier for Lexeme/Headword/Gloss modes in the same paginated query pass while FTS and Semantic modes leave the field None. | behavioral | pytest integration execution against the test database with output inspection (per-mode collection, per-record dedup, None for FTS/Semantic, mirror construction with the new field) | `src/services/linguistic_service.py`; `src/frontend/pages/records.py` (mirror container) |
| SC-4 | The MDF block renderer accepts default-off highlight span parameters, wraps matched text in `mark.search-token` elements with output escaping preserved, applies a defined coexistence rule with diagnostics diff-token spans and status line tints, clamps or ignores malformed or out-of-range spans without crashing, and leaves all non-target call sites rendering byte-identically. | behavioral | pytest/AppTest smoke execution for markup structure plus Playwright DOM assertions on rendered output | `src/frontend/ui_utils.py` |
| SC-5 | Search-token marks render with a teal/cyan tint plus bold weight, visually distinct from the yellow diff-token marks and status line tints, with defined styles for both light and dark theme variants and reasonable contrast against both block backgrounds. | behavioral | Playwright real-browser visual assertions in both theme variants with screenshots archived | `src/frontend/ui_utils.py` (CSS block); `docs/development/ui_testing_standard.md` |
| SC-6 | The Records page threads query, mode, and matched-term spans into the View-mode render call only: highlighting activates automatically when a lexical-mode query is present, produces no highlight parameters on an empty query, and never activates in Semantic modes, with no new session-state keys or preference toggle. | behavioral | Playwright real-browser behavioral execution across lexical modes, empty query, and semantic modes with output inspection | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-7 | The gated end-to-end suite on the live local app verifies the full search-to-highlight flow across all lexical modes and the absence of highlighting in Semantic modes and on an empty query, with screenshots archived under the issue's artifact directory. | behavioral | Playwright E2E execution gated by `SNEA_E2E=1` plus live app on port 8501; gate-skipping is by design and never silently treated as a pass | `test/ui/` (Playwright suite); `docs/development/ui_testing_standard.md` |

## Requirements

R-1. The system SHALL visually highlight matched terms inside the rendered MDF block in Records View mode when a search query is active in a lexical mode.
R-2. The system SHALL apply highlighting at whole-term granularity: any term containing a match SHALL highlight in full, never as a sub-word span.
R-3. The system SHALL apply highlighting in the Lexeme, Headword, Gloss, and FTS modes and SHALL NOT apply highlighting in the Semantic Gloss or Semantic All modes.
R-4. The system SHALL locate stored raw terms verbatim in rendered text for ILIKE modes (Lexeme, Headword, Gloss) using a plain substring find of the whole term string.
R-5. The system SHALL, for FTS mode, normalize the query tokens the same way the FTS search strategy does and perform a Unicode-aware normalized scan of rendered lines, honoring prefix semantics for `:*` and multi-token queries.
R-6. The system SHALL degrade gracefully when a matched term cannot be located in rendered text: it SHALL yield no highlight span for that term and SHALL NOT use fuzzy or approximate matching.
R-7. The system SHALL expose matched terms through an additive optional field on the service search result container that defaults to None, and the page-local mirror container SHALL gain the same optional field (or tolerate its absence) so the semantic seam construction remains intact.
R-8. The system SHALL expose highlight rendering through optional default-off parameters on the MDF block renderer, leaving the revision-history and import-diff call sites byte-identical without edits.
R-9. The system SHALL collect matched terms inside the service search method after strategy dispatch, so all ILIKE modes share one implementation and semantic strategies remain untouched.
R-10. The Records page SHALL thread search context (query, mode, matched-term spans) from session state and the search result into the View-mode render call only.
R-11. The FTS span scan SHALL reuse the service normalization function as the single normalizer; a second normalizer implementation SHALL NOT be introduced.
R-12. Span computation SHALL be implemented as pure helpers, testable without Streamlit or database dependencies.
R-13. Search-token marks SHALL render with a teal/cyan tint plus bold weight, visually distinct from the yellow diff-token marks and status line tints, with defined styles for both light and dark theme variants.
R-14. All matching logic SHALL be Unicode-aware: NFD-decomposed diacritics, IPA characters, infinity symbols, and fancy quotes SHALL be handled; ASCII-only character classes SHALL NOT be used; the infinity symbol SHALL map to its normalized form consistently with the service normalizer.
R-15. The change SHALL introduce no database schema change, no migration, no new endpoints, and no modifications to MDF parsing or database write paths (read-path only).
R-16. Search-token marks SHALL NOT alter diagnostics behavior: the coexistence and precedence rule between search-token marks, diff-token spans, and status line tints SHALL be defined and tested.
R-17. Search-token styling SHALL hold reasonable contrast against both the light and dark block backgrounds.
R-18. Per-rendered-record span computation SHALL remain bounded (linear in lines times terms over the paginated page window), with matched-term collection as a join-side aggregation in the existing paginated query and no new caching layer.
R-19. User-visible highlight behavior SHALL be verified with Playwright real-browser tests per the UI testing standard; AppTest SHALL be smoke-only; end-to-end tests SHALL be gated by `SNEA_E2E=1` plus the live app on port 8501, and gate-skipping SHALL be by design and never silently treated as a pass.

## Items

### Item 1 (SC-1): Stored-term span computation helper

- RED: pytest unit test that fails because the pure stored-term span helper does not exist — samples cover verbatim find, NFD diacritics, IPA characters, infinity symbols, overlapping/adjacent term occurrences, absent terms, and empty term lists.
- GREEN: implement the pure helper in the new presentation-adjacent module (no Streamlit or database imports): deterministic left-to-right whole-term substring find returning per-line (start, end) offsets.
- verify: run the unit suite; confirm empty-span behavior for absent terms and empty term lists.
- commit: new pure module plus its unit tests.

### Item 2 (SC-2): FTS query-token span computation helper

- RED: pytest unit test that fails because the pure FTS span helper does not exist — samples cover query normalization parity with the FTS strategy (tsquery-unsafe stripping, `:*` prefix semantics, multi-token queries), Unicode-safe line tokenization without ASCII-only classes, infinity→normalized-form consistency, and empty-query no-op.
- GREEN: implement the pure helper reusing the service normalizer as the sole normalization entry point; scan candidate words, normalize each on the fly, and emit whole-word spans for matches.
- verify: run the unit suite; confirm normalization parity and no-op behavior on empty or token-free queries.
- commit: helper extension plus its unit tests.

### Item 3 (SC-3): Matched-term collection in the service search plus additive result fields

- RED: pytest integration test that fails because the additive matched-terms field and per-record collection do not exist — covers per-mode collection (Lexeme/Headword/Gloss), None for FTS/Semantic, per-record dedup, existing construction sites remaining source-compatible, and mirror construction with the new field.
- GREEN: add the optional default-None field to the service search result container and the page-local mirror container; implement join-side matched-term aggregation in the service search method within the existing paginated query.
- verify: run the service integration suite; confirm the semantic seam construction does not raise.
- commit: service layer plus mirror field plus integration tests.

### Item 4 (SC-4): Renderer highlight parameters and search-token markup

- RED: markup smoke test plus Playwright DOM assertion that fail because the renderer has no highlight parameters or search-token markup.
- GREEN: add optional default-off highlight span parameters to the MDF block renderer; wrap matched text in `mark.search-token` elements with escaping preserved; define the coexistence/precedence rule with diagnostics diff-token spans and status line tints; clamp or ignore malformed and out-of-range spans.
- verify: run the smoke tests and Playwright DOM assertions; confirm non-target call sites render byte-identically.
- commit: renderer changes plus markup tests.

### Item 5 (SC-5): Search-token CSS in both theme variants

- RED: Playwright visual assertion that fails because no `mark.search-token` styles exist.
- GREEN: add the CSS block alongside the existing mark styles: teal/cyan tint plus bold, distinct from the yellow diff-token and status tints, with both light and dark theme variants and reasonable contrast on both block backgrounds.
- verify: run Playwright visual assertions in both themes; archive screenshots.
- commit: CSS plus visual tests.

### Item 6 (SC-6): View-mode wiring in the Records page

- RED: Playwright behavioral test that fails because the View-mode render call does not thread highlight context.
- GREEN: thread query, mode, and computed spans into the single View-mode render call; highlight activates automatically when a lexical-mode query is present, deactivates on empty query, and never activates in Semantic modes; no new session-state keys.
- verify: run Playwright behavioral assertions across lexical modes, empty query, and semantic modes; confirm revision-history and diff renders unaffected.
- commit: page wiring plus behavioral tests.

### Item 7 (SC-7): Gated Playwright E2E — full search-to-highlight flow

- RED: gated E2E test that fails pre-wiring when enabled (`SNEA_E2E=1` with live app on port 8501).
- GREEN: complete the end-to-end flow: search in each lexical mode highlights matches in the rendered block; Semantic mode and empty query show no highlight; screenshots archived under the issue's artifact directory.
- verify: run the gated suite; a gate-skipped run is recorded as skipped by design, never as a pass.
- commit: E2E suite plus archived screenshots when executed.

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
| R-1 | SC-4, SC-6 | Phase 3 |
| R-2 | SC-1, SC-2 | Phase 1 |
| R-3 | SC-3, SC-6 | Phase 2, Phase 3 |
| R-4 | SC-1 | Phase 1 |
| R-5 | SC-2 | Phase 1 |
| R-6 | SC-1, SC-2, SC-4 | Phase 1, Phase 3 |
| R-7 | SC-3 | Phase 2 |
| R-8 | SC-4 | Phase 3 |
| R-9 | SC-3 | Phase 2 |
| R-10 | SC-6 | Phase 3 |
| R-11 | SC-2 | Phase 1 |
| R-12 | SC-1, SC-2 | Phase 1 |
| R-13 | SC-5 | Phase 3 |
| R-14 | SC-1, SC-2, SC-3 | Phase 1, Phase 2 |
| R-15 | SC-3 | Phase 2 |
| R-16 | SC-4, SC-5 | Phase 3 |
| R-17 | SC-5 | Phase 3 |
| R-18 | SC-1, SC-2, SC-3, SC-6 | Phase 1, Phase 2, Phase 3 |
| R-19 | SC-4, SC-5, SC-6, SC-7 | Phase 3, Phase 4 |

Phases: Phase 1 = pure span helpers (SC-1, SC-2); Phase 2 = service data layer (SC-3); Phase 3 = presentation and page wiring (SC-4, SC-5, SC-6); Phase 4 = gated end-to-end verification (SC-7). Dependency ordering: SC-1 and SC-2 are independent; SC-4 depends on SC-1 and SC-2; SC-5 depends on SC-4; SC-6 depends on SC-4 and SC-3; SC-7 depends on all.

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
- SC-2: Running the FTS normalization-parity unit suite costs minutes of execution time — a normalization mismatch is caught before it can spread. Skipping costs days-to-weeks of discovery latency — highlighted spans disagree with indexed matches in production, and each fix cycle re-introduces the same drift because two normalizers disagree.
- SC-3: Running the service integration suite costs minutes of execution time — a broken mirror construction or a fabricated match is caught at the gate. Skipping costs hours-to-days — a TypeError in the semantic seam or a silently fabricated matched-terms map surfaces only when a user opens semantic search, requiring data-integrity investigation.
- SC-4: Running the markup smoke plus Playwright DOM assertions costs minutes of execution time — escaping or coexistence defects are caught before UI review. Skipping costs days — corrupted markup or altered diagnostics rendering ships to users, and the regression hunt spans renderer call sites that were supposed to stay byte-identical.
- SC-5: Running the Playwright visual assertions in both themes costs minutes of execution time — a contrast or theme defect is caught with archived screenshots as evidence. Skipping costs weeks — dark-theme-only contrast defects survive every light-theme review and surface as user complaints that are expensive to reproduce.
- SC-6: Running the Playwright behavioral suite costs minutes of execution time — wiring defects (highlight in the wrong mode, wrong call site, or missing no-op) are caught as behavior. Skipping costs days-to-weeks — highlight appears in revision history or semantic modes where it was explicitly excluded, and users lose trust in the modes that were supposed to remain untouched.
- SC-7: Running the gated E2E when enabled costs minutes of execution time — the full search-to-highlight flow is verified as users experience it. Skipping the gate is legitimate; silently treating a gate-skip as a pass costs the entire verification chain its meaning — every upstream behavioral claim degrades to structural theater with discovery latency measured in production incidents.

## Edge Cases

**Input boundaries:**
- Condition: empty search query. Expected behavior: no highlight parameters are threaded and rendering is identical to today. Resolution: the page computes spans only when a lexical-mode query is present.
- Condition: empty term list or empty rendered line. Expected behavior: the span helpers return empty span lists. Resolution: empty input short-circuits to a no-op.
- Condition: a stored term longer than the rendered line or containing line-wrap artifacts. Expected behavior: no span is emitted for that term. Resolution: verbatim find simply does not match; no approximation is attempted.
- Condition: FTS query containing only tsquery-unsafe characters. Expected behavior: no tokens survive cleaning and no spans are emitted. Resolution: mirrors the FTS strategy's own token cleaning, producing a consistent no-op.

**State transitions:**
- Condition: user switches between lexical and semantic modes with a query active. Expected behavior: highlight parameters appear for lexical modes and disappear for semantic modes. Resolution: mode is part of the threaded context; semantic modes never receive spans.
- Condition: user clears the search box. Expected behavior: highlighting deactivates entirely. Resolution: the empty-query boundary takes precedence.
- Condition: user paginates through results. Expected behavior: spans are recomputed per rendered page from the per-record matched terms. Resolution: matched-term collection is bounded to the paginated query window; nothing is cached across pages.

**Failure modes:**
- Condition: data drift — a stored term no longer appears verbatim in the rendered text. Expected behavior: that term yields no span and rendering continues normally. Resolution: graceful no-op per the data-integrity mandate; never fuzzy-matched, never fabricated.
- Condition: malformed or out-of-range span offsets reach the renderer. Expected behavior: spans are clamped or ignored and the render completes. Resolution: defensive bounds handling in the renderer; a span defect must never crash the record view.
- Condition: span computation raises unexpectedly. Expected behavior: rendering of the record still completes. Resolution: the renderer treats highlight input as advisory presentation data, never as a correctness dependency of the record display.

**Concurrency:**
- Condition: concurrent user sessions search and render simultaneously. Expected behavior: no shared mutable highlight state exists. Resolution: matched terms and spans are per-request and per-render ephemeral values; no session-state keys, caches, or shared stores are introduced, so no cross-session races are possible.

**Recovery:**
- Condition: any highlight-path failure. Expected behavior: the record renders unhighlighted and the failure is confined to presentation. Resolution: no persistent state is introduced; a page reload or re-query recomputes everything from source data.
