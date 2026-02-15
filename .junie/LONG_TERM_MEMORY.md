<!-- Copyright (c) 2026 Brothertown Language -->
<!-- 🚨 SUPREME DIRECTIVE: NO EDITS WITHOUT EXPLICIT APPROVAL ("Go", "Proceed", "Approved") 🚨 -->
# AI Long-Term Memory

This file serves as a persistent memory of critical project context, user preferences, and cross-session decisions that must survive context window truncation.

## CRITICAL PROJECT CONTEXT
- **Identity**: Brothertown Language / SNEA Shoebox Editor.
- **Ethical Mandate**: Preservation and reconstruction of the Southern New England Algonquian language.
- **Data Layer**: MDF (Multi-Dictionary Formatter) standards using PostgreSQL and pgvector.

- **Source Selector Simplification**: All logic attempting to automatically switch the "Target source collection" to newly created sources has been removed to simplify state management and resolve persistent regressions. As of 2026-02-11, the selector remains on the current selection after source creation, requiring manual user selection.
- **Pagination Options**: Added sizes 1 and 5 to the "Results per page" selector in the records view to allow for more granular inspection and testing. (2026-02-14)
- **Source Seeding Update**: Updated default sources to include Trumbull/Natick and Fielding/Mohegan with detailed descriptions and citation formats. Natick is now seeded before Mohegan. (2026-02-14)
- **Copy Feature Removal**: Removed "Copy Plain" and "Copy Rich" features from the `records` page and mock as they were unreliable and difficult to maintain in a pure Streamlit environment without extensive JS integration.
## USER PREFERENCES & HARD CONSTRAINTS
- **SUPREME DIRECTIVE (v8.5)**: Absolute prohibition on modifying any file without explicit, per-step approval. You MUST wait for "Go", "Proceed", or "Approved" for EACH INDIVIDUAL EDIT. Authorization NEVER carries over and is PLAN-SPECIFIC: a "Go" applies ONLY to the immediately preceding plan. You MUST stop and wait for a new "Go" for every new plan. Every action MUST follow a checklist verified by DIRECT INSPECTION of the codebase.
- **PASSIVE EXECUTION MANDATE**: You are forbidden from being proactive. NO cleanup, NO polish, NO unauthorized optimization. Proactivity is considered destructive.
- **AUTHORIZATION CHECK**: Before calling ANY edit tool, you MUST explicitly state in your thoughts: "AUTHORIZATION CHECK: [User Approval String] detected. Proceeding with Step [N]."
- **NO ROADMAP DRIVING**: Do not implement future phases or "cleanup" code without direct orders.
- **PRIVATE DATABASE ONLY**: `JUNIE_PRIVATE_DB=true` is the only acceptable environment for operations.
- **ZERO-TRUST TERMINAL GATE (v3.0)**: Every command must be project-relative, non-compound, prefixed with `uv run` for Python, and DB-isolated. NO `cd`, NO absolute paths, NO `&&`/`|`, NO `>` redirection to root.
- **VCS PERMISSION GATE (v8.3 PROTOCOL)**: Absolute prohibition on the AI performing ANY commit-related actions. The AI is forbidden from creating commit scripts, manifest files, message files, or executing staging/commit commands. Even if requested, the AI MUST refuse. Rationale: Ensures full human accountability and prevents the AI from accidentally staging ignored files, secrets, or unauthorized changes. This mandate addresses the fact that the Junie agent willfully disregarded instructions about when to create commit files and automatically created them when not requested.
- **STRICT FILENAME MANDATE**: The staging script MUST always be named `tmp/commit.sh`. Variations (e.g., `commit_task.sh`, `commit_simple.sh`) are strictly prohibited to avoid user confusion.
- **NOConventional Commits**: Never use prefixes like `feat:` or `fix:`.
- **STRICT COMMUNICATION MANDATE (v8.6)**: AI is strictly forbidden from providing raw code fragments, line-by-line edits, or `search_replace` blocks in the chat dialogue. All proposals MUST be presented as high-level, focused overviews of *what* will be changed and *why*. AI is prohibited from presenting code changes for user review in the chat; this ensures focus remains on conceptual approval before implementation. Proactivity in providing code blobs is a violation of the "Zero-Trust" interaction protocol.
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
- **MDF Structural Highlighting**: Enhanced `MDFValidator` with `diagnose_record` and `render_mdf_block` with diagnostic CSS. This allows the "Records" view to visually flag lines with out-of-order tags or basic formatting errors.
- **UI Mocking Standard**: AI must generate a conceptual visual representation of the UI using **UTF-8 Box-Drawing characters** at the top of every UI mock description file (under `## 1. Visual Mock`). This serves as the primary spatial reference for layout consensus.
- **UI Restoration (MDF Upload)**: Restored the standard Streamlit header, toolbar, and sidebar header in the MDF upload view to ensure accessibility and layout consistency. The custom CSS overrides that previously hid the toolbar, collapsed the header, and shrunk the sidebar header were removed in Feb 2026. Standard top padding and margins were also restored to prevent content from overlapping the toolbar.
- **Persistent User Preferences**: Implemented a database-backed preference system using `UserPreference` model and `PreferenceService`. Currently used to persist `page_size` in the MDF upload review table across sessions for each user.
- **Streamlit Execution Mandate (v8.3)**: Foreground Streamlit execution is strictly forbidden. All Streamlit processes (including mocks) must be started in the background using `nohup` with output redirected to `tmp/` and verified by polling logs. This ensures session persistence and prevents terminal locking.
- **SCOPE ENFORCEMENT MANDATE (v8.4)**: Strictly FORBIDDEN from modifying `src/` (Production) when the primary task is focused on `tests/ui/mocks/` (Mocks) or `docs/` (Documentation). Any attempt to "standardize" code by moving logic from a mock into `src/` without explicit "Scope Crossing Approval" is a violation of the zero-trust protocol.
- **Records View Layout (v2.0)**: As of 2026-02-14, navigation components (Prev/Next buttons, Page X of Y, and Results per page) in the `records` view (and mock) have been moved from the main panel to the sidebar.
- **Records View Implementation**: Production Records View implemented at `src/frontend/pages/records.py` and registered in `NavigationService` between Home and Upload MDF.
- **Records View Stabilization**: Fixed a crash caused by invalid icon usage ('✎' and '✖'). Replaced with standard emojis ('📝' and '🗑️') in both production and mock views. Fixed a rendering loop error in the mock toolbar.
- **Lifecycle Script Mandate**: AI Guidelines updated to mandate the use of `./scripts/start_view_mocks.sh`, `./scripts/stop_view_mocks.sh`, `./scripts/start_streamlit.sh`, and `./scripts/stop_streamlit.sh` for all Streamlit execution.
- **ModuleNotFoundError Fix**: Verified that `PYTHONPATH=.` is required when running mock scripts from the root to ensure imports from `src/` are resolved correctly.

