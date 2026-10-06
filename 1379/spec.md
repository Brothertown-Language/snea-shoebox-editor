# SPEC: Convert Master MDF Documentation to LaTeX/PDF and HTML

## User Intent / Original Prompt
Convert the MDF 1.9a field reference (`docs/mdf/MDFields19a_UTF8.txt`) from Toolbox/Shoebox help format into two professionally publishable formats: a XeLaTeX-compiled PDF reference document and a multi-page browsable HTML site. Both outputs derive from a single parsed intermediate representation, ensuring consistency. The HTML output deploys to GitHub Pages; the PDF attaches to release assets.

## Intent / Executive Summary
Convert the MDF 1.9a field reference (`docs/mdf/MDFields19a_UTF8.txt`, 130KB, 108 `\key` entries, 297 `\cf` cross-reference fields, 444 formatting/printing examples (`\ftx`/`\fxv`)) from Toolbox/Shoebox help format into professionally publishable formats — a XeLaTeX-compiled PDF reference document and a multi-page browsable HTML site — both derived from a single parsed intermediate representation, ensuring consistency. Per the 2026-10-05 redesign direction, the outputs integrate into the main Streamlit app as a **self-contained user reference**: an "MDF Reference" page renders all 108 keyed topics natively from the committed intermediate JSON, mirroring the source's own chapter/section hierarchy, with in-context help hooks on the app's MDF-touching surfaces and a PDF download inside the MDF view. The GitHub Pages deployment is dropped; the PDF (correctly named to match its contents) is committed to the repository, attached to release assets, and downloadable from within the MDF Reference view.

