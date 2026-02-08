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
- Updated `docs/development/roadmap.md` with discrete refactoring steps for Phase 5 and strict role definitions.
- Defined route protection strategy using `st.navigation` and role-based access control.
- Implemented automatic seeding of the corrected three default permissions (admin, editor, viewer) for the `Brothertown-Language` organization in `src/database/connection.py`.
- Enforced mandatory GitHub teams for all permissions (no NULL teams allowed).
- Added role enforcement documentation and comments to `Permission` model and project roadmap.
- Verified that the `permissions` table is correctly populated on app restart when empty with the new mappings:
    - `proto-SNEA-admin` -> `admin`
    - `proto-SNEA` -> `editor`
    - `proto-SNEA-viewer` -> `viewer`
- Updated `scripts/seed_permissions.py` and `scripts/clear_permissions.py` to support testing of the new default permissions.
- Resolved the issue where the `permissions` table was not being populated on restart.
- Implemented private Junie database separation for tests and destructive tasks (`tmp/junie_db`).
- Added `scripts/clone_db.py` for cloning the local developer database to the Junie private database.
- **Phase 5 Stage 1**: Implemented `IdentityService`, refactored `auth_utils.py`, `app.py`, `login.py`, and `user_info.py`. Verified with tests.
- **Refactored Authorization Logic**: Removed hardcoded GitHub org/team checks from `IdentityService`. Authorization is now entirely driven by the `permissions` table in the database via `SecurityManager`.
- **Security Manager API Update**: `SecurityManager.get_user_role` now accepts an explicit list of teams, facilitating early authorization during the OAuth flow.
- **Verification**: Updated and verified `tests/test_security_manager.py` and `tests/services/test_identity_service.py`. All tests passing.
- **Refactoring Plan Update**: Updated `tmp/refactoring_plan.md` to reflect Stage 2 completion.
- **Mandated Commit Script Method**: Updated AI guidelines to require the commit script method for all source code changes.
- **Prohibition on Committing Temporary Files**: Updated `.junie/guidelines.md`, `.junie/operational-standards.md`, and `.junie/development-workflow.md` to explicitly forbid committing any files from the `tmp/` directory.
- **Commit Script Timing Restriction**: Updated guidelines to explicitly prohibit creating commit scripts or messages without direct user instruction.
- **Guideline Adherence Correction**: Updated `tmp/commit_task.sh` to strictly follow mandatory path resolution rules (`git rev-parse`) for reliable execution within IDE environments.
- **Refactored HTML/CSS Injection**: Replaced `st.markdown(..., unsafe_allow_html=True)` with `st.html()` in `app.py` and `login.py`.
- **Updated UI Guidelines**: Added mandatory rule to `.junie/ui-development-spr.md` to use `st.html()` for all HTML/CSS/JS content.
- **Reinforced Path Resolution Guidelines**: Updated `.junie/development-workflow.md` to mandate the 3-step path resolution boilerplate for all shell scripts.

## Next Steps (Phase 5 Refactoring)
1. **Implement Navigation Service**: Move page definitions and navigation configuration out of `app.py`.
2. **Database Migration Management**: Clean up `src/database/connection.py` by extracting migration logic to a separate manager.

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
