# Plan: Replace fts_vector with fts_entries table — #1299

**Authorization scope:** `for_plan` (halt_at: `plan_created`, pr_strategy: `stacked`)
**Spec:** https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1299
**Branch:** `feature/1299-fts-entries`
**Base:** `dev`

## Z3 SAT Verification

The workflow was modeled as a PDDL planning problem with 28 objects, 11 fluents, 11 actions, and verified SAT by the Tamer planner. The SAT model confirms:

- All 7 phases are reachable in dependency order
- Each phase requires: start → steps → checkpoint tag → Z3 verify → complete
- PR creation requires: branch created + all tests pass + audit pass + both gates
- No deadlock states exist in the workflow

## Phase Structure

Each phase follows the invariant: **start → [steps] → checkpoint tag → Z3 verify → complete**

Checkpoint tags follow the convention: `feature/1299-fts-entries/checkpoint/phase-<N>-snea-shoebox-editor`

---

## Phase 1: Documentation — Copy Lessons Learned

**Concern:** Research artifacts from spec creation must be published to `docs/lessons-learned/`.

### Steps

#### Step 1.1: Copy lessons-learned files
- Copy all 5 files from `.issues/1299/spec-artifacts/lessons-learned/` to `docs/lessons-learned/`
- Files: `index.md`, `2026-06-13-postgres-fts-algonquian.md`, `2026-06-13-regex-linguistic-characters.md`, `2026-06-13-infinity-symbol-normalization.md`, `2026-06-13-simple-vs-english-tsconfig.md`

#### Step 1.2: Create root AGENTS.md
- Create `AGENTS.md` in repo root with research catalog table per spec

#### Step 1.3: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-1-snea-shoebox-editor`

#### Step 1.4: Z3 verify
- Run `solve check` against contract to confirm phase-1 artifacts exist

### Artifacts
- `docs/lessons-learned/index.md`
- `docs/lessons-learned/2026-06-13-*.md` (4 files)
- `AGENTS.md`

---

## Phase 2: Model — Add FTSEntry class

**Concern:** New SQLAlchemy model for the `fts_entries` table.

### Steps

#### Step 2.1: Add FTSEntry model to `src/database/models/search.py`
- New class `FTSEntry(Base)` with:
  - `id = Column(Integer, primary_key=True)`
  - `record_id = Column(Integer, ForeignKey("records.id", ondelete="CASCADE"), nullable=False, index=True)`
  - `fts_vector = Column(TSVECTOR, nullable=False)`
- Import `TSVECTOR` from `sqlalchemy.dialects.postgresql`
- Add `record = relationship("Record", back_populates="fts_entry")`

#### Step 2.2: Add Record.fts_entry relationship to `src/database/models/core.py`
- Add `fts_entry = relationship("FTSEntry", back_populates="record", uselist=False)` to `Record` class
- Import `FTSEntry` is not needed — string-based relationship resolves it

#### Step 2.3: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-2-snea-shoebox-editor`

#### Step 2.4: Z3 verify
- Run `solve check` against contract to confirm model class exists

### Artifacts
- `src/database/models/search.py` — FTSEntry class added
- `src/database/models/core.py` — Record.fts_entry relationship added

---

## Phase 3: Migration — Create fts_entries table, populate, drop fts_vector

**Concern:** Database schema migration to replace the generated column.

### Steps

#### Step 3.1: Add migration method to `src/database/migrations.py`
- Add to `_MIGRATIONS` registry: `(20260613120000, "_migrate_replace_fts_vector", "Replace records.fts_vector with fts_entries table")`
- Implement `_migrate_replace_fts_vector()`:
  1. Create `fts_entries` table (CREATE TABLE IF NOT EXISTS)
  2. Populate from all records using `generate_sort_lx(mdf_data)` → `to_tsvector('simple', normalized_text)`
  3. Create GIN index on `fts_entries.fts_vector`
  4. Drop `records.fts_vector` column (and its GIN index `idx_records_fts`)
  5. Drop GIN index `idx_records_fts` if it exists

#### Step 3.2: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-3-snea-shoebox-editor`

#### Step 3.3: Z3 verify
- Run `solve check` against contract to confirm migration method exists

### Artifacts
- `src/database/migrations.py` — new migration method + registry entry

---

## Phase 4: Upload Service — Populate fts_entries on upload

**Concern:** New records must get FTS entries populated during upload.

### Steps

#### Step 4.1: Update `populate_search_entries()` in `src/services/upload_service.py`
- After populating search_entries/headword/gloss entries, also populate `FTSEntry`:
  - Delete existing `FTSEntry` for the record
  - Normalize `mdf_data` via `generate_sort_lx()`
  - Create `FTSEntry(record_id=rid, fts_vector=func.to_tsvector('simple', normalized_text))`
- Import `FTSEntry` from models
- Import `func` from sqlalchemy

#### Step 4.2: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-4-snea-shoebox-editor`

#### Step 4.3: Z3 verify
- Run `solve check` against contract to confirm upload service updated

### Artifacts
- `src/services/upload_service.py` — updated `populate_search_entries()`

---

## Phase 5: Linguistic Service — Rewrite `_search_fts()`

**Concern:** FTS search mode uses new `fts_entries` table with `'simple'` config, no ILIKE fallback.

### Steps

