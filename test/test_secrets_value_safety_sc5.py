"""RED test for SC-5 (issue #1397) — secret-value safety in preflight.

Cross-cutting constraint: preflight output and logs must never contain
secret VALUES — the comparison is key-presence only. This test feeds a
store mapping with distinctive sentinel values and asserts:

1. The structured report contains no sentinel values (paths only).
2. Preflight logs its missing-path report at operator-visible level.
3. Captured log output contains no sentinel values.

Assertion 2 is the RED trigger: the preflight module currently emits no
log records at all, so a test requiring a value-safe log record fails.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
import logging
from pathlib import Path

import yaml

from src.services.secrets_preflight import check_required_secrets

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / ".streamlit" / "required_secrets.yaml"

SENTINEL_A = "SENTINEL-SECRET-VALUE-ALPHA-7f3a"
SENTINEL_B = "SENTINEL-SECRET-VALUE-BRAVO-9c2e"
PREFLIGHT_LOGGER = "src.services.secrets_preflight"


def _manifest_paths() -> list:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data["required_secrets"]


def _store_with_sentinel_values() -> dict:
    """Build a store whose VALUES are unique sentinels — never real secrets."""
    store: dict = {}
    for i, path in enumerate(_manifest_paths()):
        node = store
        segments = path.split(".")
        for seg in segments[:-1]:
            node = node.setdefault(seg, {})
        node[segments[-1]] = f"{SENTINEL_A}-{i}"
    store["contact"]["mastodon_url"] = SENTINEL_B
    del store["contact"]["maintainer_label"]
    return store


def test_sc5_report_contains_no_secret_values() -> None:
    """The structured report names missing PATHS only — no values leak."""
    store = _store_with_sentinel_values()
    report = check_required_secrets(store, _manifest_paths())
    serialized = json.dumps(report)
    assert SENTINEL_A not in serialized, "Report leaked a store VALUE"
    assert SENTINEL_B not in serialized, "Report leaked a store VALUE"
    assert "contact.maintainer_label" in report["missing"]


def test_sc5_preflight_logs_value_safe_report(caplog) -> None:
    """Preflight emits a log record naming the missing PATH with no values."""
    store = _store_with_sentinel_values()
    with caplog.at_level(logging.DEBUG, logger=PREFLIGHT_LOGGER):
        check_required_secrets(store, _manifest_paths())
    preflight_records = [r for r in caplog.records if r.name == PREFLIGHT_LOGGER]
    assert preflight_records, (
        "Preflight must log its report (value-safe operator visibility); no log records were emitted"
    )
    log_text = "\n".join(r.getMessage() for r in preflight_records)
    assert "contact.maintainer_label" in log_text, f"Log must name the missing key PATH; got: {log_text!r}"
    assert SENTINEL_A not in log_text, "Preflight log leaked a store VALUE"
    assert SENTINEL_B not in log_text, "Preflight log leaked a store VALUE"
