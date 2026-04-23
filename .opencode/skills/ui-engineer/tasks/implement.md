# UI Engineer — implement task

## Purpose

Produce a complete framework-specific UI implementation from design artifacts (interaction spec, mockup, wireframe) and spec requirements.

## Entry Criteria

- Design artifacts exist in the worktree (interaction-spec.yaml is REQUIRED; mockup.html, screenshot.png, wireframe.svg are recommended/reference).
- `test-ui` task has been completed (UI test specifications exist in the worktree — MANDATORY prerequisite).
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

### Step 0.5: RED Gate — UI Enforcement Test Assertions (MANDATORY)

**🚫 CRITICAL: This step MUST execute BEFORE any UI implementation. Skipping this step is a CRITICAL GUIDELINE VIOLATION.**

Before writing any implementation code, enforcement test assertions for UI behavior MUST be written and verified to be in RED state.

**Prerequisites:**
- `test-ui` task MUST have been completed (invoke `/skill ui-engineer --task test-ui` if UI test specifications do not yet exist)
- Interaction spec YAML is available in the worktree
- `worktree.path` is set and verified

**Procedure:**

1. **Invoke `test-ui` task** — If UI test specifications do not yet exist in the worktree, invoke the `test-ui` task to generate them. The `test-ui` task produces test specification files that define expected UI behavior
2. **Write enforcement test assertions** — For each success criterion in the spec that applies to UI behavior, write an enforcement test assertion in `test-enforcement.sh` that verifies the UI meets the SC's requirement. Use the format: `# SC-N: <brief UI description>` as a comment above the assertion
3. **Verify RED state** — Run the newly written assertions and confirm they are in RED state (failing). The assertions MUST fail because the UI implementation does not exist yet
4. **Produce tool-call evidence** — Record the RED state verification output as a tool-call artifact showing:
   - The test assertions written (with SC ID comments)
   - The test run output showing failure (RED state)
   - The timestamp of when the RED verification was performed

**Evidence artifact format:**

```
RED Gate: ui-engineer enforcement test assertions
Assertions written: [count]
RED state verified: [true/false]
Test output: [pasted failure output]
Timestamp: [ISO 8601]
```

**If RED state is NOT confirmed:** HALT. Do NOT proceed to implementation. The enforcement test assertions MUST exist and fail before any UI code is written.

**Cross-reference:** See `091-incremental-build.md` → Per-Item TDD Cycle → RED phase, and `080-code-standards.md` → SC-to-Test Traceability and RED-Phase Ordering.

### Step 1: Read Design Artifacts

1. Read the interaction spec YAML file from the worktree.
2. Read the mockup HTML and/or wireframe SVG for layout reference.
3. Read `docs/ui-guidelines.md` for project UI conventions.

### Step 2: Map Components and Implement

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

### Step 3: Completion

11. Invoke `completion` subtask.
12. Return result contract.