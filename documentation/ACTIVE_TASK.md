<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-01

Summary:
- Resolved Cloudflare Pages deployment error: "Configuration file cannot contain both 'main' and 'pages_build_output_dir'".
- Unified frontend and backend into a single Worker architecture using `wrangler.toml`.
- Ensured `compatibility_flags = ["python_workers"]` is present and marked as MANDATORY in `wrangler.toml`.
- Updated deployment documentation to reflect the unified Worker architecture.
- Verified that no Node.js/NPM dependencies are introduced, maintaining the 100% Python stack.
- Analyzed CI logs for run 21566990798; identified Cloudflare API error 7003 due to invalid/inaccessible IDs during backend deployment.
- Implemented `scripts/verify_cf_ids.py` to pre-validate Cloudflare Account ID and D1 Database ID using the Cloudflare API before deployment.
- Updated `.github/workflows/deploy.yml` to include the verification step, ensuring the workflow fails early with a clear error message if IDs are incorrect.
- Fixed deploy workflow to use bundled Wrangler by removing `wranglerVersion` (prefer tested, bundled version).
- Fixed CI log collector to use `${{ github.token }}` instead of `secrets.GITHUB_TOKEN` for API calls.
- Added automated CI log parsing and tracking:
  - Enhanced `.github/workflows/collect-ci-logs.yml` to unzip logs, scan for failure markers, and publish a job summary.
  - Uploads parsed analysis artifacts and auto-creates/updates a tracking issue `Deployment status: <run_id>` with findings.
- CI log downloader hardened to be non-mutating:
  - Fails fast if running under `uv run` to avoid resolver-triggered installs.
  - `tqdm` is required but never installed by the script; clear error if missing.
  - Token priority updated to prefer `PROD_GH_TOKEN` over `GH_TOKEN`; improved `.env` parsing.
  - Added CLI flags: `--token`, `--workflow`, `--branch`.
- Added `tqdm` to default Python dependencies in `pyproject.toml` so progress bars are available by default.
- Removed `wranglerVersion` from `.github/workflows/deploy.yml` to use the action-bundled Wrangler for v3 and avoid semver validation during secret upload.
- Migrated Worker deploy to `cloudflare/wrangler-action@v4` to resolve v3 secrets upload API path error (7003) while still using the bundled Wrangler.
- Pinned `wranglerVersion: '4.61.1'` while staying on `wrangler-action@v3` to use the modern CLI and fix secret upload routing.
- Updated `wranglerVersion` to '3' in `.github/workflows/deploy.yml` to resolve "Invalid Version: 3.x" error during secret upload.
- Reverted `wrangler` version to 3.x in `.github/workflows/deploy.yml` for stability, following user approval to downgrade.
- Reverted Pages project name to "snea-shoebox-editor" in `.github/workflows/deploy.yml` to match the existing Cloudflare project and fix the 404 deployment error.
- Verified that while the custom domain is "snea-editor", the underlying Pages project name must remain "snea-shoebox-editor" for successful API routing.

