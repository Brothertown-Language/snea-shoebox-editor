# Plan: Fix Sequence Reset — Log+Raise with User-Facing Error Dialog

## Status: IMPLEMENTED

## Problem

`_reset_sequences()` in `connection.py` currently swallows all exceptions silently:

```python
except Exception as e:
    _logger.warning("Sequence reset failed (non-fatal): %s", e)
```

If the reset fails, the app starts anyway with a broken DB — INSERTs will fail with
`UniqueViolation`. The user sees no indication of the problem at startup.

## Solution

Two-layer change:

1. **`_reset_sequences(engine)`** — remove the try/except entirely. Let it raise naturally.
   Log the error before re-raising so the traceback is captured in the log.

2. **`init_db()`** — wrap the `_reset_sequences(engine)` call in a try/except that:
   - Logs the full error via `_logger.error()`
   - Displays a user-facing `st.error()` dialog with the Mastodon contact link
     (read from `st.secrets["contact"]["mastodon_url"]`, same pattern as `streamlit_app.py:104–108`)
   - Re-raises the exception so startup halts and the broken state is not hidden

## Changes

### 1. `src/database/connection.py` — `_reset_sequences(engine)`

- Remove the `try/except` block wrapping the body.
- Add a single `_logger.error(...)` call before re-raise is implicit (no catch = natural raise).
- Update the docstring: remove "non-fatal" language; state that failure raises and halts startup.

### 2. `src/database/connection.py` — `init_db()`

Replace:
```python
_reset_sequences(engine)
```

With:
```python
try:
    _reset_sequences(engine)
except Exception as e:
    mastodon_url = st.secrets.get("contact", {}).get("mastodon_url")
    contact = f" Please report this issue: [{mastodon_url}]({mastodon_url})" if mastodon_url else ""
    _logger.error("Database sequence reset failed at startup — app cannot start safely: %s", e)
    st.error(
        f"⚠️ **Database startup error**: The database sequence reset failed. "
        f"The application cannot start safely — INSERTs would fail with duplicate key errors. "
        f"{contact}"
    )
    raise
```

## Checklist

- [x] `connection.py`: remove try/except from `_reset_sequences()`
- [x] `connection.py`: update `_reset_sequences()` docstring (remove "non-fatal" language)
- [x] `connection.py`: wrap `_reset_sequences(engine)` call in `init_db()` with log+st.error+raise
- [x] Verify Mastodon URL is read from secrets with `.get()` fallback (never hard-coded)
