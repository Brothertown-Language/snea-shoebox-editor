---
remote_issue: 1358
remote_url: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1358
promoted_at: 2026-07-15T00:00:00Z
status: SPEC
---

# [SPEC] Remove dead `fts_vector` column check from sync_prod_to_local.py

## Problem

`scripts/sync_prod_to_local.py:339` checks whether `fts_vector` exists as a column on the `records` table:

```python
cols = [c['name'] for c in ins.get_columns(t)]
log_message(f"    fts_vector present: {'fts_vector' in cols}")
```

This check was written when `records.fts_vector` existed as a generated column. Migration `v20260613120000` (shipped in `feature/1299-fts-entries`, documented in `CHANGELOG.md:15`) intentionally dropped that column. The FTS data now lives in the `fts_entries` table (`src/database/models/search.py:22`).

The check always prints `False` and serves no purpose. It is dead code.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | The `fts_vector present: False` log line is removed from `sync_prod_to_local.py` | `string` | grep confirms the line is absent |
| SC-2 | The sync script verification section still reports row counts for `records`, `schema_version`, and `fts_entries` | `string` | grep confirms the three count lines remain |
| SC-3 | No other references to `records.fts_vector` remain in production code (migrations are exempt) | `string` | grep confirms no hits outside `migrations.py` |

## Affected Files

- `scripts/sync_prod_to_local.py` — remove lines 337-339 (the `if t == 'records':` block that checks for `fts_vector`)

## Notes

- Migration files (`src/database/migrations.py`) that reference `records.fts_vector` are historical and MUST NOT be modified.
- The `CHANGELOG.md` entry for migration `v20260613120000` is a historical record and MUST NOT be modified.
