<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-04

- [DONE] Created `scripts/start_streamlit.sh` for persistent background execution.
- [DONE] Updated AI guidelines to mandate persistent background execution that survives session exit.
- [DONE] Fixed multipage navigation error by using file paths in `st.Page` and adding `if __name__ == "__main__":` blocks to page files.
- [DONE] Updated `src/frontend/app.py` with docstrings explaining the navigation pattern.
- [DONE] Updated AI guidelines (`.junie/`) with Streamlit multipage navigation standards.
- [DONE] Committed all changes.
- [DONE] Restarted Streamlit using the persistent start script.

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
 - ADDED native Streamlit OAuth2 reference documentation to `docs/github/native-oauth-reference.md`.
 - UPDATED `docs/github/github-oauth-doc.md` to reflect native auth callback requirements and link to the new reference.
