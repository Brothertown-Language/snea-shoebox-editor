<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-03

- Updated AI guidelines with a new critical rule: "DO NOT USE SHELL REDIRECTS - THEY ARE DANGEROUS".
- Reorganized AI guidelines into a modular set of uncompressed files in `.junie/`.
- Reset the Streamlit application to start from scratch.
- Cleared `src/frontend/app.py` and replaced it with a minimal "Hello World" structure.
- All feature phases (3-6) in `docs/development/roadmap.md` are marked as [PENDING].

Next Steps:
- [PENDING] Deploy the app to Streamlit Cloud using `src/app.py` as main file path.
- [PENDING] Configure production secrets in Streamlit Cloud UI with `https://snea-edit.streamlit.app`.
- Re-implement Database integration in the new Streamlit app (Aiven secrets added).
- Re-implement GitHub OAuth flow.
- Committed and pushed infrastructure and roadmap updates to main.

Critical Reminder:
- Do not mark things as done until the User says they are done. AI is not driving this project.

Completed Tasks:
- UPDATED AI guidelines with the rule against shell redirects.
- RESET Streamlit application to a clean slate.
- UPDATED `docs/development/roadmap.md` to reflect all phases as [PENDING].
- ADDED Aiven connection secrets to `.streamlit/secrets.toml`.
- ADDED Hello World placeholder to `src/app.py` for deployment.
- DOCUMENTED Organization access settings for Streamlit Cloud in `docs/development/PROD_SETUP.md`.
- ADDED Aiven health check to `src/app.py`.
- ADDED Environment information display to `src/app.py`.
- DEPLOYED app to `https://snea-edit.streamlit.app/`.
- REMOVED defunct deployment exclusion mechanism (Streamlit Cloud does not support exclusions).
 - ADDED DNS resolution and socket reachability checks for PostgreSQL to the landing page.
 - TESTED local IPv6 connectivity and enhanced connectivity checks to support dual-stack (IPv4/IPv6) reporting.
 - PURGED all Docker usage and Node.js artifacts from the project and updated documentation.
 - REMOVED Playwright from the project (deleted tests/ui/test_ui.py).
