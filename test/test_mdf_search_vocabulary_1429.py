"""#1429 vocabulary-table derivation verification for the MDF Reference search.

Spec of record: issue #1429 (vocabulary-table derivation — child of #1417).
Every admitted entry is demonstrated here: a bare-engine negative
demonstration pins the failure that makes the entry necessary, and the
demonstration row verifies the entry through #1417's scoring engine per
#1429's admission rules (provenance, linguistic judgment, demonstration,
no-regression).

Variant rows (index-time posting extension): ``headwords``→``headword``,
``reversals``→``reversal``, ``homonyms``→``homonym``, ``synonyms``→``synonym``,
``etymologies``→``etymology``.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
from pathlib import Path

import pytest

from src.services.mdf_search import build_search_index, search_mdf
from src.services.mdf_search_vocabulary import ALIAS_ENTRIES, VARIANT_ENTRIES

REPO_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = REPO_ROOT / "docs" / "mdf" / "build" / "master.json"


@pytest.fixture(scope="module")
def topics():
    with MASTER_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["topics"]


@pytest.fixture(scope="module")
def bare_index(topics):
    return build_search_index(topics)


@pytest.fixture(scope="module")
def index(topics):
    return build_search_index(topics, variants=VARIANT_ENTRIES)


def _ranked_keys(index, query, **kwargs):
    return [key for key, _score in search_mdf(index, query, **kwargs)]


# --- Item 1 negative demonstrations: the failures that make each entry necessary


def test_bare_headwords_zero_matches(bare_index):
    """`headwords` returns zero matches without its variant entry."""
    assert search_mdf(bare_index, "headwords") == []


def test_bare_reversals_zero_matches(bare_index):
    """`reversals` returns zero matches without its variant entry."""
    assert search_mdf(bare_index, "reversals") == []


def test_bare_homonyms_wrong_single_match(bare_index):
    """`homonyms` bare matches only the Sections topic, not the \\hm field."""
    assert _ranked_keys(bare_index, "homonyms")[0] == "Sections_in_a_Lexical_Entry"


def test_bare_synonyms_wrong_top_two(bare_index):
    """`synonyms` bare matches only the field-list topics, not the \\sy field."""
    assert set(_ranked_keys(bare_index, "synonyms")[:2]) == {"Summary_of_Fields", "Order_of_Fields"}


def test_bare_etymologies_wrong_single_match(bare_index):
    """`etymologies` bare matches only the documentation topic, not the \\et bundle."""
    assert _ranked_keys(bare_index, "etymologies")[0] == "The_MDF_Documentation"


# --- Item 1 demonstrations: the entries through the scoring engine ----------------


def test_headwords_ranks_lx_first(index):
    assert _ranked_keys(index, "headwords", aliases=ALIAS_ENTRIES)[0] == "lx"


def test_reversals_top_three_reversal_topics(index):
    assert set(_ranked_keys(index, "reversals", aliases=ALIAS_ENTRIES)[:3]) == {"rr", "rn", "re"}


def test_homonyms_ranks_hm_first(index):
    assert _ranked_keys(index, "homonyms", aliases=ALIAS_ENTRIES)[0] == "hm"


def test_synonyms_ranks_sy_first(index):
    assert _ranked_keys(index, "synonyms", aliases=ALIAS_ENTRIES)[0] == "sy"


def test_etymologies_surface_the_etymology_bundle(index):
    assert set(_ranked_keys(index, "etymologies", aliases=ALIAS_ENTRIES)[:4]) == {"es", "eg", "ec", "et"}


# --- Item 1 admission invariant: canonical forms are corpus terms ------------------


def test_variant_canonical_forms_are_corpus_terms(topics):
    """#1429 variant admission rule: the canonical form is present in the corpus."""
    from src.services.mdf_search import tokenize

    corpus_tokens = set()
    for t in topics:
        parts = [t.get("key_text") or "", t.get("heading") or ""]
        parts.extend(b.get("text", "") for b in t["blocks"])
        corpus_tokens.update(tokenize("\n".join(parts)))
    assert {"headword", "reversal", "homonym", "synonym", "etymology"} <= corpus_tokens


# --- Item 2 negative demonstrations: the headword's source-attested aliases --------


def test_bare_lexeme_ranks_lv_first(bare_index):
    """`lexeme` bare ranks the \\lv vernacular-lexeme topic above the \\lx field."""
    assert _ranked_keys(bare_index, "lexeme")[0] == "lv"


def test_bare_entry_word_ranks_summary_first(bare_index):
    assert _ranked_keys(bare_index, "entry word")[0] == "Summary_of_Fields"


def test_bare_entry_form_ranks_mn_first(bare_index):
    assert _ranked_keys(bare_index, "entry form")[0] == "mn"


def test_bare_lexical_item_ranks_le_first(bare_index):
    assert _ranked_keys(bare_index, "lexical item")[0] == "le"


def test_bare_entry_words_ranks_ge_first(bare_index):
    assert _ranked_keys(bare_index, "entry words")[0] == "ge"


# --- Item 2 demonstrations: every headword alias ranks \\lx first ------------------


@pytest.mark.parametrize(
    "query",
    ["lexeme", "entry word", "entry form", "lexical item", "entry words"],
)
def test_headword_aliases_rank_lx_first(index, query):
    assert _ranked_keys(index, query, aliases=ALIAS_ENTRIES)[0] == "lx"


# --- Item 3 negative demonstrations: the homograph aliases --------------------------


