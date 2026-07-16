# Phase 1: Delete stale documentation

## SC-to-Step Traceability

| SC ID | Criterion | Phase | Step(s) |
|-------|-----------|-------|---------|
| SC-1 | `docs/git-workflow-migration-guide.md` is deleted | 1 | 1.1, 1.3 |
| SC-2 | `docs/streamlit-dev-workflow.md` is deleted | 1 | 1.2, 1.3 |
| SC-6 | No SC weakened or deferred | 1 | 1.3 (cross-cutting audit) |

## Steps

### Step 1.1 — Delete `docs/git-workflow-migration-guide.md`

- **Command**: `git rm docs/git-workflow-migration-guide.md`
- **Pre-condition**: File exists (confirmed by `ls`)
- **Post-condition**: File deleted
- **Mapping**: SC-1
- **Safety/Rollback**: `git checkout HEAD -- docs/git-workflow-migration-guide.md` (restore from git)

### Step 1.2 — Delete `docs/streamlit-dev-workflow.md`

- **Command**: `git rm docs/streamlit-dev-workflow.md`
- **Pre-condition**: File exists (confirmed by `ls`)
- **Post-condition**: File deleted
- **Mapping**: SC-2
- **Safety/Rollback**: `git checkout HEAD -- docs/streamlit-dev-workflow.md` (restore from git)

### Step 1.3 — Verify deletions (structural check) + SC-6 audit

- **Verify SC-1**: `test ! -f docs/git-workflow-migration-guide.md` → expected: exit 0 (file absent)
- **Verify SC-2**: `test ! -f docs/streamlit-dev-workflow.md` → expected: exit 0 (file absent)
- **SC-6 cross-cutting**: Confirm no behavioral test assertions were removed or weakened in this phase. Review test files for any changes to `grep`, `assert`, or behavioral assertions.
- **Evidence type**: structural (SC-1, SC-2), behavioral (SC-6)
- **Gate**: pre-commit verification

## Safety/Rollback

- **Destructive operations**: File deletion (git-tracked, reversible)
- **Rollback plan**: `git checkout HEAD -- docs/git-workflow-migration-guide.md docs/streamlit-dev-workflow.md`
- **Data loss risk**: None — files are in git history

## Feasibility Verification

| Step | Reference | Verified? | Evidence |
|------|-----------|-----------|----------|
| 1.1 | `docs/git-workflow-migration-guide.md` | ✅ | `ls` confirmed file exists |
| 1.2 | `docs/streamlit-dev-workflow.md` | ✅ | `ls` confirmed file exists |

## Evidence/Provenance

| Claim | Evidence Source | Verified? |
|-------|----------------|----------|
| `docs/git-workflow-migration-guide.md` exists | `ls docs/git-workflow-migration-guide.md` | ✅ |
| `docs/streamlit-dev-workflow.md` exists | `ls docs/streamlit-dev-workflow.md` | ✅ |

## Exit Criteria

- `test ! -f docs/git-workflow-migration-guide.md` → exit 0 (SC-1: structural)
- `test ! -f docs/streamlit-dev-workflow.md` → exit 0 (SC-2: structural)
- No behavioral test assertions weakened in Phase 1 changes (SC-6: behavioral — clean-room `behavioral-test-evaluation` dispatch required)
- Phase committed to branch with message: `phase-1: delete stale dev-branch docs`
