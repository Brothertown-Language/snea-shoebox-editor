---
plan_schema_version: "1.0"
issue: 36
title: "Semantic Gloss Search with pgvector (db/embed revision) — pinned gte-small ONNX substrate, embedding service singleton, pgvector two-table schema, search_semantic seam, upload inline embedding, admin backfill"
authorization_scope: for_plan
pr_strategy: none
phase_count: 6
dispatch:
  - "test-driven-development --task pre-regression (pre-implementation)"
  - "verification-before-completion --task verify (pre-regression-verify + per-item verify + pre-pr-gate)"
  - "test-driven-development --task red (per item)"
  - "test-driven-development --task green (per item)"
  - "test-driven-development --task post-regression (per item + final regression-check)"
  - "finishing-a-development-branch --task checklist (structural-checks)"
  - "audit --task verification-audit DiMo investigator chain → validator → evaluator → arbiter"
  - "git-workflow-pr --task review-prep"
  - "git-workflow-pr --task create"
  - "completion-core --task completion (exec-summary)"
---

# Implementation Plan — [#36](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/36) — Semantic Gloss Search with pgvector (db/embed revision)

## Pre-Flight Guard (Mandatory)

Check your tool list for a tool named `task`.

- Present ⇒ orchestrator — proceed.
- Absent ⇒ sub-agent — do NOT execute any instruction below. Return `BLOCKED` with `ORCHESTRATOR_ONLY_SKILL_CARD` (cards) or `ORCHESTRATOR_ONLY_PLAN` (plans) and halt.