def test_bare_homograph_zero_matches(bare_index):
    """`homograph` returns zero matches — the corpus never uses the term."""
    assert search_mdf(bare_index, "homograph") == []


def test_bare_homographs_zero_matches(bare_index):
    assert search_mdf(bare_index, "homographs") == []


# --- Item 3 demonstrations: each homograph query's sole match is \\hm ---------------


@pytest.mark.parametrize("query", ["homograph", "homographs"])
def test_homograph_aliases_sole_match_hm(index, query):
    assert _ranked_keys(index, query, aliases=ALIAS_ENTRIES) == ["hm"]


# --- Item 4 negative demonstrations: the lexical-category aliases -------------------


def test_bare_grammatical_category_wrong_top_two(bare_index):
    """`grammatical category` bare matches only the restrictions topics."""
    assert set(_ranked_keys(bare_index, "grammatical category")[:2]) & {"ps", "pn"} == set()


def test_bare_grammatical_class_wrong_top_two(bare_index):
    assert set(_ranked_keys(bare_index, "grammatical class")[:2]) & {"ps", "pn"} == set()


# --- Item 4 demonstrations: both queries rank {ps, pn} first ------------------------


@pytest.mark.parametrize("query", ["grammatical category", "grammatical class"])
def test_lexical_category_aliases_top_two(index, query):
    assert set(_ranked_keys(index, query, aliases=ALIAS_ENTRIES)[:2]) == {"ps", "pn"}


# --- Item 5 negative demonstrations: the remaining aliases --------------------------


def test_bare_confer_ranks_ce_first(bare_index):
    """`confer` bare ranks the cross-reference gloss topics above the \\cf field."""
    assert _ranked_keys(bare_index, "confer")[0] == "ce"


def test_bare_etymology_ranks_es_first(bare_index):
    assert _ranked_keys(bare_index, "etymology")[0] == "es"


def test_bare_variant_ranks_ve_first(bare_index):
    assert _ranked_keys(bare_index, "variant")[0] == "ve"


def test_bare_variants_zero_matches(bare_index):
    assert search_mdf(bare_index, "variants") == []


def test_bare_finderlist_ranks_ge_first(bare_index):
    assert _ranked_keys(bare_index, "finderlist")[0] == "ge"


def test_bare_inflection_zero_matches(bare_index):
    assert search_mdf(bare_index, "inflection") == []


def test_bare_inflections_zero_matches(bare_index):
    assert search_mdf(bare_index, "inflections") == []


# --- Item 5 demonstrations -----------------------------------------------------------


def test_confer_ranks_cf_first(index):
    assert _ranked_keys(index, "confer", aliases=ALIAS_ENTRIES)[0] == "cf"


def test_etymology_ranks_et_first(index):
    assert _ranked_keys(index, "etymology", aliases=ALIAS_ENTRIES)[0] == "et"


def test_variant_ranks_va_first(index):
    assert _ranked_keys(index, "variant", aliases=ALIAS_ENTRIES)[0] == "va"


def test_variants_sole_match_va(index):
    assert _ranked_keys(index, "variants", aliases=ALIAS_ENTRIES) == ["va"]


def test_finderlist_ranks_formatting_first(index):
    assert _ranked_keys(index, "finderlist", aliases=ALIAS_ENTRIES)[0] == "Formatting_and_Printing"


@pytest.mark.parametrize("query", ["inflection", "inflections"])
def test_inflection_aliases_top_two(index, query):
    assert _ranked_keys(index, query, aliases=ALIAS_ENTRIES)[:2] == ["pd", "rd"]


# --- Item 6 invariants: provenance and recorded judgment on every derived entry -----


DERIVED_ALIAS_TERMS = [
    "lexeme",
    "entry word",
    "entry form",
    "lexical item",
    "entry words",
    "homograph",
    "homographs",
    "grammatical category",
    "grammatical class",
    "confer",
    "etymology",
    "variant",
    "variants",
    "finderlist",
    "inflection",
    "inflections",
]
DERIVED_VARIANTS = ["headwords", "reversals", "homonyms", "synonyms", "etymologies"]


def test_derived_alias_terms_are_committed_with_provenance_and_judgment():
    by_term = {e["term"]: e for e in ALIAS_ENTRIES}
    for term in DERIVED_ALIAS_TERMS:
        entry = by_term[term]
        assert entry.get("source"), f"alias {term!r} lacks a source citation"
        assert entry.get("locator"), f"alias {term!r} lacks a locator"
        assert entry.get("judgment"), f"alias {term!r} lacks the recorded linguistic judgment"


def test_derived_variants_are_committed_with_provenance_and_judgment():
    by_variant = {e["variant"]: e for e in VARIANT_ENTRIES}
    for variant in DERIVED_VARIANTS:
        entry = by_variant[variant]
        assert entry.get("source"), f"variant {variant!r} lacks a source citation"
        assert entry.get("locator"), f"variant {variant!r} lacks a locator"
        assert entry.get("judgment"), f"variant {variant!r} lacks the recorded linguistic judgment"


def test_no_duplicate_terms_across_the_table():
    alias_terms = [e["term"] for e in ALIAS_ENTRIES]
    assert len(alias_terms) == len(set(alias_terms)), "duplicate alias terms"
    variant_tokens = [e["variant"] for e in VARIANT_ENTRIES]
    assert len(variant_tokens) == len(set(variant_tokens)), "duplicate variant tokens"
