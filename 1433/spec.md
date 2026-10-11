> Full spec: this issue body (remote spec). Plan artifacts will be created at https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1433/ when this enters its plan cycle.
> Child spec: #1431 governs the in-app browser's labeling and the committed display data this spec consumes.

## Problem
#1431 defines the labeling regime — committed display labels, one enumerated shd2 exception, token+name marker entries — but scopes its requirements to the in-app browser only, leaving the published HTML and PDF editions on their current conventions. Developer instruction (2026-10-11): the published HTML and PDF need to be consistent with the new labeling requirements.

Current-state map (verified 2026-10-11 against the committed build outputs):

| Element | HTML | PDF | #1431 regime |
|---|---|---|---|
| Chapter/topic titles (nav, ToC, page/chapter headings) | human `\shd` headings | human `\shd` headings | compliant already |
| Field Marker Reference entries | `h4` topic headings: `\ce  cross-reference (English gloss)` | `\subsection{...\lx  lexeme or headword of the lexical entry}` | compliant already |
| Search hit headings (HTML lunr) | `doc.heading` = `\ce  cross-reference (English gloss)` | n/a | compliant already |
| Nav-sidebar marker entries | bare backslash-tokens (`\ce`, `\lx`) — no names | n/a (ToC lists the token+name subsections) | **gap** |
| Nav-sidebar multi-key stub | raw `\1s 1p 1e 1i 1d 2s 2p 2d 3s 3p 3d 4s 4p 4d` | n/a | **gap** |
| `\shd2` headings | source-verbatim `h3`, including the paren-wrapped one | source-verbatim `\section`, including the paren-wrapped one (which also enters the print ToC) | **gap** |
| `\cf` cross-reference links | source tokens (`Range_Sets`) | source tokens (`Range\_Sets`) | unchanged by design (uniform raw across all editions, the source's own stated convention) |

So the editions' gaps are exactly two: navigation entry labels in the HTML sidebar, and `\shd2` display text in both editions.

## Design direction (developer-stated, 2026-10-11)
The static-data principle of #1431 applies unchanged: the renderers consume the committed display fields #1431's converter emits (`docs/mdf/build/master.json`, schema `/2`) — no string surgery in the HTML or LaTeX renderers, and the exception inventory remains the single deviation source.

## Definitions (normative)
- **Display data:** the committed per-topic and per-block presentation fields in `docs/mdf/build/master.json` schema `/2` — display labels (per topic) and shd2 display text (per `\shd2` block) — as defined normatively by #1431. This spec adds no fields and no exceptions.
- **Edition parity:** for a given topic (or shd2 block), every edition that presents an entry label (or shd2 heading) presents content derived from the same committed display data. Editions may differ in typographic presentation of that content (the HTML sidebar's `\`-prefixed marker token, the app's plain token), never in its content.
- **Indexed/searched text:** the raw source text per #1417's corpus definition — display fields are presentation-only additions; search corpora and indexes (in-app BM25, HTML lunr) remain keyed to raw text and are unaffected by display data.

## Requirements
- **SC-1 (structural; HTML nav gap):** every marker entry and the multi-key stub in the built HTML nav sidebar renders content from the committed display data — single-marker entries: marker token together with its marker name; the stub: its display label ("Old verb paradigm markers"). Chapter and home entries are already compliant and remain so.
- **SC-2 (structural; shd2 gap, both editions):** the paren-wrapped `\shd2` renders as "Understanding the hierarchical structure of an entry" in the built HTML chapter page (`h3`) and the built PDF (`\section` title and the print ToC entry, which follows the section title) — via #1431's single enumerated exception; every other `\shd2` heading in both editions remains byte-identical to its marker-stripped source text.
- **SC-3 (structural; single-sourcing):** the HTML and LaTeX renderers read the committed display fields from `master.json`; no render-time string transformation of label or shd2-heading text exists in `scripts/convert_mdf_master.py`'s rendering paths beyond the marker-token strip #1431 already defines; the exception inventory count is unchanged (exactly one entry).
- **SC-4 (structural; edition parity):** for every chapter topic, the stub, and all 89 single-marker topics, the label content presented by HTML nav, PDF (ToC/reference headings), and the app rail derives from the same committed display data per the parity definition; the home entry is excluded (its label is edition-appropriate by #1379/#1431: the app rail chip reads "Home", the editions present the document title).
- **SC-5 (structural; corpus invariance):** the display fields change no searched text — #1417's corpus definition and candidate suite are unaffected; the HTML lunr index's `text` and `heading` fields are unchanged by this spec's delta (nav labels are not indexed content).
- **SC-6 (structural; build discipline):** regenerating the artifacts reproduces the committed outputs byte-for-byte — `master.json`, the LaTeX master, the built site files, and the PDF (the existing round-trip and renderer census suites extended to the new fields); `\cf` links remain source-raw in both editions (uniform with the app's detail pane).

## Verification instruments
- **Artifact censuses (SC-1, SC-2, SC-3, SC-4, SC-6):** fact-decidable checks over the committed build outputs, per the established renderer-suite pattern (`test_mdf_renderers_sc2_sc3_sc14.py`): HTML nav sidebar parsed for entry labels (89 marker entries token+name, stub label, zero underscore-bearing labels); HTML `h3`/PDF `\section` shd2 titles compared byte-wise against source-derived expectations with exactly one exception; parity census joining `master.json` display data against HTML nav, LaTeX subsection/section titles, and (via the app suite) the rail; byte-exact rebuild verification.
- **PDF surface (SC-2):** the committed `.tex` is the checked source of truth for section titles; the built PDF's ToC follows from it (checked via the build's successful compile and a text-extraction spot check of the ToC page for the exception-free title).
- **Regression (SC-5, SC-6):** pytest — #1417's W1/W2 candidate suites, #1431's display-data census, the round-trip census, the renderer suite. Declared dependency: #1431's schema-`/2` fields must exist before this spec's censuses can run.

## Out of scope
- `\cf` cross-reference labels in every edition — raw source tokens, uniform, unchanged (the source's own stated convention; matches the app detail pane's unchanged cf rendering).
- The app browser — governed entirely by #1431; this spec changes no app code.
- The source (`MDFields19a_UTF8.txt`), the exception inventory's content, the foreword, and any new display fields.
- PDF/HTML typography and layout beyond the label text substitutions this spec requires.

## Impact
- **Dependencies:** #1431's committed display data (schema `/2`) — this spec consumes it; it adds none.
- **Risk:** edition drift — mitigated by the parity census joining all three surfaces against the single committed source; typographic variation is explicitly permitted, content variation is not.
- **Data integrity:** no new text is invented — every rendered label traces to the source's own `\shd` headings through #1431's derivation, plus its one enumerated exception.
- **Test impact:** the renderer suite gains the nav/shd2 censuses; build script output assertions extended; no app or search test changes.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
