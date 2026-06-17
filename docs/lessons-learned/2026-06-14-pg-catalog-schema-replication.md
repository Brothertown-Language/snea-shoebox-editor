# pg_catalog Schema Replication — Replacing ORM-Based Database Sync

Date: 2026-06-14

## Context

`sync_prod_to_local.py` originally used `Base.metadata.create_all()` to create tables from the current code's ORM models, then copied prod data via row-by-row INSERT. This produced a database whose schema matched neither prod nor the current development code — an untestable hybrid. Generated columns (`records.fts_vector`), new tables (`fts_entries`), and schema versions were all wrong.

## Findings

### Why ORM-Based Sync Fails

The ORM model defines the **current** schema, not prod's schema. This fundamentally cannot produce a correct replica because:
- Generated columns (like `fts_vector`) are defined outside the ORM via raw SQL migrations
- Schema version history is not transferred
- Sequences are not properly preserved by row-by-row INSERT

### Solution: pg_catalog Introspection

The fix replaces ORM-based table iteration with a two-phase approach that avoids external binary dependencies (`pg_dump`/`psql`):

**Phase 1 — Schema replication via pg_catalog introspection:**
- Query `pg_catalog.pg_tables` to discover all production tables
- Query `pg_attribute` + `pg_type` for each table to get column names, types, and generated column status
- Query `pg_get_expr()` for generated column expressions
- Query `pg_constraint` for primary keys, foreign keys, unique constraints, and check constraints
- Generate `CREATE TABLE IF NOT EXISTS` DDL per table with exact column types, generated column expressions, and constraints
- Drop all local tables and recreate them in dependency order (topological sort based on foreign key references)
- Recreate indexes (excluding PKs and unique constraints already baked into CREATE TABLE)

**Phase 2 — Data copy via parameterized INSERT:**
- Copy production data into recreated local tables using parameterized INSERT batches (1,000 rows per batch)
- Skip generated columns in INSERT statements — they are populated automatically by the DDL-defined expressions
- Reset sequences after data copy to match the max ID in each table

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| pg_catalog over pg_dump | Avoids external binary dependency; pg_dump may not be available in all environments |
| Topological sort for table ordering | Ensures foreign key constraints are satisfied during CREATE TABLE |
| Parameterized INSERT batches | Prevents SQL injection; handles large datasets (7,609 records) |
| Sequence reset via `pg_get_serial_sequence` | Ensures auto-increment IDs don't collide with imported data |
| Companion `reset_schema_to_prod.py` | Handles the pg_dump path for heavy schema resets where external binaries are acceptable |

## Recommendation

For schema-aware database sync where `pg_dump`/`psql` may not be available, use pg_catalog introspection to replicate the exact production schema. This approach handles generated columns, constraints, indexes, and sequences correctly without ORM involvement.

## Files Referenced

| File | Lines | Purpose |
|------|-------|---------|
| `scripts/sync_prod_to_local.py` | 78-189 | `get_table_metadata()` — pg_catalog introspection and DDL generation |
| `scripts/sync_prod_to_local.py` | 192-336 | `sync_data()` — full sync pipeline |
| `scripts/reset_schema_to_prod.py` | 78, 147, 228, 270, 353 | Companion script using pg_dump for schema-only resets |
