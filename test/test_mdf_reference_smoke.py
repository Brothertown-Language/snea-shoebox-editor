"""In-process smoke tests for the MDF Reference page (.issues/1379 Phase 5).

Serverless checks of the page module's pure helpers (master.json loader,
hierarchy data, deep-link resolution) and the navigation registration.
Real-browser user-visible behavior is verified by the Playwright E2E suite
(test/ui/test_mdf_reference_e2e.py) per docs/development/ui_testing_standard.md.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
from pathlib import Path

import pytest

streamlit = pytest.importorskip("streamlit")

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = REPO_ROOT / "src" / "frontend" / "pages" / "mdf_reference.py"
MASTER_PATH = REPO_ROOT / "docs" / "mdf" / "build" / "master.json"

EXPECTED_TOPIC_COUNT = 108
EXPECTED_CHAPTER_COUNT = 17
EXPECTED_HOME_KEY = "aa"

_SPEC = importlib.util.spec_from_file_location("mdf_reference_page", PAGE_PATH)


def _page_module():
    assert _SPEC is not None and _SPEC.loader is not None
    mod = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(mod)
    return mod


def test_smoke_sc7_page_module_exists_with_entrypoint():
    """SC-7 (structural): the MDF Reference page module exists and exposes the
    page entrypoint Streamlit executes."""
    mod = _page_module()
    assert callable(mod.mdf_reference), "page module must define mdf_reference()"


def test_smoke_sc7_loader_reads_master_with_108_topics():
    """SC-7 (data): the loader reads the committed master.json and exposes the
    108 keyed topics, the 17 chapter keys in home-TOC order, and home key aa."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    assert master is not None, "master.json must load from the repo root"
    assert master["schema"] == "snea-mdf-master/1"
    topics = master["topics"]
    assert len(topics) == EXPECTED_TOPIC_COUNT
    assert len(master["chapter_keys"]) == EXPECTED_CHAPTER_COUNT
    assert master["home_key"] == EXPECTED_HOME_KEY
    keys = {t["key"] for t in topics}
    assert EXPECTED_HOME_KEY in keys
    assert set(master["chapter_keys"]) <= keys


def test_smoke_sc7_loader_missing_file_returns_none():
    """Edge case: a missing master.json must return None (the page shows an
    actionable error instead of crashing)."""
    mod = _page_module()
    assert mod.load_master(REPO_ROOT / "does" / "not" / "exist") is None


def test_smoke_sc7_selection_defaults_to_home_entry():
    """SC-7 (behavior): with no ?marker= query parameter the selection resolves
    to the source's home/TOC entry (aa)."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics_by_key = {t["key"]: t for t in master["topics"]}
    selected, notice = mod.resolve_selection(None, topics_by_key, master["home_key"])
    assert selected == EXPECTED_HOME_KEY
    assert notice is None


def test_smoke_sc7_selection_resolves_known_deep_link():
    """SC-7 (behavior): ?marker=ge resolves to the ge topic."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics_by_key = {t["key"]: t for t in master["topics"]}
    selected, notice = mod.resolve_selection("ge", topics_by_key, master["home_key"])
    assert selected == "ge"
    assert notice is None


def test_smoke_sc7_unknown_deep_link_falls_back_to_home_with_notice():
    """Edge case: ?marker=zz must fall back to the home entry with a visible
    notice (never an error or blank pane)."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics_by_key = {t["key"]: t for t in master["topics"]}
    selected, notice = mod.resolve_selection("zz", topics_by_key, master["home_key"])
    assert selected == EXPECTED_HOME_KEY
    assert notice is not None and "zz" in notice


def test_smoke_sc7_nav_registers_mdf_reference_in_main_for_all_roles():
    """SC-7/R-12 (structural): the MDF Reference page is registered under the
    Main section for viewer, editor, and admin, and in the unauthenticated
    deep-link capture list."""
    from src.services.navigation_service import NavigationService

    page = NavigationService.PAGE_MDF_REFERENCE
    assert page is not None
    for role in ("viewer", "editor", "admin"):
        tree = NavigationService.get_navigation_tree(logged_in=True, user_role=role)
        assert page in tree["Main"], f"MDF Reference missing from Main for role {role}"
    unauth = NavigationService.get_navigation_tree(logged_in=False)
    assert page in unauth, "MDF Reference missing from the unauthenticated page list"


def test_smoke_sc7_every_topic_has_browser_material():
    """SC-7 (data): every topic carries the fields the browser and detail pane
    render (key, blocks) and chapter topics are flagged; marker topics carry
    their chapter assignment."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics = master["topics"]
    chapters = [t for t in topics if t["is_chapter"]]
    markers = [t for t in topics if not t["is_chapter"]]
    assert len(chapters) == EXPECTED_CHAPTER_COUNT
    assert len(markers) == EXPECTED_TOPIC_COUNT - EXPECTED_CHAPTER_COUNT
    for t in topics:
        assert t["key"]
        assert isinstance(t["blocks"], list)
    for t in markers:
        if t["key"] == master["home_key"]:
            # The home/TOC entry belongs to no chapter — it sits above them.
            continue
        assert t["chapter"] in set(master["chapter_keys"]), t["key"]