- **Issue:** `.issues/36/spec.md` (https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/36/)
- **Goal:** Deliver semantic search over English glosses — byte-pinned gte-small INT8 ONNX artifacts, a load-once embedding service whose process-wide session singleton keeps multi-user memory flat, an additive two-table pgvector schema built by DDL-only migrations, a UI-agnostic `search_semantic()` seam backend-reachable through additive SearchMode widening, inline upload-path embedding, and a role-gated admin Embedding Backfill — with all 12 success criteria passing on fresh production-synced data.
- **Architecture:** Six strictly sequential phases following the concern chain substrate → schema → services → calibration → data plane. The embedding model ships as git-committed byte-exact binaries verified by SHA256 hash check; it runs in-process via onnxruntime behind a process-wide load-once session singleton (module-level holder in `embedding_service.py`, streamlit-import-free, one-at-a-time in-flight lock) because Streamlit runs one script thread per user session. pgvector `vector(384)` storage spans two additive tables (`gloss_search_entries` gains 3 columns; new `semantic_search_entries` table) created by append-only versioned migrations with a pgvector extversion assertion and no startup backfill. Rows are searchable only when `embedding_model` matches the committed pin — NULL/stale rows degrade to safe statuses, never errors. The `SearchMode` Literal widening and its two dispatch entries are additive-only (the seam #1385 binds to); the sole `st.*` surface in this spec is the admin backfill section in `table_maintenance.py`.
- **Files:**
  - `models/gte-small/` (new committed bytes: ONNX + tokenizer.json)
  - `scripts/` (artifact hash check)
  - `src/services/` (new `embedding_service.py`, new `semantic_search_service.py`; edit `linguistic_service.py`, `upload_service.py`; calibration module)
  - `src/database/` (edit `models/search.py`, `migrations.py`)
  - `src/frontend/pages/` (edit `table_maintenance.py`)
  - `test/` (edit `test_upload_search_entries.py`; new embed/seam/calibration/migration tests)
  - `pyproject.toml` (runtime deps gain `onnxruntime` + `tokenizers`)
- **Dispatch:** red/green/post-regression via `test-driven-development`; verify via `verification-before-completion`; audit via `audit`; structural checks via `finishing-a-development-branch`; PR gates via `git-workflow-pr`; summary via `completion-core`; commits and Z3 check run orchestrator-direct.

## Blast Radius

| Phase | Affected Components | Impact | Risk |
|-------|-------------------|--------|------|
| 1 | `models/gte-small/` (new bytes), `scripts/` hash check | New committed artifacts; verification script | Low |
| 2 | `src/services/embedding_service.py` (new) | New leaf module, no streamlit import | Low |
| 3 | `src/database/models/search.py`, `src/database/migrations.py`, `pyproject.toml` | Additive columns + new table; 2 appended migrations; runtime deps | Medium |
| 4 | `src/services/semantic_search_service.py` (new), `src/services/linguistic_service.py` | New seam; additive Literal widening + dispatch entries | Medium |
| 5 | calibration module, `src/services/semantic_search_service.py` | Anchor floors evidence; edge guards | Medium |
| 6 | `src/services/upload_service.py`, `test/test_upload_search_entries.py`, `src/frontend/pages/table_maintenance.py` | Inline embedding internals (signature unchanged); sibling admin section | Medium |

Overall risk: MEDIUM — additive changes dominate; the only shared-surface edits (`linguistic_service.py` Literal+dispatch, `upload_service.py` internals) are constrained to additive/extension-only by R-13/R-8.

Untouched by directive: Lexeme/FTS/Headword/Gloss strategies, `search_records` signature, `RecordSearchResult` return type, `preference_service.py`, MDF parser, migration registry numbering (append-only), live `gloss_search_entries` RESTRICT FK policy.

> **Compliance:** All SCs must pass before completion. Partial implementation is not permitted. Each item is daisy-chained — item N's commit is precondition for item N+1's RED.

> **One step at a time.** Execute exactly one step. Report progress. Wait for instruction before the next step.

> **Step status:** Report `[item N] [PASS|FAIL]` after each step. If FAIL, report blocker and halt.

> **Enforcement gate:** All SCs must pass before this plan is complete.

## Phase Table

| Phase | Name | Concern | SCs | Depends On | Step Range | Dispatch |
|-------|------|---------|-----|------------|------------|----------|
| 1 | Pinned model artifacts substrate | Commit byte-pinned gte-small INT8 ONNX + tokenizer.json with SHA256 hash check | SC-1 | — | 5-9 | task-card (5-8) + direct (9) |
| 2 | Embedding service substrate (encode + singleton) | embedding_service encode pipeline + load-once process-wide session singleton | SC-2, SC-12 | 1 | 10-19 | task-card (10-18) + direct (19) |
| 3 | pgvector schema + DDL migrations + dependency manifest | Additive two-table schema models, DDL-only versioned migrations, dependency manifest + memory envelope | SC-3, SC-4, SC-10 | 2 | 20-34 | task-card (20-33) + direct (34) |
| 4 | Search semantic seam + mode dispatch | search_semantic() v1 contract service + additive SearchMode widening and dispatch entries | SC-5, SC-11 | 1, 2, 3 | 35-44 | task-card (35-43) + direct (44) |
| 5 | Calibration + degraded semantics | Calibration anchor floors on freshly synced data + degraded status edge semantics | SC-6, SC-7 | 4 | 45-54 | task-card (45-53) + direct (54) |
| 6 | Data plane — upload inline embedding + admin backfill UI | Inline embedding inside populate_search_entries() + admin Embedding Backfill in Table Maintenance | SC-8, SC-9 | 2, 3, 4, 5 | 55-64 | task-card (55-63) + direct (64) |
| Post | Verification, audit, review, PR | Final gates after all phases | SC-1..SC-12 | 1-6 | 65-72 | task-card (65, 67-72) + direct (66) |

## SC Coverage

Every SC maps to exactly one implementing item and one phase; per-item RED/GREEN/post-regression/verify/commit-inline cycles are enumerated inside each phase file.

| SC | Evidence Type | Item | Phase |
|----|--------------|------|-------|
| SC-1 | structural | Item 1 | 1 |
| SC-2 | behavioral | Item 2 | 2 |
| SC-12 | behavioral | Item 12 | 2 |
| SC-3 | structural | Item 3 | 3 |
| SC-4 | behavioral | Item 4 | 3 |
| SC-10 | structural | Item 10 | 3 |
| SC-5 | behavioral | Item 5 | 4 |
| SC-11 | behavioral | Item 11 | 4 |
| SC-6 | behavioral | Item 6 | 5 |
| SC-7 | behavioral | Item 7 | 5 |
| SC-8 | behavioral | Item 8 | 6 |
| SC-9 | behavioral | Item 9 | 6 |

## Pre-Implementation Steps

- [ ] 1. **Coherence gate (**direct**).** Re-read the spec enforcement gate, the 12 SC success criteria with evidence types, and this plan's phase DAG. Confirm spec revision state matches the sc-summary evidence types SC-4/SC-11 behavioral, SC-1/SC-3/SC-10 structural. Confirm no SC is uncovered and no item covers more than one SC.
  - Sub-bullet: blocking condition — any SC without a phase, any item covering multiple SCs, or any phase DAG cycle halts plan execution with a BLOCKED report.
- [ ] 2. **Baseline check (**direct**).** Verify the working tree is on the feature branch created from a trunk-tip parent with submodules synced, zero pending changes. Confirm `scripts/sync_prod_to_local.sh` exists and is executable.
  - Sub-bullet: R-12 gate — every SC test cycle in phases 3-6 begins immediately after a fresh `bash scripts/sync_prod_to_local.sh` run from the branch under test; sync replication carries embeddings so local DBs never re-embed.
- [ ] 3. **pre-regression (**task-card**).** Dispatch `test-driven-development` phase-0 task: run regression test patterns before any RED phase to capture the baseline failure set.
  - Sub-bullet: pre-clean previous-run artifacts first: `rm -f ./tmp/issue-36/artifacts/pipeline-pre-regression-*`.
- [ ] 4. **pre-regression-verify (**task-card**).** Dispatch `verification-before-completion` verify task to verify the pre-regression baseline results are recorded and consistent.
  - Sub-bullet: pre-clean first: `rm -f ./tmp/issue-36/artifacts/pipeline-pre-regression-verify-*`.

## Phase 1 — Pinned model artifacts substrate

(Phase file: `plan-01-pinned-model-artifacts.md` — steps 5-9)

## Phase 2 — Embedding service substrate (encode + singleton)

(Phase file: `plan-02-embedding-service.md` — steps 10-19)

## Phase 3 — pgvector schema + DDL migrations + dependency manifest

(Phase file: `plan-03-schema-migrations-manifest.md` — steps 20-34)

## Phase 4 — Search semantic seam + mode dispatch

(Phase file: `plan-04-semantic-seam-dispatch.md` — steps 35-44)

## Phase 5 — Calibration + degraded semantics

(Phase file: `plan-05-calibration-degraded.md` — steps 45-54)

## Phase 6 — Data plane — upload inline embedding + admin backfill UI

(Phase file: `plan-06-data-plane.md` — steps 55-64)

## Post-Implementation Steps (end of plan, after Phase 6)

- [ ] 65. **audit (**task-card**).** Dispatch the adversarial audit chain — `audit` verification-audit DiMo investigator first (read `audit/tasks/verification-audit-investigator.md` before dispatch), then validator, evaluator, arbiter in sequence — over the delivered artifacts against the 12 SCs.
  - Sub-bullet: pre-clean first: `rm -f ./tmp/issue-36/artifacts/pipeline-audit-*`.
- [ ] 66. **z3-check (**direct**).** Run `.opencode/tools/solve check --state-path ./tmp/issue-36/artifacts/state.yaml --contract-path ./tmp/issue-36/artifacts/contract.yaml` to verify phase ordering and state consistency.
  - Sub-bullet: pre-clean first: `rm -f ./tmp/issue-36/artifacts/pipeline-z3-check-*`; a solver failure reports BLOCKED with the inconsistent phase.
- [ ] 67. **structural-checks (**task-card**).** Dispatch `finishing-a-development-branch` checklist task — lint (`uvx ruff check src/ test/`), format check, typecheck (`uvx pyright src/`), targeted regression suites.
  - Sub-bullet: pre-clean first: `rm -f ./tmp/issue-36/artifacts/pipeline-structural-checks-*`.
- [ ] 68. **pre-pr-gate (**task-card**).** Dispatch `verification-before-completion` verify task reading all 12 SC verdicts; the gate BLOCKs PR creation if any SC verdict is FAIL, DONE_WITH_CONCERNS (coerced to FAIL per the workflow coercion rules), or EVIDENCE_TYPE_MISMATCH.
  - Sub-bullet: pre-clean first: `rm -f ./tmp/issue-36/artifacts/pipeline-pre-pr-gate-*`.
- [ ] 69. **regression-check (**task-card**).** Dispatch `test-driven-development` phase-4 task for the final regression sweep across all suites after the last GREEN.
  - Sub-bullet: pre-clean first: `rm -f ./tmp/issue-36/artifacts/pipeline-regression-check-*`.
- [ ] 70. **review-prep (**task-card**).** Dispatch `git-workflow-pr` review-prep task (read `git-workflow-pr/tasks/review-prep.md` first) with reviewer context for the stacked feature PR.
  - Sub-bullet: squash to exactly one commit per issue at PR creation per the stacked-PR mandate.
- [ ] 71. **create-pr (**task-card**).** Dispatch `git-workflow-pr` create task to open the stacked feature PR targeting the trunk.
  - Sub-bullet: PR body describes the deliverable without auto-closing keywords for stakeholder issues; byline per code-standards attribution rules.
- [ ] 72. **exec-summary (**task-card**).** Dispatch `completion-core` completion task to generate the completion executive summary.
  - Sub-bullet: report once after the full pipeline; HALT — PR merge is human-only.

> **Self-Remediation Protocol:** If a step FAILs: diagnose root cause, fix the deliverable, re-verify. If the fix requires spec revision, update the spec and re-enter the plan. Escalate only after remediation failure.

## Exit Criteria

- [ ] C1. SHA256 hash check exits 0 against the recorded ONNX and tokenizer.json pins, with both artifacts committed at `models/gte-small/` (SC-1)
- [ ] C2. `embedding_service.encode` returns float32 (1,384) unit-norm vectors through the tokenize(512) → onnxruntime → mean-pool → L2-normalize pipeline with the batch-64 padding path verified (SC-2)
- [ ] C3. `embedding_service.load_model` returns one process-wide `InferenceSession` under the one-at-a-time in-flight lock for N concurrent callers (SC-12)
- [ ] C4. Schema introspection on the synced DB shows `gloss_search_entries` +3 columns and the new `semantic_search_entries` table with existing columns untouched (SC-3)
- [ ] C5. The two DDL-only migrations apply in order, version rows advance, rerun is a no-op, and the pgvector extversion assertion is present in the append-only registry (SC-4)
- [ ] C6. `search_semantic` returns the full ranked list desc cosine with record_id-asc tie-break, None→0.80 threshold, pin-join exclusion, exact SemanticSearchResult field list, and no streamlit import (SC-5)
- [ ] C7. Calibration evidence artifact records per-anchor floors for round/bed/house/peas/hunt within the 0.85-0.90 summary band with negatives ≥0.07 below and default threshold 0.80 on freshly synced data (SC-6)
- [ ] C8. The degraded-input matrix yields empty_query/no_embeddings/stale_model/ok+empty statuses with backfill-remedy messages and zero exceptions (SC-7)
- [ ] C9. `populate_search_entries` (signature unchanged) embeds new primary ge rows inline with pin-stamped embedding_model, batch ≤512, and exact Unicode preservation on real synced records (SC-8)
- [ ] C10. The admin-role Embedding Backfill button passes the Playwright role-gated click-through with st.progress + callback + st.status and handle_ui_error surfacing (SC-9)
- [ ] C11. Runtime dependencies gain onnxruntime + tokenizers with sentence-transformers still dev-only, and the batch-64 profile evidence fits the 1 GiB envelope (SC-10)
- [ ] C12. The SearchMode Literal widens additively with 'Semantic Gloss'/'Semantic All', both dispatch to search_semantic(), and the four existing modes route unchanged (SC-11)
- [ ] C13. All 12 SC verdicts are PASS at the pre-PR gate; post-regression sweep is clean
- [ ] C14. No scope creep — every executed step traces to exactly one SC

## lifecycle_events

```yaml
- event: plan_created
  timestamp: 2026-09-29T18:27:02Z
  issuer: OpenCode (ollama-cloud/glm-5.3-flash)
  plan_file: ".issues/36/plan.md"
  phase_count: 6
  severity: info
```