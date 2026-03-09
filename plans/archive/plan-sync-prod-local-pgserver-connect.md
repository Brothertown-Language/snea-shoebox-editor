# Plan: Fix sync_prod_to_local.py — Use Canonical pgserver DB Path
**Status:** ✅ Complete

## Problem

`scripts/sync_prod_to_local.py` has a custom `_ensure_pgserver()` function that
reimplements the local DB path logic (`tmp/local_db` vs `tmp/junie_db`) inline,
duplicating the canonical logic in `src.database.connection._get_local_db_path()`.
This divergence means any future change to the canonical path logic will not be
reflected in the sync script, causing connection failures.

## Fix

**1 step (flat plan).**

### Step 1 — Replace inline db path logic with `_get_local_db_path` import ✔️ Completed

**File:** `scripts/sync_prod_to_local.py`

**What:** In `_ensure_pgserver()`, replace the inline `is_junie / db_dir / db_path`
block with a call to `src.database.connection._get_local_db_path()`.

**Why:** Eliminates duplication; sync script will always use the same DB path
resolution as the rest of the repository.

**Change detail:**

Remove:
```python
is_junie = os.getenv("JUNIE_PRIVATE_DB", "").lower() not in ("", "false", "0")
db_dir = "junie_db" if is_junie else "local_db"
db_path = project_root / "tmp" / db_dir
db_path.mkdir(parents=True, exist_ok=True)
```

Replace with:
```python
from src.database.connection import _get_local_db_path
db_path = _get_local_db_path()
db_path.mkdir(parents=True, exist_ok=True)
```

Note: `_get_local_db_path()` uses `Path.cwd()` — the shell wrapper already
`cd`s to project root before invoking the script, so this is safe.

No other changes. No new tests required (script-level integration; path logic
is already tested via connection.py).

## Scope

`scripts/sync_prod_to_local.py` only. No `src/` changes.
