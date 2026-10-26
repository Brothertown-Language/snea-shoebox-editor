# Spec — Dedicated phonetic (`\ph`) search: multi-valued ordered indexing + separate search mode

> Full spec and plan artifacts: https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1442/
> Remote issue: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1442

## Problem

`\ph` (phonetic/phonemic form) is valid MDF and present in production data, but structurally invisible to search:

1. **Parser:** `parse_mdf` extracts no `ph` value — the record dict in `_process_block_into_record` (`src/mdf/parser.py:46–59`) has no `ph` key; `\ph` lines ride only inside the raw `mdf_data` blob. `\ph` is a valid tag (`src/mdf/tags.json`; `MDFValidator.REQUIRED_HIERARCHY`, `src/mdf/validator.py:21`), so uploads pass the watermark audit.
2. **Index:** `populate_search_entries` indexes only `("va", "se", "cf", "ve")` (`src/services/upload_service.py:1802`) — no `entry_type='ph'` rows exist anywhere.
3. **UI:** the records page's search modes are Headword / Gloss / Lexeme / FTS / Semantic Gloss / Semantic All (`src/frontend/pages/records.py:448–457`) — no phonetic mode. The only reachability today is FTS mode over the whole normalized `mdf_data` blob (`to_tsvector('simple', generate_sort_lx(mdf_data))`, `upload_service.py:1843`): diacritics-insensitive, order-flattened, not confined to phonetic values, and indistinguishable from any other field's token in the blob.

Production evidence: `docs/lessons-learned/2026-07-16-local-postgresql-setup.md:102` documents ~430 records matching `mdf_data ILIKE '%\ph%'`. Seed files contain zero `\ph` markers (verified across `src/seed_data/`), so all real `\ph` mass lives in the production database replica.

## Requirement source

Developer instruction (2026-10-25): "file a spec to setup searching via \ph fields. the \ph fields may appear multiple times in each section in reach record so needs to be treated multi-valued and ordered as found in the record"; clarified in the same session: "phonemic searching should be a separate search" (dedicated mode, not folded into existing modes).

## MDF authority (progressive set)

- `docs/mdf/ai-progressive/markers/ph.md` — frontmatter `hierarchy_level: any`: the source fixes no level, so **every section takes `\ph`**.
- `docs/mdf/ai-progressive/markers/Sections_in_a_Lexical_Entry.md:19–21` — section boundaries `\lx`, `\ps` (`\pn`), `\sn`, `\se`; each takes a full field set except `\lc`/`\hm` (top-of-record only).
- Multiple Fields rule (migrated at `MDFields19a_UTF8.txt:1075–1081`): occurrences unrestricted; multiple occurrences within one section concatenate in print, occurrences across separate sections stay separate — hence multi-valued-at-rest with order-as-found is the correct storage shape for search.
- `markers/se.md:15–18` — a subentry is "all the fields that comprise a typical lexical entry."

## Requirements

- **R-1 (multi-valued, ordered extraction):** `parse_mdf` SHALL extract every `\ph` occurrence in a record into an ordered list (`record["ph"]`), in document line order — all sections included (headword level, `\ps`, `\sn`, `\se`, example-bundle contexts); not first-win, not concatenated.
- **R-2 (per-occurrence indexing):** `populate_search_entries` SHALL index `\ph` values as own `search_entries` rows with `entry_type='ph'` (`term` + `normalized_term` via `LinguisticService.generate_sort_lx`), processed in record order. Exact-duplicate values within one record collapse, per the existing `(record_id, term, entry_type)` unique index (`src/database/migrations.py:1062–1065`) — the same semantics already governing `va`/`se`/`cf`/`ve`; all distinct occurrences are preserved. Empty `\ph` lines (bare tag) never index — the existing empty-value skip rule applies uniformly.
- **R-3 (dedicated mode):** the records page SHALL offer a **Phonetic** search mode matching `entry_type='ph'` values only — ILIKE on `normalized_term`, the same contract as sibling ILIKE modes (Lexeme/Headword/Gloss), including `matched_terms` collection so highlight parity with sibling modes holds. Mode label "Phonetic"; the field's own MDF name is "phonetic/phonemic form" (`markers/ph.md`), so the label is faithful to the developer's "phonemic searching" wording.
- **R-4 (existing-record coverage):** existing records' `\ph` values SHALL be indexed via the established populate/backfill path (a migration following the backfill-search-entries pattern), so the mode works on already-ingested records without re-upload.
- **R-5 (existing modes untouched):** existing modes' behavior SHALL be unchanged — the mode selector gains exactly one entry; FTS blob handling, headword/gloss tables and the `chk_headword_entry_type` CHECK constraint (`entry_type IN ('lx','va')`, `migrations.py:986–988`) are untouched.

## Success criteria

