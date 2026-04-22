# UI Design — review task

## Purpose

Review a design artifact against spec requirements for completeness, consistency, and toolkit-agnostic compliance.

## Entry Criteria

- Design artifact(s) exist in the worktree.
- Spec or context document is available for comparison.
- `worktree.path` is set and verified.

## Exit Criteria

- Review findings documented as a result contract.
- Each finding has severity (critical, warning, info), description, and recommendation.
- `completion` subtask has been invoked.
- Result contract returned: `{status, findings, summary}`.

## Procedure

1. Read the spec or context document defining the design requirements.
2. Read each design artifact (wireframe, mockup, interaction spec).
3. Check each artifact for:
   - Completeness: all spec-required screens, components, and flows are present.
   - Consistency: naming, layout, and interactions are consistent across artifacts.
   - Toolkit-agnostic compliance: no framework-specific references (no Streamlit, React, Vue, Godot, Flutter, Android).
   - Accessibility: ARIA labels, keyboard navigation, and screen reader considerations are addressed.
4. Validate SVG artifacts with `scripts/validate_svg.py`.
5. Validate interaction specs with `scripts/validate_interaction_spec.py`.
6. Compile findings with severity levels.
7. Invoke `completion` subtask.
8. Return result contract.