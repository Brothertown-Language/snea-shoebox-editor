# Copyright (c) 2026 Brothertown Language
"""In-process BM25 full-text search over the MDF Reference corpus (#1417).

Pure module over the committed ``docs/mdf/build/master.json`` corpus (108
keyed topics) — no database, no external service, no new dependencies.

Definitions (normative, per the #1417 spec of record):

- **Document text** per topic: the ``\\key`` line, the heading (when
  present), and every block's text.
- **Token:** a maximal run of Unicode word characters — ``[^\\W_]+``
  (Unicode ``\\w`` minus underscore), lowercased. Hyphenated compounds
  split; ``\\``-marker tokens (the ``cf`` in ``\\cf``) are ordinary index
  terms.
- **Scoring:** Okapi BM25 (k1 = 1.5, b = 0.75) with the non-negative
  Lucene/ATIRE IDF ``ln(1 + (N − df + 0.5)/(df + 0.5))`` (the original
  Robertson form goes negative when df > N/2 — true here for ``cf``, df 93
  of 108). Heading field weighting: tokens of the ``\\key`` line and heading
  weigh 3× body tokens in the term-frequency term. Marker-code key boost:
  a query containing a topic's own marker code adds +10 to its final score
  (accumulating across matching entries). Score ties break by the topic's
  index in ``master.json``'s ``topics`` array.

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

import math
import re
from collections import Counter
from collections.abc import Sequence

K1 = 1.5
B = 0.75
HEADING_WEIGHT = 3
KEY_BOOST = 10.0
ALIAS_BOOST = 10.0

# Non-ASCII letter census of the corpus document text (the spec's
# character-survival census): tokenization must preserve these exactly.
TOKEN_CENSUS = {"á": 26, "ñ": 3, "é": 1}

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Maximal runs of Unicode word characters (no underscore), lowercased.

    No normalization, no stripping, no stemming, no stop words: the corpus's
    accented content (á, ñ, é) survives exactly; ``•`` is punctuation and
    yields no token.
    """
    return [match.group(0).lower() for match in _TOKEN_RE.finditer(text)]


class MdfSearchIndex:
    """The BM25 index over the MDF Reference corpus."""

    def __init__(self, topics: list[dict], variants: list[dict] | None = None):
        self.topic_count = len(topics)
        self.docs: list[dict] = []
        for position, topic in enumerate(topics):
            key_line = topic.get("key_text") or ""
            heading = topic.get("heading") or ""
            body = "\n".join(block.get("text", "") for block in topic.get("blocks", []))
            head_tokens = tokenize(key_line) + tokenize(heading)
            body_tokens = tokenize(body)
            tf: Counter[str] = Counter(body_tokens)
            for token in head_tokens:
                tf[token] += HEADING_WEIGHT
            self.docs.append(
                {
                    "key": topic["key"],
                    "index": position,
                    "tf": tf,
                    "dl": len(head_tokens) + len(body_tokens),
                    "code": tokenize(topic["key"]),
                }
            )
        # Vocabulary-table variant entries (index-time posting extension):
        # every document whose token stream contains an entry's canonical form
        # is additionally indexed under the entry's variant tokens. The table
        # OWNS the variant token: a document's variant term frequency IS its
        # canonical term frequency — a document's native variant occurrences
        # are subsumed by the entry (zeroed where the canonical form is
        # absent). This is what makes the pinned `cross references` row rank
        # identically to `cross reference`: the References bibliography
        # topic's native plural mentions must not displace the marker topics.
        for entry in variants or []:
            canonical = entry["canonical"]
            variant = entry["variant"]
            if canonical == variant:
                continue
            for doc in self.docs:
                canonical_tf = doc["tf"].get(canonical, 0)
                if canonical_tf:
                    doc["tf"][variant] = canonical_tf
                else:
                    doc["tf"].pop(variant, None)
        self.avgdl = sum(doc["dl"] for doc in self.docs) / self.topic_count
        self.term_df: dict[str, int] = Counter()
        for doc in self.docs:
            for token in doc["tf"]:
                self.term_df[token] += 1

    def idf(self, term: str) -> float:
        """Non-negative Lucene/ATIRE IDF: ln(1 + (N − df + 0.5)/(df + 0.5))."""
        df = self.term_df.get(term, 0)
        return math.log(1.0 + (self.topic_count - df + 0.5) / (df + 0.5))


