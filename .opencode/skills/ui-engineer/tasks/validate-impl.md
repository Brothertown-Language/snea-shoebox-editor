# UI Engineer — validate-impl task

## Purpose

Validate a framework-specific UI implementation against interaction spec requirements for completeness, correctness, and convention compliance.

## Entry Criteria

- Implementation files exist in the worktree.
- Interaction spec YAML is available for comparison.
- `worktree.path` is set and verified.

## Exit Criteria

- All interaction spec routes, component states, navigation guards, and accessibility requirements are verified present in the implementation.
- Review findings documented as a result contract with severity levels.
- `completion` subtask has been invoked.
- Result contract returned: `{status, findings, summary}`.

## Procedure

1. Read the interaction spec YAML file from the worktree.
2. Read each implementation file in the worktree.
3. For each route in `navigation.routes`, verify a corresponding view or page exists.
4. For each transition in `navigation.transitions`, verify the navigation trigger is implemented.
5. For each guard in `navigation.guards`, verify the RBAC check or condition is present.
6. For each component in `components`, verify a corresponding Streamlit widget exists.
7. For each accessibility requirement in `accessibility`, verify ARIA labels, keyboard navigation, or screen reader announcements are present.
8. Check convention compliance with `docs/ui-guidelines.md`:
   - Sidebar pattern: `hide_sidebar_nav()`, sidebar header, back navigation.
   - RBAC: role guard at page entry.
   - Per-record controls inline, not in global toolbar.
   - Status feedback via `st.status()` or `st.toast()`, not `st.error()` for advisory messages.
9. Compile findings with severity levels (critical, warning, info).
10. Invoke `completion` subtask.
11. Return result contract.