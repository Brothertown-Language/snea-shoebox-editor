# Plan: Lazy Imports — Guideline, Pydoc, Code Comments, and Fix

**Status:** ⏳ Pending Approval

## Scope

Three areas of change:
1. **Project guideline** — add a "Lazy Imports" rule to `05-code-standards.md`
2. **Code fix** — apply the lazy import pattern to `src/database/connection.py` (the active bug)
3. **Pydoc / comments** — update docstrings and inline comments in affected files to document the pattern

No logic changes. No new tests required (import-order fix; existing tests cover the affected functions).

---

## Steps

### 1. 🔄 Pending — Update `05-code-standards.md`

Add a new **Lazy Imports** bullet under `## Design Principles`:

> **Lazy Imports**: Use lazy (deferred) imports — `import` or `from … import` inside a function
> body — as the standard guard against circular imports and module initialization errors. Any
> cross-package import that could create a circular dependency MUST be lazy. Module-level imports
> are reserved for stdlib, third-party packages, and intra-module symbols that carry no circular
> risk.

---

### 2. 🔄 Pending — Fix `src/database/connection.py`

- Remove module-level `from .base import Base` (line 11).
- Add `from .base import Base` as the first statement inside `_reset_sequences()` and `init_db()`.
- Update the module-level docblock / inline comment near the import block to note that `.base` is
  imported lazily inside functions to avoid circular initialization.

---

### 3. 🔄 Pending — Update `src/database/__init__.py` comment

Add a brief inline comment on the `from .base import Base` line noting that this import is safe
here because `connection.py` no longer imports `base` at module level (lazy import pattern).

---

### 4. 🔄 Pending — Verify

Run:
```
uv run python -c "from src.database import init_db, get_db_url; print('OK')"
```
Must print `OK` with no errors.

---

### 5. 🔄 Pending — Archive plan

Move plan to `plans/archive/` and update `memory.md`.
