<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-03

- Finalized PostgreSQL migration (Phase 3) by implementing direct Supabase integration via SQLAlchemy.
- Implemented GitHub OAuth (Phase 4) with client-side token exchange and session persistence via browser `localStorage`.
- Added Admin MDF Upload Tool for bulk record importing.
- Purged sensitive seed data (`natick.txt`) from Git history while maintaining local access for development.
- Refactored `src/frontend/app.py` for direct database interaction, removing the need for a separate backend API layer.
- Updated project guidelines and `.gitignore` for improved security and environment management.

Next Steps:
- Implement optimistic locking for concurrent record editing.
- Implement Full-Text Search (FTS) in PostgreSQL [Phase 5].
- Add detailed visual MDF validation hints in the editor.
- Set up automated deployment to Streamlit Community Cloud.

Completed Tasks:
- REFACTORED `src/frontend/app.py` to use SQLAlchemy/PostgreSQL.
- IMPLEMENTED `src/backend/database.py` with SQLAlchemy models for Supabase.
- PURGED `src/backend/seed_data/natick.txt` from Git history using `git filter-branch`.
- IMPLEMENTED GitHub OAuth flow (Authorize -> Callback -> Token Exchange -> User Sync).
- ADDED bulk MDF upload functionality in the Streamlit UI.
- UPDATED `docs/database/SCHEMA.md` to be fully PostgreSQL/Supabase compatible.
- CLEANED UP Docker-related untracked files and host-resident venvs.