- Updated `docs/deployment/MANUAL_SETUP.md` to reflect Cloudflare's modern "Import a repository" flow for both Workers and Pages, removing all references to the obsolete "Pages" tab in the unified dashboard.
- Explicitly detailed the "Set up your application" fields in `MANUAL_SETUP.md`, specifying mandatory `wrangler` commands for deployment.
- Added mandatory `--project-name snea-editor` to frontend deploy commands in `MANUAL_SETUP.md` to fix "Must specify a project name" error.
- Added `--no-config` to frontend deploy commands in `MANUAL_SETUP.md` to prevent conflict with the Worker-specific `wrangler.toml`.
- Reverted `pages_build_output_dir = "."` in `wrangler.toml` as it conflicts with the `main` key used for the Python Worker.
- Added tips to `docs/deployment/MANUAL_SETUP.md` about the scrollable repository selection box in the Cloudflare dashboard to improve UX discovery.
- Updated `docs/deployment/MANUAL_SETUP.md` to use 'Settings' -> 'Domains & Routes' for Worker custom domains, matching the current Cloudflare UI.
- Updated `docs/deployment/MANUAL_SETUP.md` to specify the mandatory Cloudflare API Token permissions (`Cloudflare Pages`, `Workers Scripts`, `D1`) to resolve authentication error 10000.
- Restored mandatory `npx wrangler pages deploy` commands for the frontend in `MANUAL_SETUP.md` as requested by the user, using the `--project-name snea-editor --no-config` flags.
- Added a troubleshooting note regarding "Authentication error [code: 10000]" and its link to API Token permissions in Section 1.B.
- Clarified what "API Token" refers to in `docs/deployment/MANUAL_SETUP.md` (Cloudflare User API Token), including creation steps and storage in GitHub Secrets.
- Simplified `docs/deployment/MANUAL_SETUP.md` by assuming usage of `bootstrap_env.py`, removing redundant manual steps for GitHub Secrets and `wrangler.toml`.
- Added a "Prerequisites" section to `MANUAL_SETUP.md` for creating the Cloudflare API Token, including a "clean slate" tip for confusing tokens.
- Refined dashboard navigation ("at the top") and permission lists in `MANUAL_SETUP.md` to perfectly match the Cloudflare UI and user feedback.
- Removed pedantic language and non-standard numbering from the deployment guides.

Next Steps:
- DEPRECATE automated subdomain scripts (`bootstrap_domains.py`, `bootstrap_env.py`) in favor of manual setup.
- FOLLOW `docs/deployment/MANUAL_SETUP.md` for manual Cloudflare Worker configuration.
- Update AI Guidelines to reflect private repo status. (Completed)
- If Worker shows Wrangler/secrets issues, prefer bundled Wrangler or pin compatible version; adjust secrets syntax if needed.
- Implement optimistic locking for concurrent record editing.
- Monitor sorting performance as the database grows.
- Continue with further linguistic data processing features.

- Triggered fresh deploy and collector run to verify bundled Wrangler in a private repo context.
- Verified local code structure for unified Worker architecture.
- Using action-bundled Wrangler for maximum compatibility.

CI trigger: verify deployment stability and collector automation.

