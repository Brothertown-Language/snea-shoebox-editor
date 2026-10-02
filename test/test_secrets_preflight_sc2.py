"""RED test for SC-2 (issue #1397) — preflight verification.

Asserts a preflight check compares a deploy target secrets store mapping
(nested dict, e.g. parsed secrets structure) against the required-secrets
manifest's dotted key paths and returns a structured report naming missing
key PATHS only (never values).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

import pytest
import yaml

from src.services.secrets_preflight import check_required_secrets

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / ".streamlit" / "required_secrets.yaml"


def _manifest_paths() -> list:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data["required_secrets"]


def _complete_store() -> dict:
    """Build a store mapping satisfying every manifest path."""
    store: dict = {}
    for path in _manifest_paths():
        node = store
        segments = path.split(".")
        for seg in segments[:-1]:
            node = node.setdefault(seg, {})
        node[segments[-1]] = "dummy-value"
    return store


def test_sc2_missing_key_is_reported() -> None:
    """A store mapping missing one manifest key yields a report naming that PATH."""
    store = _complete_store()
    del store["contact"]["maintainer_label"]
    report = check_required_secrets(store, _manifest_paths())
    assert isinstance(report, dict), "Preflight must return a structured report"
    missing = report.get("missing")
    assert missing is not None, "Report must contain a 'missing' entry"
    assert "contact.maintainer_label" in missing, (
        f"Report must name the missing key PATH 'contact.maintainer_label'; got {missing!r}"
    )


def test_sc2_complete_store_reports_nothing_missing() -> None:
    """A store mapping satisfying every manifest path reports no missing paths."""
    report = check_required_secrets(_complete_store(), _manifest_paths())
    assert isinstance(report, dict)
    missing = report.get("missing")
    assert missing == [] or not missing, f"Complete store must report no missing paths; got {missing!r}"


def test_sc2_multiple_missing_keys_all_named() -> None:
    """Every missing manifest path is named in the report."""
    store = _complete_store()
    del store["contact"]["maintainer_label"]
    del store["aiven"]["api_token"]
    report = check_required_secrets(store, _manifest_paths())
    missing = report.get("missing")
    assert "contact.maintainer_label" in missing
    assert "aiven.api_token" in missing


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
