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
    # --- #1429 derived entries (admission, provenance, and judgment per #1429) ---
    {
        "variant": "headwords",
        "canonical": "headword",
        "source": "Regular English plural of the corpus's own \\lx headword topic "
        "(in-corpus derivation); the plural is attested in the source book, "
        "Coward & Grimes, Making Dictionaries (SIL 2000), §2.1 \\lx discussion — "
        "'phrasal lexemes as separate headwords'",
        "locator": "docs/mdf/build/master.json, topic lx (lexeme or headword of the lexical entry)",
        "judgment": "\\lx is the headword field; 'headwords' is its regular English "
        "plural and no other corpus topic answers it",
    },
    {
        "variant": "reversals",
        "canonical": "reversal",
        "source": "Regular English plural of the corpus's own reversal topics "
        "(in-corpus derivation — the bare plural query matches nothing)",
        "locator": "docs/mdf/build/master.json, topics rr, rn, re (reversal form)",
        "judgment": "the \\rr/\\rn/\\re topics are the reversal fields; 'reversals' is their regular English plural",
    },
    {
        "variant": "homonyms",
        "canonical": "homonym",
        "source": "Regular English plural of the corpus's own \\hm homonym topic "
        "(in-corpus derivation); the plural is attested in the source book, "
        "Coward & Grimes, Making Dictionaries (SIL 2000), §2.1 \\lx discussion — "
        "'distinguish between homonyms and multiple senses of a single lexeme'",
        "locator": "docs/mdf/build/master.json, topic hm (homonym number)",
        "judgment": "\\hm is the homonym-number field; bare 'homonyms' matches only "
        "a passing mention in the Sections topic, not the field that encodes them",
    },
    {
        "variant": "synonyms",
        "canonical": "synonym",
        "source": "Regular English plural of the corpus's own \\sy synonym topic "
        "(in-corpus derivation); the plural is attested in the source book, "
        "Coward & Grimes, Making Dictionaries (SIL 2000), §2.1 field list — "
        "'\\sy Synonyms: Available for those who do not want to use the \\lf bundles'",
        "locator": "docs/mdf/build/master.json, topic sy (synonym)",
        "judgment": "\\sy is the synonym field; bare 'synonyms' matches only the "
        "Summary/Order field-list topics, not the field that records them",
    },
    {
        "variant": "etymologies",
        "canonical": "etymology",
        "source": "Regular English plural of the corpus's own \\et etymology topic "
        "(in-corpus derivation — the bare plural query matches only the "
        "documentation topic)",
        "locator": "docs/mdf/build/master.json, topics et, eg, es, ec (etymology bundle)",
        "judgment": "the \\et topic heads the etymology bundle (\\eg gloss, \\es source, "
        "\\ec comment); the plural query's answer is that bundle",
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
    # --- #1429 derived entries (admission, provenance, and judgment per #1429) ---
    {
        "term": "lexeme",
        "keys": ["lx"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\lx field description — 'Lexeme: also known as lemma or headword'",
        "judgment": "\\lx is the lexeme field (its corpus heading: 'lexeme or "
        "headword of the lexical entry'); the \\lv topic answers the "
        "lexical-function bundle's vernacular lexeme reference, not the "
        "lexeme field itself, but out-ranks \\lx on the bare query",
    },
    {
        "term": "entry word",
        "keys": ["lx"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "headword — 'Also Known As' field: Entry Form, Entry Word, Lemma, Lexical Item",
        "judgment": "the entry word is the headword — the form the dictionary is sorted by, which is the \\lx field",
    },
    {
        "term": "entry form",
        "keys": ["lx"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "headword — 'Also Known As' field: Entry Form, Entry Word, Lemma, Lexical Item",
        "judgment": "the entry form is the headword (\\lx); the \\mn 'main entry "
        "form' topic out-ranks \\lx on the bare query but answers minor-entry "
        "cross-referencing, not the entry word itself",
    },
    {
        "term": "lexical item",
        "keys": ["lx"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "headword — 'Also Known As' field: Entry Form, Entry Word, Lemma, Lexical Item",
        "judgment": "lexical item = headword (\\lx); the \\lf lexical-function "
        "topics out-rank \\lx on the bare query through the shared 'lexical' token",
    },
    {
        "term": "entry words",
        "keys": ["lx"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§4.6 (root-oriented vs. lexeme-oriented databases) — 'by the form of the entry words (morphemic)'",
        "judgment": "plural of entry word; the book uses 'entry words' for the "
        "forms a dictionary is organized by — the \\lx headword field",
    },
    {
        "term": "homograph",
        "keys": ["hm"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\hm field description — '\\hm Homonym/homophone/homograph'",
        "judgment": "\\hm is the homonym/homophone/homograph number field — the "
        "book's own \\hm description names homograph; the corpus never uses the "
        "term, so the query needs the mapping",
    },
    {
        "term": "homographs",
        "keys": ["hm"],
        "source": "TEI P5 Guidelines, ch. 10 'Dictionaries' (CC BY 3.0 / BSD 2-Clause)",
        "locator": "§10.1 Dictionary Body and Overall Structure — 'distinct "
        "entries for homographs … a numeric superscript on the headword "
        "identifying the homograph number'",
        "judgment": "plural; TEI ties homographs to the homograph number — the number the \\hm field encodes",
    },
    {
        "term": "grammatical category",
        "keys": ["ps", "pn"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "lexical category — 'Also Known As' field: Part of speech, "
        "Word class, Grammatical category, Grammatical class",
        "judgment": "lexical category = part of speech — the same mapping as the "
        "seeded 'word class'; the bare query matches only the restrictions "
        "topics' 'grammatical' mentions",
    },
    {
        "term": "grammatical class",
        "keys": ["ps", "pn"],
        "source": "SIL Glossary of Linguistic Terms (glossary.sil.org)",
        "locator": "lexical category — 'Also Known As' field: Part of speech, "
        "Word class, Grammatical category, Grammatical class",
        "judgment": "same mapping as 'grammatical category'; the bare query's "
        "top match is the \\pd paradigm topic, not the part-of-speech fields",
    },
    {
        "term": "confer",
        "keys": ["cf"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\cf field description — '\\cf Confer/cross-reference "
        "to other headwords: MDF converts this code to See:'",
        "judgment": "\\cf is the confer/cross-reference marker; the cross-reference "
        "gloss topics (\\ce/\\cn/\\cr) out-rank it on the bare query through shared "
        "tokens, but the word 'confer' names the \\cf field",
    },
    {
        "term": "etymology",
        "keys": ["et"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\et field description — '\\et Etymology (historical)'",
        "judgment": "\\et is the etymology field; its bundle members (\\eg/\\es/\\ec) "
        "out-rank it on the bare query but are its subfields, reachable from "
        "\\et's own cross-references",
    },
    {
        "term": "variant",
        "keys": ["va"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\va field description — '\\va Variant forms of headword'",
        "judgment": "\\va is the variant-forms field; the variant-comment bundle "
        "(\\ve/\\vn/\\vr) out-ranks it on the bare query, but those comment fields "
        "exist to annotate the forms \\va carries",
    },
    {
        "term": "variants",
        "keys": ["va"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§6.5 (handling dialect information) — 'The \\va (variants) field is dual purpose'",
        "judgment": "plural; the book names \\va 'the \\va (variants) field'. The "
        "singular query's bundle visibility comes from \\va's own cross-references",
    },
    {
        "term": "finderlist",
        "keys": ["Formatting_and_Printing"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§3.3.4 'English and national language finderlists'; finderlist production workflow §2.3",
        "judgment": "finderlist production — audience, format, reversal finderlist "
        "options — is described in the corpus's formatting/printing section (the "
        "topic titled 'Formatting and Printing Your Dictionary and Finderlists'); "
        "the bare query instead surfaces the gloss/reversal fields that feed one",
    },
    {
        "term": "inflection",
        "keys": ["pd", "rd"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\va field description — 'incomplete inflections or "
        "reduplication … should be handled under the field(s) for paradigms "
        "(\\pd) or reduplication (\\rd)'",
        "judgment": "the book directs inflection material to the paradigm (\\pd) "
        "or reduplication (\\rd) fields; the corpus never uses the term",
    },
    {
        "term": "inflections",
        "keys": ["pd", "rd"],
        "source": "Coward & Grimes, Making Dictionaries: a guide to lexicography "
        "and the Multi-Dictionary Formatter (SIL 2000)",
        "locator": "§2.1 \\va field description — 'incomplete inflections or "
        "reduplication … should be handled under the field(s) for paradigms "
        "(\\pd) or reduplication (\\rd)'",
        "judgment": "plural of the same book passage ('incomplete inflections')",
    },
]
