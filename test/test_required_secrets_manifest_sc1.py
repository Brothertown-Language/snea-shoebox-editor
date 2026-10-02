"""RED test for SC-1 (issue #1397) — required-secrets manifest.

Asserts a machine-checkable required-secrets manifest exists at
``.streamlit/required_secrets.yaml`` and covers every ``st.secrets`` key
path accessed in code, with the manifest containing dotted key PATHS only
(never values).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / ".streamlit" / "required_secrets.yaml"

# Every st.secrets key path accessed in code (inventory of access sites in
# streamlit_app.py, src/services/infrastructure_service.py, src/aiven_utils.py,
# src/services/identity_service.py, src/database/connection.py,
# src/logging_config.py, src/frontend/ui_utils.py, src/frontend/pages/login.py).
EXPECTED_REQUIRED_KEY_PATHS = {
    "runtime.mode",
    "github_oauth.client_id",
    "github_oauth.client_secret",
    "github_oauth.authorize_url",
    "github_oauth.token_url",
    "github_oauth.user_info_url",
    "github_oauth.redirect_uri",
    "contact.maintainer_label",
    "contact.mastodon_url",
    "connections.postgresql.url",
    "aiven.project_name",
    "aiven.service_name",
    "aiven.api_token",
}


def _load_manifest() -> list:
    assert MANIFEST_PATH.exists(), (
        f"Required-secrets manifest missing at {MANIFEST_PATH}. "
        "Create .streamlit/required_secrets.yaml as the single source of truth."
    )
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert data is not None, "Manifest file is empty"
    if isinstance(data, dict):
        assert "required_secrets" in data, "Manifest dict must contain a 'required_secrets' list of dotted key paths"
        data = data["required_secrets"]
    assert isinstance(data, list), "Manifest must be a list of dotted key paths"
    return data


def test_sc1_manifest_exists() -> None:
    _load_manifest()


def test_sc1_manifest_is_dotted_paths_without_values() -> None:
    entries = _load_manifest()
    for entry in entries:
        assert isinstance(entry, str), f"Manifest entry is not a string: {entry!r}"
        assert "=" not in entry, f"Manifest entry contains '=' (value leakage): {entry!r}"
        # A dotted key path: non-empty segments, no spaces or value text.
        segments = entry.split(".")
        assert len(segments) >= 2, f"Manifest entry is not a dotted path: {entry!r}"
        assert all(seg and seg == seg.strip() and " " not in seg for seg in segments), (
            f"Manifest entry is not a clean dotted key path: {entry!r}"
        )


def test_sc1_manifest_covers_every_accessed_key_path() -> None:
    entries = _load_manifest()
    manifest_paths = set(entries)
    missing = EXPECTED_REQUIRED_KEY_PATHS - manifest_paths
    assert not missing, f"Manifest is missing required key paths accessed in code: {sorted(missing)}"


def test_sc1_manifest_covers_critical_contact_keys() -> None:
    entries = _load_manifest()
    manifest_paths = set(entries)
    assert "contact.maintainer_label" in manifest_paths
    assert "contact.mastodon_url" in manifest_paths


def test_sc1_manifest_matches_reference_store_structure() -> None:
    """Manifest paths must resolve against the reference store structure."""
    import tomllib

    store = tomllib.loads((PROJECT_ROOT / ".streamlit" / "secrets.toml").read_text(encoding="utf-8"))

    def resolve(path: str, mapping: dict) -> bool:
        node = mapping
        for seg in path.split("."):
            if not isinstance(node, dict) or seg not in node:
                return False
            node = node[seg]
        return True

    unresolvable = [p for p in _load_manifest() if not resolve(p, store)]
    assert not unresolvable, f"Manifest paths not present in reference store .streamlit/secrets.toml: {unresolvable}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
