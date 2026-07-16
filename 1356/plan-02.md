# Phase 02 — Update dev→main References

**Concern:** Update remaining documentation references from `dev` to `main` as the target branch after the `dev` branch retirement.

**Files:**
- `AGENTS.md` — REMOVE line 52 (exception for PRs merging to `dev`)
- `docs/security/credential-leakage-remediation.md` — UPDATE line 84 (`origin dev` → `origin main`)

**SCs:** SC-3 (AGENTS.md line 52 removed), SC-4 (credential doc references `origin main`)

**Dependencies:** Phase 1 complete (retired doc files already deleted)

**Entry criteria:** Phase 1 committed, working tree clean

**Exit criteria:**
- `grep -c 'merging to \`dev\`' AGENTS.md` returns 0
- `grep -c 'origin dev' docs/security/credential-leakage-remediation.md` returns 0
- Commit made with descriptive message

**Evidence type:** String (`grep` pattern match)

**Safety/Rollback:**
- Destructive operations: None (line-level edits, reversible via `git checkout`)
- Rollback plan: `git checkout HEAD~1 -- AGENTS.md docs/security/credential-leakage-remediation.md`
- Data loss risk: None

---

### Step-by-Step

- [ ] 9. (**sub-agent**) Pre-RED baseline — verify both target lines exist
  - Command: `grep -n 'merging to \`dev\`' AGENTS.md && grep -n 'origin dev' docs/security/credential-leakage-remediation.md`
  - Expected: line 52 in AGENTS.md, line 84 in credential doc
  - SC: SC-3, SC-4

- [ ] 10. (**sub-agent**) RED — verify SC-3 assertion fails
  - Command: `grep -c 'merging to \`dev\`' AGENTS.md`
  - Expected: returns > 0 (RED — line still present)
  - SC: SC-3

- [ ] 11. (**sub-agent**) GREEN — remove line 52 from AGENTS.md
  - Command: Edit AGENTS.md to delete line 52 (the `dev` exception line)
  - Expected: line removed
  - SC: SC-3

- [ ] 12. (**sub-agent**) Verify GREEN for SC-3
  - Command: `grep -c 'merging to \`dev\`' AGENTS.md`
  - Expected: returns 0 (PASS)
  - SC: SC-3

- [ ] 13. (**sub-agent**) RED — verify SC-4 assertion fails
  - Command: `grep -c 'origin dev' docs/security/credential-leakage-remediation.md`
  - Expected: returns > 0 (RED — old reference still present)
  - SC: SC-4

- [ ] 14. (**sub-agent**) GREEN — update line 84 in credential doc
  - Command: Edit line 84 of `docs/security/credential-leakage-remediation.md` to replace `origin dev` with `origin main`
  - Expected: line updated
  - SC: SC-4

- [ ] 15. (**sub-agent**) Verify GREEN for SC-4
  - Command: `grep -c 'origin dev' docs/security/credential-leakage-remediation.md`
  - Expected: returns 0 (PASS)
  - SC: SC-4

- [ ] 16. (**sub-agent**) Commit phase
  - Command: `git add -A && git commit -m "Phase 2: update dev->main references in docs"`
  - Expected: commit succeeds
  - SC: SC-3, SC-4

---

### Phase Completion

- [ ] Both SC-3 and SC-4 PASS with string evidence (`grep` pattern match)
- [ ] Commit made with descriptive message
- [ ] `git status` confirms clean working tree for this phase
- [ ] Transition to Phase 3