| ID | Criterion | Class | Instrument |
|---|---|---|---|
| SC-1 | A multi-`\ph` record (headword-level occurrence, one inside a `\sn` section, one after a `\se` boundary) parses to `record["ph"]` listing every occurrence in exact line order | behavioral | pytest on real-data fixtures; exact list equality in line order |
| SC-2 | Record shape keeps all existing keys' behavior; `record["ph"]` is `[]` when the record contains no `\ph` | structural | existing parser suites pass unchanged (`tests/mdf/test_parser.py`, `test_parser_phase_a.py`); new key asserted both present-default and extracted |
| SC-3 | After `populate_search_entries`, each distinct `\ph` value is its own `search_entries` row with `entry_type='ph'`; row insert order (by id) preserves first-occurrence order | behavioral | pytest seeding a real multi-`\ph` record through the real populate path; rows enumerated by id compared to parser list order |
| SC-4 | Phonetic mode retrieves records by `\ph` value via normalized substring matching (sibling-mode contract) and collects `matched_terms` | behavioral | pytest via `LinguisticService.search_records` with the new mode |
| SC-5 | The records page exposes the Phonetic mode and it returns results end-to-end | behavioral | Playwright real-browser E2E per `docs/development/ui_testing_standard.md` (`SNEA_E2E=1` gate; a skip is never treated as pass) + AppTest in-process smoke as auxiliary only |
| SC-6 | Existing search behavior is unchanged; records without `\ph` gain zero `'ph'` rows | behavioral | existing search suites green (`test/test_upload_search_entries.py`, `test/test_search_records_matched_terms_sc7_red.py`, `test/ui/test_records_lexeme_regression.py`) + zero-`'ph'`-row assertion for no-`\ph` fixtures |
| SC-7 | Indexed `\ph` terms carry `generate_sort_lx` normalization | structural | pytest: stored `normalized_term` == `LinguisticService.generate_sort_lx(term)` |

## Constraints (repo mandates)

- **Data integrity (AGENTS.md):** no synthetic linguistic data. Fixture `\ph` material comes from the MDF documentation's own example (`markers/ph.md` prints `\ph apa`) and from values sampled on the synced production replica. Seed files contain no `\ph`, so doc/prod sourcing is required.
- **Regression protocol (AGENTS.md):** `bash scripts/sync_prod_to_local.sh` from the feature branch before every regression test cycle.
- **Normalization lessons (AGENTS.md-mandated consultation):** `to_tsvector('simple', …)` only — never `'english'` (`2026-06-13-postgres-fts-algonquian.md`, `2026-06-13-simple-vs-english-tsconfig.md`); `∞`→`oozzz` mapping must survive (`2026-06-13-infinity-symbol-normalization.md`); no ASCII-collapsing regex on Algonquian text (`2026-06-13-regex-linguistic-characters.md`). The ILIKE design inherits `generate_sort_lx`'s diacritics-stripping semantics — matching is on base-letter normalized forms, consistent with every sibling mode.

## Approach

1. `_process_block_into_record`: add `record["ph"] = []` to the dict shape and an ungated `_extract_tag(line, "ph")` append in line order (analog of the `va`/`se` list handling; no `in_headword` gating — the developer's requirement carries no primary/secondary distinction for `\ph`).
2. `populate_search_entries`: extend the field tuple at line 1802 to `("va", "se", "cf", "ve", "ph")`.
3. `src/services/linguistic_service.py`: add `"Phonetic"` to the `SearchMode` literal, the strategy map, and the dispatch — join `Record.search_entries` filtered on `entry_type='ph'`, ILIKE on `normalized_term`; `matched_terms` collection flows through the existing ILIKE-mode path.
4. `src/frontend/pages/records.py`: add `Phonetic` to the mode radio (caption referencing `\ph` values), dispatch to the new mode; highlight path reuses the `matched_terms` spans unchanged.
5. `src/database/migrations.py`: backfill migration reusing `populate_search_entries` (established backfill-search-entries pattern) so production rows gain `ph` entries.

Alternatives weighed: single-value `records` column like `ps`/`ge` (violates the multi-valued requirement); `headword_search_entries` type (the developer wants a separate search, and that table's CHECK constraint is `'lx'/'va'`-limited by design); FTS-only (already implicit in the blob — not `\ph`-specific, no mode, no order); new table (the `search_entries` free-form `entry_type` extension point already exists — no schema change needed).

## Out of scope

- Section-attribution metadata for `\ph` values (which sense/subentry a value belongs to).
- Folding `\ph` values into the Lexeme / Headword / Gloss / FTS modes.
- REST search endpoint (the API's records route is a full dump today; no search endpoint exists).
- FTS blob handling changes; positional storage of duplicate identical values.
- The MDF-reference-doc search surfaces (`src/services/mdf_search.py`, `mdf_search_vocabulary.py` — BM25 over the documentation corpus, unrelated; naming hazard recorded for implementers).

## Impact

- **Code touched:** `src/mdf/parser.py`, `src/services/upload_service.py`, `src/services/linguistic_service.py`, `src/frontend/pages/records.py`, `src/database/migrations.py` (backfill), plus tests.
- **Consumers:** records-page search users; all `populate_search_entries` call sites (apply/commit/homonym/reprocess/rollback paths gain `ph` rows automatically — no call-site signature changes; the signature-stability test `test/test_upload_search_entries.py:271–290` continues to hold).
- **Risk:** production `\ph` volume (~430 matches) makes the backfill a one-time populate pass over existing rows; the ILIKE `%…%` substring scan behavior of sibling modes is inherited (no new index path introduced; behavior parity is the point).
- **Edge cases pinned:** empty `\ph` lines never index; exact-duplicate `\ph` values collapse to one row (parser list stays faithful — all occurrences, in order); local replicas synced from production carry rows built by the old code, so the backfill must run on the replica before tests are valid (schema_version machinery governs).

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)