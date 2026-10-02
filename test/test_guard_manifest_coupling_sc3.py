"""RED test for SC-3 (issue #1397) — guard/manifest single-source coupling.

Asserts the startup guard's required-key list is sourced from the
required-secrets manifest through one shared loader:

1. A shared loader function exists (in the preflight module) that reads
   ``.streamlit/required_secrets.yaml`` and returns the dotted key paths.
2. Adding a key to the manifest changes the loader's output — the guard
   therefore cannot silently diverge from the manifest.
3. ``streamlit_app.py`` contains NO duplicated hardcoded required-key list:
   the guard no longer indexes ``st.secrets["contact"]["maintainer_label"]``
   directly and instead delegates to the shared manifest-sourced path list.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / ".streamlit" / "required_secrets.yaml"
APP_PATH = PROJECT_ROOT / "streamlit_app.py"
SENTINEL_PATH = "contact.zzz_sc3_sentinel_probe"


def _manifest_paths() -> list:
    import yaml

    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    return data["required_secrets"]


def test_sc3_shared_manifest_loader_exists_and_returns_paths() -> None:
    """SC-3: a shared loader reads the manifest and returns its dotted paths."""
    from src.services.secrets_preflight import load_required_secret_paths

    paths = load_required_secret_paths()
    assert isinstance(paths, list), "loader must return a list of dotted key paths"
    assert paths == _manifest_paths(), f"loader output must equal the manifest contents; got {paths!r}"


def test_sc3_manifest_addition_changes_loader_output(tmp_path, monkeypatch) -> None:
    """SC-3 divergence check: adding a key to the manifest must change the
    required-key list the guard consumes — proving single-source coupling."""
    from src.services import secrets_preflight

    custom = tmp_path / "required_secrets.yaml"
    custom.write_text(
        f"required_secrets:\n  - contact.maintainer_label\n  - {SENTINEL_PATH}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(secrets_preflight, "MANIFEST_PATH", custom)
    paths = secrets_preflight.load_required_secret_paths()
    assert SENTINEL_PATH in paths, (
        f"adding a manifest key must change the guard-consumed required-key list; got {paths!r}"
    )


def test_sc3_no_duplicated_hardcoded_key_list_in_guard() -> None:
    """SC-3: streamlit_app.py must not hardcode the required-key list.

    The guard must delegate to the shared manifest-sourced path list instead
    of directly indexing st.secrets["contact"]["maintainer_label"].
    """
    from src.services.secrets_preflight import load_required_secret_paths

    assert callable(load_required_secret_paths)

    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # No direct st.secrets["contact"]["maintainer_label"] indexing remains:
    # the guard's hardcoded access is the duplication defect this SC removes.
    subscript_keys: list[str] = []

    def _walk(node) -> None:
        if isinstance(node, ast.Subscript):
            try:
                rendered = ast.unparse(node)
            except Exception:
                rendered = ""
            if "st.secrets" in rendered and "maintainer_label" in rendered:
                subscript_keys.append(rendered)
        for child in ast.iter_child_nodes(node):
            _walk(child)

    _walk(tree)
    assert not subscript_keys, (
        "guard must not hardcode st.secrets['contact']['maintainer_label'] "
        f"access; found {subscript_keys!r}. Required keys must come from the "
        "shared manifest loader."
    )

    # The guard module must consume the shared manifest loader — the same
    # source of truth preflight uses.
    assert "load_required_secret_paths" in source or "check_required_secrets" in source, (
        "streamlit_app.py guard must consume the shared manifest loader "
        "(load_required_secret_paths / check_required_secrets from "
        "src.services.secrets_preflight)"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