def _contains_subsequence(haystack: Sequence[str], needle: Sequence[str]) -> bool:
    """True when ``needle`` appears as a contiguous run inside ``haystack``."""
    if not needle:
        return False
    n = len(needle)
    return any(haystack[i : i + n] == list(needle) for i in range(len(haystack) - n + 1))


def build_search_index(topics: list[dict], variants: list[dict] | None = None) -> MdfSearchIndex:
    """Build the BM25 index from ``master.json``'s ``topics`` list.

    ``variants`` are the vocabulary table's morphological-variant entries
    (index-time posting extension); ``None`` builds the bare engine.
    """
    return MdfSearchIndex(topics, variants=variants)


def search_mdf(
    index: MdfSearchIndex,
    query: str,
    aliases: list[dict] | None = None,
) -> list[tuple[str, float]]:
    """Ranked full-text search: ``[(topic_key, score)]`` best first.

    Ties break by the topic's index in the ``topics`` array. A query whose
    tokenization is empty (empty, whitespace, punctuation only) matches
    nothing. ``aliases`` are the vocabulary table's semantic-alias entries
    (query-time mapping): when the query's token sequence contains an
    entry's term (a token or a contiguous token phrase), each mapped topic's
    final score gains +10 — accumulating across matching entries.
    """
    tokens = tokenize(query or "")
    if not tokens:
        return []
    k1 = K1
    b = B
    scores: dict[int, float] = {}
    for token in tokens:
        idf = index.idf(token)
        for doc in index.docs:
            tf = doc["tf"].get(token, 0)
            if not tf:
                continue
            denom = tf + k1 * (1.0 - b + b * doc["dl"] / index.avgdl)
            scores[doc["index"]] = scores.get(doc["index"], 0.0) + idf * tf * (k1 + 1.0) / denom
    # Two boost semantics, forced by the pinned candidate rows:
    # - The marker-code key boost augments an existing matched score — it
    #   never summons an unmatched topic ("that topic's final score gains
    #   +10"). This keeps the References bibliography topic out of the
    #   pinned `cross references` row: the variant entry zeroes its variant
    #   posting, so it has no match for the query despite the query carrying
    #   its key token.
    # - The alias boost DOES summon: the mapped topic's score gains +10 even
    #   with no BM25 match — the corpus contains zero `inflect*`/`lemma`
    #   tokens, so for the alias rows the mapping IS the match.
    for doc in index.docs:
        if doc["index"] in scores and _contains_subsequence(tokens, doc["code"]):
            scores[doc["index"]] += KEY_BOOST
    if aliases:
        positions_by_key: dict[str, list[int]] = {}
        for doc in index.docs:
            positions_by_key.setdefault(doc["key"], []).append(doc["index"])
        for entry in aliases:
            term_tokens = tokenize(entry["term"])
            if term_tokens and _contains_subsequence(tokens, term_tokens):
                for key in entry["keys"]:
                    for doc_index in positions_by_key.get(key, []):
                        scores[doc_index] = scores.get(doc_index, 0.0) + ALIAS_BOOST
    ranked = [(index.docs[doc_index]["key"], doc_index, score) for doc_index, score in scores.items() if score > 0.0]
    # Deterministic ordering: score descending, then the topic's index in the
    # topics array ascending.
    ranked.sort(key=lambda item: (-item[2], item[1]))
    return [(key, score) for key, _position, score in ranked]
