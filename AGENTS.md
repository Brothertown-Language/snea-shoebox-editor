# AGENTS.md — Repository Guidelines for Coding Agents

## Linguistic Data Requirements

This project handles **Southern New England Algonquian (SNEA)** linguistic data. Agents MUST understand these constraints:

### Unicode & Character Handling
- **Unicode IPA characters** (ə, ʃ, tʃ, ŋ, ã, č, etc.) are first-class data — never normalize or strip
- **Unicode diacritics and combining characters** must be preserved exactly
- **Direct Unicode input** — no \-escape sequences in source data
- **fontspec** for OpenType font selection in LaTeX builds

### XeLaTeX Requirement
All `.tex` files MUST use modern UTF-8 XeLaTeX (`xelatex`), not legacy `pdflatex`. This is non-negotiable because linguistic data requires:
- Unicode IPA characters
- Unicode diacritics and combining characters
- Direct Unicode input without \-escape sequences
- fontspec for OpenType font selection

Every `.tex` file MUST begin with:
```
% !TEX program = xelatex
% !TEX encoding = UTF-8 Unicode
```

### Cross-Reference: Lessons Learned
Before making changes to search infrastructure, text normalization, FTS configuration, or regex processing linguistic data, consult `docs/lessons-learned/`:

| File | Topic |
|------|-------|
| `docs/lessons-learned/index.md` | Entry catalog with cross-references |
| `docs/lessons-learned/2026-06-13-postgres-fts-algonquian.md` | Why 'english' tsconfig corrupts Algonquian search |
| `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | ASCII-based regex destroys linguistic data |
| `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | ∞ is a valid letter, maps to oozzz |
| `docs/lessons-learned/2026-06-13-simple-vs-english-tsconfig.md` | Live PG verification evidence |
| `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` | Local PostgreSQL instance management and query patterns |

### Data Integrity — NO SYNTHETIC DATA
**Global absolute prohibition:** NO synthetic, imaginary, fabricated, proxy, or guessed linguistic data. Only real, verifiable data from real sources. See `.opencode/guidelines/090-data-integrity.md`.

---

## Regression Test Protocol

Before every regression test cycle, the local database MUST be re-synced from production:

```bash
bash scripts/sync_prod_to_local.sh
```

This ensures the test runs against a fresh exact replica of production data. The sync script MUST be the one from the feature branch under test, not from `dev` or `main`. Running against stale or branch-mismatched data produces invalid test results.

## Research Catalog

Before making changes to search infrastructure, text normalization, FTS configuration, or regex processing linguistic data, consult `docs/lessons-learned/` for relevant research findings and design decisions.

| File | Topic |
|------|-------|
| `docs/lessons-learned/index.md` | Entry catalog with cross-references |
| `docs/lessons-learned/2026-06-13-postgres-fts-algonquian.md` | Why 'english' tsconfig corrupts Algonquian search |
| `docs/lessons-learned/2026-06-13-regex-linguistic-characters.md` | ASCII-based regex destroys linguistic data |
| `docs/lessons-learned/2026-06-13-infinity-symbol-normalization.md` | ∞ is a valid letter, maps to oozzz |
| `docs/lessons-learned/2026-06-13-simple-vs-english-tsconfig.md` | Live PG verification evidence |
| `docs/lessons-learned/2026-07-16-local-postgresql-setup.md` | Local PostgreSQL instance management and query patterns |

## Release PR Version Bump Protocol

When creating a release PR that includes a version bump, the agent MUST discover all version-bearing locations through live project analysis — never use a static list.

**Mandatory discovery procedure:**

1. Search the project for version patterns: `grep` for `__version__`, `version =`, `"version":`, `version=` across all file types
2. Inspect each match to confirm it is a project version (not a dependency version, not a subproject with independent versioning)
3. Bump every confirmed project version location
4. Verify no stale version references remain after the bump

**Prohibited:** Maintaining a hardcoded list of version locations in AGENTS.md or any other file. Drift between the static list and the actual project structure produces silent version mismatches. Every release PR must re-discover.

**Rationale:** Files get renamed, moved, added, or removed between releases. A static list from a previous release is stale by definition on the next release. Live discovery is the only reliable mechanism.

## Release PR Body — No Auto-Closing Keywords for Stakeholder Issues

Release PR bodies MUST NOT include auto-closing keywords (`Closes`, `Fixes`, `Resolves`) that reference stakeholder-facing issues. Feature requests from stakeholders must be closed manually after the stakeholder has had an opportunity to verify the release and confirm the work meets their needs.

**Correct:** Describe the feature in release notes without auto-closing syntax.

```
Closes #N
```

Instead, close the stakeholder issue manually after deployment and stakeholder verification.

## LaTeX Build Standard — Modern UTF-8 XeLaTeX

All ".tex" files in this repository MUST use modern UTF-8 XeLaTeX
(`xelatex`), not legacy 8-bit LaTeX (`pdflatex`). This is non-negotiable
because the linguistic data requires:

- Unicode IPA characters (ə, ʃ, tʃ, ŋ, ã, č, etc.)
- Unicode diacritics and combining characters
- Direct Unicode input without \-escape sequences
- fontspec for OpenType font selection

Every .tex file MUST begin with:

```
% !TEX program = xelatex
% !TEX encoding = UTF-8 Unicode
```

The build script (`paper/build.sh`) uses `latexmk -pdf` which auto-detects
xelatex from the % !TEX program directive. Do NOT use `pdflatex` for any
.tex file in this project.
