# UI Design — screenshot task

## Purpose

Capture a screenshot of a rendered design artifact (HTML mockup or SVG wireframe).

## Entry Criteria

- An HTML mockup or SVG wireframe file exists in the worktree.
- `worktree.path` is set and verified.
- The rendering script dependencies are available via PEP 723.

## Exit Criteria

- Screenshot PNG file exists in the worktree.
- Screenshot accurately represents the source artifact.
- `completion` subtask has been invoked.
- Result contract returned: `{status, artifact_path, summary, concerns}`.

## Procedure

1. Identify the source artifact (HTML mockup or SVG wireframe) to capture.
2. For HTML mockups: run `scripts/render_html_screenshot.py` with the mockup path, output path, and viewport dimensions.
3. For SVG wireframes: first render to PNG with `scripts/render_svg_to_png.py`, then optionally capture a screenshot of the rendered output.
4. Verify the screenshot file was created and is non-empty.
5. Invoke `completion` subtask.
6. Return result contract.