"""SC-7 enforcement test: maintainer_label documented in local-development.md.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

DOC = Path("docs/development/local-development.md")


def test_maintainer_label_documented_in_local_development():
    """SC-7: contact.maintainer_label key SHALL be documented in the
    "Configure local secrets" guidance of docs/development/local-development.md."""
    content = DOC.read_text(encoding="utf-8")
    assert "maintainer_label" in content, (
        "SC-7 RED: docs/development/local-development.md carries zero "
        "'maintainer_label' hits; contact.maintainer_label is undocumented."
    )
