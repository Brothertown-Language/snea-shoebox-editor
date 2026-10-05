"""SC-9 RED (Issue #1413, Item 1): shared key-namespaced pagination-row helper.

The Records page currently duplicates the page-change + auto-save-on-page-change
block once per sidebar button (Prev and Next). SC-9 requires that logic to exist
exactly once, inside a shared pagination-row helper ("_render_pagination_row")
referenced by exactly two call sites (top and bottom rows) with position-distinct
widget keys.

RED state (pre-change): the helper is absent and the auto-save block occurs more
than once, so the assertions FAIL. This is a source-inspection (structural) test
per the spec's SC-9 evidence type.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

from pathlib import Path

RECORDS_PATH = Path("src/frontend/pages/records.py")

AUTO_SAVE_MARKER = 'change_summary="Auto-save via pagination"'
HELPER_MARKER = "def _render_pagination_row"


def test_auto_save_block_exists_exactly_once():
    source = RECORDS_PATH.read_text(encoding="utf-8")
    count = source.count(AUTO_SAVE_MARKER)
    assert count == 1, (
        f"records.py contains the auto-save-on-page-change block {count} times "
        "(expected exactly 1): SC-9 requires a single shared helper"
    )


def test_shared_pagination_row_helper_present():
    source = RECORDS_PATH.read_text(encoding="utf-8")
    assert HELPER_MARKER in source, (
        "records.py has no shared _render_pagination_row helper; "
        "SC-9 requires one helper rendering the full-form navigation row"
    )


def test_helper_referenced_by_exactly_two_call_sites():
    source = RECORDS_PATH.read_text(encoding="utf-8")
    calls = [line for line in source.splitlines() if line.strip().startswith("_render_pagination_row(")]
    assert len(calls) == 2, (
        f"records.py references _render_pagination_row {len(calls)} times "
        "(expected exactly 2: top and bottom rows)"
    )


def test_widget_keys_are_position_namespaced():
    source = RECORDS_PATH.read_text(encoding="utf-8")
    assert '"pagination_{position}_prev"' in source and '"pagination_{position}_next"' in source, (
        "pagination-row widget keys are not position-namespaced "
        "(expected f-string keys pagination_{position}_prev/_next)"
    )


def test_helper_validates_position_fail_fast():
    source = RECORDS_PATH.read_text(encoding="utf-8")
    assert 'if position not in ("top", "bottom")' in source, (
        "the shared helper must fail fast on an invalid position value "
        "rather than silently defaulting (spec edge case)"
    )