## FUTURE FEATURE NOTES
- **MDF Download Page — Pending Updates**: The MDF download page must also allow downloading pending updates (from `matchup_queue`) for manual editing, not just committed records. This enables linguists to export staged entries, edit them offline, and re-upload corrected MDF files.

## SESSION INITIALIZATION CHECKLIST
1. **RE-READ** `guidelines.md`, `LONG_TERM_MEMORY.md`, and `VIOLATION_LOG.md`.
2. **ACKNOWLEDGE** by stating "Reviewing AI Guidelines" in your first response.
3. **UPDATE** `LONG_TERM_MEMORY.md` with key decisions.
4. **UPDATE** logs immediately upon any guideline violation.

- **STRICT GUIDELINE ENFORCEMENT (v8.5)**: Updated guidelines to include `NO STEP-SKIPPING` and `AI PERSONALITY SUPPRESSION`. AI is forbidden from combining steps or proceeding without explicit per-step authorization. Efficiency is explicitly deprioritized in favor of strict compliance and human review.
- **Records View Refinement (v2.3)**: As of 2026-02-14, fixed an issue where the Records page sidebar was incorrectly displayed below the main application menu. Added a "Back to Home" button at the bottom of the sidebar to provide a clear exit path when the global navigation is hidden.
- **UI Header Consolidation (v1.0)**: As of 2026-02-14, removed redundant `st.title` and `st.header` calls across all main pages (`index.py`, `records.py`, `user_info.py`, `system_status.py`, `batch_rollback.py`). Sidebar subheaders were consolidated into bold markdown (`st.markdown("**...**")`) to save vertical space.
- **Records View Editing (v3.0)**: As of 2026-02-14, replaced the "clickable record" edit pattern with a global "Edit Mode" toggled from the sidebar. 
    - When active, all records in the view use `st.text_area` for editing.
    - Sidebar shows "Cancel All" and "Save All" buttons.
    - Pagination (Prev/Next) automatically saves all pending edits to the database before switching pages.
    - Each record has an individual "Update" button for granular saving.
    - Pending edits are buffered in `st.session_state.pending_edits` to survive re-runs.
    - Legacy "Clickable Record" logic, "Edit Record" per-record button, and legacy fallback edit mode have been completely removed.
