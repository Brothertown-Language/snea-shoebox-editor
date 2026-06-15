# Implementation Workflow Checklist — #1299

## Z3 SAT Verification

**Status: SOLVED_SATISFICING** — Tamer planner, 108 objects, 100 actions, 15 fluents, 1 goal (`pr-created`).

The full PDDL domain is at `.issues/1299/spec-artifacts/fts-full-domain.yaml`. Every step below is a Z3-verified action in the ordered plan. No step may be skipped, reordered, or omitted.

## Pipeline Invariant

Each phase: **start → pre-analysis → RED → completeness-gate → GREEN → completeness-gate → adversarial-audit → Z3-verify → git-add → git-commit → git-tag → post-flight → complete**

Dispatch markers:
- `[S]` = sub-agent task() — clean-room dispatch
- `[I]` = inline — orchestrator (git ops, tags, Z3 verify, test runs)
- `[A]` = auditor sub-agent — via resolve-models

---

## Phase 0: Pre-Work (Z3 steps 1-6)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 1 | 0.1 | `[I]` | `git checkout -b feature/1299-fts-entries` from dev | ⬜ |
| 2 | 0.2 | `[I]` | Verify git state: clean working tree, correct base | ⬜ |
| 3 | 0.3 | `[I]` | `git submodule update --init` — submodules current | ⬜ |
| 4 | 0.4 | `[I]` | Tag submodule SHA: `git tag feature/1299-fts-entries/pre-work-snea-shoebox-editor` | ⬜ |
| 5 | 0.C | `[I]` | **complete-phase-0** — phase-0-prework completed | ⬜ |

## Phase 1: Documentation — Copy Lessons Learned (Z3 steps 7-19)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 6 | 1.1 | `[S]` | **start-phase-1** — phase-1-docs started | ⬜ |
| 7 | 1.2 | `[S]` | Pre-analysis: discover scope — files in `.issues/1299/spec-artifacts/lessons-learned/`, AGENTS.md format | ⬜ |
| 8 | 1.3 | `[S]` | RED: write test verifying `docs/lessons-learned/` has 5 files + AGENTS.md has research catalog | ⬜ |
| 9 | 1.4 | `[S]` | Completeness gate: verify RED test exists and is structurally sound | ⬜ |
| 10 | 1.5 | `[S]` | GREEN: copy 5 files to `docs/lessons-learned/`, create `AGENTS.md` | ⬜ |
| 11 | 1.6 | `[S]` | Completeness gate: verify all 6 files exist with correct content | ⬜ |
| 12 | 1.7 | `[A]` | Adversarial audit: dual cross-family audit of phase-1 artifacts | ⬜ |
| 13 | 1.8 | `[I]` | Z3 verify: `solve check` against contract | ⬜ |
| 14 | 1.9 | `[I]` | `git add AGENTS.md docs/lessons-learned/` | ⬜ |
| 15 | 1.10 | `[I]` | `git commit -m "Phase 1: Copy lessons-learned docs and create AGENTS.md"` | ⬜ |
| 16 | 1.11 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-1-snea-shoebox-editor` | ⬜ |
| 17 | 1.12 | `[I]` | Post-flight: verify commit exists, tag exists, working tree clean | ⬜ |
| 18 | 1.C | `[I]` | **complete-phase-1** — phase-1-docs completed | ⬜ |

## Phase 2: Model — Add FTSEntry class (Z3 steps 20-32)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 19 | 2.1 | `[S]` | **start-phase-2** — phase-2-model started | ⬜ |
| 20 | 2.2 | `[S]` | Pre-analysis: read `search.py` and `core.py` for insertion points | ⬜ |
| 21 | 2.3 | `[S]` | RED: write test importing `FTSEntry`, verifying schema columns + `Record.fts_entry` | ⬜ |
| 22 | 2.4 | `[S]` | Completeness gate: verify RED test references correct file paths and SCs | ⬜ |
| 23 | 2.5 | `[S]` | GREEN: add `FTSEntry` class to `search.py`, add `fts_entry` relationship to `core.py` | ⬜ |
| 24 | 2.6 | `[S]` | Completeness gate: verify model class exists with correct columns, relationship exists | ⬜ |
| 25 | 2.7 | `[A]` | Adversarial audit: dual cross-family audit of model changes | ⬜ |
| 26 | 2.8 | `[I]` | Z3 verify: state transition check | ⬜ |
| 27 | 2.9 | `[I]` | `git add src/database/models/search.py src/database/models/core.py` | ⬜ |
| 28 | 2.10 | `[I]` | `git commit -m "Phase 2: Add FTSEntry model and Record.fts_entry relationship"` | ⬜ |
| 29 | 2.11 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-2-snea-shoebox-editor` | ⬜ |
| 30 | 2.12 | `[I]` | Post-flight: verify commit, tag, clean tree | ⬜ |
| 31 | 2.C | `[I]` | **complete-phase-2** — phase-2-model completed | ⬜ |

