"""Deterministic whole-term substring span computation for search highlighting.

Pure module: no Streamlit, no database imports.

Co-authored with AI: OpenCode (GLM-5.3-Flash)
"""

from __future__ import annotations

import unicodedata

from src.services.linguistic_service import LinguisticService, _TSQUERY_UNSAFE


def _is_word_char(c: str) -> bool:
    """Unicode-safe word-character test: letters/digits/underscore, combining
    marks (NFD diacritics), straight/curly apostrophes, and the Algonquian
    letter ∞ (U+221E).
    """
    return (
        c.isalnum()
        or c == "_"
        or unicodedata.category(c).startswith("M")
        or c in {"'", "\u2019", "\u221e"}
    )


def _iter_words(line: str):
    """Yield (start, end, word) for maximal Unicode-safe word runs in line.

    Runs are delimited by anything that is not a word character (spaces,
    punctuation, tsquery operators, etc.), so words such as ``*|achm∞wonk|``
    are extracted intact and IPA/diacritic characters are never split.
    """
    i, n = 0, len(line)
    while i < n:
        if _is_word_char(line[i]):
            j = i + 1
            while j < n and _is_word_char(line[j]):
                j += 1
            yield i, j, line[i:j]
            i = j
        else:
            i += 1


def _query_tokens(query: str) -> list[str]:
    """Derive FTS query tokens exactly like the FTS strategy.

    Sole normalization entry point: generate_sort_lx, then strip
    tsquery-unsafe characters per whitespace-delimited word.
    """
    return [
        clean
        for w in LinguisticService.generate_sort_lx(query).split()
        if (clean := _TSQUERY_UNSAFE.sub("", w).strip())
    ]


def compute_term_spans(line: str, terms: list[str]) -> list[tuple[int, int]]:
    """Return sorted (start, end) character offsets for every occurrence of every term.

    Terms are located verbatim (exact substring match, including decomposed
    diacritics and IPA characters) using a deterministic left-to-right scan.
    Overlapping occurrences of the same term are all emitted.
    """
    spans: list[tuple[int, int]] = []
    for term in terms:
        if not term:
            continue
        start = 0
        while True:
            idx = line.find(term, start)
            if idx == -1:
                break
            spans.append((idx, idx + len(term)))
            start = idx + 1
    return sorted(spans)


def compute_fts_spans(line: str, query: str) -> list[tuple[int, int]]:
    """Return sorted (start, end) character offsets of whole line words that
    match FTS query tokens.

    Query tokens are derived the same way as the FTS strategy: normalized via
    ``LinguisticService.generate_sort_lx``, then tsquery-unsafe characters are
    stripped per word and empties dropped. A candidate line word matches a
    token when its normalized form starts with the token (prefix, ``:*``
    semantics); matching words light up in full, including any surrounding
    non-word delimiters in the line being excluded.
    """
    tokens = _query_tokens(query)
    if not tokens:
        return []
    spans: set[tuple[int, int]] = set()
    for start, end, word in _iter_words(line):
        norm = LinguisticService.generate_sort_lx(word)
        if norm and any(norm.startswith(tok) for tok in tokens):
            spans.add((start, end))
    return sorted(spans)
