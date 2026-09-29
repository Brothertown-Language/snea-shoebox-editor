# [SPEC] Semantic Gloss Search with pgvector (db/embed revision)

> **Full spec and artifacts: [`https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/36/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/36/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/36/` — analytical artifacts, sc-summary, plan, audit findings

## Intent and Executive Summary

**Problem Statement:** English-gloss semantic search requires a committed embedding-model artifact, pgvector-backed schema, an embedding service, a UI-agnostic semantic search service, upload-path embedding, DDL migrations, and an admin backfill — none of which exist today (`GlossSearchEntry` has only id/record_id/term/normalized_term columns; verified live).

**Root Cause / Motivation:** The original #36 body predates the 2026-09-28 brainstorming spike: it pins the wrong model (all-MiniLM-L6-v2, ~22 MB) via sentence-transformers, implies a startup backfill, and predates the developer's split directive. This revision records the decided db/embed scope with measured, pinned values; the end-user interface is filed as its own spec (#1385).

**Approach Chosen:** Pin `thenlper/gte-small` via committed INT8 ONNX artifacts; add `vector(384)` columns/table via DDL-only versioned migrations (no startup backfill); implement `embedding_service` + `semantic_search_service` exposing the `search_semantic` seam; inline-embed during upload; expose admin backfill as a sibling button in Table Maintenance → Data Reprocessing; correct runtime dependencies.

**Alternatives Considered & Why Discarded:**
- *sentence-transformers as runtime dep (original body)* — rejected: measured in-process ONNX load+encode covers the need at ~35 MB runtime footprint; sentence-transformers adds PyTorch-class weight for zero runtime benefit and stays dev-only (corrected dependency direction).
- *Startup backfill migration* — rejected by developer directive: DDL-only migrations keep startup side-effect-free on Streamlit Cloud boot; backfill is an explicit admin action with progress reporting.
- *External embedding API* — rejected: offline-first reframed as in-process ONNX only; no third-party embedding API calls.

**Key Design Decisions:**
- **Model pin:** `thenlper/gte-small` @ 17e1f347d17fe144873b1201da9178889c639cd; committed `models/gte-small/onnx/model_qint8_avx512_vnni.onnx` (34,118,638 B, SHA256 `c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd`) + `models/gte-small/tokenizer.json` (711,661 B, SHA256 `da0e7993…62a0`). Tradeoff: +34.8 MB repo weight for byte-pinned reproducibility and offline determinism.
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
- **Replacement/removal of existing exact-match search modes** — Lexeme, FTS, Headword, Gloss untouched; SearchMode Literal widening is additive only.
- **Changes to MDF parser or data ingestion format** — `populate_search_entries()` is extended internally; signature unchanged.
- **Migration renumbering or rewriting** — append-only registry per in-file directive.
- **`preference_service.py` changes** — consumed as-is by #1385; no change here.

## Success Criteria

| ID | Criterion | Evidence Type | Documentation Sources | Verification Method |
|----|-----------|---------------|----------------------|---------------------|
| SC-1 | Committed artifacts at `models/gte-small/` (ONNX 34,118,638 B, tokenizer.json 711,661 B) match the recorded SHA256 pins byte-for-byte | structural | `handoff.yaml` pins (measured 2026-09-28); `blast-radius.yaml` | CI/script hash check vs recorded pins |
| SC-2 | `embedding_service.encode(texts, batch≤64)` returns float32 (1,384) unit-norm vectors via tokenize(512) → onnxruntime → attention-mask mean-pool → L2-normalize | behavioral | spike-executed session 2026-09-28; `decompose-output.yaml` D1-ITEM-2 | pytest unit: vector shape, norm=1.0, batch-64 padding path |
| SC-3 | Schema contains `gloss_search_entries` +3 new columns (`embedding vector(384)`, `entry_type`, `embedding_model`) and new `semantic_search_entries` table (id, record_id FK CASCADE, entry_type, term, embedding vector(384), embedding_model); existing columns untouched | structural | `models/search.py:63-78` + `state-analysis.yaml`; `interface-compat.yaml` v1 field list | schema introspection after migration on synced DB |
| SC-4 | Two DDL-only migrations (CREATE TABLE + ALTER TABLE ADD COLUMN) apply in order, version-gated idempotent, in the append-only `YYYYMMDDSSSSS` registry with a pgvector extversion assertion; no data writes, no renumbering | structural | `migrations.py:67-72` directive (verified live); #1346 flake isolation pattern | isolated migration test: version rows advanced; objects created; rerun is no-op |
| SC-5 | `search_semantic(mode: 'gloss'\|'all', query, threshold=None, source_id=None, limit=None) → SemanticSearchResult{results: list[(record_id, score)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message}` returns the full ranked list desc cosine with record_id-asc tie-break, threshold-filtered (None → 0.80), excluding NULL/stale rows via the pin join; service never imports streamlit | behavioral | `concern-map.yaml` seam contract; `interface-compat.yaml` dependency_contract | pytest service-layer vs freshly synced local DB |
| SC-6 | Calibration anchors on freshly synced real data: positives (round/bed/house/peas/hunt) score ≥ their 0.85-0.90 recorded floors; unrelated negatives score ≥0.07 below the positive floor; default threshold 0.80 | behavioral | `handoff.yaml` calibration (6,266 unique terms, measured 2026-09-28); REQ-E13 | pytest calibration module producing per-anchor evidence artifact; re-baseline procedure owns drift |
| SC-7 | Degraded inputs produce the correct status+message and never an exception: empty/whitespace query → `empty_query` before model invocation; no embedded rows → `no_embeddings`; pin mismatch rows → `stale_model`; all-below-threshold → `ok` with empty results; `stale_model`/`no_embeddings` message names the admin backfill remedy | behavioral | `state-analysis.yaml` state machine invariants; `decompose-output.yaml` D1-ITEM-7 | pytest edge-input matrix on service |
| SC-8 | `populate_search_entries(record_ids, session=None) → int` (signature unchanged) embeds the new primary `ge` rows inline during ingestion (1-5 strings/record, measured 10-60 ms/record) with `embedding_model` set to the pin; batch ≤ 512; Unicode preserved exactly | behavioral | `upload_service.py:1750-1751` (verified live); `test_upload_search_entries.py` | extend existing test with real synced records; assert embeddings + pin + Unicode fidelity |
| SC-9 | An admin-role Embedding Backfill button in Table Maintenance → Data Reprocessing re-embeds all records with `st.progress` + progress callback + `st.status`, surfacing completion results and errors via `handle_ui_error`; non-admin role is rejected | behavioral | `table_maintenance.py:125-130,:169-196` idiom (verified live); Role gate reused | Playwright click-through on synced DB; rate reference 6,266 terms/72.2 s |
| SC-10 | Runtime dependencies gain `onnxruntime` + `tokenizers`; `sentence-transformers>=3.0.0` remains in the dev group (already there — verified live); `model_qint8_avx512_vnni.onnx` load + batch-64 encode profile fits the 1 GB Streamlit Cloud envelope (measured 312 MiB RSS) | structural | `pyproject.toml:7-19,:28-34` (verified live 2026-09-28); profiler evidence | dependency manifest check + profiler evidence artifact |

## Requirements

R-1. The system SHALL commit the pinned gte-small INT8 ONNX artifact and tokenizer at `models/gte-small/` byte-identical to the recorded SHA256 pins.

R-2. The system SHALL provide `embedding_service.encode(texts: list[str], batch≤64) → float32 array` producing L2-normalized 384-dimension vectors via tokenize(512) → onnxruntime → attention-mask mean-pool → L2-normalize.

R-3. The database schema SHALL add `embedding vector(384)`, `entry_type`, `embedding_model` to `gloss_search_entries` and a new `semantic_search_entries` table, additive-only, with existing rows and columns untouched.

R-4. Schema changes SHALL ship as DDL-only versioned migrations appended to the registry (no data writes, no renumbering, no startup backfill), with a pgvector availability assertion and reversible DDL drop statements documented.

R-5. The system SHALL expose `search_semantic(mode, query, threshold=None, source_id=None, limit=None) → SemanticSearchResult` per the v1 seam contract: full ranked list desc cosine score with record_id-asc tie-break, default threshold 0.80, NULL/stale rows excluded via the `embedding_model == pin` join, no streamlit imports.

R-6. Calibration anchors SHALL hold on freshly synced real data — positive query floors (round/bed/house/peas/hunt) 0.85-0.90, negatives ≥0.07 below positives — and a material distribution shift SHALL trigger re-baseline via the owned calibration procedure rather than silent threshold changes.

R-7. Semantic search SHALL degrade safely: `empty_query`, `no_embeddings`, `stale_model`, and zero-below-threshold states return the designated status+message payloads without exceptions; degraded-state messages name the admin backfill remedy.

R-8. The upload pipeline SHALL embed new primary `ge` rows inline inside `populate_search_entries()` with the signature unchanged, embedding_model set to the pin, write batches ≤ 512, and exact Unicode preservation.

R-9. An admin-role Embedding Backfill control in Table Maintenance → Data Reprocessing SHALL re-embed all records with progress reporting (`st.progress`, callback, `st.status`), reuse the :128-130 role gate, and support model-change recompute (pin change → stale rows re-embedded).

R-10. Runtime dependencies SHALL add `onnxruntime` and `tokenizers`; `sentence-transformers` SHALL remain dev-only; the batch-64 runtime profile SHALL fit the 1 GB Streamlit Cloud memory envelope.

R-11. Every embedding upsert SHALL be batched ≤ 512 rows and every embed failure SHALL raise contextually (fail-fast) with no silent skip.

R-12. The regression database SHALL be re-synced from production (`scripts/sync_prod_to_local.sh` from the branch under test) immediately before every SC test cycle; sync replication SHALL carry embeddings so local DBs never re-embed.

## Items

### Item 1 (SC-1): Committed model artifacts with SHA-pinned integrity
- RED: CI hash check script fails on absent/mismatched `models/gte-small/` artifacts
- GREEN: commit ONNX (34,118,638 B; SHA256 c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd) + tokenizer.json (711,661 B)
- verify: hash check exit 0 vs recorded pins
- commit: models/ artifacts + hash check

### Item 2 (SC-2): embedding_service encode/load
- RED: pytest asserting encode() missing → fails
- GREEN: `src/services/embedding_service.py`: load_model() cached ONNX session; encode() per R-2 invariants; errors raised with context
- verify: pytest unit — shape (1,384), norm 1.0, batch-64 padding
- commit: embedding service

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
- verify: manifest check + batch-64 RSS measurement vs 1 GB envelope
- commit: pyproject.toml + evidence

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

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| SearchMode Literal + search_records entry | code | `src/services/linguistic_service.py:28,:391` | live `rg` read 2026-09-28 |
| GlossSearchEntry columns (4 only) + RESTRICT FK | code | `src/database/models/search.py:63-78` | live `sed` read 2026-09-28 |
| Migration registry + YYYYMMDDSSSSS directive | code | `src/database/migrations.py:60-72` | live `sed` read 2026-09-28 |
| populate_search_entries signature | code | `src/services/upload_service.py:1750-1751` | live `sed` read 2026-09-28 |
| PreferenceService get/set_preference | code | `src/services/preference_service.py:17,:37` | live `sed` read 2026-09-28 |
| pgvector ensure-extensions | code | `src/database/connection.py:525-537` | live `sed` read 2026-09-28 |
| Role gate + Data Reprocessing idiom | code | `src/frontend/pages/table_maintenance.py:125-130,:169-196` | live `sed` read 2026-09-28 |
| pyproject dependency groups | config | `pyproject.toml:7-19,:28-34` (sentence-transformers dev, line 32) | live `rg` read 2026-09-28 |
| Model + artifact pins, calibration, latency/memory measurements | analysis artifact | `handoff.yaml` (measured 2026-09-28) | read this session |
| Original #36 body (pre-revision) | issue | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36 | fetched via `gh issue view` 2026-09-28 |
| Lessons learned (FTS/normalization boundaries) | docs | `docs/lessons-learned/2026-06-13-*.md` | AGENTS.md table; FTS paths unchanged by this spec |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Hash check costs seconds. Skipping means a corrupted or silently substituted model artifact ships → every embedding in the DB is wrong or irreproducible — weeks of calibration drift diagnosed downstream.
- **SC-2:** Vector unit test costs minutes. Skipping means malformed/denormalized vectors silently poison every cosine ranking, discovered only through user-visible nonsense results (100× escalation).
- **SC-3:** Schema introspection costs minutes. Skipping means a schema/model mismatch breaks every semantic query at runtime — production failure (1000×).
- **SC-4:** Isolated migration test costs minutes. Skipping means a non-idempotent or wrongly-versioned migration bricks startup for every environment simultaneously.
- **SC-5:** Seam pytest costs minutes. Skipping means the contract the whole UI spec binds to is wrong → cross-spec rework (compound escalation).
- **SC-6:** Calibration run costs minutes against real synced data. Skipping means an uncalibrated threshold ships and linguists tune blind — correctness of the feature itself is unverifiable.
- **SC-7:** Edge pytest costs minutes. Skipping means production support tickets for every missing-embedding state — highest-frequency failure surface (1000×).
- **SC-8:** Extended upload test costs minutes. Skipping means silently unsearchable new records — data-integrity defect discovered only by absence of results.
- **SC-9:** Playwright click-through costs minutes. Skipping means a broken admin tool is discovered during the first real backfill attempt, under operational pressure.
- **SC-10:** Manifest+profile check costs minutes. Skipping means a dependency/memory envelope breach surfaces as a Streamlit Cloud runtime crash in production.

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
| Model pin changes (future) | Rows with old pin excluded; re-running admin backfill recomputes | R-9 + SC-7 |
| Partial backfill failure | Error surfaced via handle_ui_error idiom; stale rows remain excluded at query (self-healing) | SC-9 |
| Malformed/whitespace-only query | Status `empty_query` before any model invocation — never an exception | SC-7 (REQ-I2) |
| Concurrent upload during backfill | Batch ≤ 512 upserts; per-row pin stamping; no partial-state rows become searchable | R-11, SC-8 |
| Batch near 65,535 parameter cap | Write batches ≤ 512 rows | R-11 (090 guideline) |

---

*Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)*