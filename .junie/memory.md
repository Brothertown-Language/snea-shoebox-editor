<!-- Last pruned: 2026-03-04 -->
<!-- Max 40 lines. Format: key: value. Prune order: session_state → oldest persistent_notes → least-used key_symbols. -->
<!-- No rule duplication from guidelines/. Clear session_state per new task. -->

project: SNEA Shoebox Editor — Brothertown Language / Southern New England Algonquian preservation
data_layer: MDF (Multi-Dictionary Formatter) + PostgreSQL (pgserver/Aiven) + pgvector
db_pool: pool_size=0, max_overflow=10, pool_recycle=300, pool_pre_ping=True (zero idle footprint)
migration_format: YYYYMMDDSSSSS (seconds-since-midnight); incremental versioning forbidden
search: ILIKE + Native FTS only; pg_trgm forbidden (incompatible with pgserver envelope)
mdf_filename_pattern: <prefix>_<Source>_<GitHubUsername>_<YYYY-MM-DD>_<SSSSS>.txt via UploadService.generate_mdf_filename
mdf_spacing: double blank lines (\n\n) between records mandatory
mdf_validation: advisory only — never block export/edit; use "Suggestion"/"Note" framing, never "Error"
mdf_tags_source: docs/mdf/original/MDFields19a_UTF8.txt (authoritative); 90 modern tags in mdf_tags_metadata.json; 25 legacy in legacy_tags_metadata.json
no_fallback_language: never assume/apply default language for records lacking \ln tags
record_locking: is_locked/locked_by/locked_at/lock_note columns on records table; strict immutability all roles
ui_html_injection: st.html() only; unsafe_allow_html=True deprecated in this project
ui_edit_mode: global Edit Mode toggle in sidebar; pending edits buffered in st.session_state.pending_edits
ui_nav: sidebar controls for all detail/nav/filter; icon buttons preferred
streamlit_execution: background only via nohup + lifecycle scripts; foreground forbidden
port_main: 8501 (main app); port_mock: 8502 (mock viewer)
private_db: JUNIE_PRIVATE_DB=true required for all DB-interactive commands
commit_protocol: AI forbidden from any git add/commit/push/staging actions — user-only
memory_file: .junie/memory.md (this file); replaces LONG_TERM_MEMORY.md as of 2026-03-03
sort_symbol_map: ∞(U+221E)→oozzz (Algonquian letter, after oo*/before op); ✔(U+2714)→"" (annotation, stripped)
ln_remediation: ALL sections ✅ complete; DB audit assumed remediated; plan closed
extend_existing: ALL model classes have __table_args__ with extend_existing=True; convention documented in models/__init__.py
session_state: new task starting
last_task: Fixed blank line before \nt Record: — normalize_nt_record no longer inserts blank line; format_mdf_record is now last in chain at all 6 upload_service.py call sites
