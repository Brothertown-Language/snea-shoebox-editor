# UI Engineer — framework-config task

## Purpose

Configure the target framework, component library, and project conventions for UI implementation. Establishes the binding between toolkit-agnostic design artifacts and framework-specific code patterns.

## Entry Criteria

- `worktree.path` is set and verified.
- Project structure is accessible (especially `src/frontend/` and `docs/ui-guidelines.md`).

## Exit Criteria

- Framework configuration is documented with target framework, component conventions, and project-specific patterns.
- Supported frameworks are listed with their status (primary, experimental, planned).
- `completion` subtask has been invoked.
- Result contract returned: `{status, config_path, summary, concerns}`.

## Procedure

1. Read `docs/ui-guidelines.md` for established UI conventions.
2. Scan `src/frontend/` for existing UI components, utilities, and patterns:
   - `ui_utils.py` for shared utilities (e.g., `hide_sidebar_nav()`).
   - Existing pages for layout patterns (e.g., `upload_mdf.py`, `table_maintenance.py`).
   - Session state patterns for RBAC and state management.
3. Determine the target framework:
   - Primary: **Streamlit** (the project's current and only supported frontend framework).
   - Experimental: None currently.
   - Planned: None currently.
4. Document component conventions:
   - Navigation: `st.sidebar` with `hide_sidebar_nav()`.
   - RBAC: `st.session_state.get("user_role")` guard.
   - Status feedback: `st.status()` or `st.toast()` for non-blocking feedback.
   - Per-record controls: inline with data rows, not in global toolbar.
   - Import pattern: `import streamlit as st`, `from src.frontend.ui_utils import ...`.
5. Write configuration to `ui_framework_config.yaml` in the worktree (or update existing).
6. Invoke `completion` subtask.
7. Return result contract.