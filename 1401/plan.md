---
plan_schema_version: 1
issue: 1401
title: "Search-match highlighting in Records view"
authorization_scope: for_pr
pr_strategy: stacked
phase_count: 4
dispatch:
  - "Phase 1: test-driven-development — red/green/post-regression/verify task cards + commit-inline direct"
  - "Phase 2: test-driven-development — red/green/post-regression/verify task cards + commit-inline direct"
  - "Phase 3: test-driven-development — red/green/post-regression/verify task cards + commit-inline direct"
  - "Phase 4: test-driven-development — red/green/post-regression/verify task cards (E2E gating per test/ui/AGENTS.md) + commit-inline direct"
---

# Implementation Plan — #1401 — Search-Match Highlighting in Records View

**Issue:** .issues/1401/spec.md

**Goal:** Visually highlight matched search terms inside the rendered MDF block in Records View mode for the lexical search modes (Lexeme, Headword, Gloss, FTS) via a three-layer additive design: pure span-computation helpers, an additive service `matched_terms` field, and default-off renderer highlight parameters threaded only into the View-mode render call.

**Architecture:** A new pure span-computation module (`src/frontend/search_highlight.py`) produces per-line offsets from stored raw terms (verbatim find) and from FTS-normalized query tokens (reusing the service normalizer as the single normalization entry point). The service search layer collects matched raw terms per record during the existing paginated query and returns them in an additive optional `matched_terms` field (None for FTS and Semantic modes). The MDF block renderer accepts default-off highlight span parameters and wraps matches in `mark.search-token` elements with ignore-not-clamp malformed-span handling and diff-token precedence. The Records page threads query, mode, and computed spans into the View-mode render call only. Key design decisions pinned by the spec: whole-term granularity, single-normalizer reuse (`generate_sort_lx`), additive-optional field, ignore-not-clamp for malformed spans, WCAG 2.1 AA 4.5:1 contrast threshold, diff-token precedence, no session-state keys, no caching layer, no database schema change.

**Files:**
- `src/frontend/search_highlight.py` (new — pure span helpers)
- `src/services/linguistic_service.py` (additive field + collection)
- `src/frontend/ui_utils.py` (renderer highlight parameters + CSS)
- `src/frontend/pages/records.py` (mirror container field + View-mode threading)
- `test/` (pytest unit and integration tests)
- `test/ui/` (gated Playwright E2E suite)

## Blast Radius

- **Directly modified:** `src/frontend/search_highlight.py` (new), `src/services/linguistic_service.py`, `src/frontend/ui_utils.py`, `src/frontend/pages/records.py`
- **Test zones:** `test/` unit and integration suites; `test/ui/` gated Playwright E2E suite
- **Impact zones protected (read-path only):** MDF parsing and database write paths untouched; revision-history and import-diff renderer call sites byte-identical; `fts_entries` table untouched; no new session-state keys; no migrations; no new endpoints

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

> **Enforcement gate:** All SCs must pass before this plan is complete.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Pure span-computation module | Verbatim stored-term find and FTS normalized query-token scan producing per-line offsets | SC-1, SC-2, SC-3, SC-4 | — | 5-24 | task-card (5-24) + direct (commits) |
| 2 | Service data layer | Additive matched-terms field, mirror container field, ILIKE-mode collection, FTS/Semantic None | SC-5, SC-6, SC-7, SC-8 | — | 25-44 | task-card (25-44) + direct (commits) |
| 3 | Renderer, styling, and page wiring | Default-off highlight parameters, markup, precedence, styling, View-mode threading | SC-9 through SC-20 | 1, 2 | 45-104 | task-card (45-104) + direct (commits) |
| 4 | Gated Playwright E2E | Live-app end-to-end verification of highlight flow and absence boundaries | SC-21, SC-22, SC-23 | 3 | 105-119 | task-card (105-119) + direct (commits) |
| 5 | Post-implementation | Audit, structural checks, gates, PR | — | 1-4 | 120-127 | mixed |

## Pre-Implementation

- [ ] 1. **Coherence gate (**direct**).** Confirm spec SC list, structure artifact phase mappings, and phase DAG are mutually consistent; confirm every SC maps to exactly one phase and every phase item maps to exactly one SC.
  - Blocked if any SC is unmapped, duplicated across phases, or mapped to a phase whose dependency edges are violated.
