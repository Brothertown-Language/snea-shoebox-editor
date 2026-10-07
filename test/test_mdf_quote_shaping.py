"""Unit tests for the deterministic typographic quote shaper (issue 1379).

Developer directive 2026-10-06: a per-character lookback state machine — no
regex on content. A straight double/single quote whose PRECEDING character is
alphanumeric, or is one of ")", "]", ".", ",", ";", ":", "!", "?", "_", "-",
or "}" becomes the CLOSING form (American typesetting: sentence punctuation
sits inside the quotes; the offline corpus census of master.json prose paths
shows "_", "-", and "}" immediately before a straight quote only where the
quote closes a quoted token — '_', '-', and " |fl{ }"); any other preceding
character — whitespace, string/line start, "(", or anything else — becomes the
OPENING form. Refined pair window (census 2026-10-06, 34 matches / 0
counterexamples): reading backward from a quote Q — one space, a run of one
or more non-whitespace non-quote item chars, optionally exactly one space,
then a straight quote O — Q closes its pair when O itself classifies as an
OPENER under the same look-behind rule; the 12 sequences the unconditioned
window would also match all have O preceded by an alphanumeric (a closer) and
are excluded. The decision is look-behind only: a bounded backward scan, no
lookahead, no pairing memory, no alternation counting. Already-curly input
passes through unchanged (idempotent). Shaping applies only to prose rendering
paths; \\ftx/\\fxv verbatim blocks stay byte-exact straight quotes, and
master.json is never touched.

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
    for prev in "aZ0)].,;:!?_-}":
        assert shape_quotes(f'x{prev}"', "unicode") == f"x{prev}”", repr(prev)
        assert shape_quotes(f"x{prev}'", "unicode") == f"x{prev}’", repr(prev)


def test_corpus_census_cases_close():
    assert shape_quotes("gloss 'put out' as a single gloss", "unicode") == "gloss ‘put out’ as a single gloss"
    assert (
        shape_quotes("any underline character '_' in a gloss field", "unicode")
        == "any underline character ‘_’ in a gloss field"
    )
    assert (
        shape_quotes("The underline character '_' in the example glosses above", "unicode")
        == "The underline character ‘_’ in the example glosses above"
    )
    assert (
        shape_quotes("A space or any punctuation (except the '-') terminates", "unicode")
        == "A space or any punctuation (except the ‘-’) terminates"
    )
    assert shape_quotes('code " |fl{ }" tells MDF', "unicode") == 'code “ |fl{ }” tells MDF'


def test_decision_is_look_behind_only():
    assert shape_quotes("a_'", "unicode") == "a_’"
    assert shape_quotes("a_'y", "unicode") == "a_’y"
    assert shape_quotes("a_'x'y", "unicode") == "a_’x’y"
    assert shape_quotes("a '_'", "unicode") == "a ‘_’"


def test_pair_window_closes_padded_literals():
    """2026-10-06 pair-window census: the padded literals ' ; ' (ge/gn/gr/re/rn
    discussions), ' } ' (Character_Style_Codes), and ' f '
    (Summary_of_Fields) — the window's closing quote follows a space, so the
    base rule mis-opens it; the window closes it. The two ge/gn sentences also
    carry a hug-right ', ', now closed by the same window."""
    assert shape_quotes("The sequence ' ; ' is also converted to ', '", "unicode") == (
        "The sequence ‘ ; ’ is also converted to ‘, ’"
    )
    assert shape_quotes("MDF will convert the ' ; ' sequence to ', '", "unicode") == (
        "MDF will convert the ‘ ; ’ sequence to ‘, ’"
    )
    assert (
        shape_quotes("you must not forget the closing brace ' } '. If you", "unicode")
        == "you must not forget the closing brace ‘ } ’. If you"
    )
    assert shape_quotes("( ' f ' marks free-form fields)", "unicode") == "( ‘ f ’ marks free-form fields)"
    assert shape_quotes("separated by ' ; '. ", "unicode") == "separated by ‘ ; ’. "
    assert shape_quotes("' ; ' and ' , '", "unicode") == "‘ ; ’ and ‘ , ’"
    assert shape_quotes('x " ; " y', "unicode") == 'x “ ; ” y'


def test_pair_window_closes_hug_right_and_label_families():
    """2026-10-06 refined-window census: 27 open->close flips — the hug-right
    sequences ', ' (ge/gn/gr) and '; ' (lf) and the quoted-label family
    ("Ant: "-style, 23 instances). All sentences are real corpus text."""
    assert shape_quotes(
        "Toolbox can recognize either format and when interlinearizing will give the user "
        "the choice of both glosses in either case. The sequence ' ; ' is also converted "
        "to ', ' by MDF printing when formatting a dictionary or finderlist.",
        "unicode",
    ) == (
        "Toolbox can recognize either format and when interlinearizing will give the user "
        "the choice of both glosses in either case. The sequence ‘ ; ’ is also converted "
        "to ‘, ’ by MDF printing when formatting a dictionary or finderlist."
    )
    assert shape_quotes(
        "If the other glosses were filled in, they would be included in the printout "
        "(if a triglot dictionary was requested). Multiple lexical function bundles are "
        "concatenated with a semicolon '; ', e.g.:",
        "unicode",
    ) == (
        "If the other glosses were filled in, they would be included in the printout "
        "(if a triglot dictionary was requested). Multiple lexical function bundles are "
        "concatenated with a semicolon ‘; ’, e.g.:"
    )
    assert shape_quotes("MDF's standard printing adds the label \"Ant: \" to this field.", "unicode") == (
        "MDF’s standard printing adds the label “Ant: ” to this field."
    )
    assert shape_quotes('If selected for output, MDF adds the label "Semantics: " to this field.', "unicode") == (
        'If selected for output, MDF adds the label “Semantics: ” to this field.'
    )
    assert shape_quotes('MDF adds the label "Usage: " to this field.', "unicode") == (
        'MDF adds the label “Usage: ” to this field.'
    )
    assert shape_quotes('"Ant: "', "unicode") == "“Ant: ”"


def test_pair_window_requires_pair_opener():
    """The O-is-opener condition (census: all 12 excluded sequences have O
    immediately preceded by an alphanumeric, so O is a closer and the pair
    reading fails): a window-shaped Q whose O classifies closing stays
    base-rule opening."""
    assert shape_quotes('"a", "b"', "unicode") == "“a”, “b”"
    assert shape_quotes("'his', 'hers'", "unicode") == "‘his’, ‘hers’"
    assert shape_quotes('"a", "b"', "latex") == "``a'', ``b''"


def test_counterexample_sentences_render_unchanged():
    """Negative cases — the 12 census positions the refined window must NOT
    match, across 8 real corpus sentences (byte-identical to the pre-window
    shaper's output; each fragment starts at a corpus whitespace boundary so
    the backward-local classification matches the full sentence's)."""
    assert shape_quotes("'-aswasw kaha' means 'high water mark'", "unicode") == (
        "‘-aswasw kaha’ means ‘high water mark’"
    )
    assert shape_quotes("'-nya' means 'his' 'hers' or 'its', but for glossing '3sPOS' may be adequate", "unicode") == (
        "‘-nya’ means ‘his’ ‘hers’ or ‘its’, but for glossing ‘3sPOS’ may be adequate"
    )
    assert shape_quotes("('his', 'hers', or 'its')", "unicode") == "(‘his’, ‘hers’, or ‘its’)"
    assert shape_quotes('("period" or "full stop")', "unicode") == "(“period” or “full stop”)"
    assert shape_quotes(
        "'huma' might mean 'house', 'hut', 'shack', 'dwelling', 'lean-to', etc.", "unicode"
    ) == (
        "‘huma’ might mean ‘house’, ‘hut’, ‘shack’, ‘dwelling’, ‘lean-to’, etc."
    )
    assert shape_quotes("(e.g. 'shower' (n) 'shower' (v) are still clearly related", "unicode") == (
        "(e.g. ‘shower’ (n) ‘shower’ (v) are still clearly related"
    )
    assert shape_quotes('"synonym" and "antonym"', "unicode") == "“synonym” and “antonym”"
    assert shape_quotes('"do not" and "don\'t"', "unicode") == "“do not” and “don’t”"


def test_pair_window_stays_narrow():
    """Deliberate exclusions: whitespace other than a space terminates the item
    run without counting as pad, and a second pad space fails the exactly-one
    requirement — both keep the base rule (rendered open-open)."""
    assert shape_quotes("'  x  ' stays", "unicode") == "‘  x  ‘ stays"
    assert shape_quotes("' a  x ' stays", "unicode") == "‘ a  x ‘ stays"


def test_pair_window_closes_multi_char_item_runs():
    """A run of more than one item char (no corpus instance, rule shape probe):
    ' ab ' matches the window and closes."""
    assert shape_quotes("' ab ' stays", "unicode") == "‘ ab ’ stays"


def test_three_quote_chain_third_quote_stays_open():
    """False-positive guard: a three-quote run's third quote fails the opener
    check — its putative pair-opener already classified closing — so the base
    rule keeps it opening. Pairing would be required to do better on such
    synthetic runs; the corpus contains none (documented limitation)."""
    assert shape_quotes("' a ' b ' c", "unicode") == "‘ a ’ b ‘ c"
    assert shape_quotes("x 'a.' b ' c", "unicode") == "x ‘a.’ b ‘ c"
    assert shape_quotes("'a.' b ' c", "latex") == "`a.' b ` c"


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
