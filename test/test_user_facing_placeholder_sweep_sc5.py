"""SC-5 enforcement sweep: no user-facing string may contain an unrendered
``<ALL_CAPS_TEMPLATE_TOKEN>`` placeholder.

Sweeps string literals passed to user-facing Streamlit render calls
(``st.write``, ``st.info``, ``st.error``, ``st.warning``, ``st.success``,
``st.markdown``, ``st.caption``) in ``src/`` and the root ``streamlit_app.py``
using Python's :mod:`ast` module. AST parsing excludes docstrings and comments
by construction, so the ``<SSSSS`` filename-format documentation inside
``src/services/upload_service.py`` stays out of scope.

Two assertions:

1. Current tree: zero placeholder tokens in user-facing render-call strings.
2. RED baseline validity: the identical assertion, applied to the pre-fix
   trunk state (commit ``eb467b8`` file contents fetched via ``git show``),
   MUST raise ``AssertionError`` — proving the sweep detects the raw
   ``<MAINTAINER_CONTACT>`` tokens that the committed fix removed.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_COMMIT = "eb467b8"
RENDER_ATTRS = {
    "write",
    "info",
    "error",
    "warning",
    "success",
    "markdown",
    "caption",
}
PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9_]{2,}>")


def _target_files() -> list[Path]:
    files = sorted(PROJECT_ROOT.glob("src/**/*.py"))
    root_app = PROJECT_ROOT / "streamlit_app.py"
    if root_app.exists():
        files.append(root_app)
    return files


def _string_constants_in_call(call: ast.Call) -> list[str]:
    """Collect string literals inside a render call, including f-string parts.

    For JoinedStr nodes, only the static ``Constant`` parts are scanned; the
    dynamic ``FormattedValue`` interpolations are not string literals.
    """
    constants: list[str] = []

    def visit(node: ast.AST) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            constants.append(node.value)
        elif isinstance(node, ast.JoinedStr):
            for value in node.values:
                visit(value)
        else:
            for child in ast.iter_child_nodes(node):
                visit(child)

    for arg in (*call.args, *call.keywords):
        visit(arg)
    return constants


def _collect_user_facing_strings(source: str) -> list[tuple[str, int, str]]:
    """Return (call_attr, lineno, literal) for user-facing render strings."""
    hits: list[tuple[str, int, str]] = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr in RENDER_ATTRS
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
        ):
            continue
        for literal in _string_constants_in_call(node):
            hits.append((func.attr, node.lineno, literal))
    return hits


def sweep_source(source: str) -> list[tuple[str, int, str]]:
    """Sweep one source file; return placeholder hits in render-call strings."""
    violations: list[tuple[str, int, str]] = []
    for attr, lineno, literal in _collect_user_facing_strings(source):
        for match in PLACEHOLDER_RE.finditer(literal):
            violations.append((attr, lineno, match.group(0)))
    return violations


def _read_baseline(path_rel: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{BASELINE_COMMIT}:{path_rel}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def sweep_baseline() -> list[tuple[str, str, int, str]]:
    """Run the same sweep over eb467b8 file contents fetched via git show."""
    violations: list[tuple[str, str, int, str]] = []
    for path in _target_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        source = _read_baseline(rel)
        if source is None:
            continue
        for attr, lineno, token in sweep_source(source):
            violations.append((rel, attr, lineno, token))
    return violations


def test_current_tree_user_facing_strings_have_no_placeholders():
    violations: list[str] = []
    for path in _target_files():
        for attr, lineno, token in sweep_source(path.read_text(encoding="utf-8")):
            violations.append(f"{path.relative_to(PROJECT_ROOT)}:{lineno} {attr} {token}")
    assert violations == [], "Unrendered placeholders in user-facing strings:\n" + "\n".join(
        violations
    )


def test_baseline_eb467b8_sweep_flags_raw_tokens():
    """RED validity: the sweep detects raw tokens in the pre-fix trunk state.

    Applied to eb467b8 contents, the sweep must flag the raw
    <MAINTAINER_CONTACT> literals in streamlit_app.py and
    src/frontend/pages/login.py render-call strings.
    """
    baseline_violations = sweep_baseline()
    assert baseline_violations, "Baseline sweep found no tokens — RED baseline invalid"
    flagged_files = {rel for rel, _attr, _lineno, _token in baseline_violations}
    assert "streamlit_app.py" in flagged_files, flagged_files
    assert "src/frontend/pages/login.py" in flagged_files, flagged_files
    assert all(token == "<MAINTAINER_CONTACT>" for *_lead, token in baseline_violations)


def test_zero_placeholder_assertion_raises_against_baseline():
    """Direct RED event: the enforcement assertion itself fails on eb467b8.

    The zero-placeholder assertion, applied to the eb467b8 pre-fix contents,
    must raise AssertionError — this is the confirmed-failing RED run, executed
    against the historical baseline without breaking the current-tree suite.
    """
    raised = False
    try:
        assert not sweep_baseline(), "Unrendered placeholders in user-facing strings"
    except AssertionError:
        raised = True
    assert raised, "Zero-placeholder assertion did not FAIL against eb467b8 contents"
