# Plan: SQL Injection Audit

## Status: FINDINGS COMPLETE — No Vulnerabilities Found

## Audit Methodology

- AST-based scan of all `src/**/*.py` files using `ast` module
- Two passes:
  1. Broad scan: f-strings, `%`-format, `.format()`, string concatenation near SQL keywords
  2. Targeted scan: dynamic strings passed directly to `text()`, `execute()`, `scalar()`, `fetchall()`, `fetchone()`

## Findings

### ✅ No SQL Injection Vulnerabilities Found

All SQL queries in the codebase use **SQLAlchemy parameterized queries** via `text()` with bound parameters (`:param` syntax) or ORM methods. No user-supplied input is interpolated directly into SQL strings.

### One Dynamic SQL String — Reviewed and Safe

**File:** `src/database/connection.py:600`

```python
text(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table.name}), 1))")
```

**Assessment: SAFE — Not a vulnerability.**

- `seq` is the return value of `pg_get_serial_sequence(:tbl, 'id')` — a PostgreSQL system function that returns a fully-qualified sequence name (e.g., `public.records_id_seq`). It is never derived from user input.
- `table.name` is sourced from `Base.metadata.sorted_tables` — SQLAlchemy ORM-defined table names, hardcoded in the application's model definitions. Never derived from user input.
- Both values are internal, system-derived identifiers with no user-controlled path.

### False Positives Eliminated

The broad scan flagged 69 items; all were:
- `st.text()` / `status_container.text()` — Streamlit UI display functions (not SQL)
- `logger.info()` / `logger.error()` / `logger.warning()` — logging calls (not SQL)
- UI string construction for labels, keys, messages (not SQL)

## Recommendation

No code changes required. The codebase is clean with respect to SQL injection:

- All parameterized queries use SQLAlchemy's `text()` with `:param` bound parameters
- ORM queries use SQLAlchemy model methods exclusively
- No raw string interpolation of user input into SQL

## TODO Completion

This audit satisfies the TODO item:
> `- [ ] Audit for security vulnerabilities related to SQL injection.`