def test_smoke_sc8_every_cf_target_resolves_among_topics():
    """SC-8: every cross-reference target named by the source's \\cf fields
    must resolve to a rendered topic key in master.json."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    targets = mod.collect_cf_targets(master)
    assert targets, "the source's \\cf fields must yield cross-reference targets"
    keys = {t["key"] for t in master["topics"]}
    unresolved = sorted({target for target in targets if target not in keys})
    assert not unresolved, f"{len(unresolved)} \\cf targets do not resolve: {unresolved[:10]}"


def test_smoke_sc8_split_flags_missing_targets_for_placeholder():
    """SC-8 (defensive): a \\cf target absent from the topic keys must be
    flagged for the visible placeholder, while resolved targets pass through."""
    mod = _page_module()
    resolved, missing = mod.split_cf_targets(["aa", "ge", "zz"], {"aa", "ge"})
    assert resolved == ["aa", "ge"]
    assert missing == ["zz"]


def test_smoke_sc9_filter_matches_keys_case_insensitively():
    """SC-9: an uppercase query matches the lowercase topic key (substring
    over definition text may also legitimately match other topics that
    mention the marker)."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics = master["topics"]
    keys = [t["key"] for t in mod.filter_topics(topics, "LX")]
    assert "lx" in keys, "the lowercase key must match the uppercase query"


def test_smoke_sc9_filter_matches_definition_text():
    """SC-9: a query term occurring only in definition text (not the key)
    matches the topics whose text contains it."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics = master["topics"]
    matches = [t["key"] for t in mod.filter_topics(topics, "interlinear morpheme-level glossing")]
    assert "ge" in matches, "the ge definition contains 'interlinear morpheme-level glossing'"


def test_smoke_sc9_filter_matches_accented_source_content():
    """SC-9: accented source content (á, é) matches losslessly — plain
    substring on raw text, no normalization stripping the diacritics."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    topics = master["topics"]
    assert [t["key"] for t in mod.filter_topics(topics, "adá")] == ["Alternate_Hierarchy"]
    assert [t["key"] for t in mod.filter_topics(topics, "léwat")] == ["lc"]
    # Case-insensitivity must also hold for the accented query term itself.
    keys = [t["key"] for t in mod.filter_topics(topics, "ADÁ")]
    assert keys == ["Alternate_Hierarchy"]


def test_smoke_sc9_filter_does_not_normalize():
    """SC-9: matching operates on raw text — a NFD-decomposed query must NOT
    match the source's precomposed á (normalization is out of scope by spec)."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    decomposed = "ad\u0301a" if False else "ada\u0301"  # 'a' + combining acute + 'a'
    assert mod.filter_topics(master["topics"], decomposed) == []


def test_smoke_sc9_filter_empty_query_returns_all_topics():
    """SC-9: an empty query yields the full topic list (browser tree mode)."""
    mod = _page_module()
    master = mod.load_master(REPO_ROOT)
    assert len(mod.filter_topics(master["topics"], "")) == 108


def test_smoke_sc11_pdf_loader_and_r14_filename():
    """SC-11/R-14 (structural): the PDF loader reads the committed deliverable
    and the served filename constant is exactly mdf-lexical-fields-1.9a.pdf."""
    mod = _page_module()
    assert mod.PDF_FILENAME == "mdf-lexical-fields-1.9a.pdf"
    pdf_path = REPO_ROOT / "docs" / "mdf" / "build" / "mdf-lexical-fields-1.9a.pdf"
    if pdf_path.exists():  # the concurrent build may not have produced it yet
        data = mod.load_pdf_bytes(REPO_ROOT)
        assert data == pdf_path.read_bytes()
    missing = mod.load_pdf_bytes(REPO_ROOT / "does" / "not" / "exist")
    assert missing is None
