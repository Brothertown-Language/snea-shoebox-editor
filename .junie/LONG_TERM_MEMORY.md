<!-- Copyright (c) 2026 Brothertown Language -->
<!-- 🚨 SUPREME DIRECTIVE: NO EDITS WITHOUT EXPLICIT APPROVAL ("Go", "Proceed", "Approved") 🚨 -->
# AI Long-Term Memory

This file serves as a persistent memory of critical project context, user preferences, and cross-session decisions that must survive context window truncation.

## CRITICAL PROJECT CONTEXT
- **Identity**: Brothertown Language / SNEA Shoebox Editor.
- **Ethical Mandate**: Preservation and reconstruction of the Southern New England Algonquian language.
- **Data Layer**: MDF (Multi-Dictionary Formatter) standards using PostgreSQL and pgvector.

- **Source Selector Simplification**: All logic attempting to automatically switch the "Target source collection" to newly created sources has been removed to simplify state management and resolve persistent regressions. As of 2026-02-11, the selector remains on the current selection after source creation, requiring manual user selection.
## USER PREFERENCES & HARD CONSTRAINTS
- **SUPREME DIRECTIVE (v8.1)**: Absolute prohibition on modifying any file without explicit, per-step approval. You MUST wait for "Go", "Proceed", or "Approved" for EACH INDIVIDUAL EDIT.
- **PASSIVE EXECUTION MANDATE**: You are forbidden from being proactive. NO cleanup, NO polish, NO unauthorized optimization. Proactivity is considered destructive.
- **AUTHORIZATION CHECK**: Before calling ANY edit tool, you MUST explicitly state in your thoughts: "AUTHORIZATION CHECK: [User Approval String] detected. Proceeding with Step [N]."
- **NO ROADMAP DRIVING**: Do not implement future phases or "cleanup" code without direct orders.
- **PRIVATE DATABASE ONLY**: `JUNIE_PRIVATE_DB=true` is the only acceptable environment for operations.
- **ZERO-TRUST TERMINAL GATE (v3.0)**: Every command must be project-relative, non-compound, prefixed with `uv run` for Python, and DB-isolated. NO `cd`, NO absolute paths, NO `&&`/`|`, NO `>` redirection to root.
- **VCS PERMISSION GATE (v8.1 PROTOCOL)**: Absolute prohibition on performing `git add` or `git commit` in the terminal. Commits are strictly manifest-driven and validated via `bash scripts/pre_commit_check.sh` within a single, mandatory `tmp/commit.sh` script. This validation MUST use `tmp/commit_files.txt` for target selection and include a review of all uncommitted and untracked files in the repository. **Every commit script MUST include `set -e` to ensure security check failures halt the process.** Logical grouping is mandatory. Use of `-f` is a fatal violation. AI is forbidden from executing the commit script; only the user is authorized to review and run it. Autonomous preparation of commit scripts, message files, or ANY git-related artifact is strictly forbidden unless the user explicitly requests it (e.g., "prepare a commit", "stage files").
- **STRICT FILENAME MANDATE**: The staging script MUST always be named `tmp/commit.sh`. Variations (e.g., `commit_task.sh`, `commit_simple.sh`) are strictly prohibited to avoid user confusion.
- **NOConventional Commits**: Never use prefixes like `feat:` or `fix:`.
- **STRICT COMMUNICATION MANDATE (v7.5)**: AI is strictly forbidden from providing raw code fragments, line-by-line edits, or `search_replace` blocks in the chat dialogue. All proposals MUST be presented as high-level, focused overviews of *what* will be changed and *why*. Proactivity in providing code blobs is a violation of the "Zero-Trust" interaction protocol.
- **1-BASED COUNTING ONLY**: Use natural counting (1, 2, 3...) for all plans and lists.
- **MANDATORY MDF SPACING**: Always use double blank lines (`\n\n`) between records in text files and exports.
- **MANDATORY MDF FILENAME PATTERN**: All MDF downloads must use the pattern `<prefix>_<Source>_<GitHubUsername>_<YYYY-MM-DD>_<SSSSS>.txt` via `UploadService.generate_mdf_filename`. This pattern uses underscores as separators, collapses multiple underscores, and allows alphanumeric, dot, at, and dash characters. As of 2026-02-13, the GitHub username is used instead of the email address.

