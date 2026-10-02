"""RED test for SC-4 (issue #1397, phase 4): outage remediation runbook.

Asserts a developer-only remediation runbook exists under docs/ that:
1. names the exact Streamlit Cloud key to add (``contact.maintainer_label``),
2. documents the preflight verification as the post-remediation confirmation
   step, and
3. names key PATHS only — never secret VALUES.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_CANDIDATES = [
    "remediation",
    "outage",
    "secrets",
]


def _find_runbook() -> Path | None:
    docs = PROJECT_ROOT / "docs"
    if not docs.is_dir():
        return None
    for path in sorted(docs.rglob("*.md")):
        lowered = path.name.lower()
        if "runbook" in lowered and any(term in lowered for term in RUNBOOK_CANDIDATES):
            return path
    return None


def test_runbook_exists_for_streamlit_cloud_outage():
    runbook = _find_runbook()
    assert runbook is not None, (
        "No remediation runbook found under docs/ — SC-4 requires a runbook "
        "documenting the developer-only Streamlit Cloud secrets-store action."
    )


def test_runbook_names_exact_cloud_store_key():
    runbook = _find_runbook()
    assert runbook is not None, "runbook missing"
    text = runbook.read_text(encoding="utf-8")
    assert "contact.maintainer_label" in text, (
        f"{runbook} does not name the exact Cloud-store key 'contact.maintainer_label' to add."
    )


def test_runbook_names_preflight_confirmation_step():
    runbook = _find_runbook()
    assert runbook is not None, "runbook missing"
    text = runbook.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "preflight" in lowered, (
        f"{runbook} does not document the preflight verification as the post-remediation confirmation step."
    )


def test_runbook_names_no_secret_values():
    runbook = _find_runbook()
    assert runbook is not None, "runbook missing"
    text = runbook.read_text(encoding="utf-8")
    # The runbook must instruct adding key PATHS only. The only value the
    # guard expects for maintainer_label (a display label) must not be
    # prescribed as a secret value; assert no 'maintainer_label = ' value
    # assignment form appears (the production template uses that form).
    assert "maintainer_label =" not in text, (
        f"{runbook} appears to prescribe a secret VALUE for "
        "contact.maintainer_label — runbooks must name key PATHS only."
    )
