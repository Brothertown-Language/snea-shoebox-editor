# UI Design — design task

## Purpose

Produce a complete toolkit-agnostic UI design covering layout, components, navigation, and accessibility from a spec.

## Entry Criteria

- Spec or context document is available and has been read.
- `worktree.path` is set and verified.
- Target design scope is understood (which screens/flows the spec covers).

## Exit Criteria

- One or more design artifact files exist in the worktree.
- Design artifacts contain no framework-specific references.
- `completion` subtask has been invoked.
- Result contract returned: `{status, artifacts, summary, concerns}`.

## Procedure

1. Read the spec issue and any linked context files from the worktree.
2. Identify screens, flows, and components required by the spec.
3. For each screen/flow, produce a design artifact:
   - Wireframes (SVG) for layout structure — use `templates/wireframe_template.svg` as starting point.
   - Interaction specs (YAML) for navigation and data flow — use `templates/interaction_spec_schema.yaml` for validation.
   - Mockups (HTML) for visual fidelity — use `templates/mockup_template.html` as starting point.
4. Validate all SVG artifacts with `scripts/validate_svg.py`.
5. Validate all interaction specs with `scripts/validate_interaction_spec.py`.
6. Ensure no artifact contains framework-specific terminology (Streamlit, React, Vue, Godot, Flutter, Android, etc.).
7. Invoke `completion` subtask to clean up temporary resources and produce final summary.
8. Return result contract.