## KEY CROSS-SESSION DECISIONS
- **Deep Inspection Mandate**: Memory-based verification is strictly prohibited. AI must always perform deep inspection of source files before confirming any status or re-evaluating state.
- **MDF Upload Fixes**: Completed fixes for `WidgetKeyedBeforeCreationError` and source selector persistence.
    - Used `default_index` calculation for `st.selectbox` to avoid key conflicts.
    - Implemented session state popping for `upload_active_source_name` and input field keys upon successful source creation to ensure correct UI state and auto-selection.
    - **Source Creation UI**: Implemented persistent success indicators and widget disabling in the sidebar to provide clear feedback after source creation, while maintaining manual selector usage to ensure state stability. Added explicit database re-query via `st.rerun()` to ensure the dropdown remains synchronized with all user changes.
- **Table Maintenance UI Refinement**: Adjusting the Sources table maintenance view to remove the `short_name` column (UI-only) and replace text-based action buttons with icons. As of 2026-02-11, the "Reassign" and "Delete" buttons are mutually exclusive: "Reassign" appears only for sources with records, and "Delete" appears only for empty sources.
- **Phase 5 Stage 3 Refactoring**: Decoupling navigation and redirection logic into `NavigationService`. (Current focus).
- **Security Strategy**: Case-insensitive matching for GitHub identifiers is mandatory due to case mismatches between GitHub API and DB seeds.
- **Phase D-4 Step 1**: Generated `src/seed_data/natick_sample_100_no_diacritics.txt` for base-form matching verification. Verified that stripping diacritics correctly produces a different file when diacritics are present.
- **UI Standard**: Use `st.html()` for all HTML/CSS/JS injections. `unsafe_allow_html=True` is deprecated in this project.
- **Local LLM**: Using Ollama with `qwen2.5-coder:14b` (~9GB, Q4_K_M) for coding assistance in PyCharm. A startup script `scripts/start_ollama_qwen.sh` and PyCharm launcher `launchers/Ollama_Qwen.xml` manage this. Detailed setup instructions for PyCharm plugins are available in `docs/development/ai-setup.md`.
- **Path Resolution**: Always use the mandatory one-liner `cd/git rev` shell fragment `cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"` in shell scripts (including `tmp/commit.sh`) for reliability.
- **Manual Testing Requirement**: The **Full Auth Flow** (OAuth -> Sync -> RBAC -> Navigation tree update) requires manual verification by the user end-to-end, as it cannot be fully automated in the current environment.
- **pgserver Resilience**: Refined the local database startup mechanism in `src/database/connection.py`. Removed the 30-second PID file age check and replaced it with a duration-based "stuckness" detection using `st.session_state["pg_shutdown_first_seen"]`. If the database reports a "shutting down" state for more than 5 seconds across connection attempts, an immediate force-stop (`-m immediate`) and PID file cleanup are triggered to restore availability.
- **Audit Logging**: Updated `AuditService.log_activity` to support an optional `session_id`. This enables linking specific upload/edit events to a batch process. Used in `UploadService` to log `upload_start`, `upload_staged`, and `upload_committed` actions.
- **UI Restoration (MDF Upload)**: Restored the standard Streamlit header, toolbar, and sidebar header in the MDF upload view to ensure accessibility and layout consistency. The custom CSS overrides that previously hid the toolbar, collapsed the header, and shrunk the sidebar header were removed in Feb 2026. Standard top padding and margins were also restored to prevent content from overlapping the toolbar.
- **Persistent User Preferences**: Implemented a database-backed preference system using `UserPreference` model and `PreferenceService`. Currently used to persist `page_size` in the MDF upload review table across sessions for each user.

## FUTURE FEATURE NOTES
- **MDF Download Page — Pending Updates**: The MDF download page must also allow downloading pending updates (from `matchup_queue`) for manual editing, not just committed records. This enables linguists to export staged entries, edit them offline, and re-upload corrected MDF files.

## SESSION INITIALIZATION CHECKLIST
1. **RE-READ** `guidelines.md`, `LONG_TERM_MEMORY.md`, and `VIOLATION_LOG.md`.
2. **ACKNOWLEDGE** by stating "Reviewing AI Guidelines" in your first response.
3. **UPDATE** `LONG_TERM_MEMORY.md` with key decisions.
4. **UPDATE** logs immediately upon any guideline violation.
