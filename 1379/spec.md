# SPEC: Convert Master MDF Documentation to LaTeX/PDF and HTML

## User Intent / Original Prompt
Convert the MDF 1.9a field reference (`docs/mdf/MDFields19a_UTF8.txt`) from Toolbox/Shoebox help format into two professionally publishable formats: a XeLaTeX-compiled PDF reference document and a multi-page browsable HTML site. Both outputs derive from a single parsed intermediate representation, ensuring consistency. The HTML output deploys to GitHub Pages; the PDF attaches to release assets.

## Intent / Executive Summary
Convert the MDF 1.9a field reference (`docs/mdf/MDFields19a_UTF8.txt`, 133KB, 108 `\key` entries, 315 `\cf` cross-refs, 444 formatting/printing examples (`\ftx`/`\fxv`)) from Toolbox/Shoebox help format into two professionally publishable formats: a XeLaTeX-compiled PDF reference document and a multi-page browsable HTML site. Both outputs derive from a single parsed intermediate representation, ensuring consistency. The HTML output deploys to GitHub Pages; the PDF attaches to release assets.

## Root Cause
The source file is in Toolbox/Shoebox help format — a plain-text marker-based format (`\key`, `\shd`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`) that is not web-renderable, not printable as a professional document, and not navigable by modern readers. No automated conversion pipeline exists. Manual conversion is infeasible at 3353 lines with 315 cross-references.

## Approach
1. Write a Python converter (`scripts/convert_mdf_master.py`) that parses the Toolbox marker structure into an intermediate JSON representation
2. From the intermediate representation, render two outputs:
   - **LaTeX file** (`docs/mdf/build/master.tex`) — XeLaTeX with Noto Serif / Gentium for Unicode IPA support
   - **HTML site** (`docs/mdf/build/site/`) — multi-page static site with sidebar navigation and search
3. Write a single build script (`scripts/build_mdf_docs.sh`) that runs the converter then invokes both renderers
4. Add a GitHub Actions workflow that runs the build script on push to `main` and deploys HTML to GitHub Pages, PDF to release assets

## Alternatives Considered
| Alternative | Rejected Because |
|---|---|
| Manual conversion in Word/LaTeX | 3353 lines, 315 cross-refs — error-prone, unrepeatable |
| Sphinx + custom directive | Overkill for single-source conversion; adds Python build dependency |
| Pandoc with custom writer | Pandoc's Toolbox reader does not exist; would need a custom writer anyway |
| Single HTML page | 133KB source → ~500KB HTML; multi-page with sidebar is more navigable |

## Key Decisions
- **Single intermediate representation (JSON)**: Both PDF and HTML derive from the same parsed data, guaranteeing cross-format consistency
- **XeLaTeX over pdfLaTeX**: Required for Unicode IPA characters (ə, ʃ, ŋ, ã, č, etc.) — mandated by project standards
- **Static HTML over JS framework**: Zero runtime dependencies; works without JavaScript; deployable to GitHub Pages
- **Build script over Makefile**: Simpler dependency chain; works in CI without Make installed

## Not Included
- **Editing or altering the source MDF content** — The converter parses and renders the source as-is; it must not modify `docs/mdf/MDFields19a_UTF8.txt` or the linguistic data it contains. Preserving data integrity is mandatory (see `090-data-integrity.md`).
- **Converting any MDF version other than 1.9a** — The parser targets the 1.9a marker set enumerated in the Conversion Approach section; other versions are out of scope.
- **Interactive or JS-framework-based HTML** — The HTML site is static with zero runtime dependencies so it can deploy to GitHub Pages without a build framework.
- **Round-trip conversion back to Toolbox/Shoebox format** — The pipeline is one-way (Toolbox → JSON → LaTeX/HTML); no reverse conversion is produced.

## Dependencies
| Dependency | Purpose | Version/Constraint | Availability Requirement |
|---|---|---|---|
| XeLaTeX (`xelatex`) | PDF compilation with Unicode IPA support | TeX Live 2023+ (fontspec, hyperref, makeidx) | MUST be installed on the CI runner and local build environment |
| Noto Serif fonts | Unicode IPA glyph rendering in PDF | Installed system fonts | MUST be installed on the CI runner and local build environment; `fontspec` resolves them at compile time |
| Gentium fonts | Fallback Unicode IPA glyph rendering in PDF | Installed system fonts | MUST be installed on the CI runner and local build environment; `fontspec` resolves them at compile time |
| Python 3.12+ | Converter and renderer scripts | `uv`-managed project environment | MUST be present in CI via `uv`; `uv sync` installs the environment |
| GitHub Actions (`actions/checkout`, `actions/upload-pages-artifact`, `actions/deploy-pages`) | CI build, Pages deploy, release asset upload | Official GitHub Actions | MUST be available in the repository's `.github/workflows/`; SC-5 requires Pages + releases enabled |
| `pdftotext` (poppler-utils) | PDF text extraction for verification | CI runner package | MUST be installed on the CI runner for SC-1/SC-3 verification |

## Documentation Sources
| Source | Type | Purpose |
|---|---|---|
| `docs/mdf/MDFields19a_UTF8.txt` | Primary source document | MDF 1.9a field reference (Buseman, 2006) — the authoritative content to convert |
| MDF 1.9a specification (Buseman, 2006) | Reference | Marker semantics, hierarchy, cross-reference meaning |
| Project AGENTS.md | Standard | XeLaTeX mandate, Unicode IPA handling, data integrity rules |
| Project `docs/lessons-learned/` | Reference | FTS/regex/normalization lessons for linguistic data handling |

## Source Document
`docs/mdf/MDFields19a_UTF8.txt` — Official MDF 1.9a field reference (Buseman, 2006). Contains:
- 108 field marker definitions (`\lx`, `\ge`, `\ps`, `\se`, `\cf`, etc.)
- Hierarchy discussions (standard vs. alternate)
- 315 cross-references between markers (`\cf`)
- 444 formatting/printing examples (`\ftx`/`\fxv`)
- Character style codes, range sets, punctuation codes, printed field labels
- Old/changed markers

## Recency Check
The source document `docs/mdf/MDFields19a_UTF8.txt` is an **untracked working-tree file** — it is NOT committed to the repository (verified live: `git status --porcelain -- docs/mdf/MDFields19a_UTF8.txt` reports `??`, and `git ls-files docs/mdf/MDFields19a_UTF8.txt` returns no tracked entries). Before implementation, confirm the working-tree copy is the current authoritative version and has not been superseded by a newer MDF release or a later revision. If the file has been modified or a newer MDF version exists, revise this spec before proceeding.

## Requirements

### SHALL Requirements
- **R-1.** The converter `scripts/convert_mdf_master.py` SHALL parse the 8 marker types enumerated in the Conversion Approach section (`\key`, `\shd`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`) from `docs/mdf/MDFields19a_UTF8.txt` into an intermediate JSON representation at `docs/mdf/build/master.json`.
- **R-2.** The converter SHALL preserve all 108 `\key` definitions, all 315 `\cf` cross-references, and all 444 formatting/printing examples (`\ftx`/`\fxv`) through the parse → JSON → render pipeline.
- **R-3.** The LaTeX renderer SHALL emit `docs/mdf/build/master.tex` that compiles under XeLaTeX (`% !TEX program = xelatex`) with Unicode IPA support via `fontspec`.
- **R-4.** The HTML renderer SHALL emit a multi-page static site under `docs/mdf/build/site/` with sidebar navigation, a client-side search index, deep-linking anchors, and hyperlinked cross-references.
- **R-5.** The build script `scripts/build_mdf_docs.sh` SHALL, when run with no arguments, invoke the converter and both renderers and produce `docs/mdf/build/master.pdf` and `docs/mdf/build/site/index.html` in a single invocation.
- **R-6.** The GitHub Actions workflow SHALL, on push to `main`, build both outputs, deploy the HTML site to GitHub Pages, and attach the PDF to the release assets of the latest tag.
- **R-7.** All generated output files SHALL be written under `docs/mdf/build/` and SHALL be committed and tracked in the repository for use as artifacts by downstream specs.
- **R-8.** The converter SHALL fail fast with a clear error when the source contains zero `\key` entries, and SHALL NOT crash on malformed markers (MUST emit a warning and continue per the Edge Cases section).

