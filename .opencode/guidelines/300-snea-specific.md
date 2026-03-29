# SNEA-Specific Guidelines

Project-specific rules for Snea-Shoebox-Editor. These override or supplement the core guidelines.

## Zero-Trust Terminal Gate

- **LOCAL DB PRESERVATION**: NEVER delete, truncate, or drop the local development database (`tmp/local_db` or `tmp/junie_db`). Strictly FORBIDDEN unless user explicitly instructs "reset" or "wipe".
- **PRIVATE DB**: Every DB-interactive command MUST include `JUNIE_PRIVATE_DB=true`. The variable is active when present, regardless of value.
- **STREAMLIT EXECUTION**: NEVER run Streamlit as a foreground app. Background only via `nohup`. Any blocking `streamlit run` call is a CRITICAL VIOLATION.
- **RAW STRINGS FOR MDF**: When writing tests or code that include MDF tags (e.g., `\lx`, `\ln`) in docstrings or strings, ALWAYS use raw strings (`r"""..."""` or `r'...'`) to avoid `SyntaxWarning: invalid escape sequence`.
- **EXCLUSIVE PGSERVER**: No PostgreSQL server except `pgserver` via `uv`. All local dev and testing MUST use the `pgserver` instance managed by the application. No `pg_config`, `postgres`, or `psql` binaries outside `uv` env.
- **ENVELOPE AUTHORITY**: The `uv`-bundled `pgserver` defines the strict feature envelope.
  - **FORBIDDEN**: PostgreSQL `pg_trgm` (Trigram search) — incompatible with `pgserver` envelope.
  - No feature (extension, operator class, contrib module) may be used unless it exists identically in both local and production environments.
- **ENVIRONMENT PARITY**: Local dev MUST support 100% of production features. No `try-except` to ignore local deficiencies. No conditional feature branches between dev and production. Codebase MUST be identical on both.
- **UV ONLY**: `uv` for all dependency management. No Conda, no `pip`.

---

## Scope Enforcement

- **PRODUCTION/MOCK ISOLATION**: Strictly FORBIDDEN from modifying `src/` when task is focused on `tests/ui/mocks/` or `docs/`. Any scope crossing requires explicit "Scope Crossing Approval".
- **DISCRETE EXECUTION**: Complex tasks MUST be broken into discrete, verifiable steps. Log progress in memory or plan status. FORBIDDEN from attempting to finish a complex task in a single large operation.

---

## Development Workflow

- **STREAMLIT LIFECYCLE SCRIPTS**: Use provided scripts for all Streamlit execution:
  - Main App: `./scripts/start_streamlit.sh` and `./scripts/kill_streamlit.sh`
  - Mocks: `./scripts/start_view_mocks.sh` and `./scripts/stop_view_mocks.sh`
  - Stop existing instance before starting a new one. Never run more than one main app or one mock viewer.
  - **PORT PROTOCOL**: Main App → port 8501. Mock Viewer → port 8502.
- **PATH RESOLUTION BOILERPLATE**: See `210-scripting.md` § Script Headers for the mandatory shell and Python root resolution patterns.
- **TESTING STANDARDS**:
  - Terminal only. Never simulate.
  - Schema Change Verification: always check `tmp/streamlit.log` for schema changes (migrations, extensions).
  - Reproduction First: see `070-environment.md` § Testing.
  - 3-Strike Rule: after 3 failed fix attempts, stop and ask the user.
  - Lazy Execution: forbidden from pre-generating expensive data in UI loops.
- **MIGRATION VERSIONING**: `YYYYMMDDSSSSS` format (Year, Month, Day, seconds-since-midnight). MUST reflect actual creation time. Incremental versioning strictly FORBIDDEN.

---

## VCS Protocol

- **COMMIT PROTOCOL**: AI MUST NOT proactively create commit message files, commit scripts, stage files, or execute any `git commit` related commands. These actions are permitted only when explicitly requested by the user. See `111-git-commit-workflow.md` for full commit preparation rules.

---

## UI Patterns

- **Sidebar Controls**: Detail view controls (nav, filters, buttons) MUST be in `st.sidebar`.
- **Icon Buttons**: Prefer icons for common actions to conserve space.
- **Visual Consistency**: Strict iconography and labeling consistency within component groups. If a group uses icons (e.g., 📥, 🗑️), all new elements in that group MUST use icons.
- **MDF Rendering**: Always use `render_mdf_block()` for record text. No `st.code()`.
- **HTML Injection**: `st.html()` only. `unsafe_allow_html=True` is deprecated in this project.
- **Linguistic Diff Icons**: Contiguous deletions+additions → `→` (Transformation, Blue). Isolated deletions → `×` (Red). Isolated additions → `+` (Green).
- **Line Indicators**: SVG-based line indicators MUST use "Large Format" pattern: `background-size` ~`2.2rem 1.5em`, centered vertically, `padding-left` ~`2.5rem`.
- **Semantic Precision**: Use descriptive structural labels (e.g., "Main Menu") not colloquial ones (e.g., "Home").
- **Mocking**: Generate/update mocks in `tests/ui/mocks/` only from explicit instructions. Mocks MUST remain runnable. Use `st.container`, `st.expander`, `st.tabs` for composite layouts.
- **Per-Record Controls**: Per-record action controls (e.g., edit, delete) MUST be placed inline with the record, not in a sidebar or global toolbar. All new views MUST follow this pattern for any action that targets a specific record.
- **Pre-flight & Consistency Audit**: Before any UI change, verify design matches surrounding patterns. After implementing, audit for mismatched icons, inconsistent spacing, or redundant labels.

---

## MDF Standards

- **Record Spacing**: Double blank lines (`\n\n`) MANDATORY between records.
- **Core Tags**: `\lx` (Lexeme), `\ps` (POS), `\ge` (Gloss), `\inf` (Inflection).
- **Suggested Hierarchy**: `\lx` → `\ps` → `\ge`. Advisory only.
- **NON-ENFORCEMENT POLICY**: All MDF validation MUST be advisory only. NEVER block export, editing, or any operation based on tag order or presence. Use "Suggestion" or "Note" framing — never "Error".
- **NO FALLBACK LANGUAGES**: NEVER assume or apply a default/fallback language for records lacking `\ln` tags. If language data is missing, it MUST remain missing. DO NOT ALTER LINGUISTIC DATA based on assumptions.
- **TAG INTEGRITY**: FORBIDDEN from suggesting or implementing fictional MDF tags. All tags MUST be verified by DIRECT INSPECTION of `docs/mdf/original/MDFields19a_UTF8.txt` or `docs/mdf/mdf-tag-reference.md`.

---

## Ethics & Linguistic Context

- **Nation Sovereignty**: Use "Nation" instead of "Tribal."
- **Tech Stack**: 100% Python, Streamlit, PostgreSQL (Aiven/pgserver), `uv`.