- [ ] 2. **Baseline check (**direct**).** Verify the local database is re-synced from production via `bash scripts/sync_prod_to_local.sh`; verify the feature branch exists per `git-workflow`; verify the test suite baseline is green before any RED.
  - Required documents read before any matching/tokenization or UI test work: `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md`, `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md`, `docs/development/ui_testing_standard.md`.
- [ ] 3. **Pre-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-0 task from test-driven-development")` — run regression test patterns before RED phase.
- [ ] 4. **Pre-regression verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify pre-regression results.

# Phase 1 — Pure Span-Computation Module

**Concern:** Deterministic whole-term span computation, isolated from Streamlit and the database, with normalization parity with the FTS strategy.

**Files:** `src/frontend/search_highlight.py` (new); unit tests under `test/`

**SCs:** SC-1, SC-2, SC-3, SC-4

**Dependencies:** None (independent of Phase 2)

**Entry Conditions:** Pre-implementation steps 1-4 complete; baseline test suite green; Unicode regex and infinity-symbol lessons-learned documents read.

**Exit Conditions:** Pure helpers exist with unit-testable occurrence and no-match contracts; all Phase 1 unit suites pass.

**Code Path Coverage:** New presentation-adjacent module only — no renderer, service, parser, or database write paths touched in this phase.

**Cross-Cutting SCs:** R-2 (whole-term granularity), R-14 (Unicode-aware matching — NFD diacritics, IPA, infinity, fancy quotes; no ASCII-only classes), R-12 (pure, no Streamlit/database imports), R-18 (linear cost bound).

