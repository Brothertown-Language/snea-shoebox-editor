# SPEC: Clean up redundant orthography research data after migration to snea-phonetics

> **Full spec and artifacts: [`.issues/1383/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/1383)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> **Local artifacts:** `.issues/1383/` — implementation plan, card catalogue, dependency contracts, research, designs, audit findings

## Intent / Executive Summary

The orthography→phoneme research workflow was migrated out of this repository into the new repository `Brothertown-Language/snea-phonetics`. The redundant research data that remains in this repo's `.issues/research-cards/` worktree must be cleaned up. This spec removes the multi-volume archives, the broken Abenaki file, and the duplicate `mirrored-sources/` directory that were NOT migrated, and confirms the migrated high-relevance data is preserved in `snea-phonetics`. It also removes the redundant `paper/` directory (22 tracked files) that was migrated to `snea-phonetics` (PR #12). Mutations on the `.issues/` worktree use `git -C .issues/ rm`; mutations on the parent repo git use `git rm`.

## Root Cause

The orthography→phoneme research data was originally stored under `.issues/research-cards/` in this repo's `issues-data` worktree. The research workflow migrated to `Brothertown-Language/snea-phonetics` (source issues #1362–#1370, #1374 are all CLOSED with migration links). The migration moved the high-relevance data (proto-algonquian, central-algonquian, eastern-algonquian, plains arapaho, ojibwe CSVs) and the three small Cunningham-Kopris PDFs to the new repo. However, the redundant and broken data that was NOT migrated still occupies ~530MB in this repo's worktree: the 428MB Cunningham Nanticoke multi-volume archive, the 82MB Cheyenne multi-volume archive, a broken Abenaki 404 file, and a duplicate `mirrored-sources/` directory. No source code references any of these paths (verified via grep across `src/`, `test/`, `tests/`, `scripts/`, `streamlit_app.py`).

Additionally, the `paper/` directory (22 tracked files: `master.tex`, `build.sh`, `outputs/master.pdf` + `master.epub`, `part-i-source-workflows/*.tex`, `part-ii-thematic-synthesis/*.tex`, `part-iii-external-resources/*.tex`, `section-1-overview.tex`) was also migrated to `snea-phonetics` (PR #12 merged, all 26 files verified present on the new repo's main branch). The old repo's `paper/` is therefore redundant and a cleanup target. It is tracked in the PARENT repo git, NOT the `.issues/` worktree, so its removal uses `git rm` in the parent repo.

## Approach

1. Remove the redundant multi-volume archives and broken/duplicate data from the `.issues/` worktree via `git -C .issues/ rm` (SC-1, SC-2, SC-3, SC-4).
2. Remove the redundant `paper/` directory from the parent repo git via `git rm` (SC-7).
3. Confirm the high-relevance data migrated to `snea-phonetics` is preserved there and the three small Cunningham-Kopris PDFs are kept (SC-5, SC-6).
4. Verify the end state: removed paths are absent from this repo's worktree, preserved data remains present, and migrated data exists in `snea-phonetics`.

All SCs are structural (file presence/absence). No source code is modified. Two git domains are involved: deletion of research-cards data uses the `.issues/` worktree (`git -C .issues/ rm`); deletion of `paper/` uses the parent repo git (`git rm`).

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Delete the entire `research-cards/` directory | Would destroy the canonical `sources/` directory and the three small Cunningham-Kopris PDFs that retain research value |
| Leave the redundant data in place | Wastes ~530MB of worktree storage; keeps broken 404 files and duplicate directories that confuse future research |
| Migrate the multi-volume archives to snea-phonetics | The archives are redundant (Cunningham replaced by migrated text PDF) or peripheral (Cheyenne); not worth migrating |

## Key Decisions

- **Per-file operations, not per-directory**: `plains-algonquian/` holds both the Cheyenne archive (remove) and the arapaho PDF (keep/migrated); `eastern-algonquian/` holds both the broken Abenaki (remove) and Brinton/Gilwell (migrated). Per-file `git -C .issues/ rm` prevents accidental removal of valid data.
- **Migration-before-removal ordering**: No data is removed from this repo before it is confirmed present in `snea-phonetics`. The migration (SC-5) is already executed; this spec's deletion scope does not re-migrate.
- **Keep the three small Cunningham-Kopris PDFs**: `hdls-2-proceedings.pdf`, `kopris-sons-wyandots.pdf`, `kopris-wyandot-phonology.pdf` are migrated to `snea-phonetics` and retained — they are not deleted.
- **Preserve the canonical `sources/` directory**: Only the duplicate `mirrored-sources/` is removed; the canonical `sources/` directory is untouched.

## Requirements

- Remove the 428MB Cunningham Nanticoke multi-volume archive (`cunningham-nanticoke.{zip,z01..z09}`) from the `.issues/` worktree.
- Remove the 82MB Cheyenne multi-volume archive (`petter-1915-cheyenne-dictionary.{zip,z01}`) from the `.issues/` worktree.
- Remove the broken Abenaki 404 file (`day-1994-western-abenaki-dictionary.pdf`) from the `.issues/` worktree.
- Remove the duplicate `mirrored-sources/` directory from the `.issues/` worktree.
- Confirm the high-relevance data migrated to `snea-phonetics` is preserved there.
- Keep the three small Cunningham-Kopris PDFs (migrated to `snea-phonetics`).
- Remove the redundant `paper/` directory from the parent repo git (all 22 tracked files), confirmed present in `snea-phonetics` main.
- All mutations use `git -C .issues/ rm` on the `.issues/` worktree; the `paper/` removal uses `git rm` on the parent repo git.

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Documentation Sources |
|----|-----------|---------------|---------------------|----------------------|
| SC-1 | The Cunningham Nanticoke multi-volume archive (`cunningham-nanticoke.{zip,z01..z09}`, 10 files, 428MB) is removed from the `.issues/` worktree | `structural` | `git -C .issues/ ls-files research-cards/data/papers/ \| grep -c 'cunningham-nanticoke'` returns 0; `find .issues/research-cards/data/papers -name 'cunningham-nanticoke*'` returns nothing | `.issues/research-cards/data/papers/cunningham-kopris/` |
| SC-2 | The Cheyenne multi-volume archive (`petter-1915-cheyenne-dictionary.{zip,z01}`, 2 files, 82MB) is removed from the `.issues/` worktree | `structural` | `git -C .issues/ ls-files research-cards/data/papers/ \| grep -c 'petter-1915'` returns 0; `find .issues/research-cards/data/papers -name 'petter-1915*'` returns nothing | `.issues/research-cards/data/papers/reference/plains-algonquian/` |
| SC-3 | The broken Abenaki 404 file (`day-1994-western-abenaki-dictionary.pdf`, 137KB, confirmed HTML 404 page) is removed from the `.issues/` worktree | `structural` | `git -C .issues/ ls-files research-cards/data/papers/ \| grep -c 'day-1994'` returns 0; `find .issues/research-cards/data/papers -name 'day-1994*'` returns nothing | `.issues/research-cards/data/papers/reference/eastern-algonquian/` |
| SC-4 | The duplicate `mirrored-sources/` directory (12 files, 20MB) is removed from the `.issues/` worktree, while the canonical `sources/` directory is preserved | `structural` | `git -C .issues/ ls-files research-cards/data/papers/reference/mirrored-sources/` returns empty; `git -C .issues/ ls-files research-cards/sources/` returns non-empty (canonical preserved) | `.issues/research-cards/data/papers/reference/mirrored-sources/`, `.issues/research-cards/sources/` |
| SC-5 | The high-relevance data migrated to `snea-phonetics` is present there: proto-algonquian (hewson), central-algonquian (baraga, bloomfield, sauk, watkins), eastern-algonquian (brinton, gilwell), plains (arapaho), and ojibwe CSVs | `structural` | `gh api "repos/Brothertown-Language/snea-phonetics/git/trees/issues-data?recursive=1"` lists each migrated path under `research-cards/data/` | `https://github.com/Brothertown-Language/snea-phonetics` (issues-data branch) |
| SC-6 | The three small Cunningham-Kopris PDFs (`hdls-2-proceedings.pdf`, `kopris-sons-wyandots.pdf`, `kopris-wyandot-phonology.pdf`) are kept and present in `snea-phonetics` | `structural` | `gh api "repos/Brothertown-Language/snea-phonetics/git/trees/issues-data?recursive=1"` lists all three under `research-cards/data/papers/cunningham-kopris/` | `https://github.com/Brothertown-Language/snea-phonetics` (issues-data branch) |
| SC-7 | The redundant `paper/` directory in this repo (all 22 tracked files) is removed from the parent-repo git, given it is fully present in `snea-phonetics` main branch (PR #12) | `structural` | `git ls-files paper/` returns empty and `find paper -type f` returns nothing | `https://github.com/Brothertown-Language/snea-phonetics` (main branch, PR #12) |

## Implementation Phases

### Phase 1: Remove redundant data (SC-1, SC-2, SC-3, SC-4)

- Remove the Cunningham Nanticoke multi-volume archive via `git -C .issues/ rm research-cards/data/papers/cunningham-kopris/cunningham-nanticoke.{zip,z01..z09}` (SC-1).
- Remove the Cheyenne multi-volume archive via `git -C .issues/ rm research-cards/data/papers/reference/plains-algonquian/petter-1915-cheyenne-dictionary.{zip,z01}` (SC-2).
- Remove the broken Abenaki file via `git -C .issues/ rm research-cards/data/papers/reference/eastern-algonquian/day-1994-western-abenaki-dictionary.pdf` (SC-3).
- Remove the duplicate `mirrored-sources/` directory via `git -C .issues/ rm -r research-cards/data/papers/reference/mirrored-sources/` (SC-4).
- Verify: each removed path is absent from the `.issues/` worktree; the canonical `sources/` directory remains present.

### Phase 1b: Remove redundant `paper/` directory (SC-7)

- Remove the `paper/` directory (all 22 tracked files) from the parent repo git via `git rm -r paper/` (SC-7).
- Verify: `git ls-files paper/` returns empty and `find paper -type f` returns nothing.

### Phase 2: Confirm migration and keep decision (SC-5, SC-6)

- Confirm the high-relevance data is present in `snea-phonetics` (issues-data branch): hewson, central-algonquian, eastern-algonquian, arapaho, ojibwe CSVs (SC-5).
- Confirm the three small Cunningham-Kopris PDFs are present in `snea-phonetics` (SC-6).
- Verify: all migrated paths listed in the `snea-phonetics` issues-data tree.

### Phase 3: Verify end state

- Confirm removed paths are absent from this repo's `.issues/` worktree.
- Confirm the `paper/` directory is absent from the parent repo git (`git ls-files paper/` empty, `find paper -type f` nothing).
- Confirm preserved data (canonical `sources/`, arapaho PDF, Brinton/Gilwell) is present.
- Confirm migrated data is present in `snea-phonetics`.
- Verify: all SCs satisfied via the structural verification commands.

## Requirements → SCs → Phases Traceability

| Requirement | SCs | Phases |
|---|---|---|
| Remove Cunningham Nanticoke archive | SC-1 | Phase 1 |
| Remove Cheyenne archive | SC-2 | Phase 1 |
| Remove broken Abenaki file | SC-3 | Phase 1 |
| Remove duplicate mirrored-sources/ | SC-4 | Phase 1 |
| Confirm migrated data preserved in snea-phonetics | SC-5 | Phase 2 |
| Keep three small Cunningham-Kopris PDFs | SC-6 | Phase 2 |
| Remove redundant paper/ directory | SC-7 | Phase 1b |
| Verify end state | SC-1..SC-7 | Phase 3 |

## Affected Files

- Removed (via `git -C .issues/ rm`): `.issues/research-cards/data/papers/cunningham-kopris/cunningham-nanticoke.{zip,z01..z09}` (SC-1)
- Removed: `.issues/research-cards/data/papers/reference/plains-algonquian/petter-1915-cheyenne-dictionary.{zip,z01}` (SC-2)
- Removed: `.issues/research-cards/data/papers/reference/eastern-algonquian/day-1994-western-abenaki-dictionary.pdf` (SC-3)
- Removed: `.issues/research-cards/data/papers/reference/mirrored-sources/` (SC-4)
- Preserved (in snea-phonetics): hewson, central-algonquian, eastern-algonquian, arapaho, ojibwe CSVs (SC-5)
- Preserved (in snea-phonetics): `hdls-2-proceedings.pdf`, `kopris-sons-wyandots.pdf`, `kopris-wyandot-phonology.pdf` (SC-6)
- Removed (via `git rm` in parent repo git): `paper/` — `master.tex`, `build.sh`, `outputs/master.pdf` + `master.epub`, `part-i-source-workflows/*.tex`, `part-ii-thematic-synthesis/*.tex`, `part-iii-external-resources/*.tex`, `section-1-overview.tex` (22 tracked files, SC-7)
- Unchanged: `.issues/research-cards/sources/` (canonical), all source code (`src/`, `test/`, `tests/`, `scripts/`, `streamlit_app.py`)

## Type

SPEC (data cleanup)

---

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-08-11 | Initial spec authored from completed analyze step | Cleanup spec for redundant orthography research data after migration to snea-phonetics | AI agent (spec-creation create task) |
| 2026-08-11 | Added `paper/` directory removal scope (SC-7, Phase 1b, Requirements, Approach, traceability, Affected Files, Root Cause) | The `paper/` directory (22 tracked files) was also migrated to snea-phonetics (PR #12 merged, all 26 files verified present on the new repo's main branch), making the old repo's `paper/` redundant and a cleanup target. It is tracked in the parent repo git, not the `.issues/` worktree, so removal uses `git rm`. | AI agent (spec-creation revise task) |
