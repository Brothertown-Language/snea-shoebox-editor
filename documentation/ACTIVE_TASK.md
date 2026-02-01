<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-01

Summary:
- Ensured all records' homonym numbers (`\hm`) and `sort_key` are synced with their MDF data via a migration in `src/backend/worker.py`.
- Updated `src/backend/mdf_parser.py` and `src/frontend/app.py` to extract `\hm` (defaulting to 1).
- Added `hm` column to `records` table in SQLite database.
- Implemented database migration to populate `hm` from existing MDF records.
- Updated `/api/records` endpoint to sort by `sort_key` (ASC), `hm` (ASC), then `source_name` (ASC).
- Implemented offset-based pagination in backend and frontend to replace fixed limits.
- Added `limit` and `offset` query parameter support to `/api/records` backend endpoint.
- Added pagination controls (Next/Previous) to Streamlit frontend sidebar.
- Synced pagination state with browser URL query parameters.
- Implemented NFD-form sorting for linguistic records.
- Added `sort_key` column to `records` table to store normalized form (ignores leading punctuation, keeps diacritics).
- Updated `worker.py` with `get_sort_key` utility and database migration logic.
- Treated '∞' as a valid sorting character (non-punctuation) as required for Algonquian records.
- Removed single quote (') from sorting keys entirely, including mid-word positions.
- Ensured records are sorted by `sort_key` in the API.

Next Steps:
- Implement optimistic locking for concurrent record editing.
- Monitor sorting performance as the database grows.
- Continue with further linguistic data processing features.

Completed Tasks:
- Improved session cookie persistence by adding a `time.sleep(1)` delay before `st.rerun()` to ensure JavaScript has time to execute in the browser.
- Added fallback logic to set the cookie in the iframe if `window.parent` is inaccessible.
- Fixed session cookie visibility by using `window.parent.document.cookie` via `components.html` to bypass Streamlit iframe sandboxing.
- Implemented persistent login tokens using browser cookies.
- Added session restoration from cookies in the frontend `main()` function.
- Implemented `/api/me` endpoint in the backend for user profile retrieval.
- Removed "Logged in as" and "Logout" button from the main view (now only in sidebar).
- Reverted hash-based routing to query-parameter-based routing (?view, ?id, ?page) as requested.
- Updated record homonym numbers based on the MDF records.
- Implemented secondary sorting by homonym number (\hm) and source name.
- Implemented offset-based pagination in backend and frontend.
- Added record list view and shared link support.
- Synchronized selector state with browser URL.
- Implemented NFD-form sorting for linguistic records.
- Added `sort_key` column to `records` table to store normalized form.
- Updated `worker.py` with `get_sort_key` utility and database migration logic.
- Treated '∞' as a valid sorting character (non-punctuation).
- Removed single quote (') from sorting keys entirely.
- Ensured records are sorted by `sort_key` in the API.
