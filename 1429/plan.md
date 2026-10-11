# Plan: #1429 Vocabulary table derivation for MDF Reference search

Spec of record: `.issues/1429/spec.md` (sources selected and live-verified by the developer 2026-10-11; research card `.issues/research-cards/mdf-alias-vocabulary-sources.md`). Scope: #1429 only — data derivation into the existing table; scorer parameters, mechanisms, and composition semantics are untouched (#1417's domain).

Branch: `feature/1429-mdf-vocabulary-derivation`, base tip `768c4d0` (main after #1430 merged — #1417's engine, seeded table, and W1/W2/W3 tests are present, so demonstrations can execute).

Grounding: every candidate entry below was executed against the merged engine in a scratch harness before admission — bare-engine failure recorded per entry, demonstration verified, and all 17 of #1417's candidate rows re-passed with the proposed table. Sources fetched this session: MDF_2000.pdf (downloaded, text-extracted; quotes located to sections), glossary.sil.org `term/headword` and `term/lexical-category` (two fetches, ≥10 s apart per robots Crawl-delay), TEI P5 ch. 10 (one fetch). CLARIN CCR consulted via the research card and not fetched: it contributes no term phrase for a demonstrated gap that the book/glossary/TEI do not already supply.

Deliverable shape: all new entries are data rows in `src/services/mdf_search_vocabulary.py` (`VARIANT_ENTRIES` / `ALIAS_ENTRIES`) — the page entry point (`mdf_reference.py`) reads these lists, so extension is data-only, no scorer or page change. Every new entry carries `source`, `locator`, and `judgment` (the spec's admission rule (b) recorded per entry); the scorer reads only `variant`/`canonical`/`term`/`keys`, so extra fields are inert. Seeds are untouched (their provenance and demonstrations live in #1417). Test module: `test/test_mdf_search_vocabulary_1429.py` — negative demonstrations (bare engine), admission demonstrations (full table), and admission invariants. #1417's W1/W2 modules are the regression instrument (spec: no-regression).

## Candidate table (every row empirically demonstrated)

Variant entries (index-time posting extension; canonical form present in corpus — all verified):

| variant → canonical | candidate query | bare behavior | with entry |
|---|---|---|---|
| `headwords` → `headword` | `headwords` | zero matches | lx #1 (df(headword)=10) |
| `reversals` → `reversal` | `reversals` | zero matches | {rr, rn, re} top-3 |
| `homonyms` → `homonym` | `homonyms` | only Sections_in_a_Lexical_Entry | hm #1 |
| `synonyms` → `synonym` | `synonyms` | only Summary_of_Fields/Order_of_Fields | sy #1 |
| `etymologies` → `etymology` | `etymologies` | only The_MDF_Documentation | top-4 = the etymology bundle {es, eg, ec, et} |

Rejected candidate: `variants` → `variant` — with the `variants` alias (below) the query already ranks va #1, so the variant entry has no independent demonstration under the spec's fail-without/pass-with rule; dropped (alias-only gives va as the sole match).

Alias entries (query-time +10; admission rule (c) = mapped topic(s) rank first among matched):

| term → keys | candidate query | bare behavior | with entry | source / locator |
|---|---|---|---|---|
| `lexeme` → lx | `lexeme` | lv #1 (lx #2) | lx #1 | MDF_2000 §2.1 \lx description: "Lexeme: also known as lemma or headword" |
| `entry word` → lx | `entry word` | Summary_of_Fields #1 | lx #1 | SIL Glossary term headword, "Also Known As: Entry Form, Entry Word, Lemma, Lexical Item" |
| `entry form` → lx | `entry form` | mn #1 | lx #1 | same glossary AKA field |
| `lexical item` → lx | `lexical item` | le #1 | lx #1 | same glossary AKA field |
| `entry words` → lx | `entry words` | ge #1 | lx #1 | MDF_2000 §4.6 "by the form of the entry words (morphemic)" |
| `homograph` → hm | `homograph` | zero matches | hm sole match | MDF_2000 §2.1 \hm description: "\hm Homonym/homophone/homograph" |
| `homographs` → hm | `homographs` | zero matches | hm sole match | TEI P5 §10.1: "distinct entries for homographs … the homograph number" |
| `grammatical category` → ps, pn | `grammatical category` | or/on/ov/oe top-4 | set top-2 = {ps, pn} | SIL Glossary term lexical-category, "Also Known As: … Grammatical category" |
| `grammatical class` → ps, pn | `grammatical class` | pd #1 | set top-2 = {ps, pn} | same glossary AKA field ("… Grammatical class") |
| `confer` → cf | `confer` | cf #4 | cf #1 | MDF_2000 §2.1 \cf description: "Confer/cross-reference to other headwords" |
| `etymology` → et | `etymology` | et #4 (es #1) | et #1 | MDF_2000 §2.1 \et description: "\et Etymology (historical)" |
| `variant` → va | `variant` | va #3 (ve #1) | va #1 | MDF_2000 §2.1 \va description: "Variant forms of headword" |
| `variants` → va | `variants` | zero matches | va sole match | MDF_2000 §6.5: "the \va (variants) field" |
| `finderlist` → Formatting_and_Printing | `finderlist` | Formatting #5 (ge #1) | Formatting #1 | MDF_2000 §3.3.4 "English and national language finderlists" |
| `inflection` → pd, rd | `inflection` | zero matches | top-2 = [pd, rd] | MDF_2000 §2.1 \va description: "incomplete inflections or reduplication … should be handled under the field(s) for paradigms (\pd) or reduplication (\rd)" |
| `inflections` → pd, rd | `inflections` | zero matches | top-2 = [pd, rd] | same passage (plural "incomplete inflections" in the same sentence) |

Considered and rejected (bare engine already ranks the answer topic first — an entry would do no work): `headword`→lx, `citation form`→lc, `synonym`→sy, `subentry`/`subentries`→se, `sense number`→sn, `singular`→sg, `part of speech`→ps/pn, `lexical entry`→lx, `finderlists`→Formatting, `plural`→pl, `reversal`→re/rn/rr, `etymologies`-singular-alias (plural query's correct answer is the bundle, delivered by the variant entry), `homonym`→hm, `reduplication`→rd, `datestamp`→dt, `thesaurus`→th.

## Item 1 (variant admission, spec's variant rule + instrument): five variant entries

- Deliverable: five `VARIANT_ENTRIES` rows (`headwords`, `reversals`, `homonyms`, `synonyms`, `etymologies`), each with source/locator/judgment. `etymologies`/`reversals` cite in-corpus plural derivation (same pattern as the seeds); `headwords`/`homonyms`/`synonyms` additionally cite the book's attested plurals (§2.1).
- RED: in `test/test_mdf_search_vocabulary_1429.py` — bare-engine rows: `headwords` == [] ; `reversals` == [] ; `homonyms` top-1 == Sections_in_a_Lexical_Entry ; `synonyms` top-2 == {Summary_of_Fields, Order_of_Fields} ; `etymologies` top-1 == The_MDF_Documentation. All five fail against the current tree (module missing → collection error counts as RED; rows written to pass once entries exist).
- GREEN: add the five rows.
- verify: executed pytest — negative rows turn green, demonstration rows rank per the candidate table; canonical-in-corpus assertion {headword, reversal, homonym, synonym, etymology} ⊆ corpus tokens passes.

## Item 2 (alias admission, rules (a)–(c)): the five lx aliases

- Deliverable: `lexeme`, `entry word`, `entry form`, `lexical item`, `entry words` → `["lx"]` with source/locator/judgment (book §2.1 / §4.6; glossary headword AKA).
- RED: bare rows — `lexeme` top-1 == lv ; `entry word` top-1 == Summary_of_Fields ; `entry form` top-1 == mn ; `lexical item` top-1 == le ; `entry words` top-1 == ge.
- GREEN: add the five rows.
- verify: executed pytest — with the full table each query ranks lx #1.

## Item 3 (alias admission): the two hm aliases

- Deliverable: `homograph`, `homographs` → `["hm"]` with source/locator/judgment (book §2.1 \hm description; TEI P5 §10.1).
- RED: bare rows — both queries return zero matches.
- GREEN: add the two rows.
- verify: executed pytest — each query's sole matched topic is hm.

## Item 4 (alias admission): the two ps/pn aliases

- Deliverable: `grammatical category`, `grammatical class` → `["ps", "pn"]` with source/locator/judgment (glossary lexical-category AKA).
- RED: bare rows — neither query places ps/pn in its top-2.
- GREEN: add the two rows.
- verify: executed pytest — set top-2 == {ps, pn} for both (same assertion form as the seeded `word class` row).

## Item 5 (alias admission): the remaining seven aliases

- Deliverable: `confer`→cf, `etymology`→et, `variant`→va, `variants`→va, `finderlist`→Formatting_and_Printing, `inflection`→[pd, rd], `inflections`→[pd, rd], with source/locator/judgment (book §2.1, §3.3.4, §6.5).
- RED: bare rows — `confer` top-1 == ce ; `etymology` top-1 == es ; `variant` top-1 == ve ; `variants` == [] ; `finderlist` top-1 == ge ; `inflection`/`inflections` == [].
- GREEN: add the seven rows.
- verify: executed pytest — `confer`/`etymology`/`variant`/`finderlist` rank their mapped topic #1; `variants` sole match va; `inflection`/`inflections` top-2 == [pd, rd].

## Item 6 (provenance + judgment invariants, spec's provenance rule): structural assertions

- Deliverable: in the new test module — every #1429 entry resolves in the committed lists and carries non-empty `source`, `locator`, and `judgment`; the five variant canons are corpus tokens (already asserted in Item 1's module; kept adjacent to the entries they guard).
- RED: the judgment-field assertions fail against the current tree (entries absent).
- GREEN: satisfied by Items 1–5's rows.
- verify: executed pytest.

## Item 7 (no-regression gate, spec's instrument): full suite green

- Deliverable: green full-suite run evidence.
- RED/GREEN: N/A (gate item) — full `uv run pytest -q --ignore=tmp` executed this session, 0 failed; designed skips permitted. #1417's W1/W2/W3 modules and every other module run unchanged against the extended table.
- verify: captured summary line.
- commit: any residual fixes surfaced.

## Dependency order

1 → 2 → 3 → 4 → 5 → 6 → 7. Items 1–5 are independent data additions but sequenced so each pytest run isolates one admission class; 6 asserts invariants over the accumulated table; 7 is the gate. One commit per issue ticket at PR squash time (single ticket: #1429).

## Notes

- Idempotence (spec requirement): satisfied by construction — the table is committed literal data; no derivation code exists to re-run.
- Sourcing etiquette (spec requirement): this session's fetches honored glossary.sil.org robots Crawl-delay 10 (two term pages, sequential); TEI once; the book once. No bulk crawl was needed — the demonstrated gaps are covered by per-term evidence.
- License boundary (spec requirement): every citation is a term phrase plus locator; no source definitions or prose enter the repository beyond the short quoted fragments inside `locator` fields that the seeds already establish as the provenance pattern (single-sentence quotes identifying the passage).
- Alias mechanism note: alias terms match query tokens exactly (token-sequence containment), so plural variants of alias terms need their own rows where sources attest them (`homographs`, `entry words`, `variants`, `inflections` — all attested as cited; `lemmas` is attested nowhere and stays out).
- The `variants` alias is the sole entry whose demonstration is a sole-match summon (va has no BM25 match for the plural token); its judgment field records that the singular query's bundle visibility comes from va's own cross-references.
