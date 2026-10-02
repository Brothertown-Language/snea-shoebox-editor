---
number: 1399
title: "Bug: search_semantic(limit=<n>) raises InvalidRequestError — ':lim' bind param never populated"
status: open
labels: [bug, spec-draft]
created: '2026-10-02T14:43:06+00:00'
updated: '2026-10-02T15:30:00+00:00'
remote_issue: 1399
remote_url: "https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1399"
promoted_at: '2026-10-02T15:00:00Z'
promotion_type: retroactive_import
last_sync: '2026-10-02T15:30:00Z'
author: michael-conrad
---

> **Full spec and artifacts: [`issues-data/.issues/1399/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1399/)** — this remote issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.

## 1. Intent and Executive Summary

1. **Problem Statement:** Calling `search_semantic(mode=..., query=..., limit=<n>)` with a non-None limit raises `sqlalchemy.exc.InvalidRequestError` ("A value is required for bind parameter 'lim'"), because the generated SQL contains `LIMIT :lim` but the execution params dict never contains a `lim` key. The declared `limit` parameter of the public semantic-search seam is non-functional.

2. **Root Cause / Motivation:** In `src/services/semantic_search_service.py`, `_candidate_sql(..., has_limit=True)` appends ` LIMIT :lim` to the outer query, while `search_semantic()` builds `params = {"qv": ..., "pin": ...}` and conditionally adds `thr` and `source_id` — but never adds `lim` when `limit is not None`, even though it passes `has_limit=limit is not None`. This must be fixed now because `limit` is a declared, documented parameter of the seam; the first caller that passes `limit=<n>` (e.g., a future pagination wiring) hits a hard crash. Production UI currently passes `limit=None` and is unaffected — the defect is latent at the UI but live at the seam contract.

3. **Approach Chosen:** Populate the bind param at the seam: in `search_semantic()`, add `params["lim"] = int(limit)` under the same `limit is not None` guard that already drives `has_limit`. This restores parity between SQL placeholders and params keys using the module's existing conditional-param pattern (identical to how `thr` and `source_id` are populated). No SQL string change, no signature change, no caller change.

4. **Alternatives Considered & Why Discarded:**
   - *Interpolate the limit value into the SQL string* (`LIMIT {n}`) — discarded: breaks the text()-bind-param convention, introduces a string-formatting injection class, and bypasses SQLAlchemy parameter binding.
   - *Change `_candidate_sql` to inline a literal LIMIT* — discarded for the same injection/convention reasons; also widens the change surface beyond the params seam.

5. **Key Design Decisions:**
   - *Bind-param parity invariant:* whenever `_candidate_sql` renders a `:lim` placeholder, `params` SHALL contain `lim`. Tradeoff: one extra conditional line vs. a crash contract — chosen over SQL-string surgery to keep the fix minimal and injection-safe.
   - *Type coercion:* `int(limit)` coercion before binding. Tradeoff: rejects non-integral limits with a natural Python error instead of a database error — fail-fast at the seam, consistent with the project's fail-fast data-integrity mandate.
   - *Scope isolation:* the fix touches only the limit bind-param seam. Threshold/calibration semantics remain Issue #1400 scope; UI remains untouched.

6. **User Intent / Original Prompt:** Issue #1399 filed 2026-10-02 by michael-conrad, label `bug`: "search_semantic(limit=<n>) raises InvalidRequestError — ':lim' bind param never populated." Dispatch context: fix confined to the limit bind-param defect in the seam; no threshold/calibration changes (#1400), no UI changes.

## Not Included

- **Threshold / calibration semantics (CALIBRATED_FLOOR, threshold override, default floor)** — owned by Issue #1400; this spec only restores the limit bind param.
- **Streamlit UI limit/pagination wiring in `src/frontend/pages/records.py`** — the UI passes `limit=None` today; wiring a UI limit is a separate feature decision.
- **Result-status taxonomy or messaging changes** — the `ok`/`empty_query`/`no_embeddings`/`stale_model` statuses are out of scope.
- **Schema or migration changes** — no table or column is touched.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|----------------------|
| SC-1 | `search_semantic(mode="gloss", query=<real non-empty query>, limit=5)` executes against the local DB replica without raising any exception. | behavioral | Run `pytest` on the new limit RED/GREEN test file against the local DB replica; observe no `InvalidRequestError`. | `src/services/semantic_search_service.py` (defect site, read at HEAD); `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` |
| SC-2 | With `limit=1`, the results list from `search_semantic` contains exactly the top-ranked `(record_id, score)` pair of the unlimited ordering (cap of 1, score DESC then record_id ASC tie-break). | behavioral | Same test file: compare the `limit=1` output against the first pair of the `limit=None` result ordering. | `src/services/semantic_search_service.py` (`LIMIT clause`, read); `test/test_semantic_limit_bind_sc1_red.py` (new) |
| SC-3 | A `limit=None` call returns the full ranked list — its result count equals the unlimited pre-fix baseline count for the same query. | behavioral | Guard test in the same test file: run `limit=None`, compare result count to the recorded pre-fix baseline count. | `src/services/semantic_search_service.py` (read); `test/test_semantic_search_edge_matrix_sc7.py` (baseline pattern) |
| SC-4 | All existing semantic-search suites (`test/test_semantic_*.py` + `test/test_migration_semantic_schema_sc4.py`) pass on the fixed branch. | behavioral | Run `uv run pytest test/test_semantic_*.py test/test_migration_semantic_schema_sc4.py`; observe all passing. | `test/` suite listing (directory listing verified); `test/test_semantic_search_edge_matrix_sc7.py` (representative read) |

## Requirements

R-1. `search_semantic(mode, query, threshold, source_id, limit=<n>)` with `limit` set to a positive integer SHALL execute without raising `InvalidRequestError` and SHALL return a `SemanticSearchResult` whose results list contains at most `<n>` pairs.

R-2. The LIMIT clause SHALL be parameterized through the existing `text()` bind-param mechanism (`:lim` bound from `params`); the limit value SHALL NOT be interpolated into the SQL string.

R-3. The `lim` params key SHALL be populated exactly when the SQL contains the `:lim` placeholder (parity invariant driven by `limit is not None`).

R-4. `limit=None` behavior SHALL remain unchanged: no LIMIT clause emitted, full ranked list returned, ordering unchanged.

R-5. The fix SHALL be confined to the limit bind-param seam in `search_semantic`/`_candidate_sql` in `src/services/semantic_search_service.py`; no threshold/calibration changes and no UI changes.

R-6. Existing semantic-search test suites SHALL continue to pass after the fix (no regression to any status path).

## Items

### Item 1 (SC-1): Populate the :lim bind param — no-exception path

- RED: New test file `test/test_semantic_limit_bind_sc1_red.py` calls `search_semantic(mode="gloss", query=<real query>, limit=5)` against the local DB replica and asserts no exception is raised — fails on current HEAD with `InvalidRequestError`.
- GREEN: In `search_semantic()`, add `if limit is not None: params["lim"] = int(limit)` alongside the existing conditional param population.
- verify: RED→GREEN rerun of the test file.
- commit: Test + fix committed together.

### Item 2 (SC-2): Cap semantics — LIMIT honored

- RED: Same test file adds a `limit=1` case asserting the result count is at most 1 and matches the top-ranked pair of the unlimited ordering — unreachable on current HEAD (raises first).
- GREEN: Satisfied by Item 1's params fix (shared implementation); verify cap behavior.
- verify: RED→GREEN rerun.
- commit: Committed with Item 1's slice if sequenced together, or its own commit.

### Item 3 (SC-3): limit=None invariance guard

- RED: Need not fail — invariant-preserving guard; baseline: run `limit=None` on the pre-fix branch and record the result count for a fixed real query.
- GREEN: No production code change; guard test asserts the `limit=None` result count equals the recorded pre-fix baseline count.
- verify: Guard test green on the fixed branch.
- commit: Guard test committed.

### Item 4 (SC-4): Existing-suite regression run

- RED: Need not fail — regression gate; baseline: suites green on the pre-fix branch.
- GREEN: No production code change beyond Item 1; run the suites on the fixed branch.
- verify: `uv run pytest test/test_semantic_*.py test/test_migration_semantic_schema_sc4.py` — all pass.
- commit: Recorded in the Item 1 commit (verification evidence), nothing new to deliver.

## Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #1400 (threshold calibration) | Independent — this spec MUST NOT touch calibration semantics | Satisfied (separate scope) |
| Local PostgreSQL replica of production | Test data source for behavioral SCs (real embedded rows, no synthetic data) | Satisfied (per repo sync protocol) |
| `src/services/semantic_search_service.py` at branch `feature/1400-semantic-threshold-calibration` | Defect site; fix lands on this branch | Satisfied |

## Traceability

| Requirement | SC(s) | Phase(s) |
|-------------|-------|----------|
| R-1 | SC-1, SC-2 | Phase 1 |
| R-2 | SC-1 | Phase 1 |
| R-3 | SC-1 | Phase 1 |
| R-4 | SC-3 | Phase 1 |
| R-5 | SC-1, SC-2, SC-3 | Phase 1 |
| R-6 | SC-4 | Phase 1 |

## Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| Defect site | code | `src/services/semantic_search_service.py` (`_candidate_sql`, `search_semantic`) | Read at HEAD of `feature/1400-semantic-threshold-calibration`; grep confirms no `params["lim"]` write |
| Production caller | code | `src/frontend/pages/records.py` (`search_semantic(..., limit=None)` ×2) | Read — passes limit=None, unaffected |
| SQLAlchemy text() binding | doc | SQLAlchemy `text()` bind-parameter semantics | Module-internal convention verified by reading existing `:thr`/`:source_id`/`:qv` param population in the same function |
| Existing test suites | code | `test/test_semantic_*.py`, `test/test_migration_semantic_schema_sc4.py` | Directory listing + read of representative suites |

## Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- SC-1: Running the no-exception behavioral test costs minutes of execution time — a bounded delay that surfaces the bind-param defect at the earliest gate. Skipping means the first `limit=<n>` caller discovers the crash in production, at 1000× the fix cost.
- SC-2: Verifying the cap semantics costs minutes of the same test run. Skipping means an unbounded or mis-ordered LIMIT silently returns wrong result counts — a data-correctness defect discovered downstream at exponential cost.
- SC-3: Running the existing semantic suites costs minutes. Skipping means a regression to `limit=None` (the UI's live path) ships undetected and breaks semantic search for every user.

## Edge Cases

- **Input boundaries — limit=0:** A `limit` of 0 SHALL bind `lim=0` and return zero results (SQL `LIMIT 0` semantics) without error. Covered by the same params fix; no special-casing.
- **Input boundaries — negative limit:** A negative `limit` SHALL raise naturally (PostgreSQL rejects negative LIMIT, or `int()` coercion surfaces the input as-is to the DB); no silent clamping. Behavior asserted incidentally by SC-1's coercion path; explicit non-goal to add validation beyond existing conventions.
- **Input boundaries — non-integer limit:** `int(limit)` SHALL fail fast with a natural Python error at the seam rather than a database error (fail-fast mandate).
- **State transitions — limit=None → limit=<n>:** Both paths share one code path; parity invariant R-3 ensures no state where SQL has `:lim` but params lacks it (or vice versa).
- **Failure modes — no embedded rows / stale model with limit set:** The degraded-status diagnostics path is unaffected; with `limit=<n>` and zero matching rows, the empty-results diagnostics block executes as before (status `no_embeddings`/`stale_model`/`ok`-with-empty).
- **Concurrency:** The fix adds one dict-key assignment under no lock contention — params is a local dict per call; no new race surface.
- **Recovery:** No recovery path changes; exceptions from bad limit values propagate fail-fast per project mandate.

---

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
