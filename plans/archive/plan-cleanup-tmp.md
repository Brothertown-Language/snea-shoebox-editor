# Plan: Cleanup tmp/ of No-Longer-Needed Scripts and Output Files

## Overview
Remove all ad-hoc scripts, logs, commit messages, diagnostic files, and stale test DBs from `tmp/`. Preserve only the protected live databases (`local_db`, `junie_db`) and active runtime files (`streamlit.log`).

## PRESERVE (do not delete)
- `tmp/local_db/` — protected by Zero-Trust Terminal Gate (LOCAL DB PRESERVATION)
- `tmp/junie_db/` — protected by Zero-Trust Terminal Gate (LOCAL DB PRESERVATION)
- `tmp/streamlit.log` — active runtime log used by lifecycle scripts (absent; no active session)

## DELETE — Ad-hoc Python scripts
All `*.py` files in `tmp/` (audit_*, check_*, count_*, debug_*, diag_*, find_*, fix_*, ge_score_check, inspect_*, investigate_*, reproduce_*, revert_*, search_*, sql_audit*, test_*.py, update_*, verify_*.py)

## DELETE — Log and output files
All `*.log`, `*.txt`, `*.md` (non-data), `*.msg` files in `tmp/`

## DELETE — Stale test/scratch databases
`stuck_test_db`, `test_db`, `test_linguistic_service_db`, `test_stuck_db`, `test_tcp_db`, `test_upload_match_db`, `test_upload_service_db`

## DELETE — Miscellaneous artifacts
`__pycache__/`, `img.png`, `SNEA-20260209.dbp`, `snea-local-dev.dbp`, `mohegan-fielding-mdf.txt`, `mohegan-fielding-mdf_headwords.md`, `Trmbll Natick UTF-8.txt`, `consolidated_guidelines.md`, `guidelines_draft.md`, `guidelines_full.txt`, `remediation_plan.md`, `shell_env.txt`, `original_bashrc.txt`, `updated_bashrc.txt`

## Steps
1. ✔️ Delete all ad-hoc `.py` scripts in `tmp/`
2. ✔️ Delete all log/output/message files in `tmp/`
3. ✔️ Delete all stale test databases in `tmp/`
4. ✔️ Delete miscellaneous artifacts
5. ✔️ Verify `local_db` and `junie_db` intact; `tmp/` contains only `local_db/` and `junie_db/`
6. ✔️ Plan updated to reflect completion