## Phase 3: Migration — Create fts_entries table, populate, drop fts_vector (Z3 steps 33-45)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 32 | 3.1 | `[S]` | **start-phase-3** — phase-3-migration started | ⬜ |
| 33 | 3.2 | `[S]` | Pre-analysis: read `migrations.py` for `_MIGRATIONS` insertion point and EOF | ⬜ |
| 34 | 3.3 | `[S]` | RED: write test verifying `_migrate_replace_fts_vector` exists in registry and class | ⬜ |
| 35 | 3.4 | `[S]` | Completeness gate: verify RED test | ⬜ |
| 36 | 3.5 | `[S]` | GREEN: add registry entry + implement `_migrate_replace_fts_vector()` | ⬜ |
| 37 | 3.6 | `[S]` | Completeness gate: verify migration creates table, populates, drops old column | ⬜ |
| 38 | 3.7 | `[A]` | Adversarial audit: dual cross-family audit of migration | ⬜ |
| 39 | 3.8 | `[I]` | Z3 verify: state transition check | ⬜ |
| 40 | 3.9 | `[I]` | `git add src/database/migrations.py` | ⬜ |
| 41 | 3.10 | `[I]` | `git commit -m "Phase 3: Add migration to create fts_entries, populate, drop fts_vector"` | ⬜ |
| 42 | 3.11 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-3-snea-shoebox-editor` | ⬜ |
| 43 | 3.12 | `[I]` | Post-flight: verify commit, tag, clean tree | ⬜ |
| 44 | 3.C | `[I]` | **complete-phase-3** — phase-3-migration completed | ⬜ |

## Phase 4: Upload Service — Populate fts_entries on upload (Z3 steps 46-58)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 45 | 4.1 | `[S]` | **start-phase-4** — phase-4-upload started | ⬜ |
| 46 | 4.2 | `[S]` | Pre-analysis: read `upload_service.py` `populate_search_entries()` for insertion point | ⬜ |
| 47 | 4.3 | `[S]` | RED: write test verifying `populate_search_entries()` creates `FTSEntry` rows | ⬜ |
| 48 | 4.4 | `[S]` | Completeness gate: verify RED test | ⬜ |
| 49 | 4.5 | `[S]` | GREEN: add FTSEntry population to `populate_search_entries()` | ⬜ |
| 50 | 4.6 | `[S]` | Completeness gate: verify FTSEntry is populated after search entries | ⬜ |
| 51 | 4.7 | `[A]` | Adversarial audit: dual cross-family audit of upload service changes | ⬜ |
| 52 | 4.8 | `[I]` | Z3 verify: state transition check | ⬜ |
| 53 | 4.9 | `[I]` | `git add src/services/upload_service.py` | ⬜ |
| 54 | 4.10 | `[I]` | `git commit -m "Phase 4: Update populate_search_entries() for FTSEntry"` | ⬜ |
| 55 | 4.11 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-4-snea-shoebox-editor` | ⬜ |
| 56 | 4.12 | `[I]` | Post-flight: verify commit, tag, clean tree | ⬜ |
| 57 | 4.C | `[I]` | **complete-phase-4** — phase-4-upload completed | ⬜ |

