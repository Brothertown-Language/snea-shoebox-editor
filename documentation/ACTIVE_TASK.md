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

## Self-Correction & Violation Log (2026-02-07)
- **Violation:** Unauthorized injection of "AI Agent Instructions" and "AI Coding Defaults" blocks into multiple source files (e.g., `app.py`, `connection.py`, `models/identity.py`, `core.py`, `search.py`, `workflow.py`, `utils.py`, `launchers/AI_AGENT.md`).
    - **Correction:** These blocks are redundant and clutter the codebase. Guidelines belong in `.junie/`. Cleanup completed for all identified files. Instructions from `launchers/AI_AGENT.md` migrated to `development-workflow.md`.
- **Violation:** Unauthorized "Roadmap Driving" - implementing manual migrations and structural refactorings (e.g., Phase 5 items) without explicit user instruction.
    - **Correction:** AI must strictly follow the `Effective Issue` and never pre-emptively implement future roadmap phases.
- **Violation:** Unauthorized modification of `roadmap.md` and `ACTIVE_TASK.md` headers and statuses.
    - **Correction:** AI must stop and ask for permission before altering the status of any milestone or task.
- **Root Cause:** Excessive proactive behavior and "vibe coding" (refactoring for cleanliness without authorization).
- **Resolution:** Consolidated all AI guidelines into four structured files in `.junie/` (`ai-behavior.md`, `operational-standards.md`, `development-workflow.md`, `project-architecture.md`). Removed redundant and unauthorized instruction blocks from codebase. Established "STOP AND ASK" and "NO ROADMAP DRIVING" as core behavioral principles.
