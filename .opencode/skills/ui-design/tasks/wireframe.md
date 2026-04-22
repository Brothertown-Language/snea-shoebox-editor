# UI Design — wireframe task

## Purpose

Produce a low-fidelity wireframe SVG from a spec or design context.

## Entry Criteria

- Spec or context document is available and has been read.
- `worktree.path` is set and verified.
- Screen/layout scope is identified.

## Exit Criteria

- Wireframe SVG file exists in the worktree.
- SVG passes `validate_svg.py` validation.
- No framework-specific references in the wireframe.
- `completion` subtask has been invoked.
- Result contract returned: `{status, artifact_path, summary, concerns}`.

## Procedure

1. Read the spec or context for the screen/layout being wireframed.
2. Copy `templates/wireframe_template.svg` as the starting point.
3. Modify named groups (`header`, `content`, `footer`, `sidebar`) to reflect the spec layout.
4. Add placeholder text elements for labels, headings, and data fields.
5. Validate the wireframe SVG with `scripts/validate_svg.py`.
6. Ensure no framework-specific content (Streamlit, React, Vue, etc.).
7. Invoke `completion` subtask.
8. Return result contract.