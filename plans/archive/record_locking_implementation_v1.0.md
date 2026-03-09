# Plan: Record Locking System (On-Row Implementation)

## 1. Overview
Implement a record-level locking mechanism to prevent accidental overwrites during MDF uploads and manual edits. The system uses direct columns on the `records` table for performance and simplicity, with strict enforcement across all user roles.

## 2. Database Schema Evolution
*   **Migration `2026030145060`**:
    *   Add `is_locked` (BOOLEAN, DEFAULT FALSE) to `records` table.
    *   Add `locked_by` (TEXT, Foreign Key to `users.email`), `locked_at` (TIMESTAMPTZ), and `lock_note` (TEXT) to `records`.
    *   Add a B-tree index on `records(is_locked)` to support filtering and performance.
*   **SQLAlchemy Model**: Update `Record` class in `src/database/models/core.py`.

## 3. Service Layer & Policy Enforcement
*   **Strict Immutability**: Update `LinguisticService.update_record` to reject ALL updates if `is_locked` is True (Admins and Editors).
*   **Locking API**: Implement `lock_record(record_id, user_email, note)` and `unlock_record(record_id, user_email)` in `LinguisticService`.
*   **Audit Trail**: 
    *   Every lock/unlock toggle MUST create an `EditHistory` snapshot.
    *   Log actions in `user_activity_log`.

## 4. MDF Matchup Queue & Conflict Handling
*   **Conflict Detection**: Matching engine must detect matches against locked records during ingest.
*   **Status Mapping**: Set `MatchupQueue.status` to `locked_conflict` for conflicting uploads.
*   **Conflict Workflows**:
    *   Implement bulk "Discard" for all `locked_conflict` records in a batch.
    *   Implement "Download" action to export `locked_conflict` records as an MDF fragment.

## 5. Frontend: Records Page Integration
*   **Sidebar Controls**: Add "Lock Record" / "Unlock Record" toggle in `st.sidebar`.
*   **Visual Indicators**: Add lock icon (🔒) badge to record lists.
*   **Filter View**: Integrate "Is Locked" filter into the search component.
*   **Edit Gate**: 
    *   Globally disable "Apply Now" (MDF review) and manual edit forms for locked records.
    *   Prevent record from switching to "edit" mode if `is_locked` is True.

## 6. Frontend: MDF Upload Review
*   **Warnings**: Prominent banner for `locked_conflict` detection in current batch.
*   **Toolbar**: Add "Discard All Locked Conflicts" and "Download Locked Conflicts" buttons.

## 7. Permissions Model
*   **Editors & Admins**: Full lock/unlock privileges.
*   **Viewers**: No lock/unlock access; controls hidden.

## 8. Verification
*   **Unit Tests**: Verify rejection of updates to locked records for all roles.
*   **Audit Tests**: Verify `EditHistory` and `user_activity_log` entries on lock/unlock.
*   **Integration Tests**: Verify MDF upload conflict flagging and discard/download paths.
