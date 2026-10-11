"""W2 seeded-vocabulary-table verification for the MDF Reference search.

Spec of record: issue #1417 (the GitHub issue body carries the full spec).
W1+W2 rows verify the engine PLUS the seeded table; every W2 row fails on
the bare engine (negative demonstrations pinned below), so each is a genuine
demonstration of its seeded entry.

Seeds — variants (index-time posting extension): ``paradigms``→``paradigm``,
``references``→``reference``. Aliases (query-time +10 boost):
``inflected``→``lc`` (Coward & Grimes, *Making Dictionaries*, SIL 2000,
§5.4.4), ``lemma``→``lx`` and ``word class``→``ps``, ``pn`` (SIL Glossary of
Linguistic Terms, "Also Known As" fields).

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


# --- Negative demonstrations: every W2 row fails on the bare engine -----------


def test_bare_paradigms_zero_matches(bare_index):
    """`paradigms` returns zero matches without its variant entry."""
    assert search_mdf(bare_index, "paradigms") == []


def test_bare_cross_references_displaces_cr(bare_index):
    """`cross references` fails its expectation without `references`→
    `reference`."""
    assert set(_ranked_keys(bare_index, "cross references")[:4]) != {"ce", "cn", "cr", "cf"}


def test_bare_inflected_zero_matches(bare_index):
    assert search_mdf(bare_index, "inflected") == []


def test_bare_lemma_zero_matches(bare_index):
    assert search_mdf(bare_index, "lemma") == []


def test_bare_word_class_wrong_top_two(bare_index):
    assert set(_ranked_keys(bare_index, "word class")[:2]) != {"ps", "pn"}


# --- W1+W2 candidate rows (engine plus seeded table) --------------------------


def test_paradigms_top_four_all_paradigm_topics(index):
    top4 = _ranked_keys(index, "paradigms")[:4]
    assert len(top4) == 4
    assert all(key.startswith("pd") for key in top4), f"got {top4}"


def test_cross_references_top_four(index):
    assert set(_ranked_keys(index, "cross references")[:4]) == {"ce", "cn", "cr", "cf"}


def test_inflected_ranks_lc_first(index):
    assert _ranked_keys(index, "inflected", aliases=ALIAS_ENTRIES)[0] == "lc"


def test_lemma_ranks_lx_first(index):
    assert _ranked_keys(index, "lemma", aliases=ALIAS_ENTRIES)[0] == "lx"


def test_word_class_top_two(index):
    assert set(_ranked_keys(index, "word class", aliases=ALIAS_ENTRIES)[:2]) == {"ps", "pn"}


# --- Seed-entry invariants -----------------------------------------------------


def test_variant_entries_are_canonical_corpus_terms(topics):
    """Admission rule: a variant entry's canonical form is present in the
    corpus."""
    from src.services.mdf_search import tokenize

    corpus_tokens = set()
    for t in topics:
        parts = [t.get("key_text") or "", t.get("heading") or ""]
        parts.extend(b.get("text", "") for b in t["blocks"])
        corpus_tokens.update(tokenize("\n".join(parts)))
    assert {"paradigm", "reference"} <= corpus_tokens


def test_alias_terms_have_provenance():
    """Every alias entry carries its source citation — no invented mappings."""
    for entry in ALIAS_ENTRIES:
        assert entry.get("source"), f"alias {entry['term']!r} lacks a source citation"
        assert entry.get("locator"), f"alias {entry['term']!r} lacks a locator"
    for entry in VARIANT_ENTRIES:
        assert entry.get("source"), f"variant {entry['variant']!r} lacks a source citation"