## Phase 5: Linguistic Service — Rewrite `_search_fts()` (Z3 steps 59-73)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 58 | 5.1 | `[S]` | **start-phase-5** — phase-5-linguistic started | ⬜ |
| 59 | 5.2 | `[S]` | Pre-analysis: read `linguistic_service.py` for all 3 FTS code locations | ⬜ |
| 60 | 5.3 | `[S]` | RED: write test verifying FTS mode uses `fts_entries` + `'simple'` + no ILIKE | ⬜ |
| 61 | 5.4 | `[S]` | Completeness gate: verify RED test | ⬜ |
| 62 | 5.5 | `[S]` | GREEN: rewrite `_search_fts()` — join `Record.fts_entry`, `to_tsquery('simple', ...)`, no ILIKE, empty-words → no results | ⬜ |
| 63 | 5.6 | `[S]` | GREEN: update `get_all_records_for_export()` FTS branch identically | ⬜ |
| 64 | 5.7 | `[S]` | GREEN: update `stream_records_to_temp_file()` FTS branch identically | ⬜ |
| 65 | 5.8 | `[S]` | Completeness gate: verify all 3 FTS code paths use new logic | ⬜ |
| 66 | 5.9 | `[A]` | Adversarial audit: dual cross-family audit of linguistic service changes | ⬜ |
| 67 | 5.10 | `[I]` | Z3 verify: state transition check | ⬜ |
| 68 | 5.11 | `[I]` | `git add src/services/linguistic_service.py` | ⬜ |
| 69 | 5.12 | `[I]` | `git commit -m "Phase 5: Rewrite _search_fts() to use fts_entries + simple config"` | ⬜ |
| 70 | 5.13 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-5-snea-shoebox-editor` | ⬜ |
| 71 | 5.14 | `[I]` | Post-flight: verify commit, tag, clean tree | ⬜ |
| 72 | 5.C | `[I]` | **complete-phase-5** — phase-5-linguistic completed | ⬜ |

## Phase 6: Tests — Update and add tests (Z3 steps 74-88)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 73 | 6.1 | `[S]` | **start-phase-6** — phase-6-tests started | ⬜ |
| 74 | 6.2 | `[S]` | Pre-analysis: read `test_linguistic_service.py` for test class and existing FTS tests | ⬜ |
| 75 | 6.3 | `[S]` | RED: write `test_search_records_fts_normalized()` — diacritics in mdf_data, search normalized form | ⬜ |
| 76 | 6.4 | `[S]` | RED: write `test_search_records_fts_infinity_symbol()` — ∞ in mdf_data, search oozzz | ⬜ |
| 77 | 6.5 | `[S]` | RED: write `test_search_records_fts_no_iliike_fallback()` — term only in raw mdf_data, assert no results | ⬜ |
| 78 | 6.6 | `[S]` | Completeness gate: verify all 3 RED tests exist and are structurally sound | ⬜ |
| 79 | 6.7 | `[S]` | GREEN: implement the 3 test methods | ⬜ |
| 80 | 6.8 | `[S]` | Completeness gate: verify tests compile and reference correct SCs | ⬜ |
| 81 | 6.9 | `[A]` | Adversarial audit: dual cross-family audit of test changes | ⬜ |
| 82 | 6.10 | `[I]` | Z3 verify: state transition check | ⬜ |
| 83 | 6.11 | `[I]` | `git add tests/services/test_linguistic_service.py` | ⬜ |
| 84 | 6.12 | `[I]` | `git commit -m "Phase 6: Add FTS normalization, infinity symbol, and no-ILIKE-fallback tests"` | ⬜ |
| 85 | 6.13 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-6-snea-shoebox-editor` | ⬜ |
| 86 | 6.14 | `[I]` | Post-flight: verify commit, tag, clean tree | ⬜ |
| 87 | 6.C | `[I]` | **complete-phase-6** — phase-6-tests completed | ⬜ |

## Phase 7: Verification — Run tests, completeness gate, adversarial audit (Z3 steps 89-100)

| # | Step | Dispatch | Action | Status |
|---|------|----------|--------|--------|
| 88 | 7.1 | `[S]` | **start-phase-7** — phase-7-verify started | ⬜ |
| 89 | 7.2 | `[I]` | `uv run pytest tests/ -x -v` — all tests pass | ⬜ |
| 90 | 7.3 | `[S]` | Completeness gate: verify all 13 SCs have corresponding evidence | ⬜ |
| 91 | 7.4 | `[A]` | Adversarial audit: `resolve-models` → dual auditor dispatch → `cross-validate` | ⬜ |
| 92 | 7.5 | `[S]` | Finishing checklist: `finishing-a-development-branch` — verify all files committed, branch pushed | ⬜ |
| 93 | 7.6 | `[I]` | `git push -u origin feature/1299-fts-entries` | ⬜ |
| 94 | 7.7 | `[I]` | `git tag feature/1299-fts-entries/checkpoint/phase-7-snea-shoebox-editor` | ⬜ |
| 95 | 7.8 | `[I]` | `git push --tags` | ⬜ |
| 96 | 7.9 | `[I]` | Z3 verify: final state check — all gates passed, all phases complete | ⬜ |
| 97 | 7.10 | `[I]` | Post-flight: verify push, tags, clean tree | ⬜ |
| 98 | 7.C | `[I]` | **complete-phase-7** — phase-7-verify completed | ⬜ |
| 99 | PR | `[I]` | **create-pr** — PR created, artifact-pr created | ⬜ |

---

## Summary

| Phase | Steps | [S] | [I] | [A] | Z3 Steps |
|-------|-------|-----|-----|-----|----------|
| 0. Pre-Work | 5 | 0 | 5 | 0 | 1-6 |
| 1. Documentation | 13 | 6 | 7 | 0 | 7-19 |
| 2. Model | 13 | 6 | 7 | 0 | 20-32 |
| 3. Migration | 13 | 6 | 7 | 0 | 33-45 |
| 4. Upload Service | 13 | 6 | 7 | 0 | 46-58 |
| 5. Linguistic Service | 15 | 8 | 7 | 0 | 59-73 |
| 6. Tests | 15 | 8 | 7 | 0 | 74-88 |
| 7. Verification | 12 | 4 | 7 | 1 | 89-100 |
| **Total** | **99** | **44** | **54** | **1** | **100** |

## Rollback Protocol

If any `[S]` sub-agent returns BLOCKED or any verification step FAILS:
1. Report diagnostics (`git status`, `git diff --stat`)
2. `git reset --hard feature/1299-fts-entries/checkpoint/phase-<N-1>-snea-shoebox-editor`
3. Re-dispatch the failed step with original scoped context only
4. Max 2 retries per step before escalation
