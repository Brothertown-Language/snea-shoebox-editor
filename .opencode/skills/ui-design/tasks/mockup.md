# UI Design — mockup task

## Purpose

Produce a high-fidelity mockup HTML file from a wireframe or design context.

## Entry Criteria

- Wireframe SVG or design context is available.
- `worktree.path` is set and verified.
- Visual fidelity requirements are understood from the spec.

## Exit Criteria

- Mockup HTML file exists in the worktree.
- HTML renders correctly with embedded CSS (no external framework dependencies).
- No framework-specific references in the mockup.
- `completion` subtask has been invoked.
- Result contract returned: `{status, artifact_path, summary, concerns}`.

## Procedure

1. Read the wireframe SVG or design context for the screen being mocked up.
2. Copy `templates/mockup_template.html` as the starting point.
3. Fill in component placeholders (header, nav, main, sidebar, footer) with spec content.
4. Add inline CSS for visual fidelity (colors, typography, spacing) — toolkit-agnostic.
5. Optionally capture a screenshot with `scripts/render_html_screenshot.py`.
6. Ensure no framework-specific content (no Streamlit, React, Vue classes, etc.).
7. Invoke `completion` subtask.
8. Return result contract.