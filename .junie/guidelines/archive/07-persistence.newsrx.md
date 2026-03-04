# PostgreSQL & SQLAlchemy Standards

Applies to `pubmed_data_3` and all new persistence code.

## Repository Usage (MANDATORY)

- ALL DB operations MUST go through a `Repository` class (e.g., `PubmedArticleRepository`). Direct `session.execute()`/
  `session.query()` outside Repository is PROHIBITED in `src/` modules, notebooks, and tests.
- Repositories encapsulate all ORM-to-Domain and Domain-to-ORM logic.
- `tmp/` and `scripts/` diagnostic scripts may use direct session access only for one-off exploration that does not
  inform production logic.

## Driver & ORM

- psycopg 3 (`psycopg`) only. No `psycopg2`/`psycopg2-binary`. Dialect: `postgresql+psycopg://`.
- SQLAlchemy 2.0+ only: `DeclarativeBase`, `Mapped[]`, `mapped_column()`. Legacy patterns prohibited.
- All DB ops through `Session`, not raw `connection.execute()`.

## PgServerManager (ZERO TOLERANCE)

- ALWAYS use as context manager (`with PgServerManager(...) as pg_manager:`). NEVER manual `start()`/`stop()` or raw
  connection strings.
- **Conflict Prevention**: Don't start a separate test `pgserver` on TCP if a production instance is running. Check
  for a running production instance by verifying whether the production `pgdata` path's `postmaster.pid` exists before
  starting a test instance on TCP.
- **Persistent/integration tests**: Use the production `pgserver` instance with a dedicated test schema (`junie_test`
  schema) for schema isolation.
- **Ephemeral tests** (short-lived instance and tables removed after test completion): Use a separate `pgserver`
  instance in socket-only mode (no TCP port).
- Every backfill/migration script MUST use `PgServerManager` via `with`. Use `pgserver` for embedded PostgreSQL in local
  dev.

## Database Location

- `pgdata` location: outside the project root (user-managed) or inside the project only in `tmp/` (e.g.,
  `tmp/db/pgdata`).
- Forbidden: `pubmed_data_*/db/`, `src/`, `notebooks/`, or anywhere inside project outside `tmp/`.
- Before passing a `pgdata` path to `PgServerManager`, the agent MUST verify the path is within `tmp/` or outside the
  project root. Do not rely solely on `PgServerManager` to enforce this.
- `PgServerManager` must enforce this rule and fail-fast on forbidden paths.

## Schema Standards

- `Text` for all variable-length strings. `String(N)` only for genuinely fixed-length (ISO dates, fixed-format IDs).
- Migration versions: date-based `yyyymmddhhmmss` format in UTC. Simple increments prohibited.

## Diagnostics

- NEVER modify production files to diagnose data. Use standalone scripts in `tmp/` or notebooks.
- DB enum values: see Strict Enum Mapping in `05-code-standards.md`.

## Backward Compatibility

- `sqlbind` and existing SQLite repository classes remain untouched until the `pubmed_data_3` migration to `pgserver` is
  complete. Do not refactor, remove, or replace SQLite-based repositories without explicit instruction.
