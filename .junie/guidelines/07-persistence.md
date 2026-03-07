# Guideline 07: Persistence & Test Schema Isolation

## DB Path Isolation

- `JUNIE_PRIVATE_DB=true` routes all DB operations to `tmp/junie_db` (Junie-private pgserver instance).
- Without this flag, the app uses `tmp/local_db` (shared local dev instance).
- **EVERY** DB-interactive terminal command or script executed by the agent MUST include `JUNIE_PRIVATE_DB=true`.
  The variable is active when present, regardless of value.
  Correct: `JUNIE_PRIVATE_DB=true uv run python tmp/my_script.py`
  Incorrect: `uv run python tmp/my_script.py`

## Test Schema Isolation

- All test files MUST set `os.environ["JUNIE_PRIVATE_DB"] = "true"` at module level, before any DB import or
  connection is established.
- Scripts that interact with the DB MUST check `MARKER_JUNIE_TERMINAL` at startup (see `03-tool-usage.md`). The
  variable is active when present, regardless of value. If active, the script MUST operate only against the
  test/private schema. If schema isolation cannot be guaranteed, the script MUST abort with a clear error message.
- **Env var roles**: `JUNIE_PRIVATE_DB=true` and `MARKER_JUNIE_TERMINAL` serve distinct roles: `JUNIE_PRIVATE_DB`
  routes the DB connection to `tmp/junie_db` (set in the terminal command). `MARKER_JUNIE_TERMINAL` signals to the
  script that it is running in an agent terminal context and must enforce schema isolation internally. Both MUST be
  set for any DB-interactive agent terminal command.
- NEVER run test or experimental code against the production schema or the shared `tmp/local_db` instance.

## Local DB Preservation

- NEVER delete, truncate, or drop `tmp/local_db` or `tmp/junie_db` unless the user explicitly instructs "reset"
  or "wipe".
- These directories are persistent state — treat them as production data for the purposes of destructive-operation
  approval.

## pgserver Constraints

- The only permitted PostgreSQL server is `pgserver` managed via `uv`. No `pg_config`, `postgres`, or `psql`
  binaries outside the `uv` environment.
- Junie's pgserver instance uses socket-only connections (no TCP) to avoid port conflicts with the local dev instance.
- The `uv`-bundled `pgserver` defines the strict feature envelope. Extensions or contrib modules not present in
  `pgserver` are FORBIDDEN (e.g., `pg_trgm`).
