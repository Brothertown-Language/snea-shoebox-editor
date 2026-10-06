"""Renderer-output tests for the MDF reference build (.issues/1379, SC-2/SC-3/SC-14).

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
