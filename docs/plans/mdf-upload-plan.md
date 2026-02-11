<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# MDF File Upload — Implementation Plan

This plan covers the end-to-end feature for uploading MDF files, staging
them in the `matchup_queue`, suggesting matches against existing records,
letting the user review/confirm, and committing accepted changes to the
`records` table with full audit history.

## Plan Overview

The implementation is divided into the following phases:

1.  **[Phase A: MDF Parser Enhancements](mdf-upload/phase-a-parser.md)** ✅
    *   Extracting `\nt Record:` tags and searchable sub-entry fields.
    *   Normalization helpers and unit tests.

2.  **[Phase B: Upload Service (Backend)](mdf-upload/phase-b-service.md)** ✅
    *   Database schema updates (`batch_id`, `filename`, `match_type`).
    *   Core logic for parsing, staging, matching, and committing records.
    *   Automatic duplicate removal and mismatch flagging.

3.  **[Phase C: Upload Page (Frontend)](mdf-upload/phase-c-page.md)** ✅
    *   Streamlit page registration and role-based access.
    *   File uploader, source selector, and batch management UI.

4.  **[Phase D: Review & Confirm Page (Frontend)](mdf-upload/phase-d-review.md)** 🔄
    *   Interactive review table with responsive record comparison.
    *   Bulk approval actions and per-record "Apply Now" workflow.
    *   Manual match overrides and pending changes download.

5.  **[Phase E: Cleanup & Polish](mdf-upload/phase-e-cleanup.md)** ⏳
    *   Activity logging and batch rollback support.
    *   Final documentation updates and polish.

## Key Principles

*   **Approval Mandate**: No staged upload may modify live records without explicit user approval.
*   **Batch Isolation**: Each upload is identified by a unique `batch_id` (UUID).
*   **Audit History**: Every change is tracked in the `edit_history` table.