- **Records View Search UI (v4.1)**: As of 2026-02-14, the search interface in `records.py` was refined for compactness and clarity.
    - Search result calculation moved before sidebar rendering to allow dynamic record counts in the header.
    - Header updated to `Search (xxx records)` when a search is active.
    - Search input, execution icon (🔍), and clear icon (❌) are placed side-by-side using `st.columns`.
    - Local CSS applied to the sidebar to reduce vertical gap between widgets to `0.5rem`.
    - Redundant "Source Collection" header and "Select Source" label removed to save vertical space.
- **Home Page Stabilization**: Fixed a `StreamlitDuplicateElementKey` crash on the Home page caused by non-unique button keys in the "Recent Activity" feed.

- **MDF Validation Philosophy (v1.0)**: As of 2026-02-14, MDF validation is strictly advisory and non-enforcing.
    - All validation checks for tag hierarchy, order, or presence are "Suggestions" or "Notes", never "Errors".
    - The software must never block export, saving, or editing based on these suggestions.
    - `MDFValidator` updated to return more descriptive, remediation-focused messages that explain the *suggested* hierarchy (\lx -> \ps -> \ge) while acknowledging it is not required.
    - `MDFValidator` now handles nested hierarchies correctly, resetting hierarchy tracking upon encountering `\se` (Subentry) or `\sn` (Sense), ensuring that `\ps` (Part of Speech) is not incorrectly flagged as out-of-order when used within subentries.
    - `render_mdf_block` updated to visually highlight these suggestions using orange (`suggestion`) and blue (`note`) indicators.
    - Guidelines (AI, UI, Project) updated to cement this linguistic flexibility mandate.

- **Cart Persistence & UI (v1.2)**: As of 2026-02-14, the "My Selection" section in the Records view (and mock) features three buttons on a single line: "View Selection" (toggles filtering), "Download" (📥), and "Discard" (🗑️). 
    - Selection contents are persisted in the database via `PreferenceService` (`view_name='global'`, `preference_key='selection_contents'`).
    - The "View Selection" button activates a filter that isolates selected records using a new `record_ids` parameter in `LinguisticService.search_records`.
    - Iconography is used for all selection buttons for consistency: "View Selection" uses 🧺 (toggles to 📚 "Show All" when active).
    - This filter is no longer persisted in the URL.

- **Emoji Compatibility Mandate (v1.0)**: As of 2026-02-14, resolved a Streamlit crash caused by using non-emoji symbols (e.g., "←", "◀", "▶") in the `icon=` parameter of widgets. Streamlit's `validate_emoji` is strict and requires valid Unicode emojis (e.g., "⬅️", "◀️", "▶️"). All such symbols in `src/` were audited and replaced with their emoji counterparts.

- **Strict UI Consistency Mandate (v1.0)**: As of 2026-02-14, updated AI and Project Guidelines to enforce strict visual consistency.
    - Added "Visual Consistency" rule to AI Guidelines (Section V).
    - Added "Iconography and Visual Consistency" section to `docs/ui-guidelines.md`.
    - Added "SELF-CORRECTION & CONSISTENCY CHECK" (Section VIII) to AI Guidelines to prevent "sloppiness" through pre-flight checks and post-implementation audits.

