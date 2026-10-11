# Plan: #1417 Full-text search for the in-app MDF Reference

Spec of record: `.issues/1417/spec.md` (remote issue body; validated fresh-context PASS 2026-10-11 — independent re-implementation confirmed all 17 candidate-table rows and every corpus fact). Scope: #1417 only (W1+W2 seeds+W3); #1429's extension work is explicitly out of this scope.

Branch: `feature/1417-mdf-full-text-search`, base tip `106c953`.

## Item 1 (W1, spec's W1 instrument): BM25 scoring engine

- Deliverable: pure module `src/services/mdf_search.py` — in-process Okapi BM25 (k1=1.5, b=0.75), non-negative Lucene IDF `ln(1 + (N − df + 0.5)/(df + 0.5))`, heading/key field TF ×3, marker-code key boost +10 (accumulating across matching entries), score ties broken by topic index. Token rule: `[^\W_]+` lowercased. Index built at page load, cached. No new dependencies, no DB, no CDN.
- RED: `test/test_mdf_search_w1.py` — the W1 candidate rows (`cf`, `ps`, `ge`, `pl`, `lx` → that topic #1; `plural`→`pl` #1; `part of speech`→`ps` #1 `pn` #2; `borrowed word`→`bw` #1; `cross reference`→{ce,cn,cr,cf} top 4; `reversal`→{rr,rn,re} top 3; `reduplication`→`rd` #1; `irregular`→{pdl,pd} top 2) fail against current tree (no scorer exists); plus the character-survival census assertions (á ×26, ñ ×3, é ×1 tokens preserved; • excluded as punctuation).
- GREEN: implement the scorer over the committed `master.json`.
- verify: executed pytest of the W1 module (17 → W1 rows green; ordering deterministic across repeated calls).

## Item 2 (W2, spec's W2 instrument): seeded vocabulary table

- Deliverable: committed data file beside the scorer (e.g. `src/services/mdf_search_vocabulary.py` or a JSON data file — implementation choice; deterministic data) with seed entries: variants `paradigms`→`paradigm`, `references`→`reference` (index-time posting extension); aliases `inflected`→`lc`, `lemma`→`lx`, `word class`→{`ps`,`pn`} (query-time +10 boost, accumulating). Provenance comments citing Coward & Grimes §5.4.4 and SIL Glossary per the spec.
- RED: W1+W2 candidate rows fail on the bare engine: `paradigms` top-4 all `pd*`; `cross references` top-4 {ce,cn,cr,cf}; `inflected`→`lc` #1; `lemma`→`lx` #1; `word class` top-2 {ps,pn}; plus negative demonstrations (`paradigms` zero bare matches; `cross references` bare run displaces `cr`; `inflected`/`lemma` bare zero matches).
- GREEN: wire the table into the scorer's index/query paths per the two mechanisms.
- verify: executed pytest of the W1+W2 candidate rows and negative demos.

## Item 3 (W3, spec's W3 instrument): page integration

- Deliverable: `src/frontend/pages/mdf_reference.py` — the filter input routes to the scorer; v1 `filter_topics` leaves the filter path; input element and layout unchanged (deep-link chips, match-count caption, empty-state banner, chapter tree on empty query all preserved).
- RED: structural test — the filter input's call path invokes the scorer module and `filter_topics` is not on the filter path (fails on current tree); behavioral in-process candidate-table execution through the page's search entry point fails.
- GREEN: integration.
- verify: executed structural + behavioral in-process tests; existing `test/test_mdf_reference_smoke.py` passes unchanged (regression).

## Item 4 (spec's Verification gate): full suite green

- Deliverable: green test run evidence.
- RED/GREEN: N/A (gate item) — full `uv run pytest -q --ignore=tmp` executed this session, 0 failed; designed skips permitted.
- verify: captured summary line.
- commit: any residual fixes surfaced.

## Dependency order
1 → 2 (W2 demonstrations execute through W1) → 3 → 4. One commit per issue ticket at PR squash time (single ticket: #1417).

## Notes
- The spec's candidate table (all 17 rows) is committed with the tests verbatim as assertions.
- E2E Playwright suite is not part of the spec's instruments (W3 instrument is structural + in-process behavioral); the existing `test/ui/test_mdf_reference_e2e.py` SC-9 suite is a regression gate where run live, but its skip-without-env design keeps the suite green without a live app.
