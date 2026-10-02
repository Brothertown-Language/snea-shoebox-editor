"""RED test for SC-6 (issue #1397, spec Revision 1) — default-fallback contact
resolution, never crash on a missing contact key.

Asserts that a store mapping missing ``contact.maintainer_label`` does NOT
raise RuntimeError. Instead, the startup resolution path:

1. Continues with the static default — ``contact.mastodon_url`` rendered as
   the contact when no label is configured,
2. Emits exactly ONE non-blocking operator warning naming the missing key
   PATH only (value-safety: never the secret VALUE), and
3. Proceeds — the app startup continues (no RuntimeError).

A complete store still resolves the configured label.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / ".streamlit" / "required_secrets.yaml"

MISSING_PATH = "contact.maintainer_label"
DUMMY_LABEL = "dummy-maintainer-label-value"
DUMMY_URL = "https://dummy.example/mastodon"


def _manifest_paths() -> list:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data["required_secrets"]


def _complete_store() -> dict:
    store: dict = {}
    for path in _manifest_paths():
        node = store
        segments = path.split(".")
        for seg in segments[:-1]:
            node = node.setdefault(seg, {})
        node[segments[-1]] = DUMMY_URL
    store["contact"]["maintainer_label"] = DUMMY_LABEL
    return store


def _store_missing_label() -> dict:
    store = _complete_store()
    del store["contact"]["maintainer_label"]
    return store


def test_sc6_missing_label_does_not_raise_runtime_error() -> None:
    """SC-6: a store missing contact.maintainer_label must NOT raise
    RuntimeError — resolution continues with the static default."""
    from streamlit_app import resolve_maintainer_contact

    resolved = None
    try:
        resolved = resolve_maintainer_contact(_store_missing_label())
    except RuntimeError as exc:
        pytest.fail(
            f"SC-6: startup must NOT raise RuntimeError on a missing contact.maintainer_label; got RuntimeError: {exc}"
        )
    assert resolved == DUMMY_URL, (
        "SC-6: with no label configured, the static default "
        f"({DUMMY_URL} — contact.mastodon_url) must be resolved as the "
        f"contact; got {resolved!r}"
    )


def test_sc6_complete_store_returns_configured_label() -> None:
    """SC-6: a complete store still resolves the configured label."""
    from streamlit_app import resolve_maintainer_contact

    assert resolve_maintainer_contact(_complete_store()) == DUMMY_LABEL


def test_sc6_exactly_one_warning_names_missing_path_only(caplog) -> None:
    """SC-6: exactly one non-blocking operator warning naming the missing
    key PATH only — never a secret VALUE."""
    from streamlit_app import resolve_maintainer_contact

    with caplog.at_level(logging.WARNING):
        resolve_maintainer_contact(_store_missing_label())

    warnings = [rec for rec in caplog.records if rec.levelno >= logging.WARNING]
    assert len(warnings) == 1, (
        "SC-6: exactly ONE operator warning must be emitted for the missing "
        f"key; got {len(warnings)}: {[r.getMessage() for r in warnings]}"
    )
    message = warnings[0].getMessage()
    assert MISSING_PATH in message, (
        f"SC-6: the warning must name the missing key PATH {MISSING_PATH!r}; got {message!r}"
    )
    assert DUMMY_LABEL not in message, "SC-6: value-safety — the warning must NEVER contain the secret VALUE"
    assert DUMMY_URL not in message, "SC-6: value-safety — the warning must NEVER contain any secret VALUE"


def test_sc6_no_warning_when_store_complete(caplog) -> None:
    """SC-6: a complete store emits no operator warning."""
    from streamlit_app import resolve_maintainer_contact

    with caplog.at_level(logging.WARNING):
        resolve_maintainer_contact(_complete_store())

    warnings = [rec for rec in caplog.records if rec.levelno >= logging.WARNING]
    assert not warnings, f"SC-6: complete store must emit no warning; got {[r.getMessage() for r in warnings]}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
