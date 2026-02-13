<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# Phase E — Cleanup & Polish ⏳

### E-1. Add activity logging for upload events ✅
Log `upload_start`, `upload_staged`, `upload_committed` actions via
`AuditService` with the `session_id`.

### E-2. Add batch rollback support ⏳
Implement `UploadService.rollback_session(session_id)` that restores
`prev_data` from `edit_history` for all rows matching the session.

### E-3. Write unit tests for rollback ⏳
Test that rollback restores records and removes the corresponding
`search_entries`.

### E-4. Update roadmap documentation ⏳
Add the upload feature to the roadmap as a new phase entry once all
steps are done (user approval required).  Do **not** mark the phase as
completed until the user explicitly confirms it is finished.
