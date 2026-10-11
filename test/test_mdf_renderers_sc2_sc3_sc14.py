"""Renderer-output tests for the MDF reference build (issue #1379, SC-2/SC-3/SC-14).

Runs against the committed build artifacts in docs/mdf/build/ — no database, no
network. SC-2: every \\cf hyperlink resolves to an existing anchor. SC-3: 108
anchors 1:1 against the source key list (HTML) and key presence in master.tex.
SC-14: 444 example blocks on the HTML site and in the PDF (pdftotext).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
BUILD = REPO_ROOT / "docs" / "mdf" / "build"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify_mdf_outputs = load_module("verify_mdf_outputs", SCRIPTS / "verify_mdf_outputs.py")
convert_mdf_master = load_module("convert_mdf_master", SCRIPTS / "convert_mdf_master.py")


@pytest.fixture(scope="module")
def document():
    return json.loads((BUILD / "master.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def site_dir():
    site = BUILD / "site"
    if not (site / "index.html").is_file():
        pytest.fail("docs/mdf/build/site/index.html is missing; run scripts/build_mdf_docs.sh first")
    return site


def test_sc2_every_cf_target_resolves_to_existing_anchor(document, site_dir):
    result = verify_mdf_outputs.check_sc2_html(document, site_dir)
    assert result["failures"] == []
    assert result["ok"]
    assert result["links"] == result["expected_links"]
    assert result["placeholders"] == 0


def test_sc3_html_anchors_1to1_with_source_keys(document, site_dir):
    result = verify_mdf_outputs.check_sc3_html(document, site_dir)
    assert result["failures"] == []
    assert result["ok"]
    assert result["anchors"] == 108
    assert result["expected"] == 108


def test_sc3_tex_roundtrip_all_keys_present(document):
    tex = (BUILD / "master.tex").read_text(encoding="utf-8")
    slugs = convert_mdf_master.build_slugs(document["topics"])
    missing_labels = [
        topic["key"] for topic in document["topics"] if f"\\label{{key:{slugs[topic['key']]}}}" not in tex
    ]
    assert missing_labels == []
    # 2026-10-06 directive: the visible "\key <key>" annotation lines are gone
    # from every rendered surface; the invisible \label{key:<slug>} anchors
    # carry the cross-reference identity. latex_escape never occurs inside
    # Verbatim example content, so the escaped form must not appear at all.
    assert "\\textbackslash{}key" not in tex


def test_sc14_html_examples_444(document, site_dir):
    result = verify_mdf_outputs.check_sc14_html(document, site_dir)
    assert result["failures"] == []
    assert result["examples"] == 444


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext (poppler-utils) not installed")
def test_sc14_pdf_examples_444():
    pdf = BUILD / "mdf-lexical-fields-1.9a.pdf"
    if not pdf.is_file():
        pytest.fail("docs/mdf/build/mdf-lexical-fields-1.9a.pdf is missing; run scripts/build_mdf_docs.sh first")
    result = verify_mdf_outputs.check_sc14_pdf(verify_mdf_outputs.pdf_text(pdf))
    assert result["failures"] == []
    assert result["examples"] == 444
    assert result["distinct"] == 444


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext (poppler-utils) not installed")
def test_sc1_pdf_contains_all_108_keys(document):
    pdf = BUILD / "mdf-lexical-fields-1.9a.pdf"
    if not pdf.is_file():
        pytest.fail("docs/mdf/build/mdf-lexical-fields-1.9a.pdf is missing; run scripts/build_mdf_docs.sh first")
    result = verify_mdf_outputs.check_sc1_sc3_pdf(document, verify_mdf_outputs.pdf_text(pdf))
    assert result["failures"] == []
    assert result["keys_found"] == 108


# ---------------------------------------------------------------------------
# Display-data parity (issues #1431/#1433): the committed HTML nav sidebar,
# the HTML and LaTeX shd2 headings, and the app rail (via #1431's census
# suite) all derive from the same committed display fields in master.json.
# ---------------------------------------------------------------------------


def _nav_anchor_texts(html: str) -> list[str]:
    """Anchor texts inside the <nav class="sidebar"> block, in order."""
    nav_start = html.index('<nav class="sidebar"')
    nav_end = html.index("</nav>", nav_start)
    nav = html[nav_start:nav_end]
    texts = []
    i = 0
    while True:
        open_tag = nav.find("<a ", i)
        if open_tag == -1:
            open_tag = nav.find("<a>", i)
        if open_tag == -1:
            break
        close = nav.index("</a>", open_tag)
        gt = nav.index(">", open_tag)
        texts.append(nav[gt + 1 : close])
        i = close + 4
    return texts


def _home_and_chapter_keys(document):
    return {document["home_key"], *document["chapter_keys"]}


def _marker_entries(document):
    home_key = document["home_key"]
    return [
        t
        for t in document["topics"]
        if convert_mdf_master.is_reference_entry(t, home_key)
    ]


def test_1433_nav_marker_entries_render_token_plus_name(document, site_dir):
    reference_page = (site_dir / "field-marker-reference.html").read_text(encoding="utf-8")
    nav_texts = set()
    for page in site_dir.glob("*.html"):
        nav_texts.update(_nav_anchor_texts(page.read_text(encoding="utf-8")))
    for topic in _marker_entries(document):
        expected = "\\" + topic["display_label"]
        assert expected in nav_texts, f"nav is missing \\{topic['key']} token+name entry"
        # the bare token alone must no longer be a nav label (#1431 SC-1:
        # no bare marker keys left where a name exists)
        assert f"\\{topic['key']}</a>" not in reference_page or topic["key"] in topic["display_label"]
    del reference_page


def test_1433_nav_stub_label_is_its_display_label(document, site_dir):
    stub = document["topics"][-1]
    assert stub["key"] == "1s 1p 1e 1i 1d 2s 2p 2d 3s 3p 3d 4s 4p 4d"
    nav_texts = set()
    for page in site_dir.glob("*.html"):
        nav_texts.update(_nav_anchor_texts(page.read_text(encoding="utf-8")))
    assert stub["display_label"] in nav_texts
    # the raw multi-token key must not appear as a nav label anywhere
    for page in site_dir.glob("*.html"):
        assert stub["key"] not in _nav_anchor_texts(page.read_text(encoding="utf-8"))


def test_1433_nav_has_no_underscore_labels(document, site_dir):
    for page in site_dir.glob("*.html"):
        for text in _nav_anchor_texts(page.read_text(encoding="utf-8")):
            assert "_" not in text, f"underscore nav label {text!r} in {page.name}"


def _shd2_expectations(document):
    """Per-topic map of shd2 display expectations derived independently from
    the committed block text: the marker-stripped first line, with exactly the
    one inventory entry's wrapping parens dropped."""
    inventory = convert_mdf_master.SHD2_DISPLAY_EXCEPTIONS
    expected = {}
    for topic in document["topics"]:
        for block in topic["blocks"]:
            if block["marker"] != "shd2":
                continue
            if (topic["key"], block["line"]) in inventory:
                expected[topic["key"]] = inventory[(topic["key"], block["line"])]["text"]
            else:
                expected[topic["key"]] = convert_mdf_master.field_payload(
                    convert_mdf_master.first_line(block["text"]), "shd2"
                ).strip()
    return expected