Completed Tasks:
- Added workflow `collect-ci-logs.yml` and enhanced it to parse logs, publish a summary, upload analysis artifacts, and open/update a tracking issue automatically.
- Made downloader read-only and fail-fast on missing `tqdm` and token; added uv-run guard and CLI flags.
- Updated Python environment to include `tqdm` by default for CI log download progress.
- Switched to action-bundled Wrangler by removing `wranglerVersion` from Worker deploy job in `.github/workflows/deploy.yml`.
- Updated Worker deploy step to `cloudflare/wrangler-action@v4` (bundled Wrangler) after v3 failed uploading secrets with CF API 7003.
- Pinned Wrangler CLI to `4.61.1` using `wrangler-action@v3` to restore compatibility with Cloudflare’s current secrets API.
- Fixed "Invalid Version: 3.x" error by updating `wranglerVersion` to '3' in `.github/workflows/deploy.yml`.
- Reverted `wrangler` to version 3.x in GitHub Actions deployment to resolve "Invalid Version: 4" error.
- Updated `wrangler` to version 4.61.1 in GitHub Actions deployment to satisfy validation requirements while using version 4. (REVERTED)
- Investigated `wrangler` version 4 deployment failure; identified that `wranglerVersion: '4'` in `wrangler-action` caused validation errors during secret upload.
- Updated Wrangler to version 4 in GitHub Actions deployment. (FAILED)
- Fixed GitHub deployment error: enabled `python_workers` compatibility flag in `wrangler.toml`.
- Corrected `main` entry point in `wrangler.toml` to `src/backend/worker.py`.
- Simplified `deploy-backend` job in `.github/workflows/deploy.yml` to use `wrangler.toml` configuration.
- Purge historical contents of `.env` from git history.
- Committed all pending changes before history rewrite.
- Installed `git-filter-repo` to ensure a reliable and fast history purge.
- **SECURITY ROTATION COMPLETE**: Successfully rotated all exposed secrets (GitHub OAuth, GitHub PAT, Cloudflare Tokens) and synchronized them to production via `bootstrap_env.py`.
- Fixed Cloudflare 401 Authentication Error in `bootstrap_env.py` by adding a fallback mechanism to the Global API Key if the User API Token fails verification.
- Updated `docs/development/SECURITY_ROTATION.md` to include rotation instructions for the Cloudflare Global API Key and updated the token name to "snea-editor".
- Ensured all Cloudflare-related environment variables (`PROD_CF_EMAIL`, `PROD_CF_API_KEY`, `PROD_CF_API_TOKEN`) are explicitly covered in rotation and setup documentation.
- Updated `PROD_SETUP.md` example `.env` to include both the Global Key and User Token, with clear prioritization notes.
- Fixed `bootstrap_domains.py` to prioritize `PROD_CF_API_TOKEN` while maintaining fallback logic for Global API Key authentication.
- Fixed `bootstrap_env.py` to correctly pick up GitHub OAuth credentials from `.env` by checking both `PROD_` and `SNEA_` prefixes, resolving the issue where `SNEA_GITHUB_CLIENT_ID` and `SNEA_GITHUB_CLIENT_SECRET` were being skipped.
- Enforced the use of `uv run` for all Python tasks in documentation (`README.md`, `PROD_SETUP.md`, `local-development.md`, `roadmap.md`) and within `bootstrap_env.py` completion advice.
- Removed custom domain configuration from `bootstrap_env.py` and centralized it in `bootstrap_domains.py`.
- Updated `PROD_SETUP.md` to reflect the separation of concerns between `bootstrap_env.py` and `bootstrap_domains.py`.
- Renamed Pages project name from "snea-shoebox-editor" to "snea-editor" in `bootstrap_env.py`, `bootstrap_domains.py`, and `PROD_SETUP.md` for consistency with the frontend domain.
- Fixed `bootstrap_domains.py` to be functional by adding a `__main__` entry point.
- Added missing copyright header to `bootstrap_domains.py`.
- Enhanced `bootstrap_domains.py` to support frontend domain configuration for Cloudflare Pages.
- Improved error handling and API response logging in `bootstrap_domains.py`.
- Improved session cookie persistence by adding a `time.sleep(1)` delay before `st.rerun()` to ensure JavaScript has time to execute in the browser.
- Added fallback logic to set the cookie in the iframe if `window.parent` is inaccessible.
- Fixed session cookie visibility by using `window.parent.document.cookie` via `components.html` to bypass Streamlit iframe sandboxing.
- Updated project documentation (`README.md`, `SETUP.md`, `PROD_SETUP.md`, `local-development.md`) to incorporate the `SECURITY_ROTATION.md` guide and standardize the `.env` file structure.
- Corrected inconsistent port references in `SETUP.md` (updated from `5173` to `8501` for the Streamlit frontend).
- Added explicit warnings about not committing the `.env` file and provided direct links to the security recovery process in all setup guides.
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
- **STABILIZED UNIFIED STLITE ARCHITECTURE**:
    - Completely rebuilt Stlite bundling logic from scratch to ensure robustness.
    - Moved Python source code to a hidden `<script type="text/plain">` tag to prevent raw code exposure on failure.
    - Resolved 500 Internal Server Error in the unified Worker by correctly implementing the static asset fallback in `on_fetch`.
    - Verified 200 OK status for both landing page assets and API endpoints in the unified local environment.
    - Verified local development page accessibility on `http://localhost:8787`.
