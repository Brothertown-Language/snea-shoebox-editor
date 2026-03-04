# Plan: Sanitize Error Dialog in handle_ui_error

## Status: IMPLEMENTED

## Problem

In `src/frontend/ui_utils.py`, `handle_ui_error` shows unsanitized exception details
in the dev expander:

```python
st.error(f"**Technical Error:** {type(e).__name__}: {e}")
```

This leaks raw exception type and message to the UI, violating the sanitization
requirement. The `user_message` parameter is the only safe, sanitized content.

## Fix

**File:** `src/frontend/ui_utils.py` — lines 35–41

Remove the `if is_production()` branch entirely. Always show only `user_message`.
Keep the dev hint about server logs but remove the raw exception display:

```python
    # 2. UI Display (Sanitized)
    st.error(user_message)
    if not is_production():
        st.info("💡 *Full stack trace available in server logs (tmp/streamlit.log).*")
```

## Checklist

- [ ] Replace the `if is_production()` block in `handle_ui_error` with sanitized-only output
- [ ] Verify existing tests pass
