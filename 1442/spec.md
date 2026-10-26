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
- **R-4 (existing-record coverage, manual backfill):** schema layer and backfill layer are two distinct concerns. Any schema updates this feature requires SHALL ride the automatic migration machinery (`MigrationManager`, `src/database/migrations.py`) as normal; the **backfill operation** — indexing already-ingested records' `\ph` values — SHALL be admin-triggered, working the same as the app's other backfill buttons, and SHALL NEVER run automatically (not on app start, not on schema version). The established Table Maintenance → Data Reprocessing button "Start Full Reprocessing" (`src/frontend/pages/table_maintenance.py:181` → `UploadService.reprocess_all_records`, which re-parses every record and calls `populate_search_entries` per record at `upload_service.py:1902`) is the backfill mechanism: once the populate tuple includes `ph` (R-2), that manual button run indexes every existing record's `\ph` values without re-upload. No schema change is required for `entry_type='ph'` (`search_entries.entry_type` is free-form — the `entry_type` CHECK lives only on `headword_search_entries`); the Data Reprocessing info text's index enumeration SHALL gain `ph` alongside its existing `lx, va, se, cf, ve` list so the button's description stays accurate.
- **R-5 (existing modes untouched):** existing modes' behavior SHALL be unchanged — the mode selector gains exactly one entry; FTS blob handling, headword/gloss tables and the `chk_headword_entry_type` CHECK constraint (`entry_type IN ('lx','va')`, `migrations.py:986–988`) are untouched.
- **R-6 (Lexeme exclusion):** because Lexeme mode joins `Record.search_entries` with no `entry_type` filter today (`src/services/linguistic_service.py:38`, matched-terms collection `:537–548`), introducing `'ph'` rows WOULD silently change Lexeme results and highlights — contradicting R-5 and the developer's separate-search requirement. The Lexeme strategy's `search_entries` join and its `matched_terms` collection SHALL therefore explicitly exclude `entry_type='ph'`, keeping Lexeme's searchable set exactly `('lx', 'va', 'se', 'cf', 've')` — byte-identical behavior for all pre-existing data.

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
| SC-8 | The manual backfill works: invoking the reindex the button runs (`UploadService.reprocess_all_records`) over already-ingested records whose `mdf_data` contains `\ph` gains each record's `entry_type='ph'` rows (distinct values, record order — first-occurrence order preserved) with no re-upload, and Phonetic mode retrieves the record afterward | behavioral | pytest calling `reprocess_all_records` (the service behind the "Start Full Reprocessing" button) on an ephemeral real-PG instance seeded to the pre-`\ph`-state, then asserting backfilled rows + Phonetic-mode retrieval; the regression-protocol prod-replica cycle exercises the button path over the real `\ph` mass (~430 records) |
| SC-9 | Lexeme mode is unchanged over ph-bearing records: a record whose `\ph` value matches the query while its `\lx`/`\va`/`\se`/`\cf`/`\ve` values do not is NOT retrieved by Lexeme mode, and Lexeme `matched_terms` never cites a `'ph'` term | behavioral | pytest via `LinguisticService.search_records` (Lexeme mode) on a ph-bearing real-data fixture, asserting exclusion — the negative-space case existing suites cannot observe (their fixtures carry no `\ph`) |
| SC-10 | The backfill layer is manual-only and the schema layer stays automatic: nothing auto-runs the `\ph` backfill on app start or schema version (schema work, if ever needed, rides the normal automatic migrations; the current state requires none for `entry_type='ph'`), and the Data Reprocessing info text enumerates `ph` in its index rebuild list | structural | inspect the migrations registry for automatic backfill-of-`ph` entries (none); grep `'ph'`-row population call sites (only `populate_search_entries` and its button-invoked/test callers); read the button's `st.info` copy for the `ph` enumeration |

## Constraints (repo mandates)

- **Data integrity (AGENTS.md):** no synthetic linguistic data. Fixture `\ph` material comes from the MDF documentation's own example (`markers/ph.md` prints `\ph apa`) and from values sampled on the synced production replica. Seed files contain no `\ph`, so doc/prod sourcing is required.
- **Regression protocol (AGENTS.md):** `bash scripts/sync_prod_to_local.sh` from the feature branch before every regression test cycle.
- **Normalization lessons (AGENTS.md-mandated consultation):** `to_tsvector('simple', …)` only — never `'english'` (`2026-06-13-postgres-fts-algonquian.md`, `2026-06-13-simple-vs-english-tsconfig.md`); `∞`→`oozzz` mapping must survive (`2026-06-13-infinity-symbol-normalization.md`); no ASCII-collapsing regex on Algonquian text (`2026-06-13-regex-linguistic-characters.md`). The ILIKE design inherits `generate_sort_lx`'s diacritics-stripping semantics — matching is on base-letter normalized forms, consistent with every sibling mode.

