# Plan: Show Exception Message in Error Dialog

## Status: IMPLEMENTED

## Problem

The current `handle_ui_error` shows only `user_message`, which is too generic for
data validation errors where the exception message itself is meaningful to the user
(e.g., `psycopg2.errors.SyntaxError: syntax error in tsquery: "|oo:*"`).

## Fix

**File:** `src/frontend/ui_utils.py` — lines 34–37

After `st.error(user_message)`, always show `str(e)` as an additional `st.warning`
(not `st.error`) so the user sees the specific exception message without a raw
stack trace or Python type prefix:

```python
    # 2. UI Display (Sanitized)
    st.error(user_message)
    if str(e):
        st.warning(str(e))
    if not is_production():
        st.info("💡 *Full stack trace available in server logs (tmp/streamlit.log).*")
```

## Checklist

- [ ] Add `st.warning(str(e))` after `st.error(user_message)` in `handle_ui_error`
- [ ] Verify existing tests pass
