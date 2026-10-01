"""SC-2 (#1392) enforcement: the literal ``<MAINTAINER_CONTACT>`` token MUST
NOT appear in any Python source under ``src/`` or in ``streamlit_app.py``.

This mirrors the spec's grep criterion exactly:

    grep -rn --include='*.py' "<MAINTAINER_CONTACT>" src/ streamlit_app.py

Scope notes:

- Only ``*.py`` files are scanned; the ``--include='*.py'`` semantics keep
  stale ``__pycache__/*.pyc`` compiled artifacts (which may retain the
  pre-fix literal) out of the check.
- The scan is a raw substring match on file contents, so Unicode in the
  linguistic data is untouched and preserved byte-for-byte.

The RED baseline is demonstrated by
:func:`test_red_baseline_eb4678b_token_literals_fail`, which runs the *same*
scan against the documented pre-fix trunk state (``eb467b8``) with contents
read via ``git show`` and asserts that the scan FAILS there (raises). This
is string-level historical evidence, like the SC-1 prefix-demo approach.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "<MAINTAINER_CONTACT>"
RED_BASELINE_REF = "eb467b8"
RED_BASELINE_FILES = ("streamlit_app.py", "src/frontend/pages/login.py")


def _iter_scan_paths() -> list[Path]:
    paths: list[Path] = [ROOT / "streamlit_app.py"]
    for path in sorted((ROOT / "src").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        paths.append(path)
    return paths


def find_token_matches(text: str) -> list[str]:
    """Return the lines of *text* containing the raw token."""
    return [line for line in text.splitlines() if TOKEN in line]


def test_current_tree_has_no_maintainer_contact_token() -> None:
    """SC-2: zero ``<MAINTAINER_CONTACT>`` matches across src/ + app root."""
    hits: list[str] = []
    for path in _iter_scan_paths():
        text = path.read_text(encoding="utf-8")
        for line in find_token_matches(text):
            hits.append(f"{path.relative_to(ROOT)}: {line}")
    assert not hits, (
        f"SC-2 violation: {TOKEN} literal present in {len(hits)} source line(s):\n"
        + "\n".join(hits)
    )


def test_red_baseline_eb4678b_token_literals_fail() -> None:
    """RED evidence: the same scan FAILS against the pre-fix trunk state.

    Reads ``eb467b8`` file contents via ``git show`` (no checkout) and
    asserts the token scan raises on at least one of them — proving the
    enforcement test would have failed before the fix, rather than being a
    vacuous pass.
    """
    baseline_hits: dict[str, list[str]] = {}
    for rel in RED_BASELINE_FILES:
        proc = subprocess.run(
            ["git", "show", f"{RED_BASELINE_REF}:{rel}"],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        baseline_hits[rel] = find_token_matches(proc.stdout)
    total = sum(len(lines) for lines in baseline_hits.values())
    assert total > 0, (
        "RED invalid: pre-fix trunk state "
        f"{RED_BASELINE_REF} contains no {TOKEN} literals, so the "
        "enforcement test could not have failed there"
    )
    # The historical check itself must FAIL (RED), i.e. it must raise.
    for rel, lines in baseline_hits.items():
        if not lines:
            continue
        try:
            assert not lines, f"{rel}: {lines[0]}"
        except AssertionError:
            pass
        else:  # pragma: no cover - unreachable when lines is non-empty
            raise AssertionError(f"RED invalid: historical scan did not fail on {rel}")
