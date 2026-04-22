# UI Engineer Scripts

Scripts for the `ui-engineer` skill are inherited from `ui-design` via PEP 723 path references.

There are no ui-engineer-specific scripts. All rendering and validation scripts live in the `ui-design` skill and are invoked via relative path references:

- `../../ui-design/scripts/render_svg_to_png.py` — Render SVG wireframes to PNG
- `../../ui-design/scripts/render_html_screenshot.py` — Capture screenshots of HTML mockups
- `../../ui-design/scripts/validate_svg.py` — Validate SVG wireframe structure
- `../../ui-design/scripts/validate_interaction_spec.py` — Validate interaction spec YAML against schema
- `../../ui-design/scripts/diff_mockups.py` — Compare two mockup HTML files
- `../../ui-design/scripts/animate_flow.py` — Animate interaction flows

Invoke with: `uv run --script ../../ui-design/scripts/<script>.py`

This avoids script duplication and ensures both skills use the same validated tooling.