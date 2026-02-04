<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-03

- Updated AI guidelines with a new critical rule: "DO NOT USE SHELL REDIRECTS - THEY ARE DANGEROUS".
- Reorganized AI guidelines into a modular set of uncompressed files in `.junie/`.
- Reset the Streamlit application to start from scratch.
- Cleared `src/frontend/app.py` and replaced it with a minimal "Hello World" structure.
- All feature phases (3-6) in `docs/development/roadmap.md` are marked as [PENDING].

Next Steps:
- [DONE] Deploy the app to Streamlit Cloud using `src/frontend/app.py` as main file path.
- [DONE] Configure production secrets in Streamlit Cloud UI with `https://snea-edit.streamlit.app`.
- Re-implement Database integration in the new Streamlit app (Supabase secrets added).
- Re-implement GitHub OAuth flow.

Completed Tasks:
- UPDATED AI guidelines with the rule against shell redirects.
- RESET Streamlit application to a clean slate.
- UPDATED `docs/development/roadmap.md` to reflect all phases as [PENDING].
- ADDED Supabase connection secrets to `.streamlit/secrets.toml`.
- ADDED Hello World placeholder to `src/frontend/app.py` for deployment.
- DOCUMENTED Organization access settings for Streamlit Cloud in `docs/development/PROD_SETUP.md`.
- ADDED Supabase health check to `src/frontend/app.py`.
- ADDED Environment information display to `src/frontend/app.py`.
- DEPLOYED app to `https://snea-edit.streamlit.app/`.
- VERIFIED deployment exclusions mechanism and migrated to official `config.toml`.
