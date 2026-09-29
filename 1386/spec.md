---
remote_issue: 1386
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1386
promoted_at: '2026-09-29T13:58:48+00:00'
---

# [SPEC] Algonquian term-space semantic search (backend/db)

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1386/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1386/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1386/` — analytical artifacts, sc-summary, plan, audit findings

## Intent and Executive Summary

**Problem Statement:** Algonquian (SNEA) vernacular terms, phrase forms, and their orthographic variants across the four source communities are unreachable through the existing search surface: #36's semantic entry indexes the English-gloss space only, and the exact-text FTS modes miss morphological/orthographic variants (live research-card evidence: Sachim/Sachimo/Sachem/Sagimore/Sótchĭm/Sogmŏ across 4 sources). No vernacular term-space embedding substrate, derived table, or seam exists today (live grep: no `search_terms`/`search_semantic`-adjacent term symbols; `Record.embedding` is unpopulated scaffolding).

**Root Cause / Motivation:** The developer split the original semantic-search effort into three specs: #36 (English-gloss db/embed, delivered), #1385 (end-user UI), and this spec (Algonquian vernacular term space). The gloss space covers only English gloss text; the vernacular `\lx/\va/\se/\cf/\ve` term text and `\xv` phrases — the data linguists actually search by vernacular form — has no embedding index, so vernacular queries cannot bridge variant spellings across sources. This spec is the second consumer of the substrate pattern #36 measured/spike-established (measured 2026-09-29: e5-small INT8 ~472 MB, both-models-resident ~520 MB, within the 1 GiB Streamlit Cloud envelope; #36's remaining open items — the shared embedding-service substrate this spec consumes — are still pending at the time of this revision).

**Approach Chosen:** Fine-tune `multilingual-e5-small` on real meaning-adjacency corpus data (no synthetic pairs) with phrases down-weighted; commit INT8 ONNX artifact + tokenizer as integrity-pinned artifacts; add one wide derived-index table in the SemanticTermEntry style (`record_id` FK, `entry_type {term, phrase}`, `term`, `embedding vector(384)`, `embedding_model` pin, `language_code` derived from the `\so` scan with explicit `unknown`, `language_family` constant 'Algonquian') shipped via DDL-only append-only migrations; expose a standalone `search_terms` seam (a sibling module mirroring #36's `search_semantic` pattern — NOT a SearchMode widening, which is #36's gloss-space surface); populate inline during ingestion (population delivery deferred to plan per the #36 signature-unchanged precedent — internal extension vs sibling batched method); provide an admin Term-space Backfill button; calibrate real-data anchors spanning ≥3 coded languages with independent term and phrase floors; trigger re-training on corpus + allowlist change with per-run manifest. Derived-index-only: primary record data never mutated.

**Alternatives Considered & Why Discarded:**
- *SearchMode widening for term modes (mirror #36 SC-11)* — deferred: #36's literal widening covers the gloss space; term-space modes require a UI-mode extension this spec does not own (#1385's binding today is exclusively `search_semantic`), so v1 ships the standalone service seam reachable by admin/test paths; a future UI-mode extension would be its own filed follow-up. Tradeoff: seam exists without end-user reachability in v1.
- *Per-row English normalization of vernacular text before embedding* — rejected: AGENTS.md Tier 1 Unicode mandate + lessons-learned (2026-06-13-regex-linguistic-characters, 2026-06-13-infinity-symbol-normalization) — normalization/ASCII classes destroy linguistic data; the ∞→oozzz mapping is a SORT-key-only transform (generate_sort_lx), embeddings consume the raw Unicode form.
- *Reusing #36's gte-small gloss model for terms* — rejected: gloss-space model is fine-tuned on English-gloss adjacency, not vernacular-form adjacency; a separate fine-tune with its own artifact pin keeps calibration floors language-honest and avoids cross-space contamination.
- *Synthetic meaning-adjacency training pairs* — prohibited outright: Global Absolute Prohibition (090-data-integrity); training corpus derives from real verifiable source-of-record materials with provenance recorded in the manifest.

**Key Design Decisions:**
- **Model pin:** `multilingual-e5-small` INT8 ONNX artifacts + tokenizer committed under the models directory with SHA256 manifest pins (artifact locations + full pins recorded at the substrate item); tradeoff: repo weight (~470 MB class) for byte-pinned reproducibility and offline determinism.
- **e5 prefix discipline:** encode path applies `query:`/`passage:` e5 input prefixes; process-wide singleton session shared pattern per #36 R-2/R-14 (one-at-a-time in-flight lock; concurrent `Run()` thread-safe); the memory envelope is a shared budget with #36's gte-small (both-resident ~520 MB measured, under 1 GiB).
- **Wide-table one-concern-per-table:** follows the existing derived search-entry family (FTSEntry/SearchEntry/HeadwordSearchEntry/GlossSearchEntry in models/search.py); derived-index-only — Record remains source of truth; FK policy decision (CASCADE vs RESTRICT) follows #36's documented policy-note pattern and is finalized at plan time.
- **language_code derivation:** from the record's `\so`-derived language scan (`parser._extract_iso_langs` → `record['lg']` → `_sync_languages`), enum-checked against the config-declared coded set {xnt (Narragansett), xpq (Mohegan-Pequot), wam (Wampanoag/Wôpanâak), mjy (Mahican)} with explicit `unknown` fallback — never NULL, never silently guessed.
- **Staleness is explicit:** per-row `embedding_model` pin; rows searchable only when `embedding_model == current pin`; `stale_model`/`no_embeddings` statuses name the admin remedy rather than silently serving stale vectors.
- **Tokenizer allowlist is config-driven:** full IPA + project diacritics + ꝏ (U+A76F) + ∞ (U+221E) in v1; syllabics deferred with a documented evidence trigger; allowlist changes force re-train (risk: silently corrupted embeddings). SC-11 owns the behavioral surface (run-time config consumption; no hardcoded literals in tokenization code); SC-1 owns pin integrity only.

**User Intent / Original Prompt:** [SPEC] Algonquian term-space semantic search (backend/db) — fine-tuned multilingual-e5-small for the vernacular term space with config-driven tokenizer allowlist (IPA + diacritics + ꝏ/∞ in v1, syllabics deferred with trigger); one wide SemanticTermEntry-style derived table with language metadata from the `\so` scan; `search_terms` seam contract; spike-proposed calibration anchors spanning ≥3 coded languages with independent term/phrase floors; admin backfill as a sibling button in Table Maintenance → Data Reprocessing; re-train on corpus + allowlist change with per-run manifest. SC set: SC-1..SC-13 (13 SCs; SC-11 added by tier-1 iteration 1 revision — config-driven allowlist consumption split out of compound SC-1; SC-12/SC-13 added by tier-1 iteration 2 revision — signature-unchanged interface constraint split out of compound SC-8 and re-click idempotency guard split out of compound SC-9). Backend half of a two-spec split with frontend sibling #1385.

## Not Included

- **End-user search interface (records page modes, threshold control, score display, pagination, empty states)** — owned by sibling spec #1385; this spec's UI surface is the admin-only Term-space Backfill button only. Note: #1385's current body binds exclusively to #36's `search_semantic` seam — term-space UI consumption is NOT covered by #1385 as written; if stakeholder-facing term-space search UI is wanted, file a follow-up UI-mode extension spec referencing this spec's `search_terms` contract.
- **Mutation of primary record data** — this spec builds a derived index only; Record CRUD paths, MDF parser signatures, and `\so`/language sync logic are read-only consumers.
- **Syllabics support in v1** — deferred with a documented evidence trigger (syllabic-bearing records in real corpus inputs); syllabics belong to Cree/Ojibwe-family orthographies, absent from the project's xnt/xpq/wam/mjy Roman-orthography corpus (central-algonquian-dictionaries research card, confidence 0.85).
- **Exact-text FTS/ILIKE mode changes** — existing four search modes (Lexeme/FTS/Headword/Gloss) and `_search_strategies` dispatch remain unchanged; no SearchMode Literal widening in this spec.
- **External API-based embedding services** — in-process ONNX only (offline-first precedent from #36).
- **Changes to preference_service** — consumed as-is by #1385; no change here.
- **Migration renumbering or rewriting** — append-only registry per in-file directive.
- **#36 gloss-space changes** — gloss-space SearchMode widening, `gloss_search_entries`/`semantic_search_entries` tables, and the gte-small pin are #36's surface, untouched here.
- **Synthetic training data** — prohibited outright; the fine-tune corpus must be real, verifiable source-of-record data (Global Absolute Prohibition).

## Success Criteria

13 SCs. SC-12 and SC-13 were appended by the tier-1 iteration 2 revision (compound-SC splits: SC-8's interface constraint → SC-12; SC-9's idempotency guard → SC-13); SC-1..SC-11 identities are unchanged.

| ID | Criterion | Evidence Type | Documentation Sources | Verification Method |
|----|-----------|---------------|----------------------|---------------------|
| SC-1 | Committed e5-small substrate artifacts (INT8 ONNX + tokenizer) under the models directory match a SHA256-manifest pin byte-for-byte | structural | `pre-spec-inspection.yaml` affected_surfaces (pyproject deps verified live); `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md`; `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | hash check vs manifest pins |
| SC-11 | The tokenizer character allowlist (full IPA + project diacritics + ꝏ U+A76F + ∞ U+221E in v1) is consumed from a config key at run time by the term-side tokenization path — no hardcoded character literals in tokenization code; syllabics excluded from v1 with the deferred trigger documented | behavioral | `research-card-consultation.yaml` syllabics-deferral finding; `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md`; `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md`; `decompose-output.yaml` ITEM-1 allowlist invariants | pytest: tokenization against the config allowlist at run time (config change → allowlist consumption follows without code change); hardcoded-literal scan of tokenization code; syllabic character excluded with the documented trigger |
| SC-2 | The e5-small encode path returns unit-L2-norm 384-dimension float32 vectors, applies `query:`/`passage:` e5 input prefixes, pads dynamically to batch ≤ 64, loads through the process-wide singleton session pattern (streamlit-import-free, one-at-a-time in-flight lock); encode determinism holds for identical input | behavioral | `decompose-output.yaml` ITEM-2; `cross-cutting-matrix.yaml` memory-envelope rules (measured references: e5-small INT8 ~472 MB, both-models-resident ~520 MB); #36 R-2/R-14 precedent | pytest unit: shape, norm 1.0, batch-64 padding, prefix behavior, determinism; concurrency assert (registry count == 1) |
| SC-3 | Schema contains the new term-space table per the v1 field list (id, record_id FK, entry_type CHECK ∈ {term, phrase}, term, embedding vector(384), embedding_model, language_code with explicit `unknown` fallback, language_family constant 'Algonquian'), additive-only with existing tables/columns untouched; DDL-only append-only migration applies once, idempotent on rerun, in the `YYYYMMDDSSSSS` registry | behavioral | `interface-compat.yaml` v1 columns; `state-analysis.yaml` row_state invariants; `migrations.py` registry directive (live read :65-72); `docs/lessons-learned/2026-06-14-pg-catalog-schema-replication.md` (sync carries vector columns) | schema introspection after migration on freshly synced DB + isolated migration test (apply-in-order, version rows advance, rerun no-op) |
| SC-4 | language_code and entry_type derive deterministically during term-space population: language_code ∈ {xnt, xpq, wam, mjy, unknown} traced to the record's `\so`-derived language scan (never NULL, never guessed), and entry_type ∈ {term, phrase} classified by a deterministic rule (phrase = multi-token or `\xv` source) | behavioral | `code-path-inventory.yaml` derivation note (parser.py `_extract_iso_langs` verifed live :29-34); `requirements-output.yaml` REQ-E4/REQ-I6; `state-analysis.yaml` row_state invariants | pytest on real synced records spanning coded languages + no-code records → `unknown`; phrase-rule determinism assertions |
| SC-5 | `search_terms(query, threshold=None, source_id=None, limit=None) → TermSearchResult{results: list[(record_id, score, entry_type, language_code, source_id, term)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message}` returns the full ranked list desc cosine with a deterministic tie-break, threshold-filtered (default threshold from SC-6 calibration), excluding unpinned/stale rows via the `embedding_model == current pin` join; results never include pin-mismatched rows silently | behavioral | `interface-compat.yaml` search_terms signature + TermSearchResult fields; `state-analysis.yaml` seam_status machine; `concern-map.yaml` phase-3 boundaries | pytest service-layer vs freshly synced DB; field list exact; rank order + tie-break assertions |
| SC-6 | Calibration anchors derived from real, provenance-recorded corpus term↔term adjacency data hold on the freshly synced database spanning ≥3 coded languages, with independently recorded floor values per anchor for terms and phrases (per-anchor floors recorded in the calibration evidence artifact, not a blanket floor); the default threshold is set from the measured floors; drift past floors triggers the documented re-baseline procedure | behavioral | `decompose-output.yaml` ITEM-6; pre-spec-inspection open_questions (anchor real-data provenance); #36 SC-6 precedent (per-anchor evidence artifact, re-baseline owns drift); `research-card-consultation.yaml` gap_report (e5 floors are NOT transferable from #36's gte-small measurements) | pytest calibration module producing per-anchor evidence artifact with real-source provenance cited |
| SC-7 | Degraded inputs produce the correct status+message and never an exception: empty/whitespace query → `empty_query` before model invocation; no usable rows → `no_embeddings`; all rows stale → `stale_model`; all-below-threshold → `ok` with empty results; mixed pinned/stale rows serve pinned-only with `ok`; `stale_model`/`no_embeddings` messages name the admin Term-space Backfill remedy | behavioral | `state-analysis.yaml` seam_status machine + partial_staleness_note; `concern-map.yaml` phase-3 fail-fast rule; 090-data-integrity fail-fast mandate | pytest edge-input matrix on service (statuses, never exceptions) |
| SC-8 | Inline term-space population during ingestion writes per-record term rows with `embedding_model` set to the current pin, exact Unicode preservation (ꝏ/∞/IPA/diacritics round-trip byte-identical), write batches ≤ 512 rows, tqdm on long loops, and fail-fast on embed failure with no silent skip | behavioral | `upload_service.py` populate_search_entries (live read :1756-1830); `cross-cutting-matrix.yaml` batch + Unicode rules; `requirements-output.yaml` REQ-I5/REQ-I6 | extend existing population test family with real synced records; assert rows, pin, Unicode fidelity, batch size |
| SC-12 | The signature of the existing `populate_search_entries(record_ids, session=None) → int` is unchanged after term-space population is wired in (plan decides internal extension vs sibling batched method, per the #36 signature-unchanged precedent) | behavioral | `upload_service.py` populate_search_entries (live read :1756-1830) — the existing gloss-space population entry point whose signature must not regress; #36 signature-unchanged precedent (`.issues/36/spec.md`) | pytest signature assert on the wired ingestion path (existing signature test family passes unchanged after term-space wiring) |
| SC-9 | An admin-role Term-space Backfill control in Table Maintenance → Data Reprocessing re-embeds all records (re-embedding stale rows on pin change), uses the `st.progress` + progress callback + `st.status` idiom, surfaces failures via the handle_ui_error idiom, and rejects non-admin invocation | behavioral | `table_maintenance.py` render_data_reprocessing_maintenance (live read :125-196); state-analysis backfill_run machine; `testability.yaml` phase-4 Playwright precedent | pytest service method + Playwright click-through (role-gated) on synced DB |
| SC-13 | A re-click of the Term-space Backfill control while a run is in flight is blocked by the per-run idempotency/one-at-a-time guard | behavioral | state-analysis backfill_run machine (running state exclusivity); #36 admin backfill precedent | pytest in-flight guard assert (second invocation while running is rejected/blocked; guard resets after run completes) |
| SC-10 | Re-train trigger detects corpus change (new/changed records beyond the plan-declared drift tolerance) and allowlist config change without exception; a per-training-run manifest records model id, allowlist snapshot, corpus provenance (real source-of-record references), and timestamps; backfill proceeds only with the manifest present | behavioral | `requirements-output.yaml` REQ-E9 + no-requirements (no synthetic data); `state-analysis.yaml` retrain_trigger machine; 090 Global Absolute Prohibition | pytest trigger + manifest round-trip incl. allowlist-diff detection |

## Requirements

R-1. The system SHALL commit the e5-small substrate artifacts (INT8 ONNX model + tokenizer) under the models directory, byte-identical to SHA256-manifest pins recorded in the spec's artifact record, with the manifest regenerated and verified on any artifact replacement.

R-2. The tokenizer character allowlist SHALL be read from a config key at run time (full IPA + project diacritics + ꝏ U+A76F + ∞ U+221E in v1; syllabics excluded with the documented evidence trigger); the allowlist SHOULD NOT be hardcoded in tokenization code, and any allowlist change SHALL force the re-train trigger (R-12) — allowing tokenization to proceed against a stale allowlist silently corrupts embeddings. The term-side tokenization path SHALL consume the allowlist from config at run time (verifying at run time that a config allowlist change is picked up without a code change), which is SC-11's behavioral surface; the artifact/manifest integrity of the committed substrate itself is SC-1's.

R-3. The database schema SHALL contain exactly one new term-space table (id, record_id FK, entry_type CHECK ∈ {term, phrase}, term, embedding vector(384), embedding_model, language_code, language_family), additive-only, with existing tables, columns, and rows untouched; the FK policy (CASCADE vs RESTRICT) SHALL follow #36's documented policy-note pattern and be finalized at plan time.

R-4. Schema changes SHALL ship as DDL-only versioned migrations appended to the `YYYYMMDDSSSSS` registry (no data writes, no renumbering, no startup backfill) with a pgvector availability assertion; the sync protocol (`scripts/sync_prod_to_local.sh` from the branch under test) SHALL run immediately before every SC test cycle, and sync replication SHALL carry the vector columns so local databases never re-embed from scratch.

R-5. language_code for each term row SHALL derive deterministically from the record's `\so`-derived language scan, enum-checked against the config-declared coded set, with the explicit `unknown` fallback value for records with no coded match; language_code SHALL never be NULL and SHALL never be guessed from vernacular text morphology; entry_type SHALL classify {term, phrase} via one deterministic rule (phrase = multi-token or `\xv` source) applied uniformly everywhere.

R-6. The `embedding_service` singleton semantics carry over from #36: e5-small loads SHALL share the process-wide-session pattern with a one-at-a-time in-flight lock (never per-thread/per-session loads — Streamlit runs one script thread per user session and per-session loads multiply resident memory against the shared 1 GiB envelope); encode invariants (unit L2 norm, 384-dim, batch ≤ 64 dynamic padding, `query:`/`passage:` e5 prefixes) SHALL hold; encoding SHALL consume raw Unicode forms without normalization/stripping (AGENTS.md Tier 1 mandate: IPA/diacritics/ꝏ/∞ first-class data; ∞→oozzz is SORT-key-only per generate_sort_lx and MUST NOT be applied to embedding inputs unless a plan proves otherwise from measured behavior).

R-7. The system SHALL expose the v1 seam `search_terms(query, threshold=None, source_id=None, limit=None) → TermSearchResult{results: list[(record_id, score, entry_type, language_code, source_id, term)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message}`, returning the full ranked list desc cosine with a deterministic tie-break, threshold-filtered (None → the calibrated default from SC-6), NULL/stale rows excluded identically via the `embedding_model == current pin` join, never importing streamlit; ranked results SHALL present score desc and a deterministic tie-break (plan decides record_id-asc or term-asc, applied uniformly).

R-8. Calibration anchors SHALL be derived from real, provenance-recorded corpus data (source-of-record citations per the MANIFEST); anchors SHALL span ≥3 of the 4 coded languages with independently recorded floor values per anchor for terms and phrases, recorded in the per-anchor evidence artifact; the default threshold SHALL be set from the measured floors; material distribution drift SHALL re-baseline through the owned calibration procedure rather than silent threshold changes; #36's gte-small anchor measurements are NOT transferable — e5-small anchors MUST be measured fresh.

R-9. The `search_terms` seam SHALL degrade safely: `empty_query` (before any model invocation), `no_embeddings`, `stale_model`, and zero-below-threshold states return the designated status+message payloads without exceptions; degraded-state messages name the admin Term-space Backfill remedy; mixed pinned/stale rows SHALL serve pinned-only with `ok` (mirroring #36's exclusion semantics).

R-10. The ingestion path (upload/reprocess) SHALL populate term rows inline with `embedding_model` set to the current pin, exact Unicode preservation, ≤ 512-row write batches, tqdm progress on long loops, and fail-fast contextual raising on embed failure (no silent skip); the existing `populate_search_entries(record_ids, session=None) → int` signature SHALL remain unchanged (extend internally or use a sibling batched method — plan decides, per the #36 signature-unchanged precedent). The population/derivation concern is SC-8's; the interface/signature-unchanged constraint is SC-12's.

R-11. An admin-role Term-space Backfill control in Table Maintenance → Data Reprocessing SHALL re-embed all records (covering pin-change staleness) with progress reporting (st.progress + progress callback + st.status), surface failures via the handle_ui_error idiom, and reuse the existing admin role gate; a re-click while a run is in flight SHALL be blocked by the per-run idempotency guard. The control behavior is SC-9's; the re-click idempotency/one-at-a-time guard is SC-13's.

R-12. Re-training SHALL trigger without exception when the corpus changes beyond the plan-declared drift tolerance or when the tokenizer allowlist config value changes; a per-training-run manifest SHALL record the run inputs (model id, allowlist snapshot, corpus provenance references, timestamps) and backfill SHALL proceed only when the manifest for the current pin is present; every fine-tune corpus source SHALL be a real, verifiable source of record (no synthetic pairs).

R-13. Writes SHALL be confined to the new term-space table (including its embedding_model column); primary record mutation paths SHALL remain untouched (derived-index-only); existing Lexeme/FTS/Headword/Gloss strategies, the `search_records` signature, and the `Record` model columns SHALL remain unchanged.

R-14. Term-space population and calibration SHALL satisfy the batch discipline: ≤ 512-row DB write batches (PostgreSQL 65,535-parameter cap) and ≤ 64-row inference batches with dynamic padding; long-running loops SHALL report progress via tqdm; every population/backfill failure SHALL raise contextually.

## Items

Each SC maps to exactly one item. Items are numbered sequentially from 1 in dependency order. Item 11 (SC-11) was appended by the tier-1 iteration 1 revision (config-driven allowlist consumption split out of compound SC-1); Items 12-13 (SC-12/SC-13) were appended by the tier-1 iteration 2 revision (the signature-unchanged interface constraint split out of compound SC-8, the re-click idempotency guard split out of compound SC-9); Item 1..Item 10 identities are unchanged. This revision also removed an accidental duplicate Item 11 block left by iteration 1 (blocks at the former :105 and :165 were byte-identical; the surviving copy is placed after Item 10).

### Item 1 (SC-1): Committed e5-small substrate artifacts
- RED: hash check fails on absent/mismatched artifacts
- GREEN: commit INT8 ONNX + tokenizer artifacts with SHA256 manifest pins
- verify: hash check exit 0 vs pins
- commit: model artifacts + manifest

### Item 2 (SC-2): e5-small encode path invariants (singleton + prefixes + batching)
- RED: pytest asserting term-side encode path absent/wrong invariants (shape, norm, prefixes, batch padding, singleton identity) fails
- GREEN: e5 encode extension on the #36-pattern embedding service (or sibling module per plan decision on substrate delivery state): `query:`/`passage:` prefixes, unit L2 norm, batch ≤ 64 dynamic padding, process-wide singleton session with in-flight lock, streamlit-import-free
- verify: pytest unit (shape/norm/batch/prefix/determinism) + concurrency assertion (registry count == 1)
- commit: encode path + test

### Item 3 (SC-3): Term-space table model + DDL-only migrations
- RED: schema introspection asserting table/CHECK/FK absent fails; isolated migration test asserting missing version rows/objects fails
- GREEN: SemanticTermEntry-style model in models/search.py + models/__init__.py export chain; append DDL-only migration(s) with pgvector assertion; FK policy per plan decision following #36's documented policy-note pattern
- verify: schema introspection on freshly synced DB; isolated migration test (apply-in-order, version rows advance, rerun no-op)
- commit: models/search.py + migrations.py

### Item 4 (SC-4): language_code + entry_type derivation
- RED: pytest asserting derivation logic absent/misassigns seeded real corpus records fails
- GREEN: pure-function derivation (parser-adjacent helper or service-layer): language_code from the `\so`-derived scan enum-checked against the config-declared coded set (`unknown` explicit); entry_type phrase rule (multi-token or `\xv` source)
- verify: pytest on real synced records spanning coded languages + no-code records → `unknown`; phrase-rule determinism
- commit: derivation module + test

### Item 5 (SC-5): search_terms seam service
- RED: pytest asserting the seam absent/wrong contract (field list, statuses, rank order, tie-break, pin join) fails
- GREEN: term search service module (new file mirroring #36's search_semantic pattern): encode query with `query:` prefix → cosine over term table (pin join) → threshold filter → ranked list with deterministic tie-break; no streamlit import
- verify: pytest service-layer vs freshly synced DB; contract field list exact
- commit: term search service + test

### Item 6 (SC-6): Calibration anchors with real-data provenance
- RED: calibration pytest against unimplemented floors fails
- GREEN: calibration module with anchors spanning ≥3 coded languages, independently recorded term/phrase floors per anchor, real-source provenance recorded; default threshold set from measured floors
- verify: pytest produces per-anchor evidence artifact with provenance citations on the freshly synced DB; re-baseline procedure documented for drift
- commit: calibration module + evidence artifact

### Item 7 (SC-7): Degraded status semantics matrix
- RED: pytest asserting exceptions on edge inputs fails
- GREEN: guard chain in seam service: empty/whitespace guard before model invocation; no-usable-rows → no_embeddings; all-stale → stale_model; below-threshold → ok/empty; mixed → pinned-only+ok; messages name the Term-space Backfill remedy
- verify: pytest edge matrix — every input yields the correct status, never an exception
- commit: edge handling + test

### Item 8 (SC-8): Inline term-space population in ingestion
- RED: extend existing population test family asserting no term rows written → fails
- GREEN: population delivery per plan decision (internal extension with `populate_search_entries` signature unchanged, or sibling batched method): term rows with pin stamping, Unicode-exact round-trip, ≤ 512-row batches, tqdm, fail-fast contextual errors
- verify: extended test on real synced records — rows, pin, Unicode fidelity (incl. ꝏ/∞/IPA), batch size
- commit: upload_service + test

### Item 9 (SC-9): Admin Term-space Backfill button
- RED: Playwright asserting no Term-space Backfill control exists fails; pytest asserting service method absent fails
- GREEN: sibling section beside the Data Reprocessing block in table_maintenance.py; backfill service method with st.progress + progress callback + st.status idiom, handle_ui_error failures, role gate reuse, re-click idempotency guard
- verify: Playwright click-through (role-gated; isolated from #36's simultaneously-added Embedding Backfill section) on synced DB
- commit: table_maintenance.py + backfill method + tests

### Item 10 (SC-10): Re-train trigger + per-run manifest
- RED: test asserting trigger absent/no change-detection/manifest missing fails
- GREEN: manifest writer + trigger checks (corpus drift tolerance + allowlist config diff) in the train/backfill path; backfill gated on manifest presence
- verify: pytest trigger + manifest round-trip including allowlist-diff detection
- commit: manifest + trigger + test

### Item 11 (SC-11): Config-driven tokenizer allowlist consumption
- RED: tokenization test asserting hardcoded literals in tokenization code fails; test asserting syllabic characters processed despite v1-exclusion fails
- GREEN: config-driven tokenizer allowlist key (IPA + project diacritics + ꝏ + ∞; syllabics excluded; deferred trigger documented) consumed at run time by the term-side tokenization path — no hardcoded character literals; syllabics excluded with the documented trigger
- verify: pytest allowlist-consumption at run time (config change → consumption follows without code change); scan reports no hardcoded character literals in tokenization code; syllabic exclusion asserted
- commit: allowlist config + tokenization consumption + test

### Item 12 (SC-12): populate_search_entries signature unchanged
- RED: pytest asserting the existing `populate_search_entries(record_ids, session=None) → int` signature test fails/greps a changed signature after term-space population is wired in
- GREEN: term-space population wired per plan decision (internal extension with the signature preserved, or a sibling batched method — the existing signature is not modified either way, per the #36 signature-unchanged precedent)
- verify: pytest signature assert on the wired ingestion path (existing signature test family passes unchanged after term-space wiring)
- commit: signature-preservation test + wiring change

### Item 13 (SC-13): Backfill re-click idempotency guard
- RED: pytest asserting a second backfill invocation while a run is in flight succeeds (guard absent) fails
- GREEN: per-run idempotency/one-at-a-time guard on the backfill path (second invocation while the backfill_run machine is in the running state is rejected/blocked; guard resets after run completion)
- verify: pytest in-flight guard assert (second invocation while running rejected; guard resets after run completes)
- commit: guard + test

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #36 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36) | must deliver the shared embedding-service singleton pattern, calibration procedure precedent, admin backfill idiom, and pgvector DDL precedents this spec extends/consumes; e5-small encode path shares its service substrate and the ~520 MB both-resident measured envelope | pending (open; term-space items riding the shared embedding_service model this as an external dependency, not duplicated work) |
| #36 measured memory references (R-2: e5-small INT8 ~472 MB; both-resident ~520 MB, measured 2026-09-29) | envelope co-residency precondition for the 1 GiB Streamlit Cloud budget | satisfied (measured references recorded) |
| pgvector>=0.3.6 (runtime, pyproject:13) + pgvector extension assertion in migrations | extension availability precondition for vector(384) columns | satisfied |
| `migrations.py` `YYYYMMDDSSSSS` registry directive (live :65-72) | registry format + append-only mandate for new migrations | satisfied |
| Table Maintenance Data Reprocessing idiom (live :125-196) + admin role gate (:126-131) | template + role gate for the admin Term-space Backfill button | satisfied |
| MDF parser language scan (`parser._extract_iso_langs` live :29-34; `\so` handling :95-100; second pass :130-149) | substrate for language_code derivation | satisfied |
| iso-639-3.tab codes xnt/xpq/wam/mjy (verified :4075,:6976,:7367,:7398) | coded-language enum anchors | satisfied |
| Local PostgreSQL sync protocol (AGENTS.md mandate; lessons 2026-07-16, 2026-06-14) | fresh production replica before every test cycle; vector columns replicate | satisfied (procedure) |
| Lessons learned docs (2026-06-13-regex-linguistic-characters, 2026-06-13-infinity-symbol-normalization) | Unicode-mandate grounding for allowlist + embedding-input rules | satisfied (consulted; incorporated) |
| Research cards (cross-source-comparison ≈0.9; roger-williams-key ≈0.9; modern-mohegan ≈0.9; central-algonquian-dictionaries ≈0.85) | variant-space evidence grounding the problem; orthography/diacritic evidence for the allowlist; syllabics-deferral support | satisfied (consulted; incorporated) |
| Fine-tune training corpus source-of-record materials (cross-source comparison research-card corpus materials) | real provenance data for meaning-adjacency fine-tuning; location to be established during substrate item (no data/ or models/ directory exists yet) | pending (satisfied at substrate item) |
| #1385 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385) | end-user UI; currently binds exclusively to #36's `search_semantic` — term-space UI consumption NOT covered (binding discrepancy reconciled in Not Included); a term-space UI-mode extension would be a separately filed follow-up | pending (sibling; no term-space binding as written) |

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1 | 1 (substrate) |
| R-2 | SC-1, SC-10, SC-11 | 1 (substrate), 5 (calibration + manifest), 3 (services) |
| R-3 | SC-3 | 2 (schema) |
| R-4 | SC-3 | 2 (schema) |
| R-5 | SC-4 | 3 (services) |
| R-6 | SC-2 | 1 (substrate), 3 (services) |
| R-7 | SC-5 | 3 (services) |
| R-8 | SC-6 | 5 (calibration + manifest) |
| R-9 | SC-7 | 3 (services) |
| R-10 | SC-8, SC-12 | 4 (ingestion + admin) — population concern SC-8; signature-unchanged interface constraint SC-12 |
| R-11 | SC-9, SC-13 | 4 (ingestion + admin) — control behavior SC-9; re-click idempotency guard SC-13 |
| R-12 | SC-10 | 5 (calibration + manifest) |
| R-13 | SC-3, SC-5, SC-8 | 2-4 |
| R-14 | SC-8, SC-6 | 4-5 |
| R-14 | SC-9 (re-embed path progress discipline only), SC-9 is co-resolved with SC-13's in-flight guard | 4 (ingestion + admin) — the SC-9 trace edge |
| R-10 | SC-12 | 4 (ingestion + admin) — the SC-12 trace edge (signature-unchanged interface constraint) |
| R-11 | SC-13 | 4 (ingestion + admin) — the SC-13 trace edge (re-click idempotency guard) |

Dependency order: Item 1 → Item 2 → (Item 3 ∥ Item 6 anchor provisioning) → Item 4 → Item 5 → Item 6 (floors need populated synced data) → Item 7 → Item 8 → Item 9 → Item 10 → Item 11 → Item 12 → Item 13; acyclic (Item 3 and Item 2 are parallel-safe: model vs DDL surfaces disjoint; Item 11's config allowlist surfaces are disjoint from the artifact hash check in Item 1 up to the commit boundary — the allowlist config commit and the substrate artifact commit stay separable; Items 12-13 ride phases 4 ingestion+admin — Item 12 verifies the ingestion wiring left behind Item 8 unchanged at the interface, Item 13 verifies the backfill path Item 9 built guards re-click).

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| SemanticTermEntry-style pattern (entry tables id/FK/term/normalized shape) | code | `src/database/models/search.py` | live read 2026-09-29 (index stale; freshness check run) |
| Record.embedding Vector(1536) scaffolding + source_id FK + version_id_col | code | `src/database/models/core.py:95` | live read 2026-09-29 |
| Migration registry YYYYMMDDSSSSS directive + pgvector DDL precedent (v2 embedding column) | code | `src/database/migrations.py:65-129,:328-331` | live read 2026-09-29 |
| SearchMode Literal + `_search_strategies` dispatch + generate_sort_lx (∞→oozzz sort-key) + search_records | code | `src/services/linguistic_service.py:28,:79-84,:104-170,:384-484` | live read 2026-09-29 |
| populate_search_entries(record_ids, session=None) → int | code | `src/services/upload_service.py:1756-1830` | live read 2026-09-29 |
| Parser language scan (`\so` → source_page; `_extract_iso_langs`; `record['lg']` second pass) | code | `src/mdf/parser.py:29-34,:95-100,:130-149` | live read 2026-09-29 |
| Table Maintenance admin page gate + Data Reprocessing idiom | code | `src/frontend/pages/table_maintenance.py:125-196` | live read 2026-09-29 |
| pyproject dependencies (pgvector>=0.3.6 runtime :13; sentence-transformers>=3.0.0 dev :33) | config | `pyproject.toml:7-34` | live read 2026-09-29 |
| Coded language ISO anchors | data | `iso-639-3.tab` :4075 (xnt), :6976 (xpq), :7367 (wam), :7398 (mjy); migrations.py seeded source descriptions :731-:757 | live read 2026-09-29 |
| Corpus character inventory (∞ ×511; diacritics; ꝏ = 0 occurrences in sample) | data | `src/seed_data/natick_sample_100.txt` | live grep 2026-09-29 |
| ∞ letter semantics + oozzz sort-key mapping | docs | `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | read 2026-09-29 |
| Regex safety with linguistic characters (no ASCII classes; Python \w safe) | docs | `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | read 2026-09-29 |
| Sync replication carries vector columns | docs | `docs/lessons-learned/2026-06-14-pg-catalog-schema-replication.md` | read 2026-09-29 |
| Variant-spelling evidence (Sachim/Sachimo/Sachem/Sagimore/Sótchĭm/Sogmŏ) | research card | `.issues/research-cards/cross-source-comparison.md` | read 2026-09-29 (confidence 0.9) |
| Accent/diacritic repertoire of primary sources | research card | `.issues/research-cards/roger-williams-key-research.md` | read 2026-09-29 (confidence 0.9) |
| xpq orthography + Algonquian family constant | research card | `.issues/research-cards/modern-mohegan-dictionary.md` | read 2026-09-29 (confidence 0.9) |
| Syllabics family-distribution (deferral support) | research card | `.issues/research-cards/central-algonquian-dictionaries.md` | read 2026-09-29 (confidence 0.85) |
| e5-small memory measurements + envelope co-residency | analysis artifact | #36 R-2 measured references (measured 2026-09-29, same machine) | recorded in .issues/36/spec.md R-2/R-14 |
| Stub body (original) | issue | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1386 | `gh api` read 2026-09-29 (4050-char body, 0 comments) |
| #1385 binding state (search_semantic only) | issue | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385 | live grep of `.issues/1385/spec.md` 2026-09-29 |
| #36 spec (pattern precedent) | spec | `.issues/36/spec.md` | read 2026-09-29 |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Hash checks cost seconds. Skipping means a corrupted or silently substituted model artifact ships — every term embedding in the DB is wrong or irreproducible.
- **SC-11:** Tokenization allowlist-consumption test costs minutes. Skipping means a hardcoded allowlist silently tokenizes ꝏ/∞ out of the corpus, poisoning embeddings until linguistic review fails the feature weeks later.
- **SC-2:** Vector unit + concurrency tests cost minutes. Skipping means malformed/denormalized vectors or per-session model loads silently poison ranking and multiply ~472 MB of resident memory per concurrent user — an OOM crash of the Streamlit Cloud container discovered only in production.
- **SC-3:** Introspection + isolated migration tests cost minutes. Skipping means a schema/model mismatch or non-idempotent migration breaks every term query at runtime or bricks deployment for every environment simultaneously.
- **SC-4:** Derivation pytest costs minutes. Skipping means records silently misassigned to the wrong language (or guessed from morphology) corrupt per-language calibration floors — discovered only after linguistic review of wrong-language search behavior, compounding re-calibration cost.
- **SC-5:** Seam pytest costs minutes. Skipping means the contract any future UI-mode extension binds to is wrong — cross-spec rework after #1385 grows (compound escalation).
- **SC-6:** Calibration run costs minutes against real synced data. Skipping means an uncalibrated threshold ships with floors that were never measured for e5-small on this corpus (#36's gte-small measurements are NOT transferable) — linguists tune blind and correctness of the feature itself is unverifiable.
- **SC-7:** Edge pytest costs minutes. Skipping means production support tickets for every no-embeddings/stale-model state — the highest-frequency failure surface for a derived index populated by a separate backfill.
- **SC-8:** Extended population tests cost minutes. Skipping means new records silently lack searchable term rows — a data-integrity defect discovered only by the absence of results, with no error trail to diagnose from.
- **SC-12:** Signature-unchanged pytest costs minutes. Skipping means a signature regression in `populate_search_entries` ships — every existing gloss-space consumer (#36's surface) breaks at the interface, discovered by call-site failures after deploy.
- **SC-9:** Playwright click-through costs minutes. Skipping means a broken admin tool or a non-admin-invocable re-embed surfaces during the first real backfill attempt, under operational pressure.
- **SC-13:** In-flight guard pytest costs minutes. Skipping means concurrent re-clicks spawn overlapping re-embed runs — duplicated batch writes, race-corrupted per-row pin stamping, and progress readouts contradicting each other under operational pressure.
- **SC-10:** Trigger + manifest tests cost minutes. Skipping means an allowlist or corpus change re-embeds nothing (or re-trains against stale inputs) with no manifest to reproduce the run — silently corrupted embeddings that only linguistic review catches downstream.

## Edge Cases

| Condition | Expected Behavior | Resolution |
|-----------|-------------------|------------|
| Empty term-space table (no rows) | `search_terms` returns status `no_embeddings` with a message naming the Term-space Backfill remedy — not an error | SC-7 |
| Empty/whitespace query | Status `empty_query` before any model invocation — never an exception | SC-7 (guard-first) |
| Model artifact missing from repo | Load fails with a clear error identifying the missing path | SC-1 hash check + load error |
| Committed artifact bytes drift from manifest pin | Hash check fails-fast — artifact rejected, not silently loaded | SC-1 |
| pgvector extension unavailable | Migration-time assertion error naming the missing extension | SC-3 extversion assert |
| Tokenizer allowlist config key missing/unreadable at run time | Tokenization fails-fast at config read (no silent fallback to hardcoded character set) | SC-11 |
| Term text exceeds model token limit (512) | Text truncated to model max token length before embedding; truncation logged | SC-2 (tokenizer truncation) |
| Unicode vernacular text (IPA/diacritics/ꝏ/∞) | Handled natively by the tokenizer; Unicode preserved exactly — no normalization/ASCII-strip layers; ∞→oozzz remains SORT-key-only | SC-8 (ingestion fidelity), SC-11 (allowlist charset), R-6 |
| Term string empty after extraction | No embedding generated; entry excluded from vector search (NULL-safe) | SC-3, SC-7 |
| All rows below similarity threshold | `ok` status with empty results — not an error | SC-7 |
| Mixed pinned/stale rows | Pinned-only rows served with `ok`; stale/NULL-pin rows excluded identically at query | SC-7 (partial staleness) |
| All rows stale (pin mismatch everywhere) | `stale_model` status naming the backfill remedy | SC-7 |
| Model pin changes (future) | Old-pin rows excluded; admin Term-space Backfill re-embeds | R-11 + SC-7 |
| Record with no coded language match | language_code = `unknown` explicitly (never NULL, never guessed) | SC-4 |
| Phrase-vs-term boundary ambiguity (multi-token `\lx`) | Deterministic phrase rule applied (multi-token or `\xv` source) — single rule, uniformly applied | SC-4 |
| Concurrent upload during backfill | Batch ≤ 512 upserts; per-row pin stamping; no partial-state rows become searchable | R-14, SC-8 |
| Batch near the 65,535 PG parameter cap | Write batches ≤ 512 rows | R-14 (090 guideline) |
| N concurrent user sessions | All user threads share one process-wide e5 session; concurrent loads race-safe under the in-flight lock (registry count == 1) | SC-2 |
| Allowlist config changed without re-train | Trigger detects the diff → change_pending; backfill gated on manifest presence (stale-pin rows excluded, never silently served); tokenization consumes the new allowlist at run time | SC-10, SC-11 |
| Partial backfill failure | Error surfaced via handle_ui_error idiom; completed-batch state transactional per batch; failed state reports; stale rows remain excluded at query | SC-9 |
| Re-click while backfill in flight | Blocked by the per-run idempotency guard | SC-13 (backfill_run running-state exclusivity; SC-9 is the co-resolved control surface) |
| Ingestion signature regression after term-space wiring | Existing `populate_search_entries(record_ids, session=None) → int` signature test fails-fast — wiring change rejected rather than silently breaking gloss-space consumers | SC-12 (the split interface constraint from compound SC-8) |
| Corpus grows beyond drift tolerance | Re-train trigger fires (corpus diff) → training run → manifest written → backfill follows | SC-10 |
| Training corpus provenance unverifiable | Training run blocked/fails-fast — no synthetic pairs substituted (Global Absolute Prohibition) | SC-10, R-12 |
| e5-small + gte-small both resident | Envelope check vs 1 GiB with the measured ~520 MB both-resident reference; profiled evidence on load path | SC-2, Item 2 |

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*

## Change Control

| Date | Revision | Reason | Authorized By |
|------|----------|--------|---------------|
| 2026-09-29 | Full spec body assembled by spec-creation create step from 12 analysis artifacts (tmp/1386/artifacts + tmp/1386/contracts). Stub replaced. Open items resolved: #1385 binding discrepancy recorded in Not Included (#1385 binds exclusively to search_semantic — term-space UI consumption NOT covered; follow-up UI-mode extension would be separately filed); ꝏ (U+A76F) production distribution left as a substrate-item measure-before-freeze item with allowlist committed in v1 per stub (sample shows 0 occurrences; production measurement owns the freeze); FK policy (CASCADE vs RESTRICT) deferred to plan time following #36's documented policy-note pattern; shared embedding_service vs sibling module for e5 encode path deferred to plan time (coordinated with #36's delivery state); anchor floors to be measured fresh at Item 6 (research-card gap report: #36 gte-small floors NOT transferable to e5-small). SearchMode widening rejected (Not Included) in favor of standalone seam per #36 precedent analysis. | Spec-creation create step (analysis artifacts → assembled spec); SC/Item 1:1 mapping per pipeline readiness (ITEM-8 split into SC-8/SC-9 items 8/9) | Spec-creation pipeline (spec-authorized scope) |
| 2026-09-29 | Validation revision (tier-1 iteration 1, 4 findings). Finding compound-SC + evidence-type-mismatch + testability (SC-1): SC-1 de-compounded — narrowed to the artifact-integrity claim only ("Committed e5-small substrate artifacts (INT8 ONNX + tokenizer) match a SHA256-manifest pin byte-for-byte", structural, hash-check verification); the allowlist claims were NOT removed — they now live in NEW SC-11 (tokenization consumes the config allowlist at run time; no hardcoded character literals in tokenization code; syllabics excluded with the documented trigger) as behavioral, with pytest run-time config-consumption + hardcoded-literal scan + syllabic-exclusion verification. No renumbering: SC-2..SC-10 identities intact; SC-11 appended as Item 11 (1:1 SC↔Item mapping preserved across the whole set). R-2 extended to state the SC-1/SC-11 split boundary unchanged in obligation; Key Design Decisions Tokenizer-allowlist bullet, Cost Frame SC-1 entry (split into SC-1 + SC-11 entries), Edge Cases (allowlist-missing-config row + artifact-pin-drift row + SC-11 co-resolution on the Unicode/allowlist/trigger rows), User Intent SC-set sentence updated. Finding escape-hatch/determinism (SC-8): "(sibling method preferred)" replaced with bounded plan-deferral phrasing — "plan decides internal extension vs sibling batched method, per the #36 signature-unchanged precedent" — mirroring R-10's existing deferral pattern (Approach Chosen, Item 8 GREEN updated to the same bounded form). Finding phase-label incoherence (Traceability): R-row phase labels renumbered to the concern-map's 5-phase model (1 substrate, 2 schema, 3 services, 4 ingestion+admin, 5 calibration+manifest) across all R rows; R-2 gains SC-11; R-6 phase corrected substrate→substrate+services; R-7/R-9 corrected 4/5→3 (services); R-10/R-11 corrected 6/7→4; R-12 corrected 8→5; R-13 range corrected 2-6→2-4; R-14 corrected 5-6→4-5; dependency-order sentence extended to Item 11. Finding advisory (trace edge + preamble): R-14→SC-9 trace edge added (re-embed path progress discipline, phase 4) and the preamble "substrate pattern #36 established" reworded to "measured/spike-established" with the pending/open state of #36's shared embedding-service substrate recorded. sc-summary.yaml updated (sc_count 10→11; SC-1 reworded to split; SC-11 appended behavioral/plan_item 11; SC-8 description updated to the bounded phrasing). | Spec-validation findings from tier-1 iteration 1 validate step: compound-SC (SC-1), evidence-type-mismatch (structural SC declaring behavioral verification), SC-8 escape-hatch hedging, Traceability phase-label incoherence, advisory R-14→SC-9 trace edge + preamble wording for #36's pending substrate | Spec-creation validate step (tier-1 iteration 1) |
| 2026-09-29 | Validation revision (tier-1 iteration 2, 2 blocking findings). Finding duplicate-item-block (hard structural defect): the two byte-identical "### Item 11 (SC-11)" blocks left by iteration 1 (former :105 and :165) — one removed; the single surviving Item 11 placed after Item 10, restoring strict sequential order 1..13 (no 1, 11, 2..10, 11 sequence). Finding compound-SC (SC-8, SC-9) — split WITHOUT weakening any verification target (SC Lobotomy Prohibition; SC-1→SC-11 precedent): SC-8 narrowed to the population/derivation concern (per-record term rows with current-pin stamping, exact Unicode round-trip ꝏ/∞/IPA/diacritics byte-identical, ≤ 512-row write batches, tqdm, fail-fast on embed failure with no silent skip); the `populate_search_entries(record_ids, session=None) → int` signature-unchanged interface constraint moved to NEW SC-12 (a distinct function's interface concern, independently verifiable — pytest signature assert on the wired ingestion path); SC-9 narrowed to the admin Term-space Backfill control behavior (role-gated re-embed covering pin-change staleness, st.progress + progress callback + st.status idiom, handle_ui_error failure surfacing, non-admin rejection); the re-click-while-in-flight idempotency/one-at-a-time guard moved to NEW SC-13 (pytest in-flight guard assert; guard resets after run completion). Items section: Item 12 (SC-12) and Item 13 (SC-13) appended after Item 11 matching plan_item 12/13; no SC/Item renumbering of SC-1..SC-11 identities. Traceability: R-10 → SC-8, SC-12 (+ SC-12 trace edge row); R-11 → SC-9, SC-13 (+ SC-13 trace edge row). Cost Frame: SC-12 and SC-13 entries added. Edge Cases: re-click row co-resolution remapped to SC-13 (SC-9 co-resolved control surface) + new ingestion-signature-regression row → SC-12. Dependencies: dependency-order sentence extended to Item 11 → Item 12 → Item 13 (Items 12-13 ride phase 4 ingestion+admin). R-10/R-11 reworded to name the SC-8/SC-12 and SC-9/SC-13 split boundaries unchanged in obligation. User Intent SC-set sentence updated (SC-1..SC-13, 13 SCs). sc-summary.yaml updated (sc_count 11→13; SC-8/SC-9 descriptions narrowed; SC-12/SC-13 appended behavioral/plan_item 12/13). | Spec-validation findings from tier-1 iteration 2 validate step: duplicate Item 11 block (hard structural defect), compound-SC (SC-8, SC-9) | Spec-creation validate step (tier-1 iteration 2) |