def test_1433_html_shd2_headings_carry_display_text(document, site_dir):
    expected = _shd2_expectations(document)
    for topic in document["topics"]:
        if topic["key"] not in expected:
            continue
        if topic["is_chapter"]:
            page = site_dir / f"{topic['key']}.html"
        elif convert_mdf_master.is_reference_entry(topic, document["home_key"]):
            page = site_dir / "field-marker-reference.html"
        else:
            page = site_dir / f"{topic['chapter']}.html"
        html = page.read_text(encoding="utf-8")
        escaped = expected[topic["key"]].replace("&", "&amp;").replace("<", "&lt;")
        assert f'>{escaped}</h3>' in html or f'>{escaped}</h5>' in html, (
            f"{page.name} lacks shd2 display heading {expected[topic['key']]!r}"
        )


def test_1433_html_shd2_paren_exception_is_paren_free(document, site_dir):
    page = (site_dir / "Sections_in_a_Lexical_Entry.html").read_text(encoding="utf-8")
    assert ">Understanding the hierarchical structure of an entry</h3>" in page
    assert ">(Understanding the hierarchical structure of an entry)</h3>" not in page


def test_1433_latex_shd2_headings_carry_display_text(document):
    tex = (BUILD / "master.tex").read_text(encoding="utf-8")
    expected = _shd2_expectations(document)
    for topic in document["topics"]:
        if topic["key"] not in expected:
            continue
        latex_title = convert_mdf_master.latex_escape(
            convert_mdf_master.shape_quotes(expected[topic["key"]], "latex")
        )
        assert latex_title in tex, f"master.tex lacks shd2 display heading for {topic['key']}"
    assert "(Understanding" not in tex.replace("\\(", "("), "paren-wrapped shd2 leaked into LaTeX"


def test_1433_parity_labels_join_across_surfaces(document, site_dir):
    """SC-4: HTML nav, LaTeX reference subsection titles, and master.json
    display data present the same label content for every marker entry."""
    tex = (BUILD / "master.tex").read_text(encoding="utf-8")
    nav_texts = set()
    for page in site_dir.glob("*.html"):
        nav_texts.update(_nav_anchor_texts(page.read_text(encoding="utf-8")))
    for topic in _marker_entries(document):
        label = topic["display_label"]
        assert "\\" + label in nav_texts, f"HTML nav missing {label!r}"
        latex_title = convert_mdf_master.latex_escape(
            convert_mdf_master.shape_quotes(topic["heading"], "latex")
        )
        assert latex_title in tex, f"master.tex missing heading for {topic['key']}"
