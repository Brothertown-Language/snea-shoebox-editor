> Full spec: this issue body (remote spec). Plan artifacts will be created at https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1417/ when this enters its plan cycle.
> Child spec: #1429 governs derivation of vocabulary-table entries beyond the seeded set pinned below.

## Problem
The in-app MDF Reference page delivered by #1379 ships with a v1 filter: case-insensitive substring matching over topic keys and definition text. That covers marker-code lookup but returns no relevance ranking, and substring semantics miss reformulations (e.g. plural/inflected phrasing in prose).

## Structure
Three atomic work units with declared dependencies; the shared definitions are normative for all three:

- **W1 Scoring engine** — pure module over the committed corpus; depends on nothing
- **W2 Vocabulary table** — committed data; seed set pinned here; extension beyond the seed governed by #1429; entry demonstrations execute through W1 (declared dependency: W2's verification instrument is W1)
- **W3 Page integration** — wiring; depends on W1 + W2

## Definitions (normative)
- **Corpus:** the 108 keyed topics of `docs/mdf/build/master.json`.
- **Document text** per topic: the `\key` line, the heading (when present), and every block's text.
- **Token:** a maximal run of Unicode word characters — the Python `[^\W_]+` pattern (Unicode `\w` minus underscore), lowercased. Hyphenated compounds therefore split (`cross-reference` → `cross`, `reference`); `\`-marker tokens (the `cf` in `\cf`) are ordinary index terms. (The `\w`-based rule follows the repo's regex-safety lessons for linguistic characters.)
- **Corpus statistics** under these definitions (verified 2026-10-11): 108 topics, 29–1125 words each (≈40× spread), mean 198.
- **IDF:** `ln(1 + (N − df + 0.5)/(df + 0.5))` — the non-negative Lucene/ATIRE formulation, pinned as a design choice. Rationale: the original Robertson form `ln((N − df + 0.5)/(df + 0.5))` goes negative when df > N/2 — true here for `cf` (df = 93 > 54) — producing non-interpretable negative scores for ubiquitous marker tokens; the candidate suite passes under both IDF forms with the composition pinned below, and the non-negative form is the one specified.
- **Boost composition:** the marker-code key boost and alias contributions each add 10 to a topic's final score, after the BM25 sum (verified 17/17 under this composition; accumulating across matching entries where several apply).
- **Score ties:** broken by the topic's index in `master.json`'s `topics` array (deterministic, reproducible).

## W1 — Scoring engine
In-process Okapi BM25 (k1 = 1.5, b = 0.75) over the corpus per the Definitions, with:

- **Heading field weighting (×3):** tokens of the `\key` line and heading weigh 3× body tokens in the term-frequency term.
- **Marker-code key boost (10):** if the query contains a topic's own marker code, that topic's final score gains +10.
- **Index** built at page load and cached; scorer hand-rolled; **no new dependencies**; no database storage, no external service, no CDN scripts — fully self-contained, consistent with the #1379 redesign decision.

Rationale (verified against the corpus, 2026-10-11): TF-IDF's raw term frequency ranks long chapter pages first on exactly the reformulation queries this spec targets (`plural` → Order_of_Fields, `part of speech` → Alternate_Hierarchy, `borrowed word` → Character_Style_Codes, `reversal` → Order_of_Fields); BM25's term-frequency saturation and length normalization rank the correct field topic first. Heading ×3 fixes `ps` (a long chapter topic otherwise outranks the field topic). The key boost fixes `cf` — plain BM25 ranks it #19 (df = 93/108; a 465-word topic against the 198-word mean); the boost takes it #1 with zero regressions across the marker-code candidate queries. Full BM25F, language-model, or embedding approaches are over-engineering for 108 static documents.

**W1 instrument:** the W1 rows of the candidate table below (the engine alone satisfies them — verified without any W2 mechanism), plus the **character-survival census** — tokenization preserves the corpus text's non-ASCII letters exactly: á ×26, ñ ×3, é ×1. The corpus's one non-letter non-ASCII character (• ×2, punctuation) is excluded from tokens by the word-character rule — expected, not a loss of linguistic content. (Census verified live 2026-10-05 for the source text and 2026-10-11 for `master.json` — identical.)

## W2 — Vocabulary table (seed set)
A committed data file beside the scorer supplies two mechanisms with distinct composition semantics:

- **Morphological variants — index-time posting extension:** every document whose token stream contains a token equal to an entry's canonical form is additionally indexed under the entry's variant tokens (e.g., every topic containing `paradigm` is also indexed under `paradigms`). Seeds: `paradigms`→`paradigm`; `references`→`reference`.
- **Semantic aliases — query-time mapping:** an alias term (a token or a contiguous token phrase) maps to one or more topic keys; when the query's token sequence contains the term, each mapped topic's final score gains +10 (per the Boost composition in Definitions). Seeds: `inflected`→`lc`; `lemma`→`lx`; `word class`→`ps`, `pn`.

Seed provenance: `inflected`→`lc` — *Making Dictionaries* (Coward & Grimes, SIL 2000), §5.4.4: "Where a language has lexemes in a variety of inflected forms, none of which is 'basic', a citation form must be listed as the headword"; the corpus itself contains zero `inflect*` tokens, so no in-corpus derivation exists. `lemma`→`lx` and `word class`→`ps`/`pn` — SIL Glossary of Linguistic Terms, curated "Also Known As" fields. License constraint: term phrases with citation only, never definitions.

**W2 instrument:** the W1+W2 rows of the candidate table below — all five fail on the bare engine (verified), so each is a genuine demonstration of its seeded entry; additionally, the variant demonstrations: `paradigms` returns zero matches without its entry, and `cross references` fails its expectation without `references`→`reference` (both verified 2026-10-11). Extension beyond the seeds is governed by #1429 (admission, provenance, licensing, and regression rules live there).

## W3 — Page integration
The MDF Reference page's filter input routes to the W1 scorer with the W2 table; the v1 substring matching leaves the filter path; the input element and page layout are unchanged. The seam is the one #1379 left deliberately: `src/frontend/pages/mdf_reference.py` — filter input at line 982, v1 `filter_topics` at line 250.

**W3 instrument:** structural — the filter input's call path invokes the scorer module and `filter_topics` is not on the filter path; behavioral — the candidate table is executed through the page's search entry point (in-process; no live-app run).

## Verification
Deterministic score checking over committed static data; no live-app run. The candidate table is committed with the tests; every assertion must pass (all verified 2026-10-11). The Unit column declares which unit's instrument each row belongs to: W1 rows verify the engine alone; W1+W2 rows verify engine plus seeded table.

| Query | Expected result | Unit |
|---|---|---|
| `cf`, `ps`, `ge`, `pl`, `lx` | that marker's topic ranks #1 | W1 |
| `plural` | `pl` #1 | W1 |
| `part of speech` | `ps` #1 and `pn` #2 | W1 |
| `borrowed word` | `bw` #1 | W1 |
| `cross reference` | {ce, cn, cr, cf} occupy the top 4 | W1 |
| `reversal` | {rr, rn, re} occupy the top 3 | W1 |
| `reduplication` | `rd` #1 | W1 |
| `irregular` | {pdl, pd} occupy the top 2 | W1 |
| `paradigms` | the top 4 results are all paradigm topics (`pd`/`pd*`) | W1+W2 |
| `cross references` | {ce, cn, cr, cf} occupy the top 4 | W1+W2 |
| `inflected` | `lc` #1 | W1+W2 |
| `lemma` | `lx` #1 | W1+W2 |
| `word class` | {ps, pn} occupy the top 2 | W1+W2 |

## Out of scope
Anything touching the Records search stack (Postgres FTS, search modes) — this shares no code path with it; ranking over the live dictionary records.

## Impact
- **Risk:** over-engineering a 108-entry corpus — mitigated by proportionate verification against the actual source content
- **Dependencies:** none new; `master.json` committed by #1379 (R-7); vocabulary-table extension governed by #1429

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)

