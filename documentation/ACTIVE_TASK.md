<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task (Session)

Date: 2026-02-07

## Status Overview
- OAuth session rehydration: **WORKING**
- Deep linking: **WORKING**
- Phase 5 (Navigation & Access Control): **IN PROGRESS**

## Accomplishments this Session
- Reviewed roadmap and active tasks.
- Confirmed working state of OAuth rehydration and deep linking.
- Updated `docs/development/roadmap.md` with discrete refactoring steps for Phase 5.
- Defined route protection strategy using `st.navigation` and role-based access control.
- Updated `src/database/connection.py` to automatically seed default permissions (`proto-SNEA` roles) if the `permissions` table is empty.

## Next Steps (Phase 5 Refactoring)
1. **Implement Identity Service**: Create `src/services/identity_service.py` to handle user syncing and team/role resolution.
2. **Implement Security Manager**: Create `src/services/security_manager.py` to handle session rehydration and route protection logic.
3. **Granular Route Protection**: Update `app.py` (or the new Security Manager) to filter navigation items based on user roles and permissions.
4. **Implement Navigation Service**: Move page definitions and navigation configuration out of `app.py`.

## Utility Scripts
- **`scripts/dump_users.py`**: Dumps the `users` table and `user_activity_log` to the console and CSV files in the `tmp/` directory for human review.

## Critical Reminder
- Do not mark things as done until the User says they are done. AI is not driving this project.
