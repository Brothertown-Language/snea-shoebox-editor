# UI Engineer — implement task

## Purpose

Produce a complete framework-specific UI implementation from design artifacts (interaction spec, mockup, wireframe) and spec requirements.

## Entry Criteria

- Design artifacts exist in the worktree (interaction-spec.yaml is REQUIRED; mockup.html, screenshot.png, wireframe.svg are recommended/reference).
- `worktree.path` is set and verified.
- Target framework is known (Streamlit by default, or configured via `framework-config` task).
- Spec or context document is available and has been read.

## Exit Criteria

- Framework-specific implementation files exist in the worktree.
- Implementation covers all routes, components, states, and guards defined in the interaction spec.
- RBAC guards, sidebar navigation pattern, and accessibility features from the interaction spec are implemented.
- Implementation follows `docs/ui-guidelines.md` conventions (sidebar pattern, RBAC, per-record controls, status feedback).
- `completion` subtask has been invoked.
- Result contract returned: `{status, files_changed, summary, concerns}`.

## Procedure

1. Read the interaction spec YAML file from the worktree.
2. Read the mockup HTML and/or wireframe SVG for layout reference.
3. Read `docs/ui-guidelines.md` for project UI conventions.
4. Copy `templates/streamlit_template.py` as the starting point for each page/view.
5. Map interaction spec components to Streamlit widgets:
   - `navigation_list` → `st.sidebar` navigation with `st.radio` or `st.sidebar.selectbox`
   - `content_container` → main panel with `st.container`
   - `banner` → `st.header` in sidebar
   - Data sources → `st.session_state` or API calls via `ui_utils`
6. Implement RBAC guards from interaction spec `guards` section:
   - Check `st.session_state.get("user_role")` against required roles.
   - Redirect or show error for unauthorized access.
7. Implement navigation transitions from interaction spec `transitions` section.
8. Implement accessibility features from interaction spec `accessibility` section:
   - ARIA labels via `st.markdown` with accessible HTML.
   - Keyboard navigation patterns.
   - Screen reader announcements via `st.status` or `st.toast`.
9. Implement per-record controls inline with data, not in global toolbars.
10. Use `st.status()` or `st.toast()` for feedback — no `st.error()` for advisory validation.
11. Invoke `completion` subtask.
12. Return result contract.