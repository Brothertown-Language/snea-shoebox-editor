# [SPEC] Semantic Gloss Search with pgvector (db/embed revision)

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/36/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/36/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/36/` — analytical artifacts (regenerated at issues-data HEAD 2026-09-29; not restored from history), sc-summary, plan, audit findings

## Intent and Executive Summary

**Problem Statement:** English-gloss semantic search requires a committed embedding-model artifact, pgvector-backed schema, an embedding service, a UI-agnostic semantic search service, upload-path embedding, DDL migrations, and an admin backfill — none of which exist today (`GlossSearchEntry` has only id/record_id/term/normalized_term columns; verified live).

**Root Cause / Motivation:** The original #36 body predates the 2026-09-28 brainstorming spike: it pins the wrong model (all-MiniLM-L6-v2, ~22 MB) via sentence-transformers, implies a startup backfill, and predates the developer's split directive. This revision records the decided db/embed scope with measured, pinned values; the end-user interface is filed as its own spec (#1385).

**Approach Chosen:** Pin `thenlper/gte-small` via committed INT8 ONNX artifacts; add `vector(384)` columns/table via DDL-only versioned migrations (no startup backfill); implement `embedding_service` (process-wide onnxruntime session singleton — load once per process, never per user) + `semantic_search_service` exposing the `search_semantic` seam; widen the `SearchMode` Literal and its dispatch entry additively ('Semantic Gloss'/'Semantic All') so the semantic modes are backend-reachable; inline-embed during upload; expose admin backfill as a sibling button in Table Maintenance → Data Reprocessing; correct runtime dependencies.

**Alternatives Considered & Why Discarded:**
- *sentence-transformers as runtime dep (original body)* — rejected: measured in-process ONNX load+encode covers the need at ~35 MB runtime footprint; sentence-transformers adds PyTorch-class weight for zero runtime benefit and stays dev-only (corrected dependency direction).
- *Per-user-session model loads* — rejected under the developer-authorized OOM-safety amendment (2026-09-29): Streamlit runs one script thread per user session, so per-session `load_model()` would multiply ~128 MB (gte-small INT8) of resident weight per concurrent user against the 1 GiB Streamlit Cloud envelope; replaced with a process-wide singleton (R-2).
- *External embedding API* — rejected: offline-first reframed as in-process ONNX only; no third-party embedding API calls.

**Key Design Decisions:**
- **Model pin:** `thenlper/gte-small` @ 17e1f347d17fe144873b1201da9178889c639cd; committed `models/gte-small/onnx/model_qint8_avx512_vnni.onnx` (34,118,638 B, SHA256 `c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd`) + `models/gte-small/tokenizer.json` (711,661 B, SHA256 `da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0`). Tradeoff: +34.8 MB repo weight for byte-pinned reproducibility and offline determinism. The pinned INT8 ONNX session is thread-safe for concurrent `Run()` calls (verified 2026-09-29: 8 concurrent threads, deterministic outputs, no divergence) — the singleton shares one session across all user threads.
- **Process-wide session singleton:** `load_model()` returns a single `onnxruntime.InferenceSession` held at module level inside `embedding_service.py` (which remains streamlit-import-free); never per-thread/per-session loads — Streamlit runs one script thread per user session, and per-session loads multiply resident memory per concurrent user. Concurrent `load_model()` calls are race-safe: one-at-a-time in-flight lock (`threading.Lock`) around any (re)load guards cache-eviction double-load races — the same idiom the admin backfill already requires. Measured reference values for the worst-case resident-set profile (this machine, 2026-09-29): gte-small INT8 ~128 MB, e5-small INT8 ~472 MB, both-models-resident ~520 MB — all under the 1 GiB Streamlit Cloud envelope; these are measured references for evidence, NOT a change to SC-10's envelope SC.
- **Two-table schema:** `GlossSearchEntry` gains `embedding vector(384)`, `entry_type`, `embedding_model` (primary `ge`); NEW `SemanticSearchEntry` table (record_id FK, entry_type, term, embedding, embedding_model) holds `ge_subentry`, `ge_sense`, `ge_in_sense`, `xe`, `ce`, `eg`. Matches the one-table-per-search-concern pattern.
- **FK policy note (documented difference):** new `semantic_search_entries.record_id` uses CASCADE per developer-approved intent; live sibling `gloss_search_entries.record_id` uses RESTRICT — intentional, documented here, not altered.
- **Score/pin invariant:** rows are searchable only when `embedding_model == pin`; NULL or stale rows are excluded identically at query time (degradation to empty state, never error).
- **Batching:** ≤ 64 dynamic-padded inference; ≤ 512-row DB write batches (090 guideline; 65,535 parameter cap).
- **UI ownership:** #36 owns ZERO `st.` calls outside `table_maintenance.py` (backfill section only); mode captions, threshold widgets, score badges, pagination, and empty states are the UI spec (#1385).

**User Intent / Original Prompt:** Original #36 (semantic gloss search with pgvector, offline-first) + 2026-09-28 brainstorming session (10 turns, design approved, finalization "proceed"): revise the body to the measured/pinned db/embed scope; split the end-user interface into a remote-filed follow-up spec.

## Not Included

- **End-user search interface (records page modes, threshold preference control, score display, pagination UI, empty-state rendering)** — filed as [SPEC] #1385; this spec's UI surface is the admin backfill button only.
- **Semantic search on Algonquian headwords/terms** — English gloss fields only.
- **Semantic search on non-gloss fields** — de, ue, nt, ng, dn/gn/xn excluded.
- **External API-based embedding services** — in-process ONNX only.
- **Backend search-mode integration beyond the additive seam (SC-11)** — #36 adds 'Semantic Gloss'/'Semantic All' to the `SearchMode` Literal (`linguistic_service.py:28`) and its dispatch entry only; end-user search-mode radios/UI wiring for those modes belong to #1385.
- **Replacement/removal of existing exact-match search modes** — Lexeme, FTS, Headword, Gloss untouched; SearchMode Literal widening is additive only.
- **Changes to MDF parser or data ingestion format** — `populate_search_entries()` is extended internally; signature unchanged.
- **Migration renumbering or rewriting** — append-only registry per in-file directive.
- **`preference_service.py` changes** — consumed as-is by #1385; no change here.

## Success Criteria

| ID | Criterion | Evidence Type | Documentation Sources | Verification Method |
|----|-----------|---------------|----------------------|---------------------|
| SC-1 | Committed artifacts at `models/gte-small/` (ONNX 34,118,638 B, tokenizer.json 711,661 B) match the recorded SHA256 pins byte-for-byte (full pins recorded above under Model pin) | structural | `handoff.yaml` pins (measured 2026-09-28); `blast-radius.yaml` | CI/script hash check vs recorded pins (tokenizer.json full pin `da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0`, verified live from tmp/spike-gte 2026-09-29) |
| SC-2 | `embedding_service.encode(texts, batch≤64)` returns float32 (1,384) unit-norm vectors via tokenize(512) → onnxruntime → attention-mask mean-pool → L2-normalize | behavioral | spike-executed session 2026-09-28; `decompose-output.yaml` D1-ITEM-2 | pytest unit: vector shape, norm=1.0, batch-64 padding path |
| SC-3 | Schema contains `gloss_search_entries` +3 new columns (`embedding vector(384)`, `entry_type`, `embedding_model`) and new `semantic_search_entries` table (id, record_id FK CASCADE, entry_type, term, embedding vector(384), embedding_model); existing columns untouched | structural | `models/search.py:63-78` + `state-analysis.yaml`; `interface-compat.yaml` v1 field list | schema introspection after migration on synced DB |
| SC-4 | Two DDL-only migrations (CREATE TABLE + ALTER TABLE ADD COLUMN) apply in order, version-gated idempotent, in the append-only `YYYYMMDDSSSSS` registry with a pgvector extversion assertion; no data writes, no renumbering | behavioral | `migrations.py:67-72` directive (verified live); #1346 flake isolation pattern | isolated migration test: version rows advanced; objects created; rerun is no-op |
| SC-5 | `search_semantic(mode: 'gloss'\|'all', query, threshold=None, source_id=None, limit=None) → SemanticSearchResult{results: list[(record_id, score)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message}` returns the full ranked list desc cosine with record_id-asc tie-break, threshold-filtered (None → 0.80), excluding NULL/stale rows via the pin join; service never imports streamlit | behavioral | `concern-map.yaml` seam contract; `interface-compat.yaml` dependency_contract | pytest service-layer vs freshly synced local DB |
| SC-6 | Calibration anchors on freshly synced real data: positives (round/bed/house/peas/hunt) score ≥ their 0.85-0.90 recorded floors; unrelated negatives score ≥0.07 below the positive floor; default threshold 0.80 | behavioral | `handoff.yaml` calibration (6,266 unique terms, measured 2026-09-28); REQ-E13 | pytest calibration module producing per-anchor evidence artifact (per-anchor floor values recorded per-anchor in the calibration evidence artifact — not a blanket floor; the 0.85-0.90 band is the recorded summary bound); re-baseline procedure owns drift |
| SC-7 | Degraded inputs produce the correct status+message and never an exception: empty/whitespace query → `empty_query` before model invocation; no embedded rows → `no_embeddings`; pin mismatch rows → `stale_model`; all-below-threshold → `ok` with empty results; `stale_model`/`no_embeddings` message names the admin backfill remedy | behavioral | `state-analysis.yaml` state machine invariants; `decompose-output.yaml` D1-ITEM-7 | pytest edge-input matrix on service |
| SC-8 | `populate_search_entries(record_ids, session=None) → int` (signature unchanged) embeds the new primary `ge` rows inline during ingestion (1-5 strings/record, measured 10-60 ms/record) with `embedding_model` set to the pin; batch ≤ 512; Unicode preserved exactly | behavioral | `upload_service.py:1758` (`populate_search_entries()` — stable anchor); `test_upload_search_entries.py` | extend existing test with real synced records; assert embeddings + pin + Unicode fidelity |
| SC-9 | An admin-role Embedding Backfill button in Table Maintenance → Data Reprocessing re-embeds all records with `st.progress` + progress callback + `st.status`, surfacing completion results and errors via `handle_ui_error`; non-admin role is rejected | behavioral | `table_maintenance.py:125-130,:169-196` idiom (verified live); Role gate reused | Playwright click-through on synced DB; rate reference 6,266 terms/72.2 s |
| SC-10 | Runtime dependencies gain `onnxruntime` + `tokenizers`; `sentence-transformers>=3.0.0` remains in the dev group (already there — verified live); `model_qint8_avx512_vnni.onnx` load + batch-64 encode profile fits the 1 GiB Streamlit Cloud envelope (measured 312 MiB RSS; worst-case resident-set references recorded under R-2) | structural | `pyproject.toml:7-19,:28-34` (verified live 2026-09-28); R-2 measured references; profiler evidence | dependency manifest check + profiler evidence artifact |
| SC-11 | #1385 boundary — additive only: the `SearchMode` Literal widens with `'Semantic Gloss'`/`'Semantic All'` at `linguistic_service.py:28` and the mode dispatch entries route those two modes to `search_semantic()`; no existing strategy, signature, or return type changes | behavioral | `linguistic_service.py:28,:79-84` (verified live 2026-09-29); `code-path-inventory.yaml` P1; `interface-compat.yaml` | pytest dispatch-routing test asserting the two semantic modes route to `search_semantic()` and existing four modes' dispatch behavior unchanged |
| SC-12 | `embedding_service.load_model()` returns a process-wide single onnxruntime `InferenceSession` (module-level holder in `embedding_service.py`, streamlit-import-free) — never per-thread/per-session loads; N concurrent `load_model()` calls behave under the one-at-a-time in-flight lock (registry count == 1, the same idiom the admin backfill uses) | behavioral | concurrency evidence 2026-09-29 (8 threads deterministic `Run()`); `decompose-output.yaml` D1-ITEM-2 | pytest concurrency: N threads → identical session handle, registry count == 1 |

## Requirements

R-1. The system SHALL commit the pinned gte-small INT8 ONNX artifact and tokenizer at `models/gte-small/` byte-identical to the recorded SHA256 pins.

R-2. The system SHALL provide `embedding_service.encode(texts: list[str], batch≤64) → float32 array` producing L2-normalized 384-dimension vectors via tokenize(512) → onnxruntime → attention-mask mean-pool → L2-normalize. `embedding_service.load_model()` SHALL return a process-wide single onnxruntime `InferenceSession` held at module level inside `embedding_service.py` (streamlit-import-free) — never per-thread/per-session loads, because Streamlit runs one script thread per user session and per-user session model loads multiply resident memory against the 1 GiB Streamlit Cloud envelope. N concurrent `load_model()` calls SHALL be race-safe under a single one-at-a-time in-flight lock (the same idiom the admin backfill requires); concurrent session `Run()` calls from multiple user threads are thread-safe (verified: 8 threads, deterministic outputs, no divergence). Worst-case resident-set profile evidence SHALL be recorded as measured references — gte-small INT8 ~128 MB, e5-small INT8 ~472 MB, both-models-resident ~520 MB (measured 2026-09-29, this machine) — all under the 1 GiB envelope; the 1 GiB envelope SC (SC-10) is unchanged.

R-3. The database schema SHALL add `embedding vector(384)`, `entry_type`, `embedding_model` to `gloss_search_entries` and a new `semantic_search_entries` table, additive-only, with existing rows and columns untouched.

R-4. Schema changes SHALL ship as DDL-only versioned migrations appended to the registry (no data writes, no renumbering, no startup backfill), with a pgvector availability assertion and reversible DDL drop statements documented.

R-5. The system SHALL expose `search_semantic(mode, query, threshold=None, source_id=None, limit=None) → SemanticSearchResult` per the v1 seam contract: full ranked list desc cosine score with record_id-asc tie-break, default threshold 0.80, NULL/stale rows excluded via the `embedding_model == pin` join, no streamlit imports.

R-6. Calibration anchors SHALL hold on freshly synced real data — positive query floors (round/bed/house/peas/hunt) 0.85-0.90, negatives ≥0.07 below positives — and a material distribution shift SHALL trigger re-baseline via the owned calibration procedure rather than silent threshold changes.

R-7. Semantic search SHALL degrade safely: `empty_query`, `no_embeddings`, `stale_model`, and zero-below-threshold states return the designated status+message payloads without exceptions; degraded-state messages name the admin backfill remedy.

R-8. The upload pipeline SHALL embed new primary `ge` rows inline inside `populate_search_entries()` with the signature unchanged, embedding_model set to the pin, write batches ≤ 512, and exact Unicode preservation.

R-9. An admin-role Embedding Backfill control in Table Maintenance → Data Reprocessing SHALL re-embed all records with progress reporting (`st.progress`, callback, `st.status`), reuse the :128-130 role gate, and support model-change recompute (pin change → stale rows re-embedded).

R-10. Runtime dependencies SHALL add `onnxruntime` and `tokenizers`; `sentence-transformers` SHALL remain dev-only; the batch-64 runtime profile SHALL fit the 1 GiB Streamlit Cloud memory envelope, with the worst-case resident-set profile (model load + batch-64 encode; R-2 measured references: ~128 MB gte-small INT8, ~472 MB e5-small INT8, ~520 MB both-models-resident) recorded as evidence against the envelope.

R-11. Every embedding upsert SHALL be batched ≤ 512 rows and every embed failure SHALL raise contextually (fail-fast) with no silent skip.

R-12. The regression database SHALL be re-synced from production (`scripts/sync_prod_to_local.sh` from the branch under test) immediately before every SC test cycle; sync replication SHALL carry embeddings so local DBs never re-embed.

R-13. The `SearchMode` Literal type (`linguistic_service.py:28`) SHALL widen additively to include `'Semantic Gloss'` and `'Semantic All'`, and the mode dispatch entries (`search_records` at :391 and the `_search_strategies` map at :79) SHALL route those two modes to `search_semantic()`; existing Lexeme/FTS/Headword/Gloss strategies, the `search_records` signature, and the `RecordSearchResult` return type SHALL remain unchanged. Mode captions, labels, threshold preference, pagination, and result rendering remain #1385 surface.

R-14. `load_model()` SHALL return a process-wide single `onnxruntime.InferenceSession` held at module level inside `embedding_service.py` (streamlit-import-free) — never per-thread/per-session loads, because Streamlit runs one script thread per user session and per-user session model loads multiply resident memory against the 1 GiB Streamlit Cloud envelope. N concurrent `load_model()` calls SHALL be race-safe under a single one-at-a-time in-flight lock (the same idiom the admin backfill requires); concurrent session `Run()` calls from multiple user threads are thread-safe (verified: 8 threads, deterministic outputs, no divergence). Worst-case resident-set profile evidence SHALL be recorded as measured references — gte-small INT8 ~128 MB, e5-small INT8 ~472 MB, both-models-resident ~520 MB (measured 2026-09-29, this machine) — all under the 1 GiB envelope; the 1 GiB envelope SC (SC-10) is unchanged.

## Items

### Item 1 (SC-1): Committed model artifacts with SHA-pinned integrity
- RED: CI hash check script fails on absent/mismatched `models/gte-small/` artifacts
- GREEN: commit ONNX (34,118,638 B; SHA256 c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd) + tokenizer.json (711,661 B)
- verify: hash check exit 0 vs recorded pins
- commit: models/ artifacts + hash check

### Item 2 (SC-2): embedding_service encode/load invariants
- RED: pytest asserting encode() missing → fails
- GREEN: `src/services/embedding_service.py`: encode() per R-2 invariants (vector shape, unit norm, batch-64 padding path); errors raised with context
- verify: pytest unit — shape (1,384), norm 1.0, batch-64 padding
- commit: embedding service encode + test

### Item 3 (SC-3): pgvector schema additions
- RED: introspection asserting columns/table absent → fails
- GREEN: `models/search.py`: GlossSearchEntry +3 columns; new SemanticSearchEntry model + SemanticSearchResult dataclass; additive-only
- verify: schema introspection on synced DB
- commit: models/search.py

### Item 4 (SC-4): DDL-only versioned migrations + extversion assert
- RED: migration test asserting missing version rows/objects → fails
- GREEN: append 2 registry entries (YYYYMMDDSSSSS) creating table + columns; pgvector assert; reversible drops documented
- verify: isolated migration test (#1346 pattern): applied once, idempotent on rerun
- commit: migrations.py

### Item 5 (SC-5): search_semantic seam per contract
- RED: pytest asserting seam absent/incorrect statuses → fails
- GREEN: `src/services/semantic_search_service.py`: encode query → cosine rank over both tables (pin join) → threshold → full ranked list, tie-break record_id asc
- verify: pytest service-layer vs freshly synced DB; contract field list exact
- commit: semantic search service

### Item 6 (SC-6): Calibration anchor floors
- RED: calibration pytest asserting seam against unimplemented floors → fails
- GREEN: calibration module asserting recorded anchors on freshly synced data; per-anchor evidence artifact
- verify: pytest produces calibration evidence with per-anchor scores
- commit: calibration test + evidence

### Item 7 (SC-7): Degraded status semantics
- RED: pytest asserting exceptions on edge inputs → fails
- GREEN: guard empty/whitespace before model invocation; pin-join exclusions; statuses + messages per seam enum
- verify: pytest edge matrix — every input yields correct status, never an exception
- commit: service edge handling

### Item 8 (SC-8): Upload-path inline embedding
- RED: extend test_upload_search_entries asserting no embeddings produced → fails
- GREEN: populate_search_entries() embeds new primary ge rows inline (signature unchanged)
- verify: extended test on real synced records — embeddings, pin, Unicode fidelity, batch ≤ 512
- commit: upload service + test

### Item 9 (SC-9): Admin Embedding Backfill button
- RED: Playwright asserting no backfill control exists → fails
- GREEN: sibling section beside render_data_reprocessing_maintenance(); backfill service method with st.progress+callback+st.status idiom
- verify: Playwright click-through (role-gated; isolated from #1347)
- commit: table_maintenance.py + backfill method

### Item 10 (SC-10): Dependency + memory envelope
- RED: manifest check asserting onnxruntime/tokenizers absent from runtime deps → fails; profiler absent → fails
- GREEN: pyproject.toml deps correction (sentence-transformers already dev-only — verified live at :32; ADD onnxruntime+tokenizers to `dependencies`); profiler evidence artifact
- verify: manifest check + batch-64 RSS measurement vs 1 GiB envelope
- commit: pyproject.toml + evidence

### Item 11 (SC-11): Additive SearchMode widening + semantic dispatch entry
- RED: pytest asserting 'Semantic Gloss'/'Semantic All' absent from SearchMode Literal and unmatched by dispatch → fails
- GREEN: `src/services/linguistic_service.py`: widen SearchMode Literal with 'Semantic Gloss'/'Semantic All'; add dispatch entries routing both modes to search_semantic(); do not alter existing strategies or search_records signature — primary deliverable is the Literal+dispatch seam; the companion contract obligations stated in SC-11 (existing modes unchanged, no signature/return-type change) are part of this same item's GREEN verification
- verify: pytest asserting widened Literal + new dispatch entries; existing four modes route unchanged; search_semantic() invoked for both new modes
- commit: linguistic_service.py widening + test

### Item 12 (SC-12): Load-once process-wide session singleton
- RED: pytest asserting load_model() absent or returns distinct sessions across calls → fails
- GREEN: `src/services/embedding_service.py`: load_model() returns a process-wide singleton onnxruntime session (module-level holder, streamlit-import-free) with a single one-at-a-time in-flight lock around (re)loads — never per-thread/per-session loads — as the item's primary deliverable; the encoding pipeline obligations carried by Item 2 (encode invariants exercised against the singleton session) are part of this same item's GREEN verification
- verify: pytest concurrency — N threads load_model() → identical session handle, registry count == 1; profiler artifact — measured worst-case resident-set (model load + batch-64 encode) vs R-14 references and 1 GiB envelope
- commit: embedding service load_model() singleton

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #400 (closed, merged) | provides GlossSearchEntry + populate_search_entries() pipeline this spec extends | satisfied |
| pgvector>=0.3.6 (runtime, pyproject:13) + _ensure_extensions (connection.py:525-537, verified live) | extension availability precondition for vector columns | satisfied |
| `migrations.py` YYYYMMDDSSSSS directive (:67-72) | registry format + append-only mandate for the 2 new migrations | satisfied |
| Table Maintenance Data Reprocessing idiom (:169-196) + role gate (:128-130) | template + gate for the admin backfill button | satisfied |
| Local PostgreSQL sync protocol (AGENTS.md mandate; 2026-07-16 lessons) | fresh production replica before every test cycle | satisfied (procedure) |
| UI follow-up spec #1385 (https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1385) | consumes the seam this spec delivers; dependency_contract in interface-compat.yaml | pending (filed, waiting on this spec) |

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1 | 1 (substrate) |
| R-2 | SC-2 | 2 (substrate) |
| R-3 | SC-3 | 2 (substrate) |
| R-4 | SC-4 | 3 (substrate) |
| R-5 | SC-5 | 4 (services) |
| R-6 | SC-6 | 5 (services) |
| R-7 | SC-7 | 5 (services) |
| R-8 | SC-8 | 6 (services) |
| R-9 | SC-9 | 7 (admin UI) |
| R-10 | SC-10 | 8 (envelope) |
| R-11 | SC-8, SC-9 | 6-7 |
| R-12 | SC-5, SC-6, SC-9 | 4-8 |
| R-13 | SC-11 | 4 (services) |
| R-14 | SC-12 | 2 (substrate) |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| SearchMode Literal + search_records entry | code | `src/services/linguistic_service.py:28,:391` | live `rg` read 2026-09-28 |
| GlossSearchEntry columns (4 only) + RESTRICT FK | code | `src/database/models/search.py:63-78` | live `sed` read 2026-09-28 |
| Migration registry + YYYYMMDDSSSSS directive | code | `src/database/migrations.py:60-72` | live `sed` read 2026-09-28 |
| populate_search_entries signature | code | `src/services/upload_service.py:1758` (`populate_search_entries()` def line — stable anchor; line numbers verify live) | live `sed` read 2026-09-28; re-verified :1758 2026-09-29 |
| SearchMode widening + dispatch entries for SC-11 | code | `src/services/linguistic_service.py:28` (SearchMode Literal) + `:79-84` (`_search_strategies` dict) | live `rg` read 2026-09-28; re-verified 2026-09-29 |
| PreferenceService get/set_preference | code | `src/services/preference_service.py:17,:37` | live `sed` read 2026-09-28 |
| pgvector ensure-extensions | code | `src/database/connection.py:525-537` | live `sed` read 2026-09-28 |
| Role gate + Data Reprocessing idiom | code | `src/frontend/pages/table_maintenance.py:125-130,:169-196` | live `sed` read 2026-09-28 |
| pyproject dependency groups | config | `pyproject.toml:7-19,:28-34` (sentence-transformers dev, line 32) | live `rg` read 2026-09-28 |
| Model + artifact pins, calibration, latency/memory measurements | analysis artifact | `handoff.yaml` (measured 2026-09-28) | spike session artifact; archived under `tmp/issue-36/` (not committed) — read from archive this session; NOT durable evidence |
| Original #36 body (pre-revision) | issue | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36 | fetched via `gh issue view` 2026-09-28 |
| Lessons learned (FTS/normalization boundaries) | docs | `docs/lessons-learned/2026-06-13-*.md` | AGENTS.md table; FTS paths unchanged by this spec |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Hash check costs seconds. Skipping means a corrupted or silently substituted model artifact ships → every embedding in the DB is wrong or irreproducible — weeks of calibration drift diagnosed downstream.
- **SC-2:** Vector unit test costs minutes. Skipping means malformed/denormalized vectors silently poison every cosine ranking (discovered only through user-visible nonsense results, 100× escalation).
- **SC-3:** Schema introspection costs minutes. Skipping means a schema/model mismatch breaks every semantic query at runtime — production failure (1000×).
- **SC-4:** Isolated migration test costs minutes. Skipping means a non-idempotent or wrongly-versioned migration bricks startup for every environment simultaneously.
- **SC-5:** Seam pytest costs minutes. Skipping means the contract the whole UI spec binds to is wrong → cross-spec rework (compound escalation).
- **SC-6:** Calibration run costs minutes against real synced data. Skipping means an uncalibrated threshold ships and linguists tune blind — correctness of the feature itself is unverifiable.
- **SC-7:** Edge pytest costs minutes. Skipping means production support tickets for every missing-embedding state — highest-frequency failure surface (1000×).
- **SC-8:** Extended upload test costs minutes. Skipping means silently unsearchable new records — data-integrity defect discovered only by absence of results.
- **SC-9:** Playwright click-through costs minutes. Skipping means a broken admin tool is discovered during the first real backfill attempt, under operational pressure.
- **SC-10:** Manifest+profile check costs minutes. Skipping means a dependency/memory envelope breach surfaces as a Streamlit Cloud runtime crash in production.
- **SC-11:** Dispatch pytest costs minutes. Skipping means 'Semantic Gloss'/'Semantic All' modes exist in the type but are unreachable (or route to a wrong strategy) — the seam #1385 binds to is silently dead; a dispatch regression in an existing mode breaks search for every user.
- **SC-12:** Concurrency test costs minutes. Skipping means a per-session model load multiplies ~128 MB of resident memory per concurrent user — an OOM crash of the app container under modest real-user concurrency that the singleton + concurrency test would have caught pre-deploy.

## Edge Cases

| Condition | Expected Behavior | Resolution |
|-----------|-------------------|------------|
| Empty database (no gloss rows) | Semantic search returns empty result set with status `no_embeddings` — not an error | SC-7 |
| Model file missing from repo | Startup/load fails with a clear error identifying the missing path | SC-1 hash check + load error |
| pgvector extension unavailable | Migration-time assertion error naming the missing extension | SC-4 extversion assert |
| Gloss text exceeds model token limit (512) | Text truncated to model max token length before embedding; warning logged | SC-2 (tokenizer truncation) |
| Non-ASCII / Unicode gloss text | Handled natively by the BERT tokenizer; Unicode preserved exactly — no normalization layers added | SC-8 (ingestion fidelity) |
| Empty gloss string | No embedding generated; entry excluded from vector search (NULL-safe) | SC-3, SC-7 |
| All results below similarity threshold | `ok` status with empty results — not an error | SC-7 |
| Existing records without embeddings | Excluded from search until admin backfill runs (stale/never-embedded treated identically) | SC-7 (query exclusion) + SC-9 (remedy) |
| N concurrent user sessions (per-thread script execution) | All user threads share one process-wide model session; concurrent `load_model()` race-safe under the in-flight lock (registry count == 1); concurrent `Run()` thread-safe | SC-12 (concurrency) |
| New mode selected in backend before UI modes exist (#1385 pending) | 'Semantic Gloss'/'Semantic All' route to `search_semantic()` with no UI wiring; existing modes unaffected | SC-11 |
| Model pin changes (future) | Rows with old pin excluded; re-running admin backfill recomputes | R-9 + SC-7 |
| Partial backfill failure | Error surfaced via handle_ui_error idiom; stale rows remain excluded at query (self-healing) | SC-9 |
| Malformed/whitespace-only query | Status `empty_query` before any model invocation — never an exception | SC-7 (REQ-I2) |
| Concurrent upload during backfill | Batch ≤ 512 upserts; per-row pin stamping; no partial-state rows become searchable | R-11, SC-8 |
| Batch near 65,535 parameter cap | Write batches ≤ 512 rows | R-11 (090 guideline) |

## Change Control

| Date | Revision | Reason | Authorized By |
|------|----------|--------|---------------|
| 2026-09-29 | OOM-safety amendment: Item 2 / SC-2 "cached ONNX session" amended to a load-once process-wide singleton contract (module-level holder in `embedding_service.py`, streamlit-import-free); behavioral concurrency assertion added to SC-2 (N concurrent `load_model()` calls → identical session handle, registry count == 1); R-2 extended with load/cache/lock semantics and worst-case resident-set measured references (gte-small INT8 ~128 MB, e5-small INT8 ~472 MB, both-models-resident ~520 MB — measured 2026-09-29, same-session evidence); R-10 updated to record the resident-set profile as evidence (1 GiB envelope assertion unchanged); concurrent-sessions row added to Edge Cases; Cost Frame SC-2 entry updated; Alternatives list gains the per-user-session-loads rejection. NO SCs/Requirements/Items renumbered; two-table design, #1385 boundary, gloss-space scope, model pins, and schema untouched. | Multi-user OOM risk: Streamlit runs one script thread per user session; per-session model loads multiply the pinned gte-small INT8 resident weight (~128 MB) per concurrent user against the 1 GiB Streamlit Cloud envelope (escalates toward ~470–630 MB per user only if a larger model were ever pinned, which this spec does not). Concurrency thread-safety of concurrent session `Run()` empirically verified this session (8 threads, deterministic outputs, no divergence). | Developer directive (2026-09-29, OOM-safety amendment authorization) |
| 2026-09-29 | Validation revision (tier-1 iteration 1, 3 findings). Finding D2: Change Control narrative figure corrected to the pinned gte-small INT8 ~128 MB (was ~470–630 MB), with a single clause noting size-dependent escalation only for hypothetical larger models — normative chain (R-2/SC-2, now SC-12, and SC-10) unchanged and self-consistent. Finding D3: added SC-11 + Item 11 + R-13 covering the additive `SearchMode` Literal widening ('Semantic Gloss'/'Semantic All' at `linguistic_service.py:28`) and dispatch entries routing to `search_semantic()` — the seam the analytical artifacts (code-path-inventory P1, interface-compat EXTENDING SearchMode, blast-radius) declare within #36 scope; mode captions/labels/threshold widgets/pagination remain #1385 (Not-Included bullet added). Documentation Sources gains the `linguistic_service.py:28,:79-84` anchor. Finding compound-SC (pre-amendment): SC-2 de-bundled — restored to the pre-OOM-amendment encode/load vector-invariant wording exactly (recovered from issues-data branch history); the singleton+concurrency claims were NOT removed (SC Lobotomy Prohibition) — they now live in NEW SC-12 + Item 12 + R-14; SC-9/SC-10 kept intact as single RED/GREEN cycles with their companion obligations explicitly stated as part of each item's GREEN. SCs 1–10 NOT renumbered; new SCs numbered SC-11 (SearchMode) / SC-12 (singleton) per the dual-new-SC assignment. | Spec-validation FAIL findings (compound-SC detection, D2 narrative contradiction, D3 completeness gap); SC↔Item mapping kept 1:1 | Spec-creation validate step (tier-1 iteration 1) |

| 2026-09-29 | Validation revision (tier-1 iteration 2, 2 hard FAILs + secondary + warnings). F1/BEH-EV uplift: SC-11 Evidence Type corrected structural → behavioral — dispatch routing of 'Semantic Gloss'/'Semantic All' to search_semantic() is runtime-behavioral substrate (auto-uplift); verification method already behavioral-grade (pytest dispatch routing), kept as-is; SC-11 evidence type updated in sc-summary.yaml. F2/completeness: full 64-hex tokenizer.json SHA256 (da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0, verified live from tmp/spike-gte/tokenizer.json, 711,661 B) recorded everywhere the truncated form appeared (Model pin Key Decision, SC-1 verification method); hash-check method now executable from the spec text alone. Secondary: SC-6 verification method + criterion clarified — per-anchor floor values MUST be recorded per-anchor in the SC-6 calibration evidence artifact (not a blanket floor); 0.85-0.90 retained as the recorded summary bound; thresholds unchanged. W3: '1 GB' normalized to '1 GiB' (3 occurrences, same envelope). W4: R-13 phase label corrected to '4 (services)' matching neighboring service-layer entries. W2/W1 artifact-text drift: state-analysis ONNX-session location updated to module-level holder per R-14 (drop @st.cache_resource wording); blast-radius sentence-transformers wording corrected to 'already dev-only (verified)' — artifacts re-created from spec-consumable sources. NO renumbering: SCs 1–12, Items 1–12, R-1–R-14 identities intact; gloss-space scope, model pins (commit + ONNX SHA), schema, #1385 boundary, OOM amendment untouched. | Spec-validation FAIL findings F1 (evidence_type_method) and F2 (completeness) from tier-1 iteration 2 validate step; secondary SC-6 recording clarification and zero-risk warning fixes (W1-W4) per revision_reason scope cap | Developer-authorized revision scope (revise dispatch, 2026-09-29) |

| 2026-09-29 | Validation revision (tier-1 iteration 3, 1 hard FAIL). F3/BEH-EV uplift: SC-4 Evidence Type corrected structural → behavioral — migration execution outcomes (apply-in-order, version-gated idempotency, rerun no-op) are runtime-behavioral substrate (auto-uplift per BEH-EV); verification method already behavioral-grade (isolated migration test: version rows advanced; objects created; rerun is no-op), kept unchanged; SC-4 evidence type updated in sc-summary.yaml. No other SC text changes; no renumbering (SCs 1–12, Items 1–12, R-1–R-14 identities intact); model pins, schema, #1385 boundary, OOM amendment, gloss-space scope untouched. | Spec-validation FAIL finding F3 (evidence_type_method) from tier-1 iteration 3 validate step | Developer-authorized revision scope (revise dispatch, 2026-09-29) |

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*