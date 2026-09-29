# Plan Input Verification Ledger — Issue #36

Written once (2026-09-29) per writing-plans create.md step 3a. All subsequent plan-composition
steps re-read THIS ledger, not the sources. Re-verification of ledger-covered facts is prohibited.

## Issue State

- issue: 36
- repo: snea-shoebox-editor (Brothertown-Language, github.com)
- issues_prefix: `.issues` (root repo)
- spec: `.issues/36/spec.md` (issues-data HEAD, revision tier-1 iteration 3, 2026-09-29)
- local issue.yaml labels (canonical): `approved-for-plan`
- status: open
- authorization: plan-creation scope active (approved-for-plan label); halt boundary = plan_created
- remote label surface: GitHub API available (gh auth verified by session context); remote
  `spec-cleared` write is best-effort, never blocking.

## CLI Surface Verified Live

- `./.opencode/tools/local-issues read-labels --number "snea-shoebox-editor#36"` → works
  (qualified `repo#N` form REQUIRED; bare `#N` raises ValueError)
- `./.opencode/tools/local-issues update --number "snea-shoebox-editor#36" --labels <...>`
  — NOTE: `--labels` REPLACES the entire labels array. Every label write must include all
  existing labels plus the new one. Current existing labels: `approved-for-plan`.
  Target end-state labels after spec-cleared write: `approved-for-plan spec-cleared`.
- issues-data worktree present and on branch `issues-data` (git -C .issues branch --show-current).

## SC List with Evidence Types (from spec.md + sc-summary.yaml — consistent)

