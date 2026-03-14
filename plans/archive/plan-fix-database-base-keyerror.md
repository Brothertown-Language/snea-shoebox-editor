# Plan: Fix KeyError `src.database.base` on Production Import

**Status:** ⏳ Pending Approval

## Overview

Production crashes on startup with `KeyError: 'src.database.base'`. This is a circular import
caused by import ordering in `src/database/__init__.py`:

- Line 2: `from .connection import ...` — triggers `connection.py` to load
- `connection.py` line 11: `from .base import Base` — begins loading `src.database.base`
- Line 3 of `__init__.py`: `from .base import Base` — finds `src.database.base` in `sys.modules`
  in a partially-initialized state → `KeyError`

`Base` is only used inside two functions in `connection.py`: `_reset_sequences` (line 621) and
`init_db` (line 644). It is never used at module level.

## Two Valid Approaches

**Option A — Reorder `__init__.py`** (simpler): Move `from .base import Base` to line 1 of
`__init__.py`, before the `.connection` import. `base` is then fully registered before
`connection.py` tries to load it.

**Option B — Lazy import in `connection.py`** (more robust): Remove the module-level
`from .base import Base` from `connection.py` and add `from .base import Base` inside the bodies
of `_reset_sequences` and `init_db`. This breaks the circular dependency structurally and is
immune to future reordering accidents in `__init__.py`.

The user asked whether lazy imports can be used — Option B is the recommended approach.

## Steps (Option B — Lazy Import)

1. 🔄 Pending — In `src/database/connection.py`, remove the module-level `from .base import Base`
   (line 11). Add `from .base import Base` as the first line inside `_reset_sequences()` and
   inside `init_db()`.
2. 🔄 Pending — Verify the fix locally:
   `uv run python -c "from src.database import init_db, get_db_url"` must succeed without error.
3. 🔄 Pending — Run affected unit tests to confirm no regressions.
4. 🔄 Pending — Update plan to reflect completion and archive.
