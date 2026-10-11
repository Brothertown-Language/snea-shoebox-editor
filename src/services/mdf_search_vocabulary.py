# Copyright (c) 2026 Brothertown Language
"""Seeded vocabulary table for the MDF Reference full-text search (#1417).

Committed deterministic data beside the scorer — two mechanisms with
distinct composition semantics:

- **Morphological variants** (``VARIANT_ENTRIES``): index-time posting
  extension — every document whose token stream contains an entry's
  canonical form is additionally indexed under the entry's variant tokens.
- **Semantic aliases** (``ALIAS_ENTRIES``): query-time mapping — when the
  query's token sequence contains the term (a token or a contiguous token
  phrase), each mapped topic's final score gains +10 (accumulating across
  matching entries).

Extension of this table beyond the seeds is governed by issue #1429
(admission, provenance, licensing, and regression rules live there); the
seeds below are the #1417 spec's pinned set. Term phrases with citation
only, never definitions (license boundary).

Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
"""

VARIANT_ENTRIES: list[dict] = [
    {
        "variant": "paradigms",
        "canonical": "paradigm",
        "source": "Regular English plural of the corpus's own 'paradigm' marker "
        "topic (in-corpus derivation — the corpus contains zero 'paradigms' tokens)",
        "locator": "docs/mdf/build/master.json, topic pd (paradigm)",
    },
    {
        "variant": "references",
        "canonical": "reference",
        "source": "Regular English plural of the corpus's own 'reference' marker "
        "topic (in-corpus derivation — the bare plural query otherwise matches "
        "only the References bibliography topic)",
        "locator": "docs/mdf/build/master.json, topic ce (cross reference)",
    },
]

ALIAS_ENTRIES: list[dict] = [
    {
        "term": "inflected",
        "keys": ["lc"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "\u00a75.4.4 — 'Where a language has lexemes in a variety of "
        "inflected forms, none of which is basic, a citation form must be listed "
        "as the headword'",
    },
    {
        "term": "lemma",
        "keys": ["lx"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "lemma — 'Also Known As' field",
    },
    {
        "term": "word class",
        "keys": ["ps", "pn"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "word class — 'Also Known As' field",
    },
]
