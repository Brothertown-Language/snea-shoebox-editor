> **Full spec and artifacts: [`.issues/1426/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1426)** — authoritative spec record for Issue #1426; the GitHub issue body is a condensed exec summary.

# Spec: Test-suite order independence — DB-backed tests must not contaminate or be contaminated by execution order against the synced production-replica database

## 1. Intent and Executive Summary

- **Problem Statement:** After `scripts/sync_prod_to_local.sh`, a full `uv run pytest -q --ignore=tmp` run shows **158 failed, 709 passed, 111 skipped** — identical on unmodified `main` (verified 2026-10-10, tip `1f0f9ff`). The suite is order-dependent: DB-backed tests that read real synced data fail in suite context while their modules pass in isolation. Two failure classes were recorded: (1) `psycopg2.errors.ForeignKeyViolation: matchup_queue_source_id_fkey` — staged fixture rows reference sources absent from the schema/data in effect; (2) later real-record tests (e.g. the SC-8 fixtures in `test/test_upload_search_entries.py`, which require records 5/15/6832) fail with `AssertionError: unexpectedly None : real synced record N must exist in synced DB`. The failure count also varies between runs (158 vs 153), consistent with order-dependent contamination.
- **Root Cause / Motivation:** Both recorded failure classes share one property: the database state a test module observes depends on which test modules ran (or were imported) before it in the same pytest process. Candidate couplings named in the ticket: the migration/schema recreate path and the shared pgserver tmp-dir lifecycle. One further coupling is present in the tree: `tests/database/test_migration_manager.py` sets `os.environ["OPENCODE"] = "1"` at module import — a process-global that selects the dedicated private OpenCode database path in `src/database/connection.py`, while the SC-8 fixtures target the synced local replica. Root-cause confirmation across all failure classes is implementation work, out of scope for this document.
- **Approach Chosen:** Requirements state invariants on observable outcomes — the full suite is green after a fresh sync, the synced dataset survives a full-suite run intact, and synced-data-dependent modules behave identically in suite context and in isolation. The isolation mechanism (dedicated temporary database, state restore/teardown discipline, or environment scoping) is an implementation decision, fixed by diagnosis of the actual mechanism.
- **Alternatives Considered & Why Discarded:** Pinning a specific isolation mechanism into the requirements (e.g. "give migration tests a temporary database" or "make them restore state") was discarded — the deliverable's requirement is the invariant, which any correct isolation approach satisfies; naming one technique would over-constrain the implementation or admit an unfixed branch.
- **Key Design Decisions:** D1 — requirements state invariants on observable outcomes; the isolation technique is an implementation decision. D2 — both observed failure classes are in scope; whether they share one root cause or two, the invariants cover both. D3 — resolution must be genuine: suppressing failures with new skip/xfail masks does not satisfy this spec. D4 — the sync script's faithful-exact-copy mandate (`scripts/sync_prod_to_local.py`) is untouched; production is the source of truth and remains so.
- **User Intent / Original Prompt:** Issue #1426 (filed 2026-10-10) — the disposition for the pre-existing suite failures, filed so the suite's pre-existing state does not block feature-PR boundaries. This spec formalizes that ticket's problem, evidence, and decided requirements.

## 2. Not Included

- **Production database and deployment** — production is read by the sync script only; nothing in this spec touches production.
- **Sync script behavior** — `scripts/sync_prod_to_local.py` keeps its faithful-exact-copy mandate byte-for-byte; no sync-logic changes.
- **SC-8 fixture semantics** — the fixtures' contract (transaction-scoped copies of REAL synced records; the `REAL_RECORD_IDS` set, currently 5/15/6832; unicode round-trip parsed from `mdf_data`, the current fixture behavior) is unchanged; this spec makes the suite honor that contract in every run order, it does not weaken it.
- **Existing skip guards** — `playwright_e2e` / `SNEA_E2E` gating and other designed skips are unchanged; designed skips remain permitted under SC-1.
- **Application runtime behavior** — the fix is expected in test infrastructure; any change to `src/` (e.g. `src/database/connection.py`) must preserve current app-facing behavior (production detection, pgserver auto-start, socket/TCP handling) unchanged.

## 3. Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | After `scripts/sync_prod_to_local.sh` completes, a full `uv run pytest -q --ignore=tmp` run completes with 0 failed tests (designed skips permitted). | behavioral | Executed full-suite pytest run against a freshly synced local database; the summary line showing 0 failed is captured as evidence. |
| SC-2 | The synced local dataset is intact after a full-suite run: every record id in the SC-8 fixture's `REAL_RECORD_IDS` contract (currently 5, 15, 6832) remains present in the local database the sync produced. | behavioral | Database queries for the fixture's record ids executed after the full-suite run of SC-1, with query results captured. |
| SC-3 | Synced-data-dependent test modules produce identical results in suite context and in isolation — concretely, `test/test_upload_search_entries.py` passes within the full suite exactly as its 8/8 isolation result. | behavioral | Comparison of two executed pytest outcomes: the module alone, and the module's outcome within the recorded full-suite run of SC-1. |
| SC-4 | The recorded order-coupling adjacency is resolved: running the migration/schema test module `tests/database/test_migration_manager.py` and `test/test_upload_search_entries.py` in the same pytest session leaves the upload-search module's synced-record assertions passing. | behavioral | Executed targeted multi-module pytest invocation — RED before the fix (reproducing the recorded failure mode) and GREEN after. |

## 4. Requirements

- R-1. After a fresh production sync, the full test suite SHALL complete with zero failed tests; designed skips are permitted.
- R-2. A full-suite run SHALL leave the synced local dataset intact: the records the SC-8 fixture contract requires SHALL exist in the database after the run.
- R-3. A synced-data-dependent test module SHALL produce the same result whether it runs in isolation or within the full suite.
- R-4. A pytest session that includes both the migration/schema test modules and the synced-data-dependent test modules SHALL yield passing synced-record assertions for the latter.

### Implementation Constraints

- C-1. The failures SHALL be genuinely resolved; introducing new skip/xfail masks on DB-backed tests to satisfy R-1 is not resolution. Existing designed skip guards are unaffected.
- C-2. The sync script's faithful-exact-copy behavior and production data SHALL NOT change.
- C-3. The SC-8 fixture contract (real synced records as the test basis, unicode round-trip from `mdf_data`) SHALL NOT be weakened or replaced with synthetic data.
- C-4. Changes to `src/` SHALL preserve app-facing runtime behavior unchanged; test-infrastructure changes carry no app-behavior change.

## 5. Items

### Item 1 (SC-4, SC-2): Isolate the contamination at its diagnosed mechanism

- RED: The targeted multi-module invocation (`tests/database/test_migration_manager.py` together with `test/test_upload_search_entries.py`) fails as recorded — the synced-record assertion or the fixture FK staging fails; capture the exact failure text.
- GREEN: The same targeted invocation passes; the records in the fixture's `REAL_RECORD_IDS` are present in the database after the run; the diagnosis behind the fix is documented from evidence (root cause, not symptom suppression).
- verify: Executed pytest outputs for RED and GREEN plus a post-run database check for the fixture record ids (SC-2).
- commit: Test-infrastructure isolation fix commit(s), per the diagnosed root cause.

### Item 2 (SC-1, SC-3): Full-suite gate after fresh sync

- RED: With the pre-fix tree, the full `uv run pytest -q --ignore=tmp` run after `scripts/sync_prod_to_local.sh` shows the recorded failure classes (158 failed / 153 failed depending on order).
- GREEN: With the fixed tree, the same full-suite run after a fresh sync shows 0 failed, and `test/test_upload_search_entries.py`'s outcome matches its isolation result.
- verify: Executed full-suite summary line (0 failed, designed skips permitted) plus the module-outcome comparison (SC-3); run-to-run stability confirmed by a second full-suite run also showing 0 failed.
- commit: Residual fix commits surfaced by the full-suite gate; the existing SC-8 fixtures remain the standing regression pin for contamination (no new masking allowed per C-1).

## 6. Dependencies

| Reference | Relationship | Status |
|-----------|--------------|--------|
| Issue #1426 (ticket body: problem, evidence, proposed direction) | Source of intent this spec formalizes | Satisfied |
| `test/test_upload_search_entries.py` (SC-8 fixtures, `REAL_RECORD_IDS`, isolation-pass evidence) | Contamination victim and standing regression pin; anchors verified 2026-10-10 | Satisfied |
| `tests/database/test_migration_manager.py` (module-import `OPENCODE` env set, module-scoped `init_db` engine, `MigrationManager.run_all()`) | Named adjacency in the recorded reproducer; verified 2026-10-10 | Satisfied |
| `src/database/connection.py` (`OPENCODE` → private-DB path selection, pgserver lifecycle, `is_production`) | Order-coupling surface named in the problem analysis; verified 2026-10-10 | Satisfied |
| `scripts/sync_prod_to_local.py` (faithful-exact-copy mandate; local-only schema changes via MigrationManager) | Precondition provider for SC-1/SC-2; mandate constrains C-2 | Satisfied |

## 7. Traceability

| Requirement | SC(s) | Item(s) |
|-------------|-------|---------|
| R-1 | SC-1 | Item 2 |
| R-2 | SC-2 | Item 1, Item 2 |
| R-3 | SC-3 | Item 2 |
| R-4 | SC-4 | Item 1 |
| C-1 | SC-1, SC-4 | Item 1, Item 2 |
| C-2 | SC-1, SC-2 | Item 2 |
| C-3 | SC-3, SC-4 | Item 1, Item 2 |
| C-4 | SC-1, SC-4 | Item 1 |

## 8. Documentation Sources

| Source | Type | Location | Verification |
|--------|------|----------|--------------|
| Issue #1426 ticket body | issue record | `.issues/1426/issue.yaml` (synced to GitHub #1426) | Problem, evidence, and proposed direction read in full, 2026-10-10 |
| SC-8 fixture module | code | `test/test_upload_search_entries.py` (SC-8 fixtures: `REAL_RECORD_IDS = [5, 15, 6832]`, transaction-scoped real-record copies, `mdf_data` unicode round-trip) | Direct read of the fixture region, 2026-10-10 |
| Migration test module | code | `tests/database/test_migration_manager.py` (module-import `os.environ["OPENCODE"] = "1"`, module-scoped engine via `init_db()`, `MigrationManager(engine).run_all()`) | Direct read, 2026-10-10 |
| Database connection layer | code | `src/database/connection.py` (`OPENCODE`-gated private-DB path selection, `_start_pgserver_core`, `_stop_local_db`, `is_production`) | Direct read of pattern anchors, 2026-10-10 |
| Sync script | code | `scripts/sync_prod_to_local.py` (faithful-exact-copy mandate; schema replication strategy) | Direct read of header/mandate, 2026-10-10 |
| Both test trees | code | `test/` and `tests/` both exist; `matchup_queue` DB staging in `tests/database/test_crud.py`, `tests/integration/test_mdf_upload_locking.py`, `tests/integration/test_upload_e2e.py`; mocked queue-row construction without DB writes in `tests/frontend/test_upload_review_d1.py` | Verified by content search and direct reads, 2026-10-10 |

## 9. Enforcement Gate

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## 10. Cost Frame

Cost is measured in defect-discovery-latency, not tool calls. Correctness is the only metric.

- **SC-1:** Running the full suite against a fresh sync costs minutes of execution time. Skipping costs the recorded 158-failure state shipping undetected — every DB-backed test result becomes untrustworthy after merge, and the next feature branch inherits the same blocked-PR disposition this issue was filed to end.
- **SC-2:** Querying three record ids after the suite run costs seconds. Skipping costs silent dataset destruction — a suite run that wipes synced records would leave every subsequent real-data verification session (and the stakeholder's local workflow) broken with no test evidence pointing at the cause.
- **SC-3:** Comparing two executed module outcomes costs minutes. Skipping costs order-dependent test results — a module that passes alone and fails in the suite is exactly the recorded failure mode this spec exists to eliminate.
- **SC-4:** Running the two-module targeted invocation costs seconds to minutes. Skipping costs loss of the cheapest reproducer — without it, every future regression of this class requires a full-suite bisect instead of a targeted diagnosis.

## 11. Edge Cases

- **Condition:** `OPENCODE` is already set in the invoking shell before pytest starts. **Expected behavior:** The environment is part of the test configuration, not an accident of test order; SC-1's instrument assumes the default environment (synced local database as sync_prod_to_local produced it), and any intentional private-DB invocation is a documented precondition of that run. **Resolution:** The SC-1 instrument is executed in the default environment; environment-dependent divergence is diagnosed, not masked.
- **Condition:** A stale private OpenCode database left by a previous run. **Expected behavior:** Suite results do not depend on leftover state from prior runs. **Resolution:** Covered by the order-independence invariants (R-2/R-4) and verified by the second full-suite run in Item 2's verify step.
- **Condition:** Production data changes over time (record ids in the fixture contract shift). **Expected behavior:** The fixture's `REAL_RECORD_IDS` contract is the single source of the required ids; this spec pins behavior to that contract, not to the literal values. **Resolution:** SC-2/SC-4 verify against the fixture's declared ids (currently 5/15/6832).
- **Condition:** Run-to-run failure-count variance (158 vs 153 recorded). **Expected behavior:** After the fix, variance between runs manifests only in skip counts, never in failed counts. **Resolution:** SC-1's verify requires 0 failed across repeated runs.
- **Condition:** A failure surfaced by the full suite that is genuinely unrelated to DB contamination. **Expected behavior:** It is a real defect to be fixed or dispositioned on its own evidence — not suppressed (C-1). **Resolution:** Item 2's GREEN requires 0 failed; any such failure is diagnosed and resolved or escalated with evidence before the gate closes.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