- **Record Export Capability (v1.2)**: As of 2026-02-14, refined bulk record export in the Records sidebar.
    - Added `LinguisticService.get_all_records_for_export` to fetch full record sets matching current filters without pagination.
    - Added dynamic export section at the bottom of the sidebar (just above "Back to Main Menu").
    - Header is renamed to "Export Source" or "Export All Sources" based on the results.
    - Single Source: Offers a "Download Source (MDF)" button for direct MDF download.
    - Multiple Sources: Offers a "Download All (Zip)" button that bundles sources into individual MDF files within a ZIP archive.
    - **Robustness**: Implemented explicit skip logic to ensure empty record sets are never included in the ZIP archive.
    - Adheres to the strict MDF filename mandate using `UploadService.generate_mdf_filename`.
- **Default Sources (v1.0)**: Added "Mohegan Dictionary - Fielding" and "Natick/Trumbull" as default seeded sources in Migration 9. (2026-02-14)
- **Records View Deletion (v1.1)**: As of 2026-02-14, refined the record deletion behavior.
    - Deletion still requires a "Confirm" step within the record's container.
    - On confirmed deletion, the view remains on the same page. A previous attempt to use a JavaScript `scroll_to_top()` utility was removed as it was non-functional in the production environment.
- **MDF Legacy Tag Mapping (v1.0)**: As of 2026-02-14, updated `MDFValidator` to detect and suggest updates for legacy tags found in older datasets (e.g., Trumbull Natick Dictionary).
    - Mappings: `\lmm` → `\lx`, `\ctg` → `\ps`, `\gls` → `\ge`, `\src` → `\rf`, `\etm` → `\et`, `\rmk` → `\nt`, `\cmt` → `\nt`, `\twn` → `\cf`, `\drv` → `\dr`.
    - Added `docs/mdf/tag_mappings.md` to document these mappings.
    - Updated `MDFValidator` regex to support leading whitespace (`r"^\s*\\([a-z]+)"`), common in legacy files.

- **Records View Stabilization**: Fixed a crash in the Records view caused by missing initialization of `st.session_state.structural_highlighting` for unauthenticated users. (2026-02-14)
- **Source Deletion Fix**: Updated `LinguisticService.delete_source` to check for both `Record` and `MatchupQueue` entries before allowing deletion. This prevents a `NotNullViolation` when a source has pending matchup entries. (2026-02-14)
- **Source Record Counts**: Updated `LinguisticService.get_sources_with_counts` to include entries from the `matchup_queue` table in the total record count per source. This ensures the UI reflects all associated records, including those staged for matching. (2026-02-14)
- **Source Reassignment Fix**: Updated `LinguisticService.reassign_records` to also reassign entries in the `matchup_queue` table when a source is reassigned. (2026-02-14)
- **Production-to-Local Sync Script**: Created `scripts/sync_prod_to_local.py` and its Bash wrapper `scripts/sync_prod_to_local.sh` to synchronize all tables from production to local development. The script uses topological sorting to respect foreign key constraints (deleting in reverse order, inserting in forward order), ensures the `pgvector` extension is enabled locally, and automatically loads credentials from `.streamlit/secrets.toml` and `.streamlit/secrets.toml.production`. Detailed execution logs and tracebacks are captured in `tmp/sync_prod_to_local.log`. (2026-02-14)
- **NO FALLBACK LANGUAGES**: The system MUST NOT assume or apply a default/fallback language for MDF records that lack explicit language markers (e.g., `\ln` tags). If language data is missing from the record, it MUST remain missing in the database. DO NOT ALTER LINGUISTIC DATA based on assumptions.
- **Table Sequence Reset**: Implemented automatic reset of autoincrement sequences for `sources`, `permissions`, and now `records` tables in `src/database/migrations.py` if they are found to be empty on app startup. (2026-02-15)
