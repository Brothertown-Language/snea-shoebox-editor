"""cf lookup-pair extraction tests (.issues/1379 change control 2026-10-06).

The parser derives an additive ``pairs`` field on every ``\\cf`` block:
presentation-level whitespace tokenization of the block's raw text (minus the
leading marker token) — each token resolving through the target set starts a
new pair; intervening words accumulate as that pair's gloss. Punctuation-only
tokens and the connective ``and`` in list position (directly after a bare
target) are list structure between pairs, never gloss content — the connective
case ``\\xe, \\xn, and \\xr`` stays all-empty-gloss and therefore inline.

Raw ``text`` and ``targets`` fields are untouched (round-trip is asserted in
test_mdf_converter_sc13_and_census.py).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "convert_mdf_master.py"
SOURCE_PATH = REPO_ROOT / "docs" / "mdf" / "MDFields19a_UTF8.txt"

_SPEC = importlib.util.spec_from_file_location("convert_mdf_master", SCRIPT_PATH)
convert_mdf_master = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(convert_mdf_master)


def source_text() -> str:
    return SOURCE_PATH.read_bytes().decode("utf-8")


@pytest.fixture(scope="module")
def document():
    return convert_mdf_master.parse_mdf_text(source_text(), "docs/mdf/MDFields19a_UTF8.txt")


def cf_blocks(document):
    for topic in document["topics"]:
        for block in topic["blocks"]:
            if block["marker"] == "cf":
                yield topic, block


def block_by_line(document, lineno):
    return next(block for _topic, block in cf_blocks(document) if block["line"] == lineno)


def as_triples(pairs):
    return [(p["target"], p["gloss"], p["token"]) for p in pairs]


class TestCfPairsExtraction:
    def test_every_cf_block_carries_pairs(self, document):
        blocks = list(cf_blocks(document))
        assert len(blocks) == 297
        assert all(isinstance(block.get("pairs"), list) for _topic, block in blocks)

    def test_total_pairs_census(self, document):
        assert sum(len(block["pairs"]) for _topic, block in cf_blocks(document)) == 428

    def test_glossed_pairs_census(self, document):
        glossed = [
            pair
            for _topic, block in cf_blocks(document)
            for pair in block["pairs"]
            if convert_mdf_master.pair_is_glossed(pair)
        ]
        assert len(glossed) == 210

    def test_every_pair_target_is_a_topic_key(self, document):
        keys = {topic["key"] for topic in document["topics"]}
        offenders = [
            pair["target"]
            for _topic, block in cf_blocks(document)
            for pair in block["pairs"]
            if pair["target"] not in keys
        ]
        assert offenders == []

    def test_no_stored_gloss_is_fragment_only(self, document):
        """Punctuation-only fragments and the connective 'and' never enter
        glosses — they are list structure between pairs."""
        offenders = [
            pair["gloss"]
            for _topic, block in cf_blocks(document)
            for pair in block["pairs"]
            if pair["gloss"]
            and (not any(ch.isalnum() for ch in pair["gloss"]) or pair["gloss"].lower() == "and")
        ]
        assert offenders == []

    def test_targets_and_text_fields_unchanged_shape(self, document):
        """pairs is additive: targets stays the first-line canonical list and
        text stays byte-for-byte raw."""
        block = block_by_line(document, 1011)
        assert block["targets"] == ["lx", "hm", "lc"]
        assert block["text"] == (
            "\\cf      lx lexeme           hm homonym number          lc lexical citation form"
        )


class TestShd4HeadwordGroup:
    def test_headword_group_pairs_with_exact_source_glosses(self, document):
        """The Introduction's shd4 group "Information Relating Directly to the
        Headword": one pair per marker, gloss verbatim from the source row."""
        expected = {
            1011: [("lx", "lexeme"), ("hm", "homonym number"), ("lc", "lexical citation form")],
            1012: [
                ("ph", "phonetic (pronunciation)"),
                ("ps", "part of speech"),
                ("pn", "National part of speech"),
            ],
            1013: [("sn", "sense number")],
        }
        for lineno, pairs in expected.items():
            block = block_by_line(document, lineno)
            assert [(p["target"], p["gloss"]) for p in block["pairs"]] == pairs

    def test_headword_group_is_glossed_and_coalesces(self, document):
        blocks = [block_by_line(document, n) for n in (1011, 1012, 1013)]
        assert all(convert_mdf_master.cf_block_glossed(b) for b in blocks)
        # The three cf blocks are consecutive inside the Introduction's block
        # list, so the shared coalescing helper emits exactly one list group.
        introduction = next(t for t in document["topics"] if t["key"] == "Introduction")
        headword_run = next(
            run
            for kind, run in convert_mdf_master.coalesce_cf_blocks(introduction["blocks"])
            if kind == "list" and any(b["line"] == 1011 for b in run)
        )
        assert sorted(b["line"] for b in headword_run) == [1011, 1012, 1013]