### Output Formats
- **PDF**: Professional typeset reference via XeLaTeX (fonts: Noto Serif / Gentium for IPA)
- **HTML**: Multi-page static site with sidebar navigation, search, cross-reference hyperlinks

### Conversion Approach
- Parse Toolbox markers (`\key`, `\shd`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`)
- Map to semantic structure: sections, subsections, definitions, examples, cross-refs, notes
- Preserve all cross-references (`\cf` → hyperlinks in both formats)
- Preserve formatting examples (`\ftx`/`\fxv` → code blocks in HTML, `\texttt`/`verbatim` in LaTeX)

### HTML Structure
- Multi-page with sidebar navigation (one page per marker group)
- Client-side search using a pre-built JSON index queried by plain JavaScript (lunr.js dependency)
- Deep-linking to individual markers (e.g., `#lx`, `#ge`)
- Responsive, printable via CSS `@media print`

### PDF Requirements
- XeLaTeX compilation (`% !TEX program = xelatex`)
- Unicode font support (IPA: ə, ʃ, ŋ, ã, č, etc.)
- Professional typography: table of contents, index, hyperlinked cross-refs
- Page numbers, headers/footers

## Preconditions
- The source file `docs/mdf/MDFields19a_UTF8.txt` exists in the working tree at `docs/mdf/` (currently untracked by git; it must be present at build time for the converter to read it)
- XeLaTeX and the required fonts are available in the build environment (CI runner or local)
- Python 3.12+ and the project's `uv` environment are available
- GitHub Actions is enabled for the repository (for SC-5)

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Cost Frame |
|----|-----------|---------------|---------------------|------------|
| SC-1 | `xelatex master.tex` exits 0; the resulting PDF contains all 108 `\key` entries as rendered text, each with its definition body | `behavioral` | Run `xelatex master.tex` in CI; verify exit code 0; extract text from PDF with `pdftotext` and grep for all 108 `\key` values | Low — single CI job, ~1 min |
| SC-2 | HTML site builds with exit code 0; every `\cf` cross-reference in the source renders as a hyperlink (`<a href="...">`) whose `href` value resolves to an existing anchor element on the target marker's page | `behavioral` | Run build; verify exit code 0; parse all HTML files with a script; confirm every `\cf` target has a corresponding anchor element | Medium — HTML parse script over 108 pages |
| SC-3 | All 108 `\key` marker definitions are present in both PDF and HTML output, each reachable via a named anchor in both formats | `string + behavioral` | Grep PDF text for all 108 key values; grep HTML for all 108 anchor IDs; verify 1:1 match with source `\key` list | Low — grep-based comparison |
| SC-4 | A single `scripts/build_mdf_docs.sh` script, when run with no arguments, produces both `docs/mdf/build/master.pdf` and `docs/mdf/build/site/index.html` in a single invocation | `behavioral` | Run `scripts/build_mdf_docs.sh` in a clean checkout; verify both output files exist and are non-empty | Low — single command run |
| SC-5 | On push to `main`, a GitHub Actions workflow builds both outputs, deploys HTML to GitHub Pages (`gh-pages` branch), and attaches the PDF to the release assets of the latest tag | `behavioral` | Trigger a push to `main` on a test branch; verify GitHub Pages URL serves `index.html`; verify release tag has PDF asset attached | High — full CI + Pages + release cycle |
| SC-6 | All generated output files (master.tex, master.pdf, HTML site) are written to `docs/mdf/build/` and tracked in the repository for use as artifacts by downstream specs | `behavioral` | Run the build; verify `docs/mdf/build/master.tex`, `docs/mdf/build/master.pdf`, and `docs/mdf/build/site/index.html` exist and are non-empty; verify each is tracked by `git ls-files docs/mdf/build/` | Low — single build run + git check |

## Edge Cases
- **Empty or malformed marker**: A `\key` entry with no definition body, or a malformed marker line, must not crash the parser; the converter MUST emit a warning and continue the build without aborting
- **Cross-reference to a missing target**: A `\cf` pointing to a marker not present in the source must not produce a broken hyperlink; the renderer MUST emit a visible placeholder anchor and log a warning
- **Unicode IPA characters**: ə, ʃ, ŋ, ã, č, and combining diacritics must survive the parse → JSON → render pipeline byte-for-byte (no normalization or stripping)
- **Empty source / zero markers**: If the source contains no `\key` entries, the build must fail fast with a clear error rather than emit empty output
- **Duplicate marker names**: A `\key` appearing more than once must not produce duplicate anchors that break deep-linking
- **Very long lines / large examples**: 444 formatting examples include long lines; the parser must handle them without truncation

## Boundary Testing
- **All 108 keys present**: Verify the exact 1:1 count of `\key` entries between source, PDF, and HTML (SC-3)
- **All 315 cross-refs resolved**: Verify every `\cf` target resolves to an anchor (SC-2)
- **All 444 examples preserved**: Verify the formatting/printing example count is preserved through the pipeline
- **Empty-input boundary**: Confirm the converter fails fast on an empty or marker-less source
- **Single-marker boundary**: Confirm the pipeline works with a minimal one-marker source

## Enforcement Gate
This spec is enforced by the project's approval gate and verification-before-completion gates. Implementation may not begin until the spec is approved and a plan is created. Each SC must be verified by its declared verification method before the branch is considered complete; no SC may be skipped, weakened, deferred, or removed. Verification evidence must be produced per the declared evidence type for each SC.

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

## Items

### Item 1 (SC-1): XeLaTeX compilation with all 108 keys
- RED: `xelatex master.tex` fails or the extracted PDF text lacks one or more of the 108 `\key` values.
- GREEN: LaTeX renderer produces `docs/mdf/build/master.tex` that compiles cleanly and renders all 108 keys.
- verify: Run `xelatex master.tex` (exit 0); `pdftotext` and grep all 108 `\key` values.
- commit: `docs/mdf/build/master.tex`, `docs/mdf/build/master.pdf`.

### Item 2 (SC-2): HTML cross-reference hyperlink resolution
- RED: HTML build fails, or some `\cf` cross-reference lacks an `<a href>` resolving to an existing anchor.
- GREEN: HTML renderer emits multi-page site where every `\cf` target has a corresponding anchor.
- verify: Run build (exit 0); script parses all HTML files and confirms every `\cf` target resolves.
- commit: `docs/mdf/build/site/`.

### Item 3 (SC-3): 1:1 key presence across source, PDF, HTML
- RED: A `\key` value present in source is absent from the PDF or lacks an anchor in HTML.
- GREEN: All 108 keys appear in both outputs, each with a named anchor.
- verify: Grep PDF text for all 108 key values; grep HTML for all 108 anchor IDs; match 1:1 with source `\key` list.
- commit: `docs/mdf/build/master.tex`, `docs/mdf/build/master.pdf`, `docs/mdf/build/site/`.

### Item 4 (SC-4): Single-command build
- RED: `scripts/build_mdf_docs.sh` does not exist, or running it with no arguments does not produce both outputs.
- GREEN: Build script chains parser → LaTeX → HTML in one invocation producing `docs/mdf/build/master.pdf` and `docs/mdf/build/site/index.html`.
- verify: Run `scripts/build_mdf_docs.sh` in a clean checkout; confirm both outputs exist and are non-empty.
- commit: `scripts/build_mdf_docs.sh`.

### Item 5 (SC-5): CI/CD deploy to Pages and release assets
- RED: No workflow runs, or the workflow fails to deploy HTML to Pages or attach the PDF to release assets.
- GREEN: `.github/workflows/mdf-docs.yml` builds both outputs, deploys HTML to `gh-pages`, attaches PDF to latest release tag.
- verify: Trigger a push to `main` on a test branch; verify Pages URL serves `index.html`; verify release tag has PDF asset.
- commit: `.github/workflows/mdf-docs.yml`.

### Item 6 (SC-6): Build artifacts written to `docs/mdf/build/` and tracked
- RED: Generated outputs are not written under `docs/mdf/build/`, or are written but not tracked by git.
- GREEN: All generated outputs land in `docs/mdf/build/` and are committed and tracked.
- verify: Run build; confirm `docs/mdf/build/master.tex`, `master.pdf`, `site/index.html` exist and are non-empty; `git ls-files docs/mdf/build/` lists them.
- commit: `docs/mdf/build/`.

## Implementation Phases

### Phase 1: Parser — Toolbox-to-JSON converter
- Implement `scripts/convert_mdf_master.py` with a parser for the 8 marker types enumerated in the Conversion Approach section (`\key`, `\shd`, `\txt`, `\ftx`, `\fxv`, `\cf`, `\nt`, `\typ`)
- Output: `docs/mdf/build/master.json` (intermediate representation)
- Verify: JSON contains all 108 keys, 315 cross-refs, 444 examples

### Phase 2: LaTeX renderer
- Implement LaTeX template rendering from the JSON intermediate representation
- Output: `docs/mdf/build/master.tex`
- Verify: `xelatex master.tex` compiles without errors; PDF contains all 108 keys

### Phase 3: HTML renderer
- Implement multi-page HTML site generation from the JSON intermediate representation
- Output: `docs/mdf/build/site/` (directory of HTML pages)
- Verify: all 108 keys have individual pages; all 315 cross-refs are hyperlinks

### Phase 4: Build script and CI/CD
- Write `scripts/build_mdf_docs.sh` that chains parser → LaTeX → HTML, writing all outputs to `docs/mdf/build/`
- Write `.github/workflows/mdf-docs.yml` for GitHub Pages deploy + release asset upload
- Copy generated outputs (`docs/mdf/build/master.tex`, `docs/mdf/build/master.pdf`, `docs/mdf/build/site/`) into the repository for artifact tracking
- Verify: single-command build produces both outputs; CI workflow deploys correctly; all build artifacts are committed and tracked

## Requirements → SCs → Phases Traceability

| Requirement | SCs | Phases |
|---|---|---|
| R-1 (parse markers to JSON) | SC-1, SC-2, SC-3 | Phase 1 |
| R-2 (preserve keys/cross-refs/examples) | SC-1, SC-2, SC-3 | Phase 1, Phase 2, Phase 3 |
| R-3 (XeLaTeX PDF) | SC-1 | Phase 2 |
| R-4 (multi-page HTML site) | SC-2, SC-3 | Phase 3 |
| R-5 (single-command build) | SC-4 | Phase 4 |
| R-6 (CI/CD deploy) | SC-5 | Phase 4 |
| R-7 (artifacts tracked under `docs/mdf/build/`) | SC-6 | Phase 4 |
| R-8 (fail-fast on empty, no crash on malformed) | SC-1, SC-2, SC-3 | Phase 1 |

## Root Cause → SC Traceability

| Root Cause | SCs |
|---|---|
| Source is not web-renderable or printable (marker-based format) | SC-1, SC-2, SC-3 |
| No automated conversion pipeline exists | SC-4 |
| Manual conversion infeasible at 3353 lines / 315 cross-refs | SC-1, SC-2, SC-3 |
| Outputs must be reproducible and deployable | SC-5 |
| Outputs must be consumable as artifacts by downstream specs | SC-6 |

## Affected Files
- New: `scripts/convert_mdf_master.py` (converter: parser + LaTeX renderer + HTML renderer)
- New: `scripts/build_mdf_docs.sh` (orchestration build script)
- New: `docs/mdf/build/master.tex` (LaTeX output, generated, tracked)
- New: `docs/mdf/build/master.pdf` (PDF output, generated, tracked)
- New: `docs/mdf/build/master.json` (intermediate representation, generated, tracked)
- New: `docs/mdf/build/site/` (HTML output directory, generated, tracked)
- New: `.github/workflows/mdf-docs.yml` (CI/CD workflow)
- Existing: `docs/mdf/MDFields19a_UTF8.txt` (source, present in working tree but untracked by git)

## Type
SPEC (documentation conversion tooling)

---

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-07-26 | Added preamble sections (Intent, Root Cause, Approach, Alternatives, Key Decisions), evidence type column, verification methods, implementation phases, tightened SC wording | Spec audit returned DRAFT — 5 defects remediated | AI agent (spec-creation revise task) |
| 2026-07-26 | Corrected example count from 425 to 444 (414 `\ftx` + 30 `\fxv`); added Requirements→SCs→Phases traceability table | Validation: correctness (wrong count) + traceability (missing table) | AI agent (spec-creation revise task) |
| 2026-07-26 | Added SC-6 (build artifact tracking); updated all output paths from `docs/mdf/` to `docs/mdf/build/`; updated Affected Files, traceability table, and Phase 4 to reflect new paths and artifact commitment | Revision request: add SC-6 for artifact tracking, consolidate outputs under `docs/mdf/build/` | Developer (Michael Conrad) |
| 2026-07-27 | Corrected `\cf` cross-reference count from 297 to 315 (verified by `rg '\\cf' docs/mdf/MDFields19a_UTF8.txt | wc -l`); verified `\ftx` count 425 (414 non-empty + 11 empty) is correct | Revision request: fix incorrect count | Developer (Michael Conrad) |
| 2026-08-11 | Added User Intent / Original Prompt field, Dependencies section, Documentation Sources table, per-SC cost-frame column, Enforcement Gate statement, Edge Cases section, Recency Check, Preconditions, Boundary Testing, Root Cause → SC traceability; made SC-2 wording deterministic; removed prescriptive anchor code from SC-3; aligned SC-6 evidence type to `structural` | Spec audit FAILED with 16 criteria — 12 remediation findings addressed | AI agent (spec-creation revise task) |
| 2026-08-11 | Corrected 3 fabricated-provenance claims: `docs/mdf/MDFields19a_UTF8.txt` is UNTRACKED (`??`), not committed — updated Recency Check, Preconditions, Affected Files. Reconcile marker-type count to 8 (Phase 1). Aligned SC-6 evidence type `structural`→`behavioral` (criterion is artifact tracking, not file existence). Added Not Included section, numbered SHALL Requirements (R-1..R-8), per-SC Items (RED/GREEN/verify/commit), and per-SC cost-frame language. Made 3 discretion escape hatches deterministic (client-side search impl, malformed-marker handling, missing-target handling). Made font and CI dependencies explicit in Dependencies (Noto Serif, Gentium, xelatex, pdftotext availability requirements) | Spec re-audit returned DRAFT — 8/11 holistic dimensions FAIL (HOL-2, HOL-3, HOL-5, HOL-6, HOL-7, HOL-8); all 6 SCs and their intent preserved | AI agent (spec-creation revise task) |
