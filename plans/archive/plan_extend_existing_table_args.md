# Plan: Add `extend_existing=True` to All SQLAlchemy Model `__table_args__`

## Problem

On app updates (hot-reload or module re-import), SQLAlchemy raises:

```
sqlalchemy.exc.InvalidRequestError: Table 'iso_639_3' is already defined for this
MetaData instance. Specify 'extend_existing=True' to redefine options and columns
on an existing Table object.
```

## Root Cause

No model class sets `extend_existing=True` in `__table_args__`. When modules are
re-imported (e.g., Streamlit hot-reload), SQLAlchemy sees the table already registered
in the shared `MetaData` and raises.

## Files to Change

| File | Classes | Current `__table_args__` |
|------|---------|--------------------------|
| `src/database/models/core.py` | 4 classes | None |
| `src/database/models/identity.py` | 4 classes | `UserPreference` has tuple |
| `src/database/models/iso639.py` | 1 class | None |
| `src/database/models/meta.py` | 1 class | None |
| `src/database/models/search.py` | 1 class | None |
| `src/database/models/workflow.py` | 2 classes | None |

## Changes

### Pattern A — No existing `__table_args__`

Add after `__tablename__`:

```python
__table_args__ = {'extend_existing': True}
```

Applies to all classes **except** `UserPreference`.

### Pattern B — Existing tuple `__table_args__` (`UserPreference` in `identity.py`)

Append the options dict as the final element of the tuple:

```python
__table_args__ = (
    UniqueConstraint('user_email', 'view_name', 'preference_key', name='uix_user_pref_view_key'),
    {'extend_existing': True},
)
```

## Verification

```
uv run python -m pytest tests/ -v --tb=short
```

---

**Status**: ✅ COMPLETE