class TestConnectiveCase:
    def test_xe_xn_and_xr_pairs_are_all_empty_gloss(self, document):
        """L3339: the connective 'and' and the commas are list structure —
        every pair carries gloss ""."""
        block = block_by_line(document, 3339)
        assert as_triples(block["pairs"]) == [
            ("xe", "", "\\xe,"),
            ("xn", "", "\\xn,"),
            ("xr", "", "\\xr"),
        ]

    def test_connective_case_block_stays_inline(self, document):
        block = block_by_line(document, 3339)
        assert not convert_mdf_master.cf_block_glossed(block)

    def test_bare_connective_run_does_not_coalesce(self, document):
        """Consecutive bare-target cf blocks keep their individual inline
        rendering — the aa home TOC rows are the live case."""
        aa = document["topics"][0]
        groups = convert_mdf_master.coalesce_cf_blocks(aa["blocks"])
        assert all(kind == "single" for kind, _run in groups)


class TestGlossedMarkerRows:
    def test_backslash_prefixed_pairs_keep_source_tokens(self, document):
        """L175/176 (`\\cf \\sy synonym` / `\\cf \\lf lexical function`): the
        pair keeps the source's own display token and gloss."""
        assert as_triples(block_by_line(document, 175)["pairs"]) == [("sy", "synonym", "\\sy")]
        assert as_triples(block_by_line(document, 176)["pairs"]) == [
            ("lf", "lexical function", "\\lf")
        ]
        assert convert_mdf_master.cf_block_glossed(block_by_line(document, 175))

    def test_continuation_tokens_derive_pairs(self, document):
        """L1026: the block's continuation line `(also lv* lexical function form
        and glosses)` tokenizes with the rest — lv* starts a second pair, and
        the mid-gloss 'and' stays verbatim gloss content."""
        block = block_by_line(document, 1026)
        assert as_triples(block["pairs"]) == [
            (
                "lf",
                "lexical function (like synonym, causal, generic, deverbal noun, locative, etc.) (also",
                "lf",
            ),
            ("lv", "lexical function form and glosses)", "lv*"),
        ]

    def test_mid_gloss_punctuation_stays_verbatim(self, document):
        """L1018: the '&' inside 'paradigm form & glosses)' is mid-gloss content,
        not a list fragment — fragments are list structure only in connective
        position (while the current gloss is still empty)."""
        block = block_by_line(document, 1018)
        assert as_triples(block["pairs"]) == [
            ("pd", "paradigm class", "pd"),
            ("pdl", "paradigm label (also", "pdl"),
            ("pdv", "paradigm form & glosses)", "pdv*"),
        ]

    def test_bundle_gloss_attaches_to_last_target(self, document):
        """L1369 (`\\ee, \\en, and \\er encyclopedic field bundle`): the connective
        is structure; the trailing gloss belongs to the pair it follows."""
        block = block_by_line(document, 1369)
        assert as_triples(block["pairs"]) == [
            ("ee", "", "\\ee,"),
            ("en", "", "\\en,"),
            ("er", "encyclopedic field bundle", "\\er"),
        ]
        assert convert_mdf_master.cf_block_glossed(block)
