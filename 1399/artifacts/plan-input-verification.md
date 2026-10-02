# Plan Input Verification Ledger — Issue 1399

Verified once at plan-input time; subsequent steps re-read THIS ledger, not the sources.

## Issue state + labels (from `.issues/1399/issue.yaml`, canonical)

- remote_issue: 1399, remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1399
- status: open
- labels: [approved-for-pr]  ← authorization: approved-for-pr, scope for_pr, halt_at pr_created
- Verified via `./.opencode/tools/local-issues read-labels --number snea-shoebox-editor#1399`

## SC list with evidence types (from spec.md Success Criteria table)

| SC | Criterion (short) | Evidence | Verify method |
|----|-------------------|----------|---------------|
| SC-1 | `search_semantic(mode="gloss", query=<real>, limit=5)` executes without raising | behavioral | pytest on new limit bind test vs local DB replica |
| SC-2 | `limit=1` returns exactly the top-ranked pair of unlimited ordering | behavioral | same test file; compare against limit=None ordering |
| SC-3 | `limit=None` full ranked list equals pre-fix baseline count | behavioral | guard test vs recorded pre-fix baseline |
| SC-4 | All existing semantic suites pass on fixed branch | behavioral | `uv run pytest test/test_semantic_*.py test/test_migration_semantic_schema_sc4.py` |

## Structure artifact phase/SC mappings

- Single phase: Phase 1 — limit bind-param parity. SCs: SC-1..SC-4. DAG edges: none.
- Per-item cycles: SC-1 (RED/GREEN/verify/commit), SC-2 (verify via shared fix, own cycle with Item 1), SC-3 (guard test), SC-4 (regression gate).

## Pinned fix approach (from spec)

- In `search_semantic()` at `src/services/semantic_search_service.py`: add `params["lim"] = int(limit)` under the existing `limit is not None` guard. No SQL string change, no signature change, no caller change.

## CLI surface flags actually needed

- `./.opencode/tools/local-issues update snea-shoebox-editor#1399 --labels <spec-cleared + existing>` (replaces entire labels array — include all existing labels)
- `./.opencode/tools/local-issues sync`
- solve: `./.opencode/tools/solve check --contract-path ... --state-path ...` (RED/GREEN refs in body use stable command names, no line numbers)

## Test-surface facts

- Current HEAD `src/services/semantic_search_service.py`: `_candidate_sql(..., has_limit)` renders ` LIMIT :lim` (~line 119–121 region); `search_semantic(..., limit=None)` signature at ~line 123; no `params["lim"]` write anywhere (grep-verified).
- `test/test_semantic_*.py` (19 files) + `test/test_migration_semantic_schema_sc4.py` exist.
- Branch for work: feature/1400-semantic-threshold-calibration (fix lands here per spec).
- Real DB replica is the test data source; NO synthetic data — use a real non-empty query per sync protocol (≤1,000-record repo scale; fixtures from real rows via testcontainers/replica pattern already used by existing semantic suites).
