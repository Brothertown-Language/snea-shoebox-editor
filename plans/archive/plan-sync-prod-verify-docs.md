# Plan: Verify Sync Script Table Coverage + Add Pydoc/Comments
## Status: ✅ Complete

## Overview
**WHAT**: Verify `scripts/sync_prod_to_local.py` syncs ALL tables, then add module-level docstring,
function docstrings, and inline comments that document the coverage mechanism and the maintenance
contract for future schema changes.

**WHY**: The script uses `Base.metadata.sorted_tables` (ORM-driven, auto-discovers all registered
tables), which is correct — but this is not documented. Without documentation, a future developer
adding a new table might not know whether the script needs updating, or might add a raw-SQL table
outside the ORM and silently miss it in the sync.

## Verification Result (pre-plan)
- ORM tables (13): `edit_history`, `iso_639_3`, `languages`, `matchup_queue`, `permissions`,
  `record_languages`, `records`, `schema_version`, `search_entries`, `sources`,
  `user_activity_log`, `user_preferences`, `users`
- Production DB tables (13): identical set — **no gaps found**.
- Coverage mechanism: `Base.metadata.sorted_tables` + `import src.database.models` in
  `models/__init__.py` registers all ORM models. New ORM tables are covered automatically.

## Scope
File: `scripts/sync_prod_to_local.py` only.
No logic changes — documentation only.

## Steps

1. ✅ Add module-level docstring immediately after the copyright line: state the script's purpose, list all 13 currently-synced tables (maintenance reference snapshot), document the coverage mechanism (`Base.metadata.sorted_tables`), and state the maintenance contract (new ORM tables auto-covered; raw-SQL tables outside ORM must be added explicitly).
2. ✅ Add/improve function docstrings: `sync_data()` (purpose, FK-safe ordering, maintenance contract); verify `load_secrets()`, `_ensure_pgserver()`, and `log_message()` docstrings are accurate.
3. ✅ Add inline comments at key decision points: `tables = Base.metadata.sorted_tables` (auto-discovery + ORM registration dependency); `import src.database.models` (why critical); delete loop (reverse-order FK safety); insert loop (forward-order FK safety).
4. ✅ Update this plan to reflect actual progress and declare completion if all steps are done.

## Non-Scope
- No logic changes
- No changes to `.sh` wrapper
- No changes to models or migrations
