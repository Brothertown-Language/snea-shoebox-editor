"""SC-4a RED: Records sidebar search text_input placeholder must use neutral wording.

The Records search text_input (src/frontend/pages/records.py, st.text_input
in the sidebar search controls) currently uses the Enter-instruction wording
"Enter text..." as its (collapsed) label/placeholder. SC-4a requires a
neutral wording (e.g. "Search terms...") instead of an Enter-instruction.

RED state (pre-change): the source still contains "Enter text...", so the
placeholder assertion FAILS. The companion E2E-file assertion also verifies
that test/ui/test_semantic_search_ui_flow_e2e.py no longer references the
old aria-label.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

RECORDS_PATH = Path("src/frontend/pages/records.py")
E2E_PATH = Path("test/ui/test_semantic_search_ui_flow_e2e.py")

OLD_WORDING = "Enter text..."
NEUTRAL_WORDING = "Search terms..."


def test_records_search_placeholder_is_not_enter_instruction_wording():
    """Primary RED assertion: placeholder/label is neutral, not Enter-instruction."""
    source = RECORDS_PATH.read_text(encoding="utf-8")
    assert OLD_WORDING not in source, (
        f"records.py still contains the Enter-instruction wording {OLD_WORDING!r} "
        "as the search text_input placeholder/label; SC-4a requires neutral wording"
    )


def test_records_search_placeholder_uses_neutral_wording():
    source = RECORDS_PATH.read_text(encoding="utf-8")
    assert NEUTRAL_WORDING in source, (
        f"records.py does not contain the neutral search placeholder wording {NEUTRAL_WORDING!r}"
    )


def test_e2e_flow_file_does_not_reference_old_aria_label():
    """String-level companion assertion: E2E file drops the old aria-label."""
    e2e_source = E2E_PATH.read_text(encoding="utf-8")
    assert OLD_WORDING not in e2e_source, (
        "test/ui/test_semantic_search_ui_flow_e2e.py still references the old "
        f"aria-label {OLD_WORDING!r}; update the selector to the neutral wording"
    )
