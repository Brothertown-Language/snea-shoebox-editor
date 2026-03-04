# Plan: Global Error Handler for Unhandled Exceptions

## Status: IMPLEMENTED

## Problem

Unhandled exceptions (e.g., the FTS tsquery `psycopg2.errors.SyntaxError`) propagate
to Streamlit's default error renderer, which shows the full Python stack trace to the
user instead of the intended user-friendly error dialog with Mastodon contact info.

## Root Cause

`pg.run()` in `streamlit_app.py` (line 201) is called bare — no top-level exception
boundary. Any uncaught exception from any page surfaces as a raw Streamlit traceback.

## Approach: Global `try/except` around `pg.run()`

Wrap `pg.run()` in `streamlit_app.py` with a `try/except Exception` block that:

1. Calls `handle_ui_error(e, ...)` (already imported-capable via `ui_utils`) to log
   the full trace server-side and show a sanitized message in the UI.
2. Appends the Mastodon contact URL from `st.secrets["contact"]["mastodon_url"]`
   (same pattern already used in `_initialize_database()`).

This is the minimal, single-point fix — no per-page changes needed.

## Code Change

**File:** `streamlit_app.py` — replace line 201:

```python
    # Before
    pg.run()

    # After
    try:
        pg.run()
    except Exception as e:
        from src.frontend.ui_utils import handle_ui_error
        mastodon_url = st.secrets.get("contact", {}).get("mastodon_url")
        contact = f" Please report this issue on Mastodon: {mastodon_url}" if mastodon_url else ""
        handle_ui_error(e, f"An unexpected error occurred.{contact}", logger_name="snea.app")
```

## Checklist

- [ ] Wrap `pg.run()` in `streamlit_app.py` with `try/except Exception`
- [ ] Verify `handle_ui_error` shows sanitized message (not stack trace) in production
- [ ] Verify Mastodon URL is included in the error message
- [ ] Verify existing tests pass