#### Step 5.1: Rewrite `_search_fts()` in `src/services/linguistic_service.py`
- New logic per spec:
  - `#N` record-ID lookup unchanged
  - Normalize search term via `generate_sort_lx()`
  - Split into words, strip `_TSQUERY_UNSAFE` chars
  - Build tsquery with `:*` prefix per word, `&`-joined
  - Join `Record.fts_entry` and filter via `fts_entries.fts_vector @@ to_tsquery('simple', :fts_term)`
  - **No ILIKE fallback** — if no valid words, return `query.filter(Record.id == -1)` (no results, matching other search modes)
- Update `get_all_records_for_export()` and `stream_records_to_temp_file()` FTS branches identically

#### Step 5.2: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-5-snea-shoebox-editor`

#### Step 5.3: Z3 verify
- Run `solve check` against contract to confirm FTS logic rewritten

### Artifacts
- `src/services/linguistic_service.py` — updated `_search_fts()`, `get_all_records_for_export()`, `stream_records_to_temp_file()`

---

## Phase 6: Tests — Update and add tests

**Concern:** Tests must cover new FTS behavior and verify no regression.

### Steps

#### Step 6.1: Update `test_search_records_fts()` in `tests/services/test_linguistic_service.py`
- The existing FTS test (`test_search_records_fts_mode_unchanged`) verifies FTS mode still works — it should pass as-is since the new `_search_fts` still returns results
- Add new test `test_search_records_fts_normalized()`:
  - Create record with diacritics in mdf_data (e.g., `\lx akitusu-`)
  - Search with normalized form (e.g., `akitusu`)
  - Assert record is found via FTS mode
- Add new test `test_search_records_fts_infinity_symbol()`:
  - Create record with ∞ in mdf_data
  - Search with `oozzz` or `oo`
  - Assert record is found
- Add new test `test_search_records_fts_no_iliike_fallback()`:
  - Verify that FTS mode does NOT use ILIKE fallback
  - Search for a term that exists only in mdf_data but not in normalized form
  - Assert no results (confirming ILIKE fallback is removed)

#### Step 6.2: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-6-snea-shoebox-editor`

#### Step 6.3: Z3 verify
- Run `solve check` against contract to confirm tests exist

### Artifacts
- `tests/services/test_linguistic_service.py` — updated tests

---

## Phase 7: Verification — Run tests, completeness gate, adversarial audit

**Concern:** All changes verified before PR.

### Steps

#### Step 7.1: Run all tests
- `uv run pytest tests/ -x -v` — verify all tests pass
- If any fail, remediate and re-run

#### Step 7.2: Completeness gate
- Invoke `completeness-gate --task check` against all artifacts

#### Step 7.3: Adversarial audit
- Invoke `adversarial-audit --task verification-audit` with spec #1299
- Resolve dual cross-family auditors via `resolve-models`
- Cross-validate auditor verdicts

#### Step 7.4: Finishing checklist
- Invoke `finishing-a-development-branch` checklist
- Verify all files committed, branch pushed

#### Step 7.5: Checkpoint tag
- `git tag feature/1299-fts-entries/checkpoint/phase-7-snea-shoebox-editor`

#### Step 7.6: Z3 verify
- Run `solve check` against contract to confirm all gates passed

### Artifacts
- Test results
- Audit verdicts
- PR compare URL

---

## Success Criteria (from spec)

| ID | Criterion | Evidence Type | Phase |
|----|-----------|---------------|-------|
| SC-1 | `FTSEntry` model class exists in `search.py` with correct schema | `structural` | 2 |
| SC-2 | `Record.fts_entry` relationship exists in `core.py` | `structural` | 2 |
| SC-3 | Migration creates `fts_entries` table, populates from all records, drops `records.fts_vector` | `behavioral` | 3 |
| SC-4 | GIN index on `fts_entries.fts_vector` | `structural` | 3 |
| SC-5 | `populate_search_entries()` also populates `fts_entries` | `behavioral` | 4 |
| SC-6 | `_search_fts()` uses `fts_entries` table with `'simple'` config | `behavioral` | 5 |
| SC-7 | No ILIKE fallback in FTS mode | `behavioral` | 5 |
| SC-8 | `generate_sort_lx()` normalization on both index and query sides | `behavioral` | 5 |
| SC-9 | `#N` record-ID lookup still works in FTS mode | `behavioral` | 5 |
| SC-10 | Lessons-learned files copied to `docs/` | `structural` | 1 |
| SC-11 | `AGENTS.md` created with research catalog | `structural` | 1 |
| SC-12 | All existing tests pass | `behavioral` | 7 |
| SC-13 | Adversarial audit PASS | `behavioral` | 7 |

## Rollback Protocol

If any phase verification fails and a checkpoint tag exists for the prior phase:

1. Report pre-rollback diagnostics (`git status`, `git diff --stat`)
2. Execute: `git reset --hard feature/1299-fts-entries/checkpoint/phase-<N-1>-snea-shoebox-editor`
3. Re-dispatch the failed phase

If first-step failure (no prior checkpoint): `git checkout .` and re-dispatch.

## Z3 Contract File

```yaml
# .issues/1299/spec-artifacts/contract.yaml
domain: fts-entries-workflow
invariants:
  - "phase-completed(phase-N) → phase-completed(phase-N-1)"  # strict ordering
  - "checkpoint-tagged(phase-N) → phase-started(phase-N)"     # no tag without start
  - "z3-verified(phase-N) → phase-started(phase-N)"           # no verify without start
  - "pr-created → all-tests-pass"                              # no PR without tests
  - "pr-created → audit-passed"                                # no PR without audit
  - "pr-created → branch-created"                              # no PR without branch
```
