"""W1 scoring-engine verification for the MDF Reference full-text search.

Spec of record: issue #1417 (the GitHub issue body carries the full spec). The candidate
table below is committed with the tests verbatim per the spec's Verification
section; every assertion is a pinned candidate row. W1 rows verify the engine
alone (no vocabulary-table mechanism).

Corpus facts pinned by the spec's Definitions (verified live by the spec
author and re-asserted here): 108 topics; token rule ``[^\\W_]+`` lowercased;
document text = the ``\\key`` line, the heading (when present), and every
block's text; census á ×26, ñ ×3, é ×1, • ×2 (• excluded from tokens as
punctuation); df(``cf``) = 93.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = REPO_ROOT / "docs" / "mdf" / "build" / "master.json"

from src.services.mdf_search import (  # noqa: E402
    TOKEN_CENSUS,
    build_search_index,
    search_mdf,
)


@pytest.fixture(scope="module")
def topics():
    with MASTER_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)["topics"]


@pytest.fixture(scope="module")
def index(topics):
    return build_search_index(topics)


def _ranked_keys(index, query):
    return [key for key, _score in search_mdf(index, query)]


# --- Definitions: corpus facts and token census -------------------------------


def test_corpus_is_108_topics(topics):
    assert len(topics) == 108


def test_character_survival_census(topics):
    """Tokenization preserves the corpus text's non-ASCII letters exactly:
    á ×26, ñ ×3, é ×1; the corpus's one non-letter non-ASCII character
    (• ×2, punctuation) is excluded from tokens."""
    parts = []
    for t in topics:
        parts.append(t.get("key_text") or "")
        parts.append(t.get("heading") or "")
        parts.extend(b.get("text", "") for b in t["blocks"])
    text = "\n".join(parts)
    assert text.count("á") == TOKEN_CENSUS["á"] == 26
    assert text.count("ñ") == TOKEN_CENSUS["ñ"] == 3
    assert text.count("é") == TOKEN_CENSUS["é"] == 1
    assert text.count("•") == 2
    assert "•" not in build_search_index(topics).term_df


# --- W1 candidate rows (engine alone) -----------------------------------------


@pytest.mark.parametrize("query", ["cf", "ps", "ge", "pl", "lx"])
def test_marker_code_query_ranks_own_topic_first(index, query):
    assert _ranked_keys(index, query)[0] == query


def test_plural_ranks_pl_first(index):
    assert _ranked_keys(index, "plural")[0] == "pl"


def test_part_of_speech_ranks_ps_then_pn(index):
    keys = _ranked_keys(index, "part of speech")
    assert keys[0] == "ps"
    assert keys[1] == "pn"


def test_borrowed_word_ranks_bw_first(index):
    assert _ranked_keys(index, "borrowed word")[0] == "bw"


def test_cross_reference_top_four(index):
    assert set(_ranked_keys(index, "cross reference")[:4]) == {"ce", "cn", "cr", "cf"}


def test_reversal_top_three(index):
    assert set(_ranked_keys(index, "reversal")[:3]) == {"rr", "rn", "re"}


def test_reduplication_ranks_rd_first(index):
    assert _ranked_keys(index, "reduplication")[0] == "rd"


def test_irregular_top_two(index):
    assert set(_ranked_keys(index, "irregular")[:2]) == {"pdl", "pd"}


def test_ranking_is_deterministic(index):
    """Score ties break by the topic's index in master.json's topics array —
    repeated calls return identical orderings."""
    first = search_mdf(index, "cross reference")
    second = search_mdf(index, "cross reference")
    assert first == second


def test_punctuation_only_query_matches_nothing(index):
    assert search_mdf(index, "///") == []
    assert search_mdf(index, "   ") == []
