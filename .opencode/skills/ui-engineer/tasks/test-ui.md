# UI Engineer — test-ui task

## Purpose

Generate UI test specifications from interaction spec requirements, covering navigation, component states, RBAC guards, and accessibility.

## Entry Criteria

- Interaction spec YAML is available in the worktree.
- Implementation files exist in the worktree.
- `worktree.path` is set and verified.

## Exit Criteria

- Test specification file(s) exist in the worktree.
- Every navigation route, transition, guard, and accessibility requirement from the interaction spec has a corresponding test case.
- `completion` subtask has been invoked.
- Result contract returned: `{status, artifacts, summary, concerns}`.

## Procedure

1. Read the interaction spec YAML file from the worktree.
2. Read the implementation files for context on actual component mapping.
3. Generate test specifications covering:
   - **Route tests**: Each route in `navigation.routes` is reachable and renders expected content.
   - **Transition tests**: Each transition in `navigation.transitions` triggers correctly.
   - **Guard tests**: Each guard in `navigation.guards` enforces access control (authorized roles pass, unauthorized roles are blocked).
   - **Component state tests**: Each component in `components` renders in its default state and any defined alternate states.
   - **Accessibility tests**: ARIA labels, keyboard navigation, and screen reader announcements match `accessibility` section.
4. Structure test specs as pytest-compatible test function descriptions with setup, action, and assertion steps.
5. Write test specification to a file in the worktree (e.g., `test_ui_<feature>.py` or `test_specs/<feature>_test_spec.yaml`).
6. Invoke `completion` subtask.
7. Return result contract.