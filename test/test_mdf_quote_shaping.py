"""Unit tests for the deterministic typographic quote shaper (.issues/1379).

Developer directive 2026-10-06: a per-character lookback state machine — no
regex on content. A straight double/single quote whose PRECEDING character is
alphanumeric, ")", "]", ".", ",", ";", ":", "!", or "?" becomes the CLOSING
form (American typesetting: sentence punctuation sits inside the quotes);
any other preceding character — whitespace, string/line start, "(", "[", or
anything else — becomes the OPENING form. Already-curly input passes through
unchanged (idempotent). Shaping applies only to prose rendering paths;
\\ftx/\\fxv verbatim blocks stay byte-exact straight quotes, and master.json
is never touched.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
VENDORED_LUNR = REPO_ROOT / "docs" / "mdf" / "build" / "site" / "assets" / "lunr.js"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


convert = load_module("convert_mdf_master_quote_shaping", SCRIPTS / "convert_mdf_master.py")
shape_quotes = convert.shape_quotes


def test_opening_contexts_yield_opening_forms():
    assert shape_quotes('say "hi"', "unicode") == "say “hi”"
    assert shape_quotes('" Leading', "unicode") == "“ Leading"
    assert shape_quotes('first\n"second', "unicode") == "first\n“second"
    assert shape_quotes('(marked "x")', "unicode") == "(marked “x”)"
    assert shape_quotes('[note "x"]', "unicode") == "[note “x”]"
    assert shape_quotes("('x')", "unicode") == "(‘x’)"
    assert shape_quotes("say 'hi'", "unicode") == "say ‘hi’"


def test_closing_contexts_yield_closing_forms():
    for prev in "aZ0)].,;:!?":
        assert shape_quotes(f'x{prev}"', "unicode") == f"x{prev}”", repr(prev)
        assert shape_quotes(f"x{prev}'", "unicode") == f"x{prev}’", repr(prev)


def test_apostrophes_in_contractions_and_possessives_close():
    assert shape_quotes("don't", "unicode") == "don’t"
    assert shape_quotes("doesn't print normally", "unicode") == "doesn’t print normally"
    assert shape_quotes("the field's label", "unicode") == "the field’s label"


def test_already_curly_input_passes_through_unchanged_and_idempotent():
    curly = "“open” ‘single’ — don’t"
    assert shape_quotes(curly, "unicode") == curly
    assert shape_quotes(curly, "latex") == curly
    once = shape_quotes('He said "hi" — it\'s fine', "unicode")
    assert shape_quotes(once, "unicode") == once


def test_latex_form_emits_tex_ligatures():
    assert shape_quotes('He said "hi".', "latex") == "He said ``hi''."
    assert shape_quotes("say 'x'", "latex") == "say `x'"
    assert shape_quotes("it's", "latex") == "it's"


def test_latex_ligatures_survive_escaping():
    shaped = shape_quotes('the "mark" & #5_2', "latex")
    assert shaped == "the ``mark'' & #5_2"
    assert convert.latex_escape(shaped) == "the ``mark'' \\& \\#5\\_2"


def minimal_document(blocks):
    return {
        "schema": "snea-mdf-master/1",
        "generator": "test",
        "source": {"path": "t.txt", "sha256": "0", "bytes": 0, "lines": 1, "git_last_modified": "2026-01-01"},
        "document_header": {"preamble": [], "title": "1.9a test", "blocks": []},
        "home_key": "aa",
        "chapter_keys": [],
        "warnings": [],
        "topics": [
            {
                "key": "aa",
                "key_text": "\\key aa",
                "line": 1,
                "index": 0,
                "heading": "Test topic",
                "is_chapter": False,
                "chapter": None,
                "occurrence": 1,
                "duplicate": False,
                "preamble": [],
                "blocks": blocks,
            }
        ],
    }


PROSE_BLOCK = {"marker": "txt", "text": "\\txt He said \"hi\" then 'left'.", "line": 2}
VERBATIM_BLOCK = {"marker": "ftx", "text": "\\ftx verbatim \"q\" and 'lit'", "line": 3}


def test_latex_verbatim_stays_straight_while_prose_shapes(tmp_path):
    tex = tmp_path / "master.tex"
    convert.render_latex(minimal_document([PROSE_BLOCK, VERBATIM_BLOCK]), str(tex))
    text = tex.read_text(encoding="utf-8")
    assert "He said ``hi'' then `left'." in text
    verbatim = (
        "\\begin{Verbatim}[fontsize=\\footnotesize,breaklines,breakanywhere]\nverbatim \"q\" and 'lit'\n\\end{Verbatim}"
    )
    assert verbatim in text


def test_html_verbatim_stays_straight_while_prose_shapes(tmp_path):
    site = tmp_path / "site"
    (site / "assets").mkdir(parents=True)
    shutil.copy(VENDORED_LUNR, site / "assets" / "lunr.js")
    convert.render_html(minimal_document([PROSE_BLOCK, VERBATIM_BLOCK]), str(site))
    html = (site / "index.html").read_text(encoding="utf-8")
    assert "He said “hi” then ‘left’." in html
    assert '<pre class="example mdf-example"><code>verbatim "q" and \'lit\'</code></pre>' in html


def test_foreword_typography_point_wording():
    expected = (
        "Typography, page layout, bookmarks, pagination, and typographic quotation marks are new "
        "to this edition; the text itself is unchanged. Formatting examples keep the source's "
        "literal straight quotes, as they depict exact database input."
    )
    assert convert.FOREWORD_CHANGES[-1] == expected


def test_foreword_renders_shaped_quotes_both_registers(tmp_path):
    latex = convert.latex_prose(" ".join(convert.FOREWORD_CHANGES))
    assert "``See also''" in latex
    assert "source's" in latex
    site = tmp_path / "site"
    (site / "assets").mkdir(parents=True)
    shutil.copy(VENDORED_LUNR, site / "assets" / "lunr.js")
    convert.render_html(minimal_document([PROSE_BLOCK]), str(site))
    foreword = (site / "foreword.html").read_text(encoding="utf-8")
    assert "“See also”" in foreword
    assert "source’s" in foreword
    assert "typographic quotation marks" in foreword
