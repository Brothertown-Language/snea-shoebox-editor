# TODO

Note for the AI Agent: interview the user for details and then develop the plan for any TODO being implemented.

- [x] Update to capture exceptions and show an appropriate error dialog.
    Date Completed: 2026-03-04
    Completed By: Audit (Junie) — `st.error()` used at 30+ call sites; `show_error()` helper in `ui_utils.py`; Mastodon contact shown on startup errors.

- [ ] Implement logging to SQL table. Use a round robin approach to manage log size.
    Date Completed:
    Completed By:
    Note: Not yet implemented. Standard Python `logging` only. Requires a new plan.

- [x] Any exceptions need to be caught and an error dialog displayed with the Mastodon contact information.
    Date Completed: 2026-03-04
    Completed By: Audit (Junie) — `connection.py:init_db()` catches exceptions and shows `st.error()` with Mastodon contact from secrets.

- [x] Audit for security vulnerabilities related to SQL injection.
    Date Completed: 2026-03-04
    Completed By: Audit (Junie) — One f-string in `text()` at `connection.py:600` uses only SQLAlchemy internal metadata (not user input); no exploitable risk found. See `plan_codebase_audit_2026_03_04.md`.

- [ ] Fix bare `except: pass` → `except OSError: pass` at `src/database/connection.py:372` (pgserver lock-file cleanup).
    Date Completed:
    Completed By:
