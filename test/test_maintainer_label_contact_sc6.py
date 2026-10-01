"""Enforcement test for SC-SC6 (issue 1392).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SECRETS_FILES = [
    PROJECT_ROOT / ".streamlit" / "secrets.toml",
    PROJECT_ROOT / ".streamlit" / "secrets.toml.production",
]


def test_maintainer_label_present_in_each_secrets_template():
    """SC-6: contact.maintainer_label key present in each secrets template."""
    for path in SECRETS_FILES:
        assert path.exists(), f"missing secrets template: {path}"
        content = path.read_text(encoding="utf-8")
        hits = [
            line
            for line in content.splitlines()
            if "maintainer_label" in line
        ]
        assert hits, f"no 'maintainer_label' hit in {path}"