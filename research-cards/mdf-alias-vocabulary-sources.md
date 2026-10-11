# MDF Alias Vocabulary — Online Terminology Sources

Date: 2026-10-11
Question: which online linguistic-terminology sources can supply user-side vocabulary for a search alias table matched to the MDF 1.9a field-reference corpus (108 topics, `docs/mdf/build/master.json`)?
Context: spec for #1417 (in-app MDF Reference full-text search); corpus has 0 `inflect*` tokens (priority gap), and Shoebox print-apparatus terms no external registry defines.

## Verified sources (all fetched live 2026-10-11)

| Source | URL | License | Coverage evidence | Conf |
|---|---|---|---|---|
| **Making Dictionaries** (Coward & Grimes, SIL 2000) — the MDF 1.9a reference's own companion book | https://s3.amazonaws.com/downloads.sil.org/legacy/shoebox/MDF_2000.pdf (via https://software.sil.org/shoebox/mdf/) | © 1995, 2000 SIL, ALL RIGHTS RESERVED — term phrases with citation only; no definitions | inflected form(s) ×6 (tied to \lc: "lexemes in a variety of inflected forms… a citation form must be listed as the headword"), finderlist ×83, reversal ×57, cross-reference ×44, headword ×120, citation form ×25, subentry ×31, part of speech ×57 | 0.95 |
| **SIL Glossary of Linguistic Terms** (glossary.sil.org, Loos et al., LinguaLinks 5.0 2003) | https://glossary.sil.org/ (~900 term pages, sitemap.xml lists slugs, robots Crawl-delay 10) | SIL Terms of Use: free use for non-commercial scholarly/education; republication/mirroring prohibited — term names + AKA values with citation | Per-term "Also Known As" = curated synonym lists: Headword ← Entry Form/Entry Word/Lemma/Lexical Item; Lexical Category ← Part of speech/Word class/Grammatical category; covers paradigm, inflection, homonym, homograph, etymology, usage-type/restrictive vocabulary. ABSENT: inflected form (site search 0), cross-reference (0), reversal (0), finderlist (0) | 0.9 |
| **Ronald Moe, Intro to Lexicography for FLEx** (rev. 2016) | https://downloads.languagetechnology.org/fieldworks/Documentation/Intro%20to%20Lexicography/Introduction%20to%20Lexicography.htm | SIL copyright, no open license stated; single HTML page ~353K chars | inflected form ×84 (§3.2.3 "Stems and inflected forms", §3.2.3.1 "Irregularly inflected forms"), citation form ×94, variant ×245, reversal ×76, cross-reference ×37, paradigm ×17; reduplication ×0, finderlist ×0 | 0.85 |
| **CLARIN Concept Registry** (ISOcat successor) | https://concepts.clarin.eu/ccr/ (Skosmos REST API verified) | Not stated — attribution-required pending confirmation | prefLabel/altLabel/definition shape; live API hits: inflected form (C-4960), headword, part of speech, gloss, cross-reference, lexical entry, etymology, plural, synonym. Zero: homonym, antonym, reversal, paradigm, citation form | 0.85 |
| **TEI P5 Guidelines ch. 10 "Dictionaries"** | https://www.tei-c.org/release/doc/tei-p5-doc/en/html/DI.html | CC BY 3.0 + BSD-2 (verbatim from tei-c.org licensing page) | headword ×55, sense ×194, gloss ×31, homograph ×28, cross-reference ×27 (xref), inflected ×23 (incl. `<form type="inflected">…number=plural`), definition ×28, etymology ×8, paradigm | 0.9 |
| OntoLex-Lemon / -Morph / LexInfo / OLiA | www.w3.org/2016/05/ontolex/, ontolex.github.io/morph/, lexinfo.net (Apache-2.0), purl.org/olia | W3C FSA / Apache-2.0 / CC-BY 3.0 | "inflected forms" present in Lemon+Morph prose; LexInfo: partOfSpeech ×120, synonym, antonym; no lexicographic apparatus | 0.75–0.8 |
| FLEx 9.3 Help "Glossary of Terms" | https://downloads.languagetection.org/… (see note) | © 2003 SIL, no open license | inflection class ("declension/conjugation classes"), inflectional variants, character style ×5, standard format ×5; page warns "Many terms are not found in this glossary" | 0.75 |

Note (FLEx glossary URL as fetched): `https://downloads.languagetechnology.org/fieldworks/Documentation/en/Glossary_of_Terms.htm`

## Dead ends / retired (verified this session)

- ISOcat retired — superseded by CLARIN CCR (DatCatInfo confirms); DatCatInfo itself is JS-gated, "work in progress" (conf 0.45)
- Linguist List hosts no terminology registry (homepage verified)
- Wikipedia: no "Glossary of linguistics" page exists (404 verified); per-term articles only — fallback, not preferred
- Oxford Reference (Crystal), Trask/Routledge: subscription-gated, not anonymously fetchable
- ODLT: content-farm provenance (essay-mill copy on homepage) — do not use
- www-01.sil.org LinguaLinks-era hosts: HTTP 403

## Gaps no external source fills

MDF print-apparatus vocabulary — **datestamp, character styles, range sets, finderlist, printed field labels, reversal, confer** — is Shoebox/Toolbox print-workflow terminology; it exists only in the MDF book (prose) and the corpus itself. These aliases can only be curated internally. "Cross-reference" likewise has no standalone glossary entry anywhere checked.

## Recommendation for the alias table

1. **Primary: MDF_2000.pdf** — same document family as the corpus; uniquely bridges the priority gap (inflected forms → \lc citation form, §5.4.4) plus finderlist/reversal/cross-reference vocabulary. Extract term phrases with citation; all-rights-reserved.
2. **Secondary: glossary.sil.org** — per-term AKA fields are ready-made curated alias pairs for standard terms (lemma, word class, entry word…).
3. **Tertiary: TEI P5 ch.10 + CLARIN CCR** — permissive/unstated-license structured registries for inflected form, homograph, paradigm, etymology.

Every alias entry must (a) trace to a source term and (b) hit actual corpus content verified by a candidate query — no invented mappings.

---
🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
