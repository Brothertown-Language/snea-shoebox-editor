# PostgreSQL & SQLAlchemy Standards

Applies to `pubmed_data_3` and all new persistence code.

## Repository Usage (MANDATORY)

- ALL DB operations MUST go through a `Repository` class (e.g., `PubmedArticleRepository`). Direct `session.execute()`, `session.query()`, or any SQLAlchemy Core constructs (`insert()`, `select()`, `update()`, `delete()`) are PROHIBITED outside Repository classes in `src/`, notebooks, and tests. **Raw SQL is FORBIDDEN.** This includes `text()`, SQL strings, or any direct execution. Repositories encapsulate all ORM-to-Domain and Domain-to-ORM logic.
- `./tmp/` and `scripts/` diagnostic scripts may use direct session access only for one-off exploration that does not
  inform production logic.

## Driver & ORM

- psycopg 3 (`psycopg`) only. No `psycopg2`/psycopg2-binary. Dialect: `postgresql+psycopg://`.
- SQLAlchemy 2.0+ only: `DeclarativeBase`, `Mapped[]`, `mapped_column()`. Legacy patterns prohibited.
- All DB ops through `Session`. Only SQLAlchemy ORM constructs (mapped model queries) are permitted via Repository — NO EXCEPTIONS.

## PgServerManager (ZERO TOLERANCE)

- ALWAYS use as context manager (`with PgServerManager(...) as pg_manager:`). NEVER manual `start()`/`stop()` or raw
  connection strings.
- **Conflict Prevention**: Don't start a separate test `pgserver` on TCP if a production instance is running. Check
  for a running production instance by verifying whether the production `pgdata` path's `postmaster.pid` exists before
  starting a test instance on TCP.
- **Persistent/integration tests**: Use the production `pgserver` instance with a dedicated test schema (`ai_test`
  schema) for schema isolation.
- **Ephemeral tests** (short-lived instance and tables removed after test completion): Use a separate `pgserver`
  instance in socket-only mode (no TCP port).
- Every backfill/migration script MUST use `PgServerManager` via `with`. Use `pgserver` for embedded PostgreSQL in local
  dev.
- **Repository-First Lifecycle (MANDATORY)**: All notebooks and scripts that need a running PostgreSQL instance MUST
  use `PubmedArticleRepository.from_pgdata()` for lifecycle management (server start, schema init, session factory).
  Direct `PgServerManager` instantiation is PROHIBITED in notebooks and scripts, with the sole exception of
  `scripts/pgserver_start.py` and `scripts/pgserver_stop.py`.
- **pgserver Projects Use pgserver**: For projects using pgserver (embedded PostgreSQL), ALL database access MUST go through
  `PgServerManager`. NEVER use `psql`, direct PostgreSQL client connections, or bypass the embedded server. This ensures
  consistent lifecycle management and avoids conflicts with the embedded instance.

## Database Location

- `pgdata` location: outside the project root (user-managed) or inside the project only in `./tmp/` (e.g.,
  `./tmp/db/pgdata`).
- Forbidden: `pubmed_data_*/db/`, `src/`, `notebooks/`, or anywhere inside project outside `./tmp/`.
- Before passing a `pgdata` path to `PgServerManager`, the agent MUST verify the path is within `./tmp/` or outside the
  project root. Do not rely solely on `PgServerManager` to enforce this.
- `PgServerManager` must enforce this rule and fail-fast on forbidden paths.

## Schema Standards

- `Text` for all variable-length strings. `String(N)` only for genuinely fixed-length (ISO dates, fixed-format IDs).
- Migration versions: date-based `yyyymmddhhmmss` format in UTC. Simple increments prohibited.
- **Migration location**: ALL schema migrations are defined inline in `src/commons/persistence/pg/schema.py` as
  `_Migration` entries in the `_MIGRATIONS` list. There is no external migrations directory. Do not search elsewhere.
  To add a migration, generate a version timestamp with `uv run python ai_bin/schema-version` — **immediately before
  adding a migration, not earlier. NEVER run `schema-version` speculatively (analysis, exploration, curiosity, or as
  a side-effect of any other task that does not need a timestamp).** Then append a
  `_Migration(version=..., description=..., statements=[...])` entry to
  `_MIGRATIONS`, and update `_CURRENT_SCHEMA_VERSION` in `models.py`.
- **NO unauthorized schema changes**: NEVER modify `schema.py`, `models.py`, or any migration without explicit user
  instruction. Schema changes are high-risk and require explicit approval — do not make them as a side-effect of
  fixing scripts or other tasks.
- **NO `IF EXISTS` / `IF NOT EXISTS` to mask broken migrations**: If a migration fails because the target object already
  exists or does not exist, the migration runner or migration itself is defective — fix the root cause. Do not paper over
  defective DDL with existence guards. The correct fix is:
  1. For "table already exists" errors: The migration runner wrongly called `create_all()` on an existing database
     before running migrations. Fix the runner logic, not the migration.
  2. For "object does not exist" errors: Either the migration was never needed (remove it) or the migration runner
     needs proper precondition checking.
  Using `IF NOT EXISTS` / `IF EXISTS` hides bugs and makes migrations unreproducible.

## Schema Migration Runner (CRITICAL)

**Simplified Design**: Schema is built **only** from migrations. `Base.metadata.create_all()` is NEVER used.

```python
def initialize_schema(engine: Engine) -> None:
    """Run all pending migrations. No create_all()."""
    ensure_schema_current(engine)
```

**Fresh & existing databases follow the same path**:
1. Check `schema_version` table for applied migrations
2. Run any pending migrations in `_MIGRATIONS` list
3. Record each applied migration in `schema_version`

**Model-to-Migration Mapping**:
- Every table defined in ORM models MUST have a corresponding CREATE TABLE migration
- The `schema_version` table creation is the first migration
- Models are for ORM mapping; migrations are the source of truth for DDL

**Adding a new model**:
1. Add model class to `models.py`
2. Create migration with CREATE TABLE statement
3. Update `_CURRENT_SCHEMA_VERSION` to new version

## Diagnostics

- NEVER modify production files to diagnose data. Use standalone scripts in `./tmp/` or notebooks.
- DB enum values: see Strict Enum Mapping in `080-code-standards.md`.

## Backward Compatibility

- `sqlbind` and existing SQLite repository classes remain untouched until the `pubmed_data_3` migration to `pgserver` is
  complete. Do not refactor, remove, or replace SQLite-based repositories without explicit instruction.
