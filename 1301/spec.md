STATUS: 1 (DRAFT)
CREATED: 2026-06-14

> **Full spec: [Issue #1301](https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1301)**

## Problem

`sync_prod_to_local.py` provisions the local database using `Base.metadata.create_all()` which creates tables from the **current code's** ORM models, then copies prod data into them via row-by-row INSERT. This produces a database whose schema matches neither prod nor the current development code — it's an untestable hybrid. Generated columns (`records.fts_vector`), new tables (`fts_entries`), and schema versions are all wrong.

## Root Cause

The script reimplements database sync with table-by-table `SELECT`/`INSERT` over `Base.metadata.sorted_tables`. This fundamentally cannot produce a correct replica because:
- The ORM model defines the **current** schema, not prod's schema
- Generated columns (like `fts_vector`) are defined outside the ORM via raw SQL migrations
- Schema version history is not transferred
- Sequences are not properly preserved by the row-by-row INSERT approach

## Solution

Replace the ORM-based table iteration with a two-phase approach:

**Phase 1 — Schema replication via pg_catalog introspection:**
Introspect production's actual schema via `pg_catalog` queries to discover all tables, columns (including generated columns), types, constraints, and indexes. Generate `CREATE TABLE` DDL per table with exact column types, generated column expressions, and constraints. Drop all local tables and recreate them in dependency order (topological sort based on foreign key references). Recreate indexes (excluding PKs and unique constraints already baked into CREATE TABLE).

**Phase 2 — Data copy via parameterized INSERT:**
Copy production data into the recreated local tables using parameterized INSERT batches (1,000 rows per batch). Skip generated columns in INSERT statements — they are populated automatically by the DDL-defined expressions. Reset sequences after data copy to match the max ID in each table.

This approach avoids external binary dependencies (`pg_dump`/`psql`) while producing an exact schema+data replica. For heavy schema resets, a companion script `reset_schema_to_prod.py` handles the `pg_dump` path.

## Out of Scope

- Multi-directional sync (local → prod)
- Selective table sync (always full)
- Schema migration (the local copy matches prod exactly; migrations run on app startup)

## Verification

After sync:
- Key record counts match between prod and local
- `SELECT * FROM schema_version` matches prod
- Generated columns produce identical values
- `pg_dump --schema-only` comparison between prod and local should show identical schemas

## Files Changed

| File | Change |
|------|--------|
| `scripts/sync_prod_to_local.py` | Replace ORM-based table iteration with pg_catalog introspection + DDL generation + parameterized INSERT batches |
| `scripts/reset_schema_to_prod.py` | New companion script using `pg_dump` for schema-only resets |

🤖 Co-authored with AI: OpenCode (deepseek-v4-flash-free)
