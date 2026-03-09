# Plan: Full SQL Sanitization Audit

## Status: FINDINGS COMPLETE

## Audit Scope

All `src/**/*.py` files audited for:
- Dynamic strings passed to `text()`, `execute()`, `scalar()`, `fetchall()`, `fetchone()`
- f-strings in ORM `filter()`, `ilike()`, `like()`, `where()`, `having()` calls
- Any user input passed unsanitized into SQL or SQL-adjacent functions

## Tools Used

- `tmp/sql_audit.py` — broad keyword scan (69 hits, all false positives)
- `tmp/sql_audit2.py` — dynamic strings to SQL functions (9 hits, all false positives — `st.text()` / logger calls)
- `tmp/sql_audit3.py` — f-strings in ORM filter/ilike/like (9 hits, assessed below)

---

## Findings

### ✅ SAFE: `connection.py:600` — Dynamic SQL (system-derived only)

```python
text(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table.name}), 1))")
```

- `seq` from `pg_get_serial_sequence()` — PostgreSQL system function, never user input
- `table.name` from `Base.metadata.sorted_tables` — ORM model definitions, never user input
- **Assessment: SAFE**

---

### ✅ SAFE: `ilike()` calls — SQLAlchemy parameterized

All 9 `ilike()` hits in `linguistic_service.py` follow this pattern:

```python
SearchEntry.normalized_term.ilike(f"%{norm_search}%")
Record.mdf_data.ilike(f"%{search_term}%")
```

SQLAlchemy's `ilike()` sends the pattern as a **bound parameter** — the f-string constructs
the `%value%` pattern in Python memory, but it is never interpolated into the SQL string.
PostgreSQL receives it as a parameterized value. **No SQL injection risk.**

Note: `norm_search` is additionally sanitized via `generate_sort_lx()` before use.

---

### ⚠️ VULNERABILITY: FTS `to_tsquery()` — Unsanitized user input

**File:** `src/services/linguistic_service.py` — three identical sites (~388, ~490, ~570)

```python
words = [w.strip() for w in search_term.split() if w.strip()]
fts_query = " & ".join([f"{w}:*" for w in words])
# fts_query passed as :fts_term to to_tsquery('english', :fts_term)
```

**Problem:** tsquery operator characters (`|`, `&`, `!`, `(`, `)`, `:`) within individual
word tokens cause `psycopg2.errors.SyntaxError`. Confirmed in `tmp/streamlit.log`:
`syntax error in tsquery: "|oo:*"`.

The value IS passed as a bound parameter (`:fts_term`) — so this is **not SQL injection**.
However, it is an **unsanitized input causing a runtime crash**.

**Fix (see `plans/fix-fts-pipe-syntax-error.md`):**

Strip tsquery operator characters from each word token before building `fts_query`:

```python
_TSQUERY_UNSAFE = re.compile(r'[|&!():]+')
words = [
    clean for w in search_term.split()
    if (clean := _TSQUERY_UNSAFE.sub('', w).strip())
]
```

Apply at all three sites. `re` is already imported.

---

## Summary

| Location | Issue | Severity | Status |
|---|---|---|---
| `connection.py:600` | Dynamic SQL f-string | None — system-derived | ✅ Safe |
| `linguistic_service.py` ilike ×9 | f-string in ilike() | None — ORM parameterized | ✅ Safe |
| `linguistic_service.py` FTS ×3 | Unsanitized tsquery input | Runtime crash (not injection) | ⚠️ Fix required |

## Action Required

Only the FTS tsquery sanitization fix is needed. Plan: `plans/fix-fts-pipe-syntax-error.md`.
