> Full spec: this issue body (remote spec). Child of #1417 (the MDF Reference full-text search feature spec): this spec governs derivation of vocabulary-table entries beyond #1417's seeded set. Plan artifacts will be created at https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1429/ when this enters its plan cycle.

## Problem
#1417 pins a seeded vocabulary table — two morphological-variant entries and three semantic-alias entries — sufficient for its own candidate table, and defers further entry derivation to this spec. Deriving additional entries from external linguistic sources is open-ended data work with its own quality bar (provenance, licensing, sourcing etiquette) and its own verification nature (per-entry audit, not score design). Separating it keeps #1417 closed and testable while the table grows under governed procedure.

## Sources (selected by the developer, 2026-10-11; live-verified the same day)
1. *Making Dictionaries: a guide to lexicography and the Multi-Dictionary Formatter* (Coward & Grimes, SIL 2000) — https://s3.amazonaws.com/downloads.sil.org/legacy/shoebox/MDF_2000.pdf — the companion book to the MDF 1.9a field reference itself
2. SIL Glossary of Linguistic Terms — https://glossary.sil.org/ — per-term "Also Known As" fields; alphabetical term index and `sitemap.xml` available; robots.txt Crawl-delay 10
3. TEI P5 Guidelines, ch. 10 "Dictionaries" — https://www.tei-c.org/release/doc/tei-p5-doc/en/html/DI.html — dual-licensed CC BY 3.0 / BSD 2-Clause
4. CLARIN Concept Registry — https://concepts.clarin.eu/ccr/ — Skosmos REST API; prefLabel/altLabel pairs; license not stated on-site (attribution-required pending confirmation)

Research findings with coverage evidence and dead ends are recorded in `.issues/research-cards/mdf-alias-vocabulary-sources.md`.

## Requirement
Extend #1417's committed vocabulary table with entries derived from these sources, under:

- **Admission — variant entries:** admitted only on demonstration: a stated candidate query fails without the entry and passes with it, and the entry's canonical form is present in the corpus (the corpus being the 108 keyed topics of `docs/mdf/build/master.json`, per #1417's Definitions).
- **Admission — alias entries:** admitted only when all three hold: (a) the term traces to a source, cited by source and locator (book section, glossary term page, TEI element, CCR concept id); (b) the mapped topic keys actually answer the term — a linguistic judgment recorded per entry; (c) demonstration through #1417's scoring engine: the term's query ranks the mapped topic(s) first among matched topics.
- **Provenance:** every entry carries its source citation; no invented mappings; term phrases only, never definitions. License boundary: SIL materials are © with Terms-of-Use limits (no republication); TEI is permissive; CCR unstated — a term phrase used as a search alias with citation is the permitted use.
- **Sourcing etiquette:** respect robots.txt (glossary.sil.org Crawl-delay 10 — the ~900-term crawl takes ~2.5 h and must not be parallelized); fetch only what candidate terms require.
- **No regression:** after any extension, #1417's full candidate suite still passes; the scorer's parameters, mechanisms, and composition semantics are untouched by this spec.
- **Idempotence:** the committed table remains deterministic data; re-derivation from the same sources yields the same entries.

## Instrument
Per entry: (1) provenance check — the citation resolves to the stated source and locator (fact-decidable); (2) demonstration — executed through #1417's scoring engine per the admission rule above (declared cross-dependency: this requires #1417's W1 engine to exist; demonstrations cannot run before it); (3) regression — #1417's candidate suite re-passes post-extension.

## Out of scope
- Any change to scorer parameters, mechanisms, or composition semantics (#1417's domain)
- Ranking over live dictionary records (out of scope in #1417; unchanged here)
- Source definitions or prose entering the repository (license boundary — term phrases and citations only)

## Impact
- **Dependencies:** #1417's scoring engine (W1) must exist for demonstrations; the seeded table is the baseline this spec extends
- **Risk:** license drift — mitigated by the phrases-only constraint and per-entry citation
- **Data integrity:** only real, verifiable mappings; every entry auditable to its source

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)

