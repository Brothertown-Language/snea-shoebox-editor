# Phase 01 — Delete Retired Workflow Docs

**Concern:** Remove two documentation files describing the retired `feature→dev→main` workflow that no longer exists after PR #1354 merged `dev` into `main`.

**Files:**
- `docs/git-workflow-migration-guide.md` — DELETE
- `docs/streamlit-dev-workflow.md` — DELETE

**SCs:** SC-1 (`docs/git-workflow-migration-guide.md` deleted), SC-2 (`docs/streamlit-dev-workflow.md` deleted)

**Dependencies:** None

**Entry criteria:** Feature branch exists, spec approved, plan created

**Exit criteria:**
- Both files removed from working tree (`git status` confirms)
- SC-1 PASS: `test ! -f docs/git-workflow-migration-guide.md`
- SC-2 PASS: `test ! -f docs/streamlit-dev-workflow.md`
- Commit made with descriptive message

**Evidence type:** Structural (`test ! -f`)

**Safety/Rollback:**
- Destructive operations: `git rm` on two files
- Rollback plan: `git checkout HEAD~1 -- docs/git-workflow-migration-guide.md docs/streamlit-dev-workflow.md`
- Data loss risk: Low — files exist in git history, restorable via checkout

---

### Step-by-Step

- [ ] 1. (**sub-agent**) Pre-RED baseline — verify both files exist on disk
  - Command: `test -f docs/git-workflow-migration-guide.md && test -f docs/streamlit-dev-workflow.md`
  - Expected: both return 0
  - SC: SC-1, SC-2

- [ ] 2. (**sub-agent**) RED — create assertion for SC-1: verify file is deleted
  - Command: `test ! -f docs/git-workflow-migration-guide.md`
  - Expected: FAIL (file still exists — RED)
  - SC: SC-1

- [ ] 3. (**sub-agent**) GREEN — execute `git rm docs/git-workflow-migration-guide.md`
  - Command: `git rm docs/git-workflow-migration-guide.md`
  - Expected: file removed from working tree
  - SC: SC-1

- [ ] 4. (**sub-agent**) Verify GREEN for SC-1
  - Command: `test ! -f docs/git-workflow-migration-guide.md`
  - Expected: PASS (0 exit code)
  - SC: SC-1

- [ ] 5. (**sub-agent**) RED — create assertion for SC-2: verify file is deleted
  - Command: `test ! -f docs/streamlit-dev-workflow.md`
  - Expected: FAIL (file still exists — RED)
  - SC: SC-2

- [ ] 6. (**sub-agent**) GREEN — execute `git rm docs/streamlit-dev-workflow.md`
  - Command: `git rm docs/streamlit-dev-workflow.md`
  - Expected: file removed from working tree
  - SC: SC-2

- [ ] 7. (**sub-agent**) Verify GREEN for SC-2
  - Command: `test ! -f docs/streamlit-dev-workflow.md`
  - Expected: PASS (0 exit code)
  - SC: SC-2

- [ ] 8. (**sub-agent**) Commit phase
  - Command: `git add . && git commit -m "Phase 1: delete retired dev workflow docs"`
  - Expected: commit succeeds
  - SC: SC-1, SC-2

---

### Phase Completion

- [ ] Both SC-1 and SC-2 PASS with structural evidence (`test ! -f`)
- [ ] Commit made with descriptive message
- [ ] `git status` confirms clean working tree for this phase
- [ ] Transition to Phase 2