**Interface Boundaries:** Helpers expose per-line `(start, end)` offset lists as their only contract; consumers (Phase 3 renderer) treat them as advisory presentation data. The FTS helper imports the service normalizer (`generate_sort_lx` and the FTS strategy's token cleaning) as the sole normalization entry point — no second normalizer.

**State Transitions:** None — pure functions; no session state, no caching, no persistent state.

**Cost frame:** Running the Phase 1 unit suites costs minutes of execution time — a Unicode or normalization-parity defect is caught at the earliest gate with zero downstream cost. Skipping costs the full rework chain — highlighted spans disagree with indexed matches in production, and each fix cycle re-introduces drift because two normalizers disagree.

### Step-by-Step

- [ ] 5. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest unit test for SC-1: the pure stored-term span helper does not exist yet; samples cover verbatim whole-term find, NFD-decomposed diacritics, IPA characters, infinity symbols, and overlapping/adjacent term occurrences, asserting deterministic left-to-right per-line `(start, end)` emission. **→ SC-1**
  - RED must fail before GREEN begins.
- [ ] 6. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — implement the minimum change: create `src/frontend/search_highlight.py` as a pure module (no Streamlit or database imports) with the deterministic left-to-right whole-term substring find returning per-line offsets for every occurrence of every provided term. **→ SC-1**
- [ ] 7. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-1**
- [ ] 8. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the unit suite and confirm the emitted span set matches the SC-1 contract exactly. **→ SC-1**
- [ ] 9. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(highlight): stored-term span helper with occurrence contract (SC-1)"` — test and implementation in one atomic slice, no co-author trailers.
- [ ] 10. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest unit test for SC-2: the helper does not yet return empty span lists for absent terms, empty term lists, and empty rendered lines. **→ SC-2**
- [ ] 11. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — implement the no-match branches: empty span list whenever no verbatim occurrence exists; no fuzzy or approximate matching. **→ SC-2**
- [ ] 12. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-2**
- [ ] 13. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the unit suite and confirm empty-span behavior for all no-match samples. **→ SC-2**
- [ ] 14. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(highlight): stored-term span helper no-match empty contract (SC-2)"`.
- [ ] 15. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest unit test for SC-3: the pure FTS span helper does not exist yet; samples cover normalization parity with the FTS strategy (tsquery-unsafe stripping, `:*` prefix semantics, multi-token queries), Unicode-safe line tokenization without ASCII-only classes, and infinity-to-normalized-form consistency. **→ SC-3**
- [ ] 16. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — implement the minimum change: the pure FTS span helper reusing the service normalizer as the sole normalization entry point; scan candidate words, normalize each on the fly, and emit whole-word spans for matches. **→ SC-3**
- [ ] 17. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-3**
- [ ] 18. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the unit suite and confirm normalization parity and correct span emission. **→ SC-3**
- [ ] 19. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(highlight): FTS query-token span helper with normalization parity (SC-3)"`.
- [ ] 20. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest unit test for SC-4: the FTS helper does not yet return empty span lists for token-free queries (only tsquery-unsafe characters), empty queries, and no-match lines. **→ SC-4**
- [ ] 21. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — implement the no-match branches: empty span list whenever no query token survives cleaning or no line word matches. **→ SC-4**
- [ ] 22. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-4**
- [ ] 23. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the unit suite and confirm no-op behavior on all no-match samples. **→ SC-4**
- [ ] 24. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(highlight): FTS span helper no-match empty contract (SC-4)"`.

#### Phase 1 Completion Block (VbC)

- [ ] Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify SC-1 through SC-4 unit suites pass with behavioral evidence; confirm the module imports neither Streamlit nor database code.

**Concern transition:** Leaving pure span computation → entering the service data layer. Phase 2 is independent of Phase 1's deliverables; Phase 3 consumes both.
# Phase 2 — Service Data Layer

**Concern:** Additive matched-terms data flow from the service search layer without breaking existing construction sites or the semantic seam contract.

**Files:** `src/services/linguistic_service.py`; integration tests under `test/`

**SCs:** SC-5, SC-6, SC-7, SC-8

**Dependencies:** None (independent of Phase 1)

**Entry Conditions:** Pre-implementation steps 1-4 complete; local PostgreSQL test instance available; tests never run against production data.

**Exit Conditions:** `matched_terms` additive optional field exists on both containers; ILIKE modes collect deduplicated per-record matched terms within the paginated query; FTS and Semantic modes return None; all Phase 2 integration suites pass.

**Code Path Coverage:** Service search result container, page-local mirror container, and the service search method's post-dispatch collection path. Semantic strategies untouched except for the None guarantee; no database schema change, no migration, no new endpoints.

**Cross-Cutting SCs:** R-7 (additive optional field, semantic seam preserved), R-9 (collection after strategy dispatch, one shared ILIKE implementation), R-15 (no schema change), R-18 (join-side aggregation bounded to the paginated window).

**Interface Boundaries:** The result container gains an additive optional field defaulting to None — all existing construction sites remain source-compatible. The page-local mirror gains the same field so semantic seam construction completes without raising.

**State Transitions:** None persistent — matched terms are per-request ephemeral values bounded to the paginated query window; nothing is cached across pages.

**Cost frame:** Running the Phase 2 integration suites costs minutes of execution time — a broken additive field, a fabricated or missing collection map, or a mode leak is caught at the gate. Skipping costs days-to-weeks — a TypeError in an existing construction site or wrong highlights surfacing only when a user opens search, requiring data-integrity investigation.

### Step-by-Step

- [ ] 25. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest integration test for SC-5: the service search result container has no matched-terms field. **→ SC-5**
- [ ] 26. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — add the optional default-None matched-terms field to the service search result container, keeping all existing construction sites source-compatible. **→ SC-5**
- [ ] 27. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-5**
- [ ] 28. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the integration suite and confirm the field defaults to None and existing construction sites still work. **→ SC-5**
- [ ] 29. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(search): additive matched_terms field on service result container (SC-5)"`.
- [ ] 30. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest integration test for SC-6: the page-local mirror container has no matched-terms field. **→ SC-6**
- [ ] 31. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — add the same optional default-None matched-terms field to the page-local mirror container. **→ SC-6**
- [ ] 32. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-6**
- [ ] 33. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the integration suite and confirm semantic seam construction completes without raising. **→ SC-6**
- [ ] 34. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(search): matched_terms field on page-local mirror container (SC-6)"`.
- [ ] 35. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest integration test for SC-7: the service search method does not collect matched raw terms — cover per-mode collection (Lexeme, Headword, Gloss), per-record grouping, and per-record dedup. **→ SC-7**
- [ ] 36. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — implement join-side matched-term aggregation in the service search method within the existing paginated query, grouped and deduplicated per record identifier, collected after strategy dispatch. **→ SC-7**
- [ ] 37. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-7**
- [ ] 38. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the integration suite and confirm the collected map matches the SC-7 contract (per-mode collection, dedup, bounded to the paginated window). **→ SC-7**
- [ ] 39. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(search): matched-term collection for ILIKE modes (SC-7)"`.
- [ ] 40. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing pytest integration test for SC-8: FTS and Semantic strategies do not leave the matched-terms field as None. **→ SC-8**
- [ ] 41. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — ensure FTS and Semantic mode searches return the matched-terms field as None. **→ SC-8**
- [ ] 42. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-8**
- [ ] 43. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the integration suite and confirm None for both strategies. **→ SC-8**
- [ ] 44. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(search): matched_terms stays None for FTS and Semantic modes (SC-8)"`.

#### Phase 2 Completion Block (VbC)

- [ ] Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify SC-5 through SC-8 integration suites pass; confirm the semantic seam construction is intact and no schema change was introduced.

**Concern transition:** Leaving the service data layer → entering renderer, styling, and page wiring. Phase 3 depends on Phase 1's span contract (SC-1, SC-3) and Phase 2's matched-terms data (SC-7).
# Phase 3 — Renderer, Styling, and Page Wiring

**Concern:** Additive default-off highlight rendering in the MDF block renderer with diagnostics-preserving precedence, measured styling, and View-mode-only wiring on the Records page.

**Files:** `src/frontend/ui_utils.py` (renderer + CSS block); `src/frontend/pages/records.py` (View-mode threading); pytest/AppTest smoke tests and Playwright DOM/style assertions under `test/` and `test/ui/`

**SCs:** SC-9, SC-10, SC-11, SC-12, SC-13, SC-14, SC-15, SC-16, SC-17, SC-18, SC-19, SC-20

**Dependencies:** Phase 1 (span contract SC-1, SC-3), Phase 2 (matched-terms data SC-7)

**Entry Conditions:** Phases 1 and 2 complete with their VbC blocks passed; UI testing standard read; Playwright real-browser environment available; AppTest used for smoke only.

**Exit Conditions:** Renderer renders byte-identically without highlight parameters, wraps supplied spans in `mark.search-token` with escaping preserved, ignores malformed spans, honors diff-token precedence, and the styling meets the measured criteria; Records page threads highlight context into the View-mode render call only with auto-activation and both no-highlight boundaries; all Phase 3 suites pass with archived screenshots where required.

**Code Path Coverage:** MDF block renderer signature and markup path; renderer CSS block; Records page View-mode render call and mirror construction. Revision-history and import-diff call sites stay untouched via default-off parameters; MDF parsing untouched.

**Cross-Cutting SCs:** R-8 (default-off parameters), R-16 (diff-token precedence + status tint non-interference), R-17 (4.5:1 contrast in both themes), R-13 (teal/cyan tint + bold, computed-distinct), R-20 (ignore-not-clamp), R-19 (Playwright real-browser standard, AppTest smoke-only), R-10 (no new session-state keys, no preference toggle).

**Interface Boundaries:** Renderer highlight parameters are optional with defaults that preserve current output byte-for-byte. Page wiring supplies query, mode, and computed spans only to the View-mode render call — revision-history and diff renders receive no highlight parameters.

**State Transitions:** Highlight context derives from session search state and the search result per render; user switching lexical/semantic modes and clearing the search box activate/deactivate highlighting per the spec's edge-case table; no new session-state keys introduced.

**Cost frame:** Running the Phase 3 smoke and Playwright suites costs minutes of execution time — markup, escaping, precedence, and styling defects are caught before UI review with archived screenshots as evidence. Skipping costs days-to-weeks — corrupted markup, crashes on malformed spans, or theme-variant contrast defects surface as user complaints that are expensive to reproduce.

### Step-by-Step

- [ ] 45. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing output-comparison smoke test for SC-9: the renderer has no highlight parameters and any parameterless change would alter output; establish the byte-identity baseline for revision-history and import-diff call sites. **→ SC-9**
- [ ] 46. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — add optional default-off highlight span parameters to the MDF block renderer; call sites that do not supply them render byte-identically. **→ SC-9**
- [ ] 47. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-9**
- [ ] 48. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the smoke tests and output comparison; confirm byte-identity at all untouched call sites. **→ SC-9**
- [ ] 49. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): default-off highlight parameters on MDF block renderer (SC-9)"`.
- [ ] 50. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write failing markup smoke test plus Playwright DOM assertion for SC-10: the renderer emits no `mark.search-token` elements. **→ SC-10**
- [ ] 51. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — wrap each supplied span's covered text range in `mark.search-token` elements with output escaping preserved. **→ SC-10**
- [ ] 52. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-10**
- [ ] 53. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the smoke tests and Playwright DOM assertions; confirm escaping on matched text containing markup-sensitive characters. **→ SC-10**
- [ ] 54. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): search-token markup wrapping with escaping preserved (SC-10)"`.
- [ ] 55. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing smoke test for SC-11: the renderer raises or misrenders on malformed or out-of-range spans (negative offsets, start greater than or equal to end, end beyond line length). **→ SC-11**
- [ ] 56. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — drop malformed and out-of-range highlight spans without raising; all other content renders unaffected; no clamping. **→ SC-11**
- [ ] 57. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-11**
- [ ] 58. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the smoke tests; confirm no exception and no mark for dropped spans. **→ SC-11**
- [ ] 59. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): ignore-not-clamp malformed span handling (SC-11)"`.
- [ ] 60. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write failing smoke test plus Playwright DOM assertion for SC-12: the diff-token overlap precedence rule is not implemented. **→ SC-12**
- [ ] 61. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — implement the precedence rule: where a highlight span overlaps a diff-token span, the diff-token span renders unchanged and the overlapping search-token mark is omitted. **→ SC-12**
- [ ] 62. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-12**
- [ ] 63. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the smoke tests and DOM assertions with overlapping span samples. **→ SC-12**
- [ ] 64. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): diff-token precedence over search-token marks (SC-12)"`.
- [ ] 65. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright DOM and computed-style assertion for SC-13: search highlighting alters status line tints. **→ SC-13**
- [ ] 66. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — ensure status line tints render unchanged when search-token highlighting is active. **→ SC-13**
- [ ] 67. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-13**
- [ ] 68. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the Playwright assertions comparing status tint output with and without active highlighting. **→ SC-13**
- [ ] 69. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): status line tint non-interference with highlighting (SC-13)"`.
- [ ] 70. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright computed-style assertion for SC-14: no `mark.search-token` styles exist. **→ SC-14**
- [ ] 71. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — add the CSS block alongside the existing mark styles: teal/cyan background tint plus bold font weight. **→ SC-14**
- [ ] 72. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-14**
- [ ] 73. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the Playwright computed-style assertions. **→ SC-14**
- [ ] 74. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): search-token teal/cyan bold styling (SC-14)"`.
- [ ] 75. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright computed-style assertion for SC-15: the search-token color is not computed-distinct from diff-token marks and status tints. **→ SC-15**
- [ ] 76. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — define theme-variant styles such that the computed background-color of search-token marks differs from the computed background-colors of diff-token marks and status line tints in both themes. **→ SC-15**
- [ ] 77. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-15**
- [ ] 78. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the Playwright computed-style comparisons in both themes; archive screenshots. **→ SC-15**
- [ ] 79. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): theme-variant distinctness of search-token styling (SC-15)"`.
- [ ] 80. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright contrast-ratio assertion for SC-16: the search-token styling does not meet the 4.5:1 threshold. **→ SC-16**
- [ ] 81. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — adjust the theme-variant styles so the contrast ratio between the mark's text color and the underlying block background is at least 4.5:1 (WCAG 2.1 AA normal-text) in both themes. **→ SC-16**
- [ ] 82. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-16**
- [ ] 83. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the Playwright contrast-ratio computation in both themes; archive screenshots. **→ SC-16**
- [ ] 84. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(render): WCAG 2.1 AA contrast threshold for search-token marks (SC-16)"`.
- [ ] 85. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright behavioral test for SC-17: the View-mode render call does not thread highlight context, or other call sites receive it. **→ SC-17**
- [ ] 86. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — supply query, mode, and computed spans to the View-mode render call only. **→ SC-17**
- [ ] 87. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-17**
- [ ] 88. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run Playwright behavioral assertions; confirm revision-history and diff renders receive no highlight parameters. **→ SC-17**
- [ ] 89. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(page): View-mode-only highlight threading on Records page (SC-17)"`.
- [ ] 90. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright behavioral test for SC-18: highlighting does not activate from a lexical-mode query alone in a fresh session. **→ SC-18**
- [ ] 91. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — activate highlighting automatically when a lexical-mode query is present, with no preference toggle or prior configuration and no new session-state keys. **→ SC-18**
- [ ] 92. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-18**
- [ ] 93. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run Playwright behavioral assertions across Lexeme, Headword, Gloss, and FTS modes from a fresh session state. **→ SC-18**
- [ ] 94. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(page): auto-activation of highlighting for lexical modes (SC-18)"`.
- [ ] 95. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright behavioral test for SC-19: an empty query still produces search-token marks. **→ SC-19**
- [ ] 96. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — ensure the empty-query boundary produces no search-token marks in the rendered block. **→ SC-19**
- [ ] 97. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-19**
- [ ] 98. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run Playwright behavioral assertions on empty-query searches with DOM assertions. **→ SC-19**
- [ ] 99. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(page): empty-query no-highlight boundary (SC-19)"`.
- [ ] 100. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development")` — write a failing Playwright behavioral test for SC-20: Semantic Gloss or Semantic All renders contain search-token marks. **→ SC-20**
- [ ] 101. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development")` — ensure Semantic Gloss and Semantic All modes never receive highlight parameters, so no search-token marks appear even with an active query. **→ SC-20**
- [ ] 102. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-20**
- [ ] 103. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run Playwright behavioral assertions across both semantic modes. **→ SC-20**
- [ ] 104. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "feat(page): semantic-mode no-highlight boundary (SC-20)"`.

#### Phase 3 Completion Block (VbC)

- [ ] Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify SC-9 through SC-20 suites pass with behavioral evidence; confirm archived screenshots exist for SC-15 and SC-16 in both themes.

**Concern transition:** Leaving renderer, styling, and page wiring → entering gated end-to-end verification. Phase 4 depends on Phase 3's fully wired highlight behavior.
# Phase 4 — Gated Playwright E2E on Live Local App

**Concern:** End-to-end verification of the highlight flow and its absence boundaries on the live local app, gated by `SNEA_E2E=1` plus live app on port 8501.

**Files:** `test/ui/` (gated Playwright E2E suite); screenshots archived under the issue's artifact directory

**SCs:** SC-21, SC-22, SC-23

**Dependencies:** Phase 3

**Entry Conditions:** Phase 3 complete with its VbC block passed; `docs/development/ui_testing_standard.md` read; live local app runnable on port 8501; local test database synced.

**Exit Conditions:** Gated E2E suite exists and, when the gate is enabled, verifies the lexical-mode highlight flow (SC-21), semantic-mode absence (SC-22), and empty-query absence (SC-23) with screenshots archived; any gate-skipped run is recorded as skipped by design and never silently treated as a pass.

**Code Path Coverage:** Full user path from search submission through rendered MDF block on the live app; no new production code paths — this phase verifies Phases 1-3 deliverables as users experience them.

**Cross-Cutting SCs:** R-19 (Playwright real-browser standard of record; E2E gating; gate-skipping is by design, never a pass), R-3 (lexical-modes-only coverage exercised end to end).

**Interface Boundaries:** Tests interact only through the app's user-visible surface (search box, mode selector, rendered block DOM); no direct database or service-layer assertions.

**State Transitions:** Fresh session state for SC-21 (auto-activation without prior configuration); query cleared for SC-23; mode switched to Semantic Gloss and Semantic All for SC-22 — each transition is exercised exactly as the spec's edge-case table defines.

**Cost frame:** Running the gated E2E when enabled costs minutes of execution time — the full search-to-highlight flow is verified as users experience it. Skipping the gate is legitimate; silently treating a gate-skip as a pass costs the entire verification chain its meaning — every upstream behavioral claim degrades to structural theater with discovery latency measured in production incidents.

### Step-by-Step

- [ ] 105. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development (E2E gating per test/ui/AGENTS.md)")` — write the gated E2E test for SC-21 that fails pre-wiring when enabled (`SNEA_E2E=1` with live app on port 8501); when the gate is absent, the test records skipped-by-design. **→ SC-21**
- [ ] 106. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development (E2E gating per test/ui/AGENTS.md)")` — complete the end-to-end flow so a search in each lexical mode highlights matches in the rendered block. **→ SC-21**
- [ ] 107. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-21**
- [ ] 108. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the gated suite; record a gate-skipped run as skipped by design, never as a pass; archive screenshots under the issue's artifact directory when executed. **→ SC-21**
- [ ] 109. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "test(e2e): gated lexical-mode highlight flow verification (SC-21)"`.
- [ ] 110. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development (E2E gating per test/ui/AGENTS.md)")` — write the gated E2E assertion for SC-22 that fails because Semantic modes show highlighting when enabled. **→ SC-22**
- [ ] 111. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development (E2E gating per test/ui/AGENTS.md)")` — verify end-to-end on the live local app that Semantic Gloss and Semantic All modes show no search-token marks. **→ SC-22**
- [ ] 112. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-22**
- [ ] 113. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the gated suite; record a gate-skipped run as skipped by design; archive screenshots when executed. **→ SC-22**
- [ ] 114. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "test(e2e): gated semantic-mode absence verification (SC-22)"`.
- [ ] 115. **RED (**task-card**).** Dispatch `task(..., prompt: "execute red task from test-driven-development (E2E gating per test/ui/AGENTS.md)")` — write the gated E2E assertion for SC-23 that fails because an empty query shows highlighting when enabled. **→ SC-23**
- [ ] 116. **GREEN (**task-card**).** Dispatch `task(..., prompt: "execute green task from test-driven-development (E2E gating per test/ui/AGENTS.md)")` — verify end-to-end on the live local app that an empty query shows no search-token marks. **→ SC-23**
- [ ] 117. **Post-regression (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — run regression test patterns after GREEN. **→ SC-23**
- [ ] 118. **Verify (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — run the gated suite; record a gate-skipped run as skipped by design; archive screenshots when executed. **→ SC-23**
- [ ] 119. **Commit (**direct**).** Orchestrator runs `git add <files> && git commit -m "test(e2e): gated empty-query absence verification (SC-23)"`.

#### Phase 4 Completion Block (VbC)

- [ ] Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — verify SC-21 through SC-23 outcomes are recorded with the gate semantics honored: executed-with-screenshots or skipped-by-design, never a silent pass.

**Concern transition:** Leaving gated E2E verification → entering post-implementation gates and PR preparation.
# Post-Implementation

- [ ] 120. **Audit (**task-card**).** Dispatch `task(..., prompt: "execute verification-audit DiMo investigator from audit. Read \`audit/tasks/verification-audit-investigator.md\` first")` — adversarial audit of the deliverable, followed by the validator, evaluator, and arbiter in sequence.
- [ ] 121. **Z3 check (**direct**).** Orchestrator runs `.opencode/tools/solve check --state-path ... --contract-path ...` directly — no sub-agent dispatch.
- [ ] 122. **Structural checks (**task-card**).** Dispatch `task(..., prompt: "execute checklist task from finishing-a-development-branch")` — run the finishing checklist (lint, typecheck, and related checks).
- [ ] 123. **Pre-PR gate (**task-card**).** Dispatch `task(..., prompt: "execute verify task from verification-before-completion")` — read all SC verdicts; BLOCK if any FAIL (DONE_WITH_CONCERNS and EVIDENCE_TYPE_MISMATCH are coerced to FAIL).
- [ ] 124. **Regression check (**task-card**).** Dispatch `task(..., prompt: "execute phase-4 task from test-driven-development")` — final regression check before PR.
- [ ] 125. **Review-prep (**task-card**).** Dispatch `task(..., prompt: "execute review-prep from git-workflow-pr. Read \`git-workflow-pr/tasks/review-prep.md\` first")` — prepare PR review context.
- [ ] 126. **Create PR (**task-card**).** Dispatch `task(..., prompt: "execute create task from git-workflow-pr")` — create the stacked pull request targeting the trunk. PR body must not include auto-closing keywords for stakeholder-facing issues.
- [ ] 127. **Executive summary (**task-card**).** Dispatch `task(..., prompt: "execute completion task from completion-core")` — generate the completion executive summary; report once and halt.

## Exit Criteria

- [ ] C1. All 23 SCs verified PASS with behavioral evidence matching their declared evidence type
- [ ] C2. Every item committed as one atomic RED/GREEN slice with its test
- [ ] C3. Revision-history and import-diff renderer call sites render byte-identically (SC-9, SC-17)
- [ ] C4. FTS and Semantic modes return `matched_terms` as None and render no search-token marks (SC-8, SC-20, SC-22)
- [ ] C5. Empty query produces no search-token marks (SC-19, SC-23)
- [ ] C6. Search-token styling meets 4.5:1 WCAG 2.1 AA contrast in both themes and is computed-distinct from diff-token marks and status tints (SC-15, SC-16)
- [ ] C7. Gated E2E suite executed when `SNEA_E2E=1` and live app on port 8501 are present; any gate-skip recorded as skipped by design, never as a pass (SC-21 through SC-23)
- [ ] C8. Audit, structural checks, pre-PR gate, and final regression check all pass before PR creation
