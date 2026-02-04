<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-03

- Updated AI guidelines with a new critical rule: "DO NOT USE SHELL REDIRECTS - THEY ARE DANGEROUS".
- Reorganized AI guidelines into a modular set of uncompressed files in `.junie/`.
- Reset the Streamlit application to start from scratch.
- Cleared `src/frontend/app.py` and replaced it with a minimal "Hello World" structure.
- All feature phases (3-6) in `docs/development/roadmap.md` are marked as [PENDING].

- [DONE] Refactored project to a monolithic structure (moved src/frontend/app.py to src/frontend/app.py, etc).
- [DONE] Removed Playwright and UI tests.
- [DONE] Committed and pushed all changes to the main branch.

Next Steps:
- [PENDING] Deploy the app to Streamlit Cloud using `src/frontend/app.py` as main file path (Verify automatic deploy).

Critical Reminder:
- Do not mark things as done until the User says they are done. AI is not driving this project.

Completed Tasks:
- UPDATED AI guidelines with the rule against shell redirects.
- RESET Streamlit application to a clean slate.
- UPDATED `docs/development/roadmap.md` to reflect all phases as [PENDING].
- ADDED Aiven connection secrets to `.streamlit/secrets.toml`.
- ADDED Hello World placeholder to `src/frontend/app.py` for deployment.
- DOCUMENTED Organization access settings for Streamlit Cloud in `docs/development/PROD_SETUP.md`.
- ADDED Aiven health check to `src/frontend/app.py`.
- ADDED Environment information display to `src/frontend/app.py`.
- DEPLOYED app to `https://snea-edit.streamlit.app/`.
- REMOVED defunct deployment exclusion mechanism (Streamlit Cloud does not support exclusions).
 - ADDED DNS resolution and socket reachability checks for PostgreSQL to the landing page.
 - TESTED local IPv6 connectivity and enhanced connectivity checks to support dual-stack (IPv4/IPv6) reporting.
 - PURGED all Docker usage and Node.js artifacts from the project and updated documentation.
 - REMOVED Playwright from the project (deleted tests/ui/test_ui.py).
 - [DONE] Updated documentation to clarify that the `src/frontend` folder structure is a mandatory legacy artifact for Streamlit Cloud deployment.
 - [DONE] Resolved Streamlit Cloud "More than one requirements file detected" false-positive warning by adding `.python-version` and updating documentation.
 - [DONE] Aligned development Python version with production (set to 3.12 due to dependency constraints).
 - [DONE] Locked Python version to exactly 3.12.* in `pyproject.toml` and `uv.lock` to ensure Streamlit Cloud uses the correct major/minor release.
 - [DONE] Updated .python-version, pyproject.toml, and documentation to reflect the strict Python 3.12 requirement.
 - [DONE] Committed and pushed changes to main branch.