## Approach

1. `_process_block_into_record`: add `record["ph"] = []` to the dict shape and an ungated `_extract_tag(line, "ph")` append in line order (analog of the `va`/`se` list handling; no `in_headword` gating — the developer's requirement carries no primary/secondary distinction for `\ph`).
2. `populate_search_entries`: extend the field tuple at line 1802 to `("va", "se", "cf", "ve", "ph")`.
3. `src/services/linguistic_service.py`: add `"Phonetic"` to the `SearchMode` literal, the strategy map, and the dispatch — join `Record.search_entries` filtered on `entry_type='ph'`, ILIKE on `normalized_term`; `matched_terms` collection flows through the existing ILIKE-mode path. Add the preserving filter to the Lexeme strategy join and its matched-terms collection — explicit `entry_type IN ('lx','va','se','cf','ve')` — so Lexeme behavior is byte-identical once `'ph'` rows exist (R-6; required because today's Lexeme join is unfiltered).
4. `src/frontend/pages/records.py`: add `Phonetic` to the mode radio (caption referencing `\ph` values), dispatch to the new mode; highlight path reuses the `matched_terms` spans unchanged.
5. No new migration — the `\ph` backfill for existing records rides the app's existing admin Data Reprocessing button ("Start Full Reprocessing" → `UploadService.reprocess_all_records`, which re-parses every record and re-runs `populate_search_entries` per record, `upload_service.py:1902`), per the developer's manual-button requirement; the button's info copy gains `ph` in its search-index enumeration. Schema updates, if ever required, ride the normal automatic migration machinery; the current state requires none for `entry_type='ph'`.

Alternatives weighed: single-value `records` column like `ps`/`ge` (violates the multi-valued requirement); `headword_search_entries` type (the developer wants a separate search, and that table's CHECK constraint is `'lx'/'va'`-limited by design); FTS-only (already implicit in the blob — not `\ph`-specific, no mode, no order); new table (the `search_entries` free-form `entry_type` extension point already exists — no schema change needed).

## Out of scope

- Section-attribution metadata for `\ph` values (which sense/subentry a value belongs to).
- Folding `\ph` values into the Lexeme / Headword / Gloss / FTS modes.
- REST search endpoint (the API's records route is a full dump today; no search endpoint exists).
- FTS blob handling changes; positional storage of duplicate identical values.
- The MDF-reference-doc search surfaces (`src/services/mdf_search.py`, `mdf_search_vocabulary.py` — BM25 over the documentation corpus, unrelated; naming hazard recorded for implementers).

## Impact

- **Code touched:** `src/mdf/parser.py`, `src/services/upload_service.py`, `src/services/linguistic_service.py`, `src/frontend/pages/records.py`, `src/frontend/pages/table_maintenance.py` (Data Reprocessing info copy), plus tests.
- **Consumers:** records-page search users; Table Maintenance admins (the "Start Full Reprocessing" button becomes the one-time `\ph` backfill); all `populate_search_entries` call sites (apply/commit/homonym/reprocess/rollback paths gain `ph` rows automatically — no call-site signature changes; the signature-stability test `test/test_upload_search_entries.py:271–290` continues to hold).
- **Risk:** production `\ph` volume (~430 matches) is backfilled by the existing manual Full Reprocessing button run — the same per-record parse + populate cadence admins already use to rebuild the search index; the ILIKE `%…%` substring scan behavior of sibling modes is inherited (no new index path introduced; behavior parity is the point).
- **Edge cases pinned:** empty `\ph` lines (bare tag) never index — same skip-existing-empty-values rule as siblings; exact-duplicate `\ph` values collapse to one row (parser list stays faithful — all occurrences, in order); local replicas synced from production carry rows built by the old code (no `ph` entries), so the regression protocol's manual Full Reprocessing run performs the backfill on the replica before Phonetic-mode results are valid.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)