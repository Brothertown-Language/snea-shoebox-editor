<!-- Copyright (c) 2026 Brothertown Language -->
# Active Task Tracking

Current focus area as of 2026-01-31:
- **Task:** Enforce Docker for Local Development
- **Description:** Remove multiple-choice confusion by making Docker the exclusive method for local development in all documentation.
- **Status:** COMPLETE
- **Completed Requirements:**
    - Updated `docs/development/local-development.md` to remove manual setup options.
    - Updated `README.md` to prioritize Docker and use `docker-compose` for commands.
    - Updated `CONTRIBUTING.md` to use `docker-compose exec` for testing and pre-commit.
    - Updated `docs/development/roadmap.md` to remove manual setup alternatives.
    - Updated `docs/mdf/mdf-tag-reference.md` to use Docker for scripts.
- **In Progress:**
    - None
- **Task:** Dedicated Dev UI
- **Description:** Implement a built-in UI for inspecting system internals (schemas, versions) without CLI.
- **Status:** COMPLETE
- **Completed Requirements:**
    - Added `/api/dev/info` endpoint to `src/backend/worker.py`.
    - Added `DevInfo` component and "Dev Info" tab to `src/frontend/app.py`.
    - Integrated frontend with backend for live data fetching.
    - Updated `docs/development/roadmap.md` with Phase 8.