## Root Cause
The source file is in Toolbox/Shoebox help format — a plain-text marker-based format (`\key`, `\shd`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`) that is not web-renderable, not printable as a professional document, and not navigable by modern readers. No automated conversion pipeline exists. Manual conversion is infeasible at 3353 lines with 297 cross-reference fields. Additionally, the app's users work with MDF markers daily (Direct Entry, Records, Upload MDF) with no in-app field reference available at the point of need.

## Approach
1. Write a Python converter (`scripts/convert_mdf_master.py`) that parses the Toolbox marker structure into an intermediate JSON representation. The parser MUST recognize all line-initial markers present in the source — `\key`, `\shd`, `\shd2`, `\shd3`, `\shd4`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`, `\bib`, `\nwt`, `\_sh` (verified census 2026-10-05) — with `\shd2` required for the subsection hierarchy and the remainder parsed as content/metadata, never treated as malformed
2. From the intermediate representation, render two outputs:
   - **LaTeX file** (`docs/mdf/build/master.tex`) — XeLaTeX with Noto Serif / Gentium for Unicode IPA support
   - **HTML site** (`docs/mdf/build/site/`) — multi-page static site with sidebar navigation and search (committed archival artifact, not deployed)
3. The build script (`scripts/build_mdf_docs.sh`) emits the PDF deliverable under its content-accurate name (`mdf-lexical-fields-1.9a.pdf`)
4. Add a GitHub Actions workflow that runs the build script on push to `main` and attaches the correctly-named PDF to release assets (no Pages deployment)
5. Implement a Streamlit "MDF Reference" page that renders all 108 keyed topics natively from `docs/mdf/build/master.json`: a chapter-grouped browser mirroring the source's own hierarchy (17 chapter topics, 21 `\shd2` subsections, marker entries nested within), an entry detail pane, landing on the source's built-in home/TOC entry (`\key aa`), deep-linkable via query parameter
6. Add in-context help hooks on the three MDF-touching surfaces (Direct Entry, Records, Upload MDF review)

## Alternatives Considered
| Alternative | Rejected Because |
|---|---|
| Manual conversion in Word/LaTeX | 3353 lines, 297 cross-reference fields — error-prone, unrepeatable |
| Sphinx + custom directive | Overkill for single-source conversion; adds Python build dependency |
| Pandoc with custom writer | Pandoc's Toolbox reader does not exist; would need a custom writer anyway |
| Single HTML page | 130KB source → ~500KB HTML; multi-page with sidebar is more navigable |
| Iframe-embedding the static HTML site in the app | Fights the app's own sidebar patterns (`hide_sidebar_nav` on task pages); double navigation; theming mismatch |
| GitHub Pages as the primary reference surface | External hosting contradicts the self-contained goal; takes users out of the app |
| Flat A–Z marker list in-app | Discards the source's own chapter/section hierarchy; worse for readers who don't know the marker |

## Key Decisions
- **Single intermediate representation (JSON)**: The PDF, HTML, and in-app page all derive from the same parsed data, guaranteeing cross-format consistency
- **XeLaTeX over pdfLaTeX**: Required for Unicode characters (ã, č, accented example words) — mandated by project standards
- **Static HTML over JS framework**: Zero runtime dependencies; works without JavaScript; committed as an in-repo archival artifact
- **Build script over Makefile**: Simpler dependency chain; works in CI without Make installed
- **Native in-app rendering from `master.json` over iframe/Pages**: The app carries its own reference (self-contained); follows Streamlit theming, role gating, and sidebar conventions
- **Mirror the source's own hierarchy**: The source provides 17 chapter topics, 21 subsections, and a built-in home/TOC entry; the page reuses that structure instead of inventing one
- **GitHub Pages deployment dropped**: The in-app page and the committed HTML archive cover the need; no external hosting dependency
- **Ranked full-text search deferred**: The v1 filter is Unicode-preserving substring matching; BM25-style full-text search is a follow-up spec (#1417) — no ranked-relevance claims in this revision
- **PDF named to match its contents**: `mdf-lexical-fields-1.9a.pdf` — derived from the document's own self-identification ("MDF Lexical Fields", draft v1.9a) and the repo's lowercase-hyphen convention

## Not Included
- **Editing or altering the source MDF content** — The converter parses and renders the source as-is; it must not modify `docs/mdf/MDFields19a_UTF8.txt` or the linguistic data it contains. Preserving data integrity is mandatory (see `090-data-integrity.md`).
- **Converting any MDF version other than 1.9a** — The parser targets the 1.9a marker set enumerated in the Conversion Approach section; other versions are out of scope.
- **Interactive or JS-framework-based HTML** — The HTML site is static with zero runtime dependencies; it is committed to the repository, not deployed.
- **Round-trip conversion back to Toolbox/Shoebox format** — The pipeline is one-way (Toolbox → JSON → LaTeX/HTML); no reverse conversion is produced.
- **Ranked full-text search (BM25 or similar)** — Deferred to follow-up issue #1417. This revision ships the Unicode-preserving filter only and makes no ranked-relevance claims.
- **Changes to the Records search stack** — The MDF Reference filter shares no code path with the Records search view (different data, different stack); the Records search is untouched.

## Dependencies
| Dependency | Purpose | Version/Constraint | Availability Requirement |
|---|---|---|---|
| XeLaTeX (`xelatex`) | PDF compilation with Unicode support | TeX Live 2023+ (fontspec, hyperref, makeidx) | MUST be installed on the CI runner and local build environment |
| Noto Serif fonts | Unicode glyph rendering in PDF | Installed system fonts | MUST be installed on the CI runner and local build environment; `fontspec` resolves them at compile time |
| Gentium fonts | Fallback Unicode glyph rendering in PDF | Installed system fonts | MUST be installed on the CI runner and local build environment; `fontspec` resolves them at compile time |
| Python 3.12+ | Converter and renderer scripts | `uv`-managed project environment | MUST be present in CI via `uv`; `uv sync` installs the environment |
| GitHub Actions (`actions/checkout`, release-asset upload) | CI build and release asset attachment | Official GitHub Actions | MUST be available in the repository's `.github/workflows/`; SC-5 requires releases enabled |
| `pdftotext` (poppler-utils) | PDF text extraction for verification | CI runner package | MUST be installed on the CI runner for SC-1/SC-3 verification |
| Streamlit (app runtime) | In-app MDF Reference page | Already the app's UI framework | No new runtime dependency; the page uses standard Streamlit widgets |
| Committed `master.json` | Data source for the in-app page | Generated by the converter, committed per R-7 | MUST exist and be readable by the app at runtime |

## Documentation Sources
| Source | Type | Purpose |
|---|---|---|
| `docs/mdf/MDFields19a_UTF8.txt` | Primary source document | MDF 1.9a field reference (Buseman, 2006) — the authoritative content to convert |
| `docs/from-other-projects/SIL-Shoe-1.24/` | Tracked format reference | SIL's own Standard Format implementation (`modules/Data.pm`) — grounds the Parsing Semantics; see its `PROVENANCE.md` |
| MDF 1.9a specification (Buseman, 2006) | Reference | Marker semantics, hierarchy, cross-reference meaning |
| Project AGENTS.md | Standard | XeLaTeX mandate, Unicode handling, data integrity rules |
| Project `docs/lessons-learned/` | Reference | FTS/regex/normalization lessons for linguistic data handling |

## Source Document
`docs/mdf/MDFields19a_UTF8.txt` — Official MDF 1.9a field reference (Buseman, 2006). Contains:
- 108 keyed topics, all unique: ~91 field-marker definitions (`\lx`, `\ge`, `\ps`, `\se`, `\cf`, etc.) + 17 conceptual chapters (e.g. `Introduction`, `Character_Style_Codes`, `Range_Sets`, `Order_of_Fields`, `Summary_of_Fields`, `Sections_in_a_Lexical_Entry`) — verified live 2026-10-05
- 21 `\shd2` subsections, plus `\shd3` ×2, `\shd4` ×9, `\bib` ×4, `\nwt` ×2, `\_sh` ×1 header — verified live 2026-10-05
- A built-in home/TOC entry (`\key aa` → "Helps Database for MDF Marker Set") whose `\cf` links index every chapter — the source's own navigation model
- Hierarchy discussions (standard vs. alternate)
- 297 cross-reference fields (`\cf`), some naming multiple targets — verified live 2026-10-05
- 444 formatting/printing examples (`\ftx`/`\fxv`; 425 `\ftx` markers total, 11 empty)
- Character style codes, range sets, punctuation codes, printed field labels
- Old/changed markers
- Non-ASCII census (verified live 2026-10-05): 32 characters across 26 lines — á ×26, ñ ×3, • ×2 (U+2022, inside `\nwt` content), é ×1; no IPA symbols; zero ∞

## Recency Check
The source document `docs/mdf/MDFields19a_UTF8.txt` is now **committed and tracked** in the repository (verified live 2026-10-05: `git ls-files docs/mdf/MDFields19a_UTF8.txt` lists it and `git status --porcelain` is empty — it was untracked when earlier revisions were written and has since been committed). Before implementation, confirm the tracked copy is the current authoritative version and has not been superseded by a newer MDF release or a later revision. If the file has been modified or a newer MDF version exists, revise this spec before proceeding.

## Requirements

### SHALL Requirements
- **R-1.** The converter `scripts/convert_mdf_master.py` SHALL parse the marker types enumerated in the Approach section — `\key`, `\shd`, `\shd2`, `\shd3`, `\shd4`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`, `\bib`, `\nwt`, `\_sh` — from `docs/mdf/MDFields19a_UTF8.txt` into an intermediate JSON representation at `docs/mdf/build/master.json`.
- **R-2.** The converter SHALL preserve all 108 `\key` definitions, every cross-reference target named by the 297 `\cf` fields, and all 444 formatting/printing examples (`\ftx`/`\fxv`) through the parse → JSON → render pipeline.
- **R-3.** The LaTeX renderer SHALL emit `docs/mdf/build/master.tex` that compiles under XeLaTeX (`% !TEX program = xelatex`) with Unicode support via `fontspec`.
- **R-4.** The HTML renderer SHALL emit a multi-page static site under `docs/mdf/build/site/` with sidebar navigation, a client-side search index, deep-linking anchors, and hyperlinked cross-references.
- **R-5.** The build script `scripts/build_mdf_docs.sh` SHALL, when run with no arguments, invoke the converter and both renderers and produce `docs/mdf/build/mdf-lexical-fields-1.9a.pdf` and `docs/mdf/build/site/index.html` in a single invocation.
- **R-6.** The GitHub Actions workflow SHALL, on push to `main`, build both outputs and attach `mdf-lexical-fields-1.9a.pdf` to the release assets of the latest tag. The workflow SHALL NOT deploy to GitHub Pages.
- **R-7.** All generated output files SHALL be written under `docs/mdf/build/` and SHALL be committed and tracked in the repository for use as artifacts by downstream specs and by the in-app page.
- **R-8.** The converter SHALL fail fast with a clear error when the source contains zero `\key` entries, and SHALL NOT crash on malformed markers (MUST emit a warning and continue per the Edge Cases section).
- **R-9.** The app SHALL provide an "MDF Reference" page (navigation under the Main section) that renders all 108 keyed topics from `docs/mdf/build/master.json` natively in Streamlit: a chapter-grouped browser mirroring the source's hierarchy (17 chapter topics as groups, `\shd2` subsections nested, marker entries inside), an entry detail pane (heading, definition body, cross-reference links, formatting examples as code blocks, notes), the landing view being the source's home/TOC entry (`\key aa`), and deep-linking via query parameter (e.g. `?marker=ge`).
- **R-10.** The MDF Reference page SHALL provide a filter input performing case-insensitive, Unicode-preserving matching over topic keys and definition text. Ranked full-text search is out of scope (deferred to #1417).
- **R-11.** The app SHALL provide in-context reference hooks: (a) Direct Entry — a help affordance on each field entry linking to that marker's reference entry; (b) Records — marker tokens in rendered MDF blocks expose the marker's definition on interaction; (c) Upload MDF review — invalid/unknown-marker warnings link to that marker's reference entry.
- **R-12.** The MDF Reference page SHALL be readable by any authenticated user (viewer, editor, admin).
- **R-13.** The MDF Reference view SHALL offer the committed PDF as a download via a control placed in the page's left browser column, serving the filename required by R-14.
- **R-14.** The PDF deliverable SHALL be named `mdf-lexical-fields-1.9a.pdf` — matching the document's self-identification ("MDF Lexical Fields", draft v1.9a) and the repository's lowercase-hyphen file convention. The committed file, the release asset, and the in-app download SHALL all carry this name.
- **R-15.** The `SNEA_E2E=1` test-only authentication bypass SHALL support role selection (viewer, editor, admin) via a test-only mechanism honored exclusively when `SNEA_E2E=1` is set, so SC-10's per-role verification can produce real Playwright evidence. With `SNEA_E2E` unset, the production auth path SHALL remain byte-identical (same invariant as the established #1400 SC-11a bypass inertness).

### Output Formats
- **PDF**: Professional typeset reference via XeLaTeX (fonts: Noto Serif / Gentium), named `mdf-lexical-fields-1.9a.pdf`
- **HTML**: Multi-page static site with sidebar navigation, search, cross-reference hyperlinks (committed archival artifact, not deployed)
- **In-app page**: Native Streamlit rendering from `master.json` (see R-9)

### Conversion Approach
- Parse Toolbox markers — `\key`, `\shd`, `\shd2`, `\shd3`, `\shd4`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`, `\bib`, `\nwt`, `\_sh` — all line-initial markers present in the source
- Map to semantic structure: chapters (`\shd` + chapter-topic keys), subsections (`\shd2`–`\shd4`), definitions, examples, cross-refs, notes, bibliographic refs (`\bib`), non-word-table content (`\nwt`)
- Preserve all cross-reference targets (`\cf` → hyperlinks/links in all three surfaces)
- Preserve formatting examples (`\ftx`/`\fxv` → code blocks in HTML and in-app, `\texttt`/`verbatim` in LaTeX)

### Parsing Semantics (deterministic)
Grounded in the tracked format reference `docs/from-other-projects/SIL-Shoe-1.24/modules/Data.pm` (SIL's own Standard Format implementation; provenance in its `PROVENANCE.md`) and verified against a live census of the source file:

1. **Structural rule**: a line opens a field record if and only if, at byte offset 0 (no leading whitespace), it consists of `\` + exactly one whitelisted marker token followed by whitespace or end-of-line. The 14-marker whitelist is closed — census shows zero other offset-0 `\token` lines in the source. Per the reference implementation, SF markers cannot start with a space: marker-like text on indented lines is always content (all 3 indented `\cf` occurrences in the source are wrapped prose at lines 393/406 and a display row at line 2661, not fields).
2. **Tokenization**: the marker token is `\` followed by the first whitespace-delimited run of non-space characters; whitelist membership is exact-token equality. `\shd2` is a distinct token from `\shd` — naive prefix matching would mis-lex all 21 subsection headings.
3. **Continuations**: every other line (blank, indented, or not beginning with a whitelisted marker) is a continuation of the current field and is preserved as a raw line. Unlike the reference's default behavior (join multi-line fields with a space, strip edge whitespace — its `nostripnl`/`nostripws` opt-outs), this parser preserves content byte-for-byte; any joining or presentation decision belongs to renderers, never the parser.
4. **Content is never regex-processed**: no character-class, normalization, or stripping pattern touches field content. Marker-like text embedded in content — mid-line mentions and `\ftx`/`\fxv` example blocks containing whole lexical entries (`\lx`, `\sn`, `\ge`, …) — remains literal text.
5. **Unknown markers**: an offset-0 `\token` outside the whitelist is a malformed-marker line: emit a warning and treat it as continuation content (this defines the SC-13 malformed fixture).
6. **Line endings**: the source is LF-only with a final newline (verified 2026-10-05); lines are read as-is minus the line terminator.

### HTML Structure (archival, in-repo)
- Multi-page with sidebar navigation (one page per marker group)
- Client-side search using a pre-built JSON index queried by plain JavaScript (lunr.js, vendored and committed — no CDN)
- Deep-linking to individual markers (e.g., `#lx`, `#ge`)
- Responsive, printable via CSS `@media print`

### PDF Requirements
- XeLaTeX compilation (`% !TEX program = xelatex`)
- Unicode font support (ã, č, accented example words, any IPA the source contains)
- Professional typography: table of contents, index, hyperlinked cross-refs
- Page numbers, headers/footers
- Deliverable filename per R-14

## Preconditions
- The source file `docs/mdf/MDFields19a_UTF8.txt` is committed and tracked at `docs/mdf/` (verified live 2026-10-05)
- XeLaTeX and the required fonts are available in the build environment (CI runner or local)
- Python 3.12+ and the project's `uv` environment are available
- GitHub Actions is enabled for the repository (for SC-5)
- `docs/mdf/build/master.json` is committed and readable by the app runtime (for R-9)
- The `SNEA_E2E=1` bypass supports the role selection required by SC-10 (per R-15)

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Cost Frame |
|----|-----------|---------------|---------------------|------------|
| SC-1 | `xelatex master.tex` exits 0; the resulting PDF contains all 108 `\key` entries as rendered text, each with its definition body | `behavioral` | Run `xelatex master.tex` in CI; verify exit code 0; extract text from PDF with `pdftotext` and grep for all 108 `\key` values | Running the XeLaTeX compile and PDF text extraction costs minutes of CI execution time — a bounded delay that surfaces a missing-key defect before it reaches consumers. Skipping this verification means a PDF missing one or more of the 108 keys ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-2 | HTML site builds with exit code 0; every `\cf` cross-reference in the source renders as a hyperlink (`<a href="...">`) whose `href` value resolves to an existing anchor element on the target topic's page | `behavioral` | Run build; verify exit code 0; parse all HTML files with a script; confirm every `\cf` target has a corresponding anchor element | Running the HTML build and cross-reference resolution script costs minutes of execution time — a bounded delay that surfaces a broken-hyperlink defect before it reaches readers. Skipping this verification means a `\cf` cross-reference that resolves to a missing anchor ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-3 | All 108 `\key` topics are present in both PDF and HTML output, each reachable via a named anchor in both formats | `string + behavioral` | Grep PDF text for all 108 key values; grep HTML for all 108 anchor IDs; verify 1:1 match with source `\key` list | Running the grep-based 1:1 key-presence comparison costs seconds of execution time — a bounded delay that surfaces a missing-key defect before it reaches consumers. Skipping this verification means a key absent from the PDF or HTML ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-4 | A single `scripts/build_mdf_docs.sh` script, when run with no arguments, produces both `docs/mdf/build/mdf-lexical-fields-1.9a.pdf` and `docs/mdf/build/site/index.html` in a single invocation | `behavioral` | Run `scripts/build_mdf_docs.sh` in a clean checkout; verify both output files exist and are non-empty | Running the single-command build in a clean checkout costs minutes of execution time — a bounded delay that surfaces a broken build chain before it reaches consumers. Skipping this verification means a build script that fails to produce both outputs ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-5 | On push to `main`, a GitHub Actions workflow builds both outputs and attaches `mdf-lexical-fields-1.9a.pdf` to the release assets of the latest tag; no Pages deployment occurs | `behavioral` | Trigger a push to `main` on a test branch; verify the release tag has the correctly-named PDF asset attached; verify no Pages deployment is configured or triggered | Running the full CI + release cycle costs minutes of execution time — a bounded delay that surfaces a deploy or asset-attachment defect before it reaches readers. Skipping this verification means a workflow that fails to attach the PDF (or unexpectedly deploys Pages) ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-6 | All generated output files (`master.tex`, `mdf-lexical-fields-1.9a.pdf`, `master.json`, HTML site) are written to `docs/mdf/build/` and tracked in the repository for use as artifacts by downstream specs and the in-app page | `behavioral` | Run the build; verify `docs/mdf/build/master.tex`, `docs/mdf/build/mdf-lexical-fields-1.9a.pdf`, `docs/mdf/build/master.json`, and `docs/mdf/build/site/index.html` exist and are non-empty; verify each is tracked by `git ls-files docs/mdf/build/` | Running the build and git-tracking check costs minutes of execution time — a bounded delay that surfaces an artifact-tracking defect before it reaches downstream consumers. Skipping this verification means build artifacts that are not written to `docs/mdf/build/` or not tracked ship to production and cost 1000× more to fix. Correctness is the only metric. |
| SC-7 | The MDF Reference page renders all 108 keyed topics from `master.json`, grouped under the source's 17 chapter topics with `\shd2` subsections nested, and lands on the home/TOC entry (`\key aa`) by default | `behavioral` | Playwright against the live app: navigate to the page; assert all 108 topics are rendered; assert the 17 chapter groups are present; assert the landing entry is `aa` | Running the live-app page verification costs minutes of test execution time — a bounded delay that surfaces a missing-topic or broken-hierarchy defect before it reaches users. Skipping this verification means a reference page missing topics or mangling the source hierarchy ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-8 | Every cross-reference target named by the source's 297 `\cf` fields resolves to a rendered topic in the in-app page; cross-references to missing targets show a visible placeholder, not a dead link | `behavioral` | Script-enumerate every cross-reference target parsed from the 297 `\cf` fields in `master.json` and confirm each exists among the rendered topic keys; Playwright spot-checks in-app navigation for a sample of targets | Running the cross-reference resolution check costs minutes of execution time — a bounded delay that surfaces a dead-link defect before it reaches users. Skipping this verification means a `\cf` link that goes nowhere ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-9 | The filter matches topic keys and definition text case-insensitively and returns the expected subset; accented content present in the source (á, ñ, é) matches without normalization loss | `behavioral` | Playwright: enter known queries; assert expected result sets; include a query term containing an accented character from the source | Running the filter verification costs minutes of test execution time — a bounded delay that surfaces a broken-filter or normalization defect before it reaches users. Skipping this verification means a filter that silently drops accented content ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-10 | The MDF Reference page is reachable and readable by any authenticated user role (viewer, editor, admin) | `behavioral` | Playwright with role-variant authenticated sessions produced by the R-15 test-only role selection under `SNEA_E2E=1`; assert the page renders for each role; verify the bypass remains inert (production path byte-identical) with `SNEA_E2E` unset | Running the per-role verification costs minutes of test execution time — a bounded delay that surfaces a role-gating defect before it reaches users. Skipping this verification means a role wrongly excluded from reference material ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-11 | The PDF download control in the MDF view serves a file named `mdf-lexical-fields-1.9a.pdf` whose bytes are identical to the committed file | `string + behavioral` | Playwright: trigger the download; assert the served filename; checksum-compare against the committed `docs/mdf/build/mdf-lexical-fields-1.9a.pdf` | Running the download verification costs minutes of test execution time — a bounded delay that surfaces a wrong-file or corrupted-download defect before it reaches users. Skipping this verification means a download serving stale or wrongly-named content ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-12 | In-context hooks render on all three surfaces — Direct Entry (per-field help + reference expander), Records (marker-token definition on interaction), Upload MDF review (warning links) — each linking to the correct marker's entry | `behavioral` | Playwright: assert hook presence and correct link targets on each of the three surfaces | Running the three-surface hook verification costs minutes of test execution time — a bounded delay that surfaces a broken or misdirected help link before it reaches users. Skipping this verification means help affordances that link to the wrong marker (or don't render) ship to production and cost 1000× more to fix. Correctness is the only metric. |
| SC-13 | The converter exits non-zero with a clear error on a zero-`\key` source, and emits a warning while continuing on a malformed-marker fixture — a line starting at byte offset 0 with a `\token` outside the Parsing Semantics whitelist (e.g. `\zzz ...`) — without crashing | `behavioral` | Run the converter against an empty/marker-less fixture (assert non-zero exit + clear error) and against a malformed-marker fixture per the Parsing Semantics definition (assert warning emitted, exit 0, valid entries still parsed) | Running the two fixture conversions costs seconds of execution time — a bounded delay that surfaces a fail-fast or crash defect before it reaches consumers. Skipping this verification means a converter that silently emits empty output or crashes on malformed input ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-14 | All 444 formatting/printing examples (414 non-empty `\ftx` + 30 `\fxv`) are preserved through the pipeline — present in the PDF, the HTML site, and the in-app page | `behavioral` | Count example blocks in each rendered surface (pdftotext for the PDF; HTML parse for the site; rendered-page check for in-app) and verify 1:1 against the source's 444 | Running the example-count comparison costs minutes of execution time — a bounded delay that surfaces a dropped-content defect before it reaches consumers. Skipping this verification means a renderer silently dropping example content ships to production and costs 1000× more to fix. Correctness is the only metric. |

## Edge Cases
- **Empty or malformed marker**: A `\key` entry with no definition body, or a malformed marker line, must not crash the parser; the converter MUST emit a warning and continue the build without aborting
- **Cross-reference to a missing target**: A `\cf` pointing to a topic not present in the source must not produce a broken hyperlink; the renderer MUST emit a visible placeholder anchor and log a warning (both in HTML and in-app)
- **Unicode preservation**: Accented characters present in the source (á, ñ, é), the • bullets inside `\nwt` content, and any IPA/combining diacritics must survive the parse → JSON → render pipeline byte-for-byte (no normalization or stripping)
- **Empty source / zero markers**: If the source contains no `\key` entries, the build must fail fast with a clear error rather than emit empty output
- **Duplicate marker names**: A `\key` appearing more than once must not produce duplicate anchors that break deep-linking
- **Very long lines / large examples**: 444 formatting examples include long lines; the parser must handle them without truncation
- **Deep link to an unknown key**: A query parameter naming a non-existent topic (e.g. `?marker=zz`) MUST fall back to the home/TOC entry with a visible notice, not an error or blank pane
- **Filter with no matches**: An empty filter result MUST render the app's standard empty-state pattern (info banner), not a blank column
- **Missing build artifacts at runtime**: If `master.json` or the committed PDF is absent (build not yet run on a checkout), the page MUST show a clear actionable error, not crash the app

## Boundary Testing
- **All 108 keys present**: Verify the exact 1:1 count of `\key` entries between source, PDF, HTML, and in-app page (SC-3, SC-7)
- **All cross-reference targets resolved**: Verify every target parsed from the 297 `\cf` fields resolves on both the HTML site and the in-app page (SC-2, SC-8)
- **All 444 examples preserved**: Verify the formatting/printing example count is preserved through the pipeline (SC-14)
- **Hierarchy fidelity**: Verify 17 chapter topics and 21 `\shd2` subsections render as groups/subgroups (SC-7)
- **Landing entry**: Verify the default view is the home/TOC entry (`\key aa`) (SC-7)
- **Download identity**: Verify served filename and byte-identity of the PDF download (SC-11)
- **Empty-input boundary**: Confirm the converter fails fast on an empty or marker-less source (SC-13)
- **Malformed-marker boundary**: Confirm the converter warns and continues on a malformed-marker fixture (SC-13)
- **Single-marker boundary**: Confirm the pipeline works with a minimal one-marker source

## Enforcement Gate
This spec is enforced by the project's approval gate and verification-before-completion gates. Implementation may not begin until the spec is approved and a plan is created. Each SC must be verified by its declared verification method before the branch is considered complete; no SC may be skipped, weakened, deferred, or removed. Verification evidence must be produced per the declared evidence type for each SC.

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Items

### Item 1 (SC-1): XeLaTeX compilation with all 108 keys
- RED: `xelatex master.tex` fails or the extracted PDF text lacks one or more of the 108 `\key` values.
- GREEN: LaTeX renderer produces `docs/mdf/build/master.tex` that compiles cleanly and renders all 108 keys.
- verify: Run `xelatex master.tex` (exit 0); `pdftotext` and grep all 108 `\key` values.
- commit: `docs/mdf/build/master.tex`, `docs/mdf/build/mdf-lexical-fields-1.9a.pdf`.

### Item 2 (SC-2): HTML cross-reference hyperlink resolution
- RED: HTML build fails, or some `\cf` cross-reference lacks an `<a href>` resolving to an existing anchor.
- GREEN: HTML renderer emits multi-page site where every `\cf` target has a corresponding anchor.
- verify: Run build (exit 0); script parses all HTML files and confirms every `\cf` target resolves.
- commit: `docs/mdf/build/site/`.

### Item 3 (SC-3): 1:1 key presence across source, PDF, HTML
- RED: A `\key` value present in source is absent from the PDF or lacks an anchor in HTML.
- GREEN: All 108 keys appear in both outputs, each with a named anchor.
- verify: Grep PDF text for all 108 key values; grep HTML for all 108 anchor IDs; match 1:1 with source `\key` list.
- commit: `docs/mdf/build/master.tex`, `docs/mdf/build/mdf-lexical-fields-1.9a.pdf`, `docs/mdf/build/site/`.

### Item 4 (SC-4): Single-command build
- RED: `scripts/build_mdf_docs.sh` does not exist, or running it with no arguments does not produce both outputs.
- GREEN: Build script chains parser → LaTeX → HTML in one invocation producing `docs/mdf/build/mdf-lexical-fields-1.9a.pdf` and `docs/mdf/build/site/index.html`.
- verify: Run `scripts/build_mdf_docs.sh` in a clean checkout; confirm both outputs exist and are non-empty.
- commit: `scripts/build_mdf_docs.sh`.

### Item 5 (SC-5): CI/CD release asset attachment (no Pages)
- RED: No workflow runs, or the workflow fails to attach the correctly-named PDF to release assets, or it deploys Pages.
- GREEN: `.github/workflows/mdf-docs.yml` builds both outputs and attaches `mdf-lexical-fields-1.9a.pdf` to the latest release tag; no Pages deployment.
- verify: Trigger a push to `main` on a test branch; verify release tag has the correctly-named PDF asset; verify no Pages deployment.
- commit: `.github/workflows/mdf-docs.yml`.

### Item 6 (SC-6): Build artifacts written to `docs/mdf/build/` and tracked
- RED: Generated outputs are not written under `docs/mdf/build/`, or are written but not tracked by git.
- GREEN: All generated outputs land in `docs/mdf/build/` and are committed and tracked.
- verify: Run build; confirm `docs/mdf/build/master.tex`, `mdf-lexical-fields-1.9a.pdf`, `master.json`, `site/index.html` exist and are non-empty; `git ls-files docs/mdf/build/` lists them.
- commit: `docs/mdf/build/`.

### Item 7 (SC-7): In-app MDF Reference page — hierarchy and landing
- RED: The page does not exist, renders fewer than 108 topics, misses chapter groups, or lands on the wrong entry.
- GREEN: Page renders all 108 keyed topics grouped under the 17 chapter topics with `\shd2` subsections nested; landing view is `\key aa`.
- verify: Playwright against the live app: assert 108 topics, 17 chapter groups, landing entry `aa`.
- commit: `src/frontend/pages/mdf_reference.py`, `src/services/navigation_service.py`.

### Item 8 (SC-8): In-app cross-reference resolution
- RED: A `\cf` rendered in-app fails to navigate to its target topic, or a missing target produces a dead link.
- GREEN: Every `\cf` target resolves among rendered topics; missing targets show a visible placeholder.
- verify: Script-enumerate `\cf` targets from `master.json` against rendered topic keys; Playwright spot-checks navigation.
- commit: `src/frontend/pages/mdf_reference.py`.

### Item 9 (SC-9): Filter behavior (Unicode-preserving)
- RED: The filter misses known keys, matches wrongly, or drops accented content.
- GREEN: Case-insensitive matching over keys and definition text; accented source content (á, ñ, é) matches losslessly.
- verify: Playwright: known queries assert expected result sets, including an accented term.
- commit: `src/frontend/pages/mdf_reference.py`.

### Item 10 (SC-10): Any-authenticated-user visibility
- RED: A role (viewer/editor/admin) cannot reach or read the page.
- GREEN: Page renders for every authenticated role.
- verify: Playwright with role-variant authenticated sessions.
- commit: `src/services/navigation_service.py`, `src/frontend/pages/mdf_reference.py`.

### Item 11 (SC-11): PDF download in MDF view
- RED: No download control, wrong filename, or bytes differ from the committed file.
- GREEN: Download control in the left browser column serves `mdf-lexical-fields-1.9a.pdf` byte-identical to the committed file.
- verify: Playwright: trigger download; assert filename; checksum-compare.
- commit: `src/frontend/pages/mdf_reference.py`.

### Item 12 (SC-12): In-context hooks on three surfaces
- RED: Hooks missing or misdirected on any surface.
- GREEN: Direct Entry per-field help + expander, Records marker-token help, Upload review warning links — each targeting the correct marker entry.
- verify: Playwright: assert hook presence and link targets per surface.
- commit: `src/frontend/pages/direct_entry.py`, `src/frontend/pages/records.py`, `src/frontend/pages/upload_mdf.py`.

### Item 13 (SC-13): Converter fail-fast and warn-continue behavior
- RED: The converter exits 0 with empty output on a marker-less source, or crashes on a malformed-marker fixture.
- GREEN: Non-zero exit with a clear error on zero-`\key` source; warning + continued parse on malformed markers.
- verify: Run the converter against both fixtures; assert exit codes and warning emission.
- commit: `scripts/convert_mdf_master.py`.

### Item 14 (SC-14): 444 examples preserved across all surfaces
- RED: Any rendered surface (PDF, HTML, in-app) contains fewer than the source's 444 example blocks.
- GREEN: Example blocks render 1:1 in all three surfaces.
- verify: Count example blocks per surface and compare against the source's 444 (414 non-empty `\ftx` + 30 `\fxv`).
- commit: `docs/mdf/build/` artifacts, `src/frontend/pages/mdf_reference.py`.

## Implementation Phases

### Phase 1: Parser — Toolbox-to-JSON converter
- Implement `scripts/convert_mdf_master.py` with a parser for all line-initial markers present in the source: `\key`, `\shd`, `\shd2`, `\shd3`, `\shd4`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`, `\bib`, `\nwt`, `\_sh`
- Output: `docs/mdf/build/master.json` (intermediate representation)
- Verify: JSON contains all 108 keys (91 marker + 17 chapter topics), every target parsed from the 297 `\cf` fields, 444 examples, and the `\shd2`–`\shd4` hierarchy; SC-13 fixtures pass

### Phase 2: LaTeX renderer
- Implement LaTeX template rendering from the JSON intermediate representation
- Output: `docs/mdf/build/master.tex`
- Verify: `xelatex master.tex` compiles without errors; PDF contains all 108 keys

### Phase 3: HTML renderer
- Implement multi-page HTML site generation from the JSON intermediate representation
- Output: `docs/mdf/build/site/` (directory of HTML pages)
- Verify: all 108 keys have individual pages; all cross-reference targets are hyperlinks

### Phase 4: Build script and CI/CD
- Write `scripts/build_mdf_docs.sh` that chains parser → LaTeX → HTML, writing all outputs to `docs/mdf/build/`, emitting the PDF deliverable as `mdf-lexical-fields-1.9a.pdf`
- Write `.github/workflows/mdf-docs.yml` for release asset upload (no Pages deployment)
- Commit generated outputs (`docs/mdf/build/master.tex`, `docs/mdf/build/mdf-lexical-fields-1.9a.pdf`, `docs/mdf/build/master.json`, `docs/mdf/build/site/`) for artifact tracking
- Verify: single-command build produces both outputs; CI workflow attaches the PDF to release assets; all build artifacts are committed and tracked

### Phase 5: In-app MDF Reference page
- Implement `src/frontend/pages/mdf_reference.py` rendering all 108 keyed topics from `master.json`: chapter-grouped browser, entry detail pane, landing on `aa`, query-parameter deep-linking
- Add the navigation entry in `src/services/navigation_service.py` (Main section, visible to any authenticated user)
- Implement the Unicode-preserving filter and the PDF download control
- Extend the `SNEA_E2E=1` test-only bypass with role selection per R-15 (viewer/editor/admin), verifying production-path inertness with `SNEA_E2E` unset
- Verify: SC-7, SC-8, SC-9, SC-10, SC-11

### Phase 6: In-context hooks
- Direct Entry: per-field help affordance + collapsed reference expander
- Records: marker-token definition on interaction within rendered MDF blocks
- Upload MDF review: invalid/unknown-marker warnings link to the marker's entry
- Verify: SC-12

## Requirements → SCs → Phases Traceability

| Requirement | SCs | Phases |
|---|---|---|
| R-1 (parse markers to JSON) | SC-1, SC-2, SC-3, SC-13 | Phase 1 |
| R-2 (preserve keys/cross-refs/examples) | SC-1, SC-2, SC-3, SC-14 | Phase 1, Phase 2, Phase 3 |
| R-3 (XeLaTeX PDF) | SC-1 | Phase 2 |
| R-4 (multi-page HTML site) | SC-2, SC-3 | Phase 3 |
| R-5 (single-command build) | SC-4 | Phase 4 |
| R-6 (CI/CD release assets, no Pages) | SC-5 | Phase 4 |
| R-7 (artifacts tracked under `docs/mdf/build/`) | SC-6 | Phase 4 |
| R-8 (fail-fast on empty, no crash on malformed) | SC-13 | Phase 1 |
| R-9 (in-app MDF Reference page) | SC-7, SC-8 | Phase 5 |
| R-10 (Unicode-preserving filter) | SC-9 | Phase 5 |
| R-11 (in-context hooks, three surfaces) | SC-12 | Phase 6 |
| R-12 (any authenticated user) | SC-10 | Phase 5 |
| R-13 (PDF download in MDF view) | SC-11 | Phase 5 |
| R-14 (PDF named to match contents) | SC-4, SC-5, SC-11 | Phase 4, Phase 5 |
| R-15 (test-only E2E role selection) | SC-10 | Phase 5 |

## Root Cause → SC Traceability

| Root Cause | SCs |
|---|---|
| Source is not web-renderable or printable (marker-based format) | SC-1, SC-2, SC-3 |
| No automated conversion pipeline exists | SC-4 |
| Manual conversion infeasible at 3353 lines / 297 cross-reference fields | SC-1, SC-2, SC-3 |
| Outputs must be reproducible and attachable to releases | SC-5 |
| Outputs must be consumable as artifacts by downstream specs | SC-6 |
| Users need the reference in-app (self-contained), mirroring the source's structure | SC-7, SC-8 |
| Users need working lookup (filter) at the reference page | SC-9 |
| Every authenticated user needs the reference | SC-10 |
| Users need the PDF at hand, correctly named | SC-11, SC-4, SC-5 |
| Users need in-context help where markers are entered/edited | SC-12 |

## Affected Files
- New: `scripts/convert_mdf_master.py` (converter: parser + LaTeX renderer + HTML renderer)
- New: `scripts/build_mdf_docs.sh` (orchestration build script)
- New: `docs/mdf/build/master.tex` (LaTeX output, generated, tracked)
- New: `docs/mdf/build/mdf-lexical-fields-1.9a.pdf` (PDF deliverable, content-accurately named, generated, tracked)
- New: `docs/mdf/build/master.json` (intermediate representation, generated, tracked)
- New: `docs/mdf/build/site/` (HTML output directory, generated, tracked, archival)
- New: `.github/workflows/mdf-docs.yml` (CI workflow: release asset upload, no Pages)
- New: `src/frontend/pages/mdf_reference.py` (in-app MDF Reference page)
- Existing: `src/services/security_manager.py` (test-only E2E role-selection extension per R-15; production path unchanged)
- Existing: `src/services/navigation_service.py` (add MDF Reference nav entry)
- Existing: `src/frontend/pages/direct_entry.py` (per-field help affordance + expander)
- Existing: `src/frontend/pages/records.py` (marker-token help)
- Existing: `src/frontend/pages/upload_mdf.py` (review warning links)
- Existing: `docs/mdf/MDFields19a_UTF8.txt` (source, committed and tracked — verified live 2026-10-05)

## Type
SPEC (documentation conversion tooling + in-app reference integration)

---

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-07-26 | Added preamble sections (Intent, Root Cause, Approach, Alternatives, Key Decisions), evidence type column, verification methods, implementation phases, tightened SC wording | Spec audit returned DRAFT — 5 defects remediated | AI agent (spec-creation revise task) |
| 2026-07-26 | Corrected example count from 425 to 444 (414 `\ftx` + 30 `\fxv`); added Requirements→SCs→Phases traceability table | Validation: correctness (wrong count) + traceability (missing table) | AI agent (spec-creation revise task) |
| 2026-07-26 | Added SC-6 (build artifact tracking); updated all output paths from `docs/mdf/` to `docs/mdf/build/`; updated Affected Files, traceability table, and Phase 4 to reflect new paths and artifact commitment | Revision request: add SC-6 for artifact tracking, consolidate outputs under `docs/mdf/build/` | Developer (Michael Conrad) |
| 2026-07-27 | Corrected `\cf` cross-reference count from 297 to 315 (verified by `rg '\\cf' docs/mdf/MDFields19a_UTF8.txt | wc -l`); verified total `\ftx` marker count 425 (414 non-empty + 11 empty) is correct. Note: 425 is the total `\ftx` MARKER count (including 11 empty/whitespace-only markers); it is DISTINCT from the 444 formatting/printing EXAMPLES figure (414 non-empty `\ftx` + 30 `\fxv`) stated in the body. These measure different things and are not contradictory [ANNOTATED 2026-10-05: the 297→315 "correction" was ERRONEOUS — `rg '\cf' | wc -l` counts prose mentions and example content, not cross-reference fields; line-initial `\cf` count is 297. Corrected back in the 2026-10-05 audit entry below] | Revision request: fix incorrect count | Developer (Michael Conrad) |
| 2026-08-11 | Added User Intent / Original Prompt field, Dependencies section, Documentation Sources table, per-SC cost-frame column, Enforcement Gate statement, Edge Cases section, Recency Check, Preconditions, Boundary Testing, Root Cause → SC traceability; made SC-2 wording deterministic; removed prescriptive anchor code from SC-3; aligned SC-6 evidence type to `structural` | Spec audit FAILED with 16 criteria — 12 remediation findings addressed | AI agent (spec-creation revise task) |
| 2026-08-11 | Corrected 3 fabricated-provenance claims: `docs/mdf/MDFields19a_UTF8.txt` is UNTRACKED (`??`), not committed — updated Recency Check, Preconditions, Affected Files. Reconcile marker-type count to 8 (Phase 1). Aligned SC-6 evidence type `structural`→`behavioral` (criterion is artifact tracking, not file existence). Added Not Included section, numbered SHALL Requirements (R-1..R-8), per-SC Items (RED/GREEN/verify/commit), and per-SC cost-frame language. Made 3 discretion escape hatches deterministic (client-side search impl, malformed-marker handling, missing-target handling). Made font and CI dependencies explicit in Dependencies (Noto Serif, Gentium, xelatex, pdftotext availability requirements) | Spec re-audit returned DRAFT — 8/11 holistic dimensions FAIL (HOL-2, HOL-3, HOL-5, HOL-6, HOL-7, HOL-8); all 6 SCs and their intent preserved | AI agent (spec-creation revise task) |
| 2026-08-11 | Replaced each SC's Cost Frame column magnitude label (e.g., "Low — single CI job, ~1 min") with a canonical dark-prose-007 cost-frame statement: action cost (what implementing the verification costs) + skipping cost (what not implementing it costs) + identity anchor ("Correctness is the only metric"). All 6 SCs (SC-1..SC-6) and their intent preserved; no SC removed, weakened, deferred, or skipped | Spec re-audit returned FAIL on single criterion SC-13 (cost-frame): Cost Frame column contained only magnitude labels rather than the canonical dark-prose-007 action-cost + skipping-cost pattern required by cost-model-standards.md | AI agent (spec-creation revise task) |
| 2026-08-11 | Clarified the 2026-07-27 Change Control entry: 425 is the total `\ftx` MARKER count (414 non-empty + 11 empty markers), which is DISTINCT from the 444 formatting/printing EXAMPLES figure (414 non-empty `\ftx` + 30 `\fxv`). The two entries measure different quantities and are not contradictory. The 444 examples count in the body (lines: Intent, Source Document, R-2, Phase 1, Boundary Testing), SCs, and all 6 success criteria are unchanged. All 6 SCs and their intent preserved | Spec re-audit returned DRAFT on a single holistic dimension (Internal Consistency, HOL-2) due to an apparent example-count contradiction between the 444 examples figure and the 425 `\ftx` marker count in the Change Control log. Authoritative counts verified live against `docs/mdf/MDFields19a_UTF8.txt`: total `\ftx` 425, empty 11, non-empty 414, `\fxv` 30 | AI agent (spec-creation revise task) |
| 2026-10-05 | Redesigned outputs for in-app integration: added R-9..R-14 and SC-7..SC-12 (in-app "MDF Reference" page rendering natively from `master.json` with the source-mirroring chapter hierarchy — 17 chapter topics, 21 `\shd2` subsections, landing on home entry `aa`; Unicode-preserving filter; in-context hooks on Direct Entry/Records/Upload MDF; any-authenticated-user visibility; PDF download in the MDF view; PDF deliverable named `mdf-lexical-fields-1.9a.pdf` per the document's self-identification and repo naming convention). Amended R-6/SC-5: GitHub Pages deployment DROPPED (self-contained goal); HTML site retained as committed archival artifact with vendored lunr.js (no CDN). Added in-app edge cases (unknown deep-link key, empty filter result, missing artifacts at runtime). Ranked full-text search deferred to follow-up issue #1417 | Developer redesign direction: self-contained in-app reference, chapter-grouped layout mirroring source structure, PDF committed in-repo with download link in the MDF view, correctly-named PDF, search deferral | Developer (Michael Conrad) |
| 2026-10-05 | Spec audit remediation (9 defects): corrected `\cf` count 315→297 cross-reference fields (line-initial census; annotated the erroneous 2026-07-27 entry); corrected non-ASCII census 30→32 chars (• ×2 U+2022 inside `\nwt`, missed earlier); expanded parser enumeration to ALL line-initial markers present (\shd2/\shd3/\shd4/\bib/\nwt/\_sh) so R-9/SC-7's hierarchy is producible and `\nwt` content survives; updated stale untracked claims (file is committed/tracked); added SC-13 (R-8 fail-fast/warn-continue verification) and SC-14 (R-2 444-example preservation, previously unverified); added R-15 (test-only E2E role selection) making SC-10's per-role Playwright method feasible — bypass currently resolves to admin only; corrected file size 133KB→130KB (130,520 bytes) | Spec audit returned FAIL — 8 defects in #1379 + 1 in #1417; all remediated with live verification | AI agent (audit remediation, authorized by developer's `audit` dispatch) |
| 2026-10-05 | Added deterministic Parsing Semantics subsection (line-anchored whitelist grammar: offset-0 structural markers, exact-token matching so \shd2 ≠ \shd, raw-line continuation preservation, content never regex-processed, unknown-marker fixture definition, LF-only source) — grounded in the newly vendored tracked format reference `docs/from-other-projects/SIL-Shoe-1.24/` (SIL's own SF implementation, curated subset, provenance + SHA-256 recorded; no explicit upstream license — reference-only, nothing imports it); added it to Documentation Sources; anchored SC-13's malformed fixture to the Parsing Semantics definition; verified live: 13/14 markers occur exclusively at offset 0, all 3 indented `\cf` occurrences are content (prose lines 393/406, display row 2661), zero non-whitelist offset-0 tokens, LF-only line endings | Developer direction: add parsing semantics from the line-based analysis; use SIL-Shoe source as the format reference and vendor it as a tracked repo resource | Developer (Michael Conrad) |
