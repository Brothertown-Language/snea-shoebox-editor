# Implementation Plan — #1426 Test-suite order independence

Spec source: `.issues/1426/spec.md` (validated PASS, zero findings, 2026-10-10; approved for plan 2026-10-10).
Branch (created at implement start): `feature/1426-suite-order-independence`, base tip `d411a76` (current `main`).

Derivation guard: every item below traces to a spec SC — no item without an SC anchor. All four SCs were judged against the validation-standards defect classes before planning: each is behavioral with an executable instrument, none is either/or, none ambiguous, none trivially true against the recorded baseline. No BLOCKED criteria.

Repository test protocol (mandatory, from AGENTS.md): before every regression test cycle the local database is re-synced from production with `bash scripts/sync_prod_to_local.sh`, and the sync script used is the one from the feature branch under test. Every full-suite instrument below runs after a fresh sync.

Constraint guards carried into every item: C-1 (no new skip/xfail masks — failures resolved genuinely), C-2 (sync script untouched), C-3 (SC-8 fixture contract untouched — the fix must not alter the fixtures' assertions or data basis), C-4 (any `src/` touch preserves app-facing behavior unchanged).

## Item 1 — SC-4: isolate the order-coupling at its diagnosed mechanism

- **Deliverable:** the fix that lets `tests/database/test_migration_manager.py` and `test/test_upload_search_entries.py` share one pytest session with the upload module's database selection resolving to the synced local replica — located at the diagnosed mechanism (candidate: the module-import `os.environ["OPENCODE"] = "1"` process-global in the migration test module selecting the private OpenCode DB path in `src/database/connection.py`). The diagnosed root cause is documented from evidence in the fix commit message and PR body. Fix expected in test infrastructure; any `src/` change preserves app-facing behavior (C-4).
- **RED:** `uv run pytest tests/database/test_migration_manager.py test/test_upload_search_entries.py -q` reproduces the recorded failure mode — `real synced record 5 must exist in synced DB` or the `matchup_queue_source_id_fkey` violation. If the two-module invocation does not reproduce, the diagnosis expands from captured evidence before any fix is written; a non-reproducing reproducer is escalated, never routed around.
- **GREEN:** the same invocation passes — the migration module's tests pass and the upload-search module passes 8/8 against the synced local database; the fixture assertions and their data basis are untouched (C-3).
- **Instrument:** executed pytest output for RED and GREEN, captured verbatim.

## Item 2 — SC-2: dataset-integrity invariant after a full-suite run

- **Deliverable:** verified invariant that the synced dataset survives a full-suite run — the post-run database holds every record in the SC-8 fixture's `REAL_RECORD_IDS` contract (currently 5, 15, 6832). This constrains whatever mechanism Item 1 shipped: the fix must not merely redirect readers while leaving the dataset destructible by suite order.
- **RED:** on the pre-fix tree, the suite-context SC-8 fixture failure (`real synced record 5 must exist in synced DB`) is the recorded observable — re-established by Item 3's RED full-suite run.
- **GREEN:** after a full-suite run, database queries for the fixture's record ids against the default local database (the sync's target) return all of them.
- **Instrument:** executed post-run query for the three record ids (via the project's default DB URL), output captured.

## Item 3 — SC-1: full-suite gate after fresh sync

- **Deliverable:** the full suite green after a fresh sync, stable across two consecutive runs, with the C-1 mask guard enforced by fact: the skip count does not exceed the recorded baseline (111) unless every additional skip is an explicitly designed guard rather than a contamination mask.
- **RED:** the recorded baseline — 158 failed (and 153 on the variant order), twice on 2026-10-10, identical on unmodified `main`; re-established by a fresh-sync full-suite run on the pre-fix tree.
- **GREEN:** after `bash scripts/sync_prod_to_local.sh`, `uv run pytest -q --ignore=tmp` reports 0 failed; a second consecutive fresh-sync run also reports 0 failed.
- **Instrument:** executed summary lines of both full-suite runs plus the skip-count comparison against the 111 baseline; any skip delta accounted for explicitly (C-1).
- **Depends on:** Items 1 and 2.

## Item 4 — SC-3: suite/isolation parity evidence

- **Deliverable:** the parity verification — `test/test_upload_search_entries.py` produces the same outcome inside the full suite as in isolation (8 passed both ways).
- **RED:** the recorded pre-fix divergence — 8 passed alone, failing assertions in suite context.
- **GREEN:** within Item 3's GREEN full-suite run the module reports 8 passed, matching a fresh isolation run of the same module on the fixed tree.
- **Instrument:** comparison of the two executed outcomes: the module's result line from Item 3's GREEN run and a fresh `uv run pytest test/test_upload_search_entries.py -q` isolation run.
- **Depends on:** Item 3.

## Dependency order

Item 1 first (diagnose and fix the coupling at its mechanism; the reproducer RED grounds the diagnosis). Item 2 verifies the dataset invariant the fix must preserve. Item 3 is the full-suite gate over the fixed tree (requires 1–2). Item 4 consumes Item 3's run for the parity comparison (requires 3).

## Verification-evidence rule

Behavioral SCs are verified by executed commands and their real output — run summaries, query results, module outcome lines — never by reading code or asserting intent. All executed evidence is collected as PR-body material for the eventual review boundary.