| SC | Summary | Evidence Type | Phase (structure.yaml) |
|----|---------|---------------|------------------------|
| SC-1 | Committed models/gte-small/ ONNX (34,118,638 B, SHA256 c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd) + tokenizer.json (711,661 B, SHA256 da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0) match pins byte-for-byte | structural | 1 |
| SC-2 | encode(texts, batch≤64) → float32 (1,384) unit-norm via tokenize(512)→onnxruntime→mean-pool→L2-normalize | behavioral | 2 |
| SC-3 | gloss_search_entries +3 columns (embedding vector(384), entry_type, embedding_model); new semantic_search_entries (record_id FK CASCADE); existing untouched | structural | 3 |
| SC-4 | Two DDL-only versioned migrations apply in order, version-gated idempotent, append-only YYYYMMDDSSSSS registry, pgvector extversion assert | behavioral | 3 |
| SC-5 | search_semantic(mode 'gloss'|'all', query, threshold=None, source_id=None, limit=None) → SemanticSearchResult{results: list[(record_id, score)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message}; full ranked desc cosine, record_id-asc tie-break, None→0.80, pin-join exclusion; no streamlit imports | behavioral | 4 |
| SC-6 | Calibration anchors on freshly synced data: positives (round/bed/house/peas/hunt) ≥ per-anchor floors (0.85-0.90 summary band, per-anchor values recorded per-anchor in evidence artifact); negatives ≥0.07 below; default threshold 0.80 | behavioral | 5 |
| SC-7 | Degraded inputs → correct status+message, never exception: empty/whitespace→empty_query pre-model; no_embeddings; stale_model; ok+empty below-threshold; messages name admin backfill remedy | behavioral | 5 |
| SC-8 | populate_search_entries(record_ids, session=None) → int (signature unchanged) embeds new primary ge rows inline, pin-stamped, batch ≤512, Unicode exact | behavioral | 6 |
| SC-9 | Admin-role Embedding Backfill button in Table Maintenance → Data Reprocessing; st.progress + callback + st.status; handle_ui_error; non-admin rejected | behavioral | 6 |
| SC-10 | Runtime deps gain onnxruntime + tokenizers; sentence-transformers stays dev-only; batch-64 profile fits 1 GiB envelope (measured 312 MiB RSS; R-2 references ~128 MB gte-small INT8 / ~472 MB e5-small / ~520 MB both) | structural | 3 |
| SC-11 | Additive: SearchMode Literal widens 'Semantic Gloss'/'Semantic All' at linguistic_service.py:28; dispatch entries route both to search_semantic(); existing 4 strategies/signature/return-type unchanged | behavioral | 4 |
| SC-12 | load_model() → process-wide single onnxruntime InferenceSession (module-level holder, streamlit-import-free); N concurrent calls race-safe under one-at-a-time in-flight lock (registry count == 1) | behavioral | 2 |

12 SCs → 12 items (1:1, D1-ITEM-1..12). Traceability column spec: R-1..R-14 all covered.

## Structure Artifact Mapping (structure.yaml — authoritative for plan)

- phase_count: 6
- Phases (strict chain, DAG: 1→2→3→4→5→6; phase 4 depends_on [1,2,3]; phase 6 depends_on [2,3,4,5]):
  1. "Pinned model artifacts substrate" — SC-1 — files: models/gte-small/onnx/model_qint8_avx512_vnni.onnx, models/gte-small/tokenizer.json, scripts/ hash check
  2. "Embedding service substrate (encode + singleton)" — SC-2, SC-12 — files: src/services/embedding_service.py (new)
  3. "pgvector schema + DDL migrations + dependency manifest" — SC-3, SC-4, SC-10 — files: src/database/models/search.py, src/database/migrations.py, pyproject.toml, profiler evidence
  4. "Search semantic seam + mode dispatch" — SC-5, SC-11 — files: src/services/semantic_search_service.py (new), src/services/linguistic_service.py
  5. "Calibration + degraded semantics" — SC-6, SC-7 — files: calibration module + per-anchor evidence artifact (new), src/services/semantic_search_service.py (edge guards)
  6. "Data plane — upload inline embedding + admin backfill UI" — SC-8, SC-9 — files: src/services/upload_service.py, test/test_upload_search_entries.py, src/frontend/pages/table_maintenance.py
- verifications: triplet_colocation PASS (every SC RED/GREEN/COMMIT in same phase); cross_phase_dependency PASS (no backward edges).
- SC→phase: SC-1→P1; SC-2,SC-12→P2; SC-3,SC-4,SC-10→P3; SC-5,SC-11→P4; SC-6,SC-7→P5; SC-8,SC-9→P6. All 12 SCs covered exactly once.

## Per-Task Cycle Steps (implementation-workflow reference card — single authoritative source)

- Pre-implementation: pre-regression (test-driven-development, phase-0 task), pre-regression-verify (verification-before-completion, verify task)
- Per item: red (tdd) → green (tdd) → post-regression (tdd, phase-4 task) → verify (verification-before-completion) → commit-inline (orchestrator git add+commit, no dispatch)
- Post-implementation: audit (audit DiMo investigator → validator → evaluator → arbiter), z3-check (orchestrator .opencode/tools/solve check), structural-checks (finishing-a-development-branch checklist), pre-pr-gate (vbc verify — reads all SC verdicts, BLOCKs on FAIL), regression-check (tdd phase-4), review-prep (git-workflow-pr), create-pr (git-workflow-pr), exec-summary (completion-core)
- Dispatch strings recorded in structure.yaml skill_task_selection / preflight_steps / post_phase_steps (copy from there, not from memory)
- Coercion rules: DONE_WITH_CONCERNS→FAIL; EVIDENCE_TYPE_MISMATCH→FAIL
- Step pre-cleanup table (rm pipeline-<step>-* artifacts) mandatory per step label

## Phase File Section Sources (per-phase content already extracted from artifacts)

- Code Path Coverage: code-path-inventory.yaml P1..P9 (SC mapping per phase listed below)
- Cross-Cutting SCs: cross-cutting-matrix.yaml (SC-2, SC-5, SC-7, SC-8, SC-9, SC-12 spanning; SC-1/3/4/6/11 single-concern)
- Interface Boundaries: interface-compatibility.yaml (5 boundaries + dependency_contract)
- State Transitions: state-analysis.yaml (6 entities)
- Testability: testability-assessment.yaml (all HIGH except SC-9 MEDIUM; global_test_protocol: R-12 sync gate, no behavioral substitution, Unicode fidelity)
- Blast radius: blast-radius.yaml (MEDIUM risk; affected files list above matches structure.yaml)

## Per-phase artifact references (for phase file sections)

- Phase 1: paths P9 (hash script part); no cross-cutting; no interface boundary; no state entity
- Phase 2: paths P3; cross-cutting SC-2? no — SC-2/SC-12 both in CC list; interface: module import graph embedding_service (NEW_LEAF_MODULE); state: embedding model (process)
- Phase 3: paths P6, P8; single-concern SC-3/SC-4; interface: schema boundary (ADDITIVE_COLUMNS + NEW_TABLE); state: migration registry (SchemaVersion), dependency manifest
- Phase 4: paths P1, P2; CC: SC-5; interface: search_semantic() seam (NEW_ADDITIVE), SearchMode Literal (EXTEND_ONLY); state: none directly (query lifecycle rides P5/P7)
- Phase 5: paths P7, P9; CC: SC-7; interface: (seam contract frozen — cross_spec #1385); state: search query lifecycle
- Phase 6: paths P4, P5; CC: SC-8, SC-9; interface: populate_search_entries (PRESERVE_SIGNATURE); state: search entry row, admin backfill run

## Composition Decimals (pinned — plan-structure-standards.md §Composition Conventions)

- Frontmatter order: plan_schema_version, issue, title, authorization_scope, pr_strategy, phase_count, dispatch
- plan_schema_version: "1.0" (plan-artifact-format §3.1); structure says split-file multi-phase plan
  — but create.md task target is single plan.md; plan-artifact-format §2: multi-phase MUST use split
  format (plan.md + plan-NN-slug.md). → Use split format: plan.md index + 6 phase files
  plan-01..plan-06.
- Phase-table columns (pinned): Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch
- Step numbering continuous 1..N across all files
- Dispatch cell style: summary form like `direct (1-4) + task-card (5-14)`
- Issue reference line: `.issues/36/spec.md` with remote URL (platform is github.com — include URL)
- No fenced code blocks in body; no machine-parseable IDs; labels C1..Cn
- Lifecycle event: exactly one plan_created with plan_file + phase_count (handled by orchestrator post-plan)
- Authorization scope: for_implementation was granted earlier? — labels say approved-for-plan;
  authorization_scope frontmatter: for_plan (halt at plan_created); pr_strategy: none
  (per approval-gate scope table for_plan → none)