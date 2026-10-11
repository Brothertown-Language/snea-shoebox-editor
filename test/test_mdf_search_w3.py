"""W3 page-integration verification for the MDF Reference search.

Spec of record: issue #1417 (the GitHub issue body carries the full spec).
W3 instrument: structural — the filter input's call path invokes the scorer
module and the v1 ``filter_topics`` is not on the filter path; behavioral —
the candidate table is executed through the page's search entry point
(in-process; no live-app run).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
import json
from pathlib import Path

import pytest

streamlit = pytest.importorskip("streamlit")

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = REPO_ROOT / "src" / "frontend" / "pages" / "mdf_reference.py"
MASTER_PATH = REPO_ROOT / "docs" / "mdf" / "build" / "master.json"

_SPEC = importlib.util.spec_from_file_location("mdf_reference_page_w3", PAGE_PATH)


def _page_module():
    assert _SPEC is not None and _SPEC.loader is not None
    mod = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def topics():
    with MASTER_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["topics"]


# --- Structural: the scorer is on the filter path, the v1 filter is not -------


def test_filter_path_invokes_scorer_not_v1_filter():
    mod = _page_module()
    assert not hasattr(mod, "filter_topics"), (
        "the v1 substring filter must leave the filter path entirely (dead code deleted, not merely bypassed)"
    )
    assert hasattr(mod, "search_topics"), "the page must expose its search entry point"
    import inspect

    source = inspect.getsource(mod.search_topics)
    assert "mdf_search" in source, "the search entry point must invoke the scorer module"
    assert "mdf_search_vocabulary" in source, "the search entry point must route through the seeded vocabulary table"


# --- Behavioral: the candidate table through the page's entry point -----------


def _keys(mod, topics, query):
    return [key for key, _score in mod.search_topics(topics, query)]


def test_entry_point_marker_code_first(topics):
    mod = _page_module()
    assert _keys(mod, topics, "cf")[0] == "cf"
    assert _keys(mod, topics, "lx")[0] == "lx"


def test_entry_point_multi_term_ranking(topics):
    mod = _page_module()
    keys = _keys(mod, topics, "part of speech")
    assert keys[0] == "ps" and keys[1] == "pn"


def test_entry_point_seeded_vocabulary_rows(topics):
    mod = _page_module()
    assert all(key.startswith("pd") for key in _keys(mod, topics, "paradigms")[:4])
    assert _keys(mod, topics, "inflected")[0] == "lc"
    assert set(_keys(mod, topics, "word class")[:2]) == {"ps", "pn"}


def test_entry_point_unicode_queries(topics):
    mod = _page_module()
    assert _keys(mod, topics, "léwat") == ["lc"]
    assert _keys(mod, topics, "ADÁ") == ["Alternate_Hierarchy"]


def test_entry_point_empty_and_punctuation_queries(topics):
    mod = _page_module()
    assert mod.search_topics(topics, "") == []
    assert mod.search_topics(topics, "   ") == []
    assert mod.search_topics(topics, "///") == []
