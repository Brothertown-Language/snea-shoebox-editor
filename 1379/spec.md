# SPEC: Convert Master MDF Documentation to LaTeX/PDF and HTML

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

## Source Document
`docs/mdf/MDFields19a_UTF8.txt` — Official MDF 1.9a field reference (Buseman, 2006). Contains:
- 108 field marker definitions (`\lx`, `\ge`, `\ps`, `\se`, `\cf`, etc.)
- Hierarchy discussions (standard vs. alternate)
- 315 cross-references between markers (`\cf`)
- 444 formatting/printing examples (`\ftx`/`\fxv`)
- Character style codes, range sets, punctuation codes, printed field labels
- Old/changed markers

## Requirements

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
- Client-side search (lunr.js or plain JS index)
- Deep-linking to individual markers (e.g., `#lx`, `#ge`)
- Responsive, printable via CSS `@media print`

### PDF Requirements
- XeLaTeX compilation (`% !TEX program = xelatex`)
- Unicode font support (IPA: ə, ʃ, ŋ, ã, č, etc.)
- Professional typography: table of contents, index, hyperlinked cross-refs
- Page numbers, headers/footers

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method |
|----|-----------|---------------|---------------------|
| SC-1 | `xelatex master.tex` exits 0; the resulting PDF contains all 108 `\key` entries as rendered text, each with its definition body | `behavioral` | Run `xelatex master.tex` in CI; verify exit code 0; extract text from PDF with `pdftotext` and grep for all 108 `\key` values |
| SC-2 | HTML site builds without errors; every `\cf` cross-reference in the source renders as a working hyperlink (`<a href="...">`) that navigates to the target marker's page | `behavioral` | Run build; verify exit code 0; parse all HTML files with a script; confirm every `\cf` target has a corresponding anchor element |
| SC-3 | All 108 `\key` marker definitions are present in both PDF and HTML output, each reachable via a named anchor (`\label{key:lx}` in LaTeX, `<a id="lx">` in HTML) | `string + behavioral` | Grep PDF text for all 108 key values; grep HTML for all 108 anchor IDs; verify 1:1 match with source `\key` list |
| SC-4 | A single `scripts/build_mdf_docs.sh` script, when run with no arguments, produces both `docs/mdf/build/master.pdf` and `docs/mdf/build/site/index.html` in a single invocation | `behavioral` | Run `scripts/build_mdf_docs.sh` in a clean checkout; verify both output files exist and are non-empty |
| SC-5 | On push to `main`, a GitHub Actions workflow builds both outputs, deploys HTML to GitHub Pages (`gh-pages` branch), and attaches the PDF to the release assets of the latest tag | `behavioral` | Trigger a push to `main` on a test branch; verify GitHub Pages URL serves `index.html`; verify release tag has PDF asset attached |
| SC-6 | All generated output files (master.tex, master.pdf, HTML site) are written to `docs/mdf/build/` and tracked in the repository for use as artifacts by downstream specs | `string` | `ls docs/mdf/build/master.tex && ls docs/mdf/build/master.pdf && ls docs/mdf/build/site/index.html` |

## Implementation Phases

### Phase 1: Parser — Toolbox-to-JSON converter
- Implement `scripts/convert_mdf_master.py` with a parser for all 9 marker types
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
| Output Formats (PDF + HTML) | SC-1, SC-2, SC-3 | Phase 2, Phase 3 |
| Conversion Approach (parse markers, preserve cross-refs/examples) | SC-1, SC-2, SC-3 | Phase 1, Phase 2, Phase 3 |
| HTML Structure (multi-page, search, deep-linking) | SC-2 | Phase 3 |
| PDF Requirements (XeLaTeX, Unicode, typography) | SC-1 | Phase 2 |
| Single-command build | SC-4 | Phase 4 |
| CI/CD deployment (GitHub Pages + release assets) | SC-5 | Phase 4 |
| Build artifact tracking (committed outputs for downstream specs) | SC-6 | Phase 4 |

## Affected Files
- New: `scripts/convert_mdf_master.py` (converter: parser + LaTeX renderer + HTML renderer)
- New: `scripts/build_mdf_docs.sh` (orchestration build script)
- New: `docs/mdf/build/master.tex` (LaTeX output, generated, tracked)
- New: `docs/mdf/build/master.pdf` (PDF output, generated, tracked)
- New: `docs/mdf/build/master.json` (intermediate representation, generated, tracked)
- New: `docs/mdf/build/site/` (HTML output directory, generated, tracked)
- New: `.github/workflows/mdf-docs.yml` (CI/CD workflow)
- Existing: `docs/mdf/MDFields19a_UTF8.txt` (source, already committed)

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
