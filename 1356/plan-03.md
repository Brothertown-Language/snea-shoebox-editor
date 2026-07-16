# Phase 03 — Verification Sweep

**Concern:** Verify zero `dev` branch workflow references remain across the documentation directory after the deletions and edits in phases 1-2.

**Files:** `docs/` directory (read-only grep sweep)

**SCs:** SC-5 (no remaining `\`dev\`` branch workflow references)

**Dependencies:** Phases 1-2 complete (files deleted and references updated)

**Entry criteria:** Phases 1-2 committed, working tree clean

**Exit criteria:**
- `grep -rn '\`dev\`' docs/` returns only false positives or empty
- Results documented

**Evidence type:** Structural (grep sweep)

**Safety/Rollback:**
- Destructive operations: None — read-only verification
- Data loss risk: None

---

### Step-by-Step

- [ ] 17. (**sub-agent**) Pre-sweep baseline — confirm phases 1-2 changes are in place
  - Command: `test ! -f docs/git-workflow-migration-guide.md && test ! -f docs/streamlit-dev-workflow.md && grep -c 'origin dev' docs/security/credential-leakage-remediation.md | grep -q 0`
  - Expected: all pass (files deleted, refs updated)
  - SC: SC-5 (precondition)

- [ ] 18. (**sub-agent**) Run verification sweep — grep for backtick-gated `dev` references
  - Command: `grep -rn '\`dev\`' docs/ || echo "No matches found"`
  - Expected: either no matches, or only false positives (generic prose, not workflow references)
  - SC: SC-5

- [ ] 19. (**sub-agent**) Review grep results — classify each match as workflow reference or generic prose
  - Command: Inspect each match context
  - Expected: all matches are generic prose ("development", "dev machine", "dev environment") — zero workflow references
  - SC: SC-5

- [ ] 20. (**sub-agent**) Verify SC-5 PASS
  - Command: Confirm that `grep -rn '\`dev\`' docs/` produced no workflow references
  - Expected: PASS
  - SC: SC-5

- [ ] 21. (**sub-agent**) Document sweep results
  - Command: Write sweep results to `.issues/1356/verification-sweep-results.md`
  - Expected: file created with match count and classification
  - SC: SC-5

- [ ] 22. (**sub-agent**) Commit sweep results
  - Command: `git add .issues/1356/verification-sweep-results.md && git commit -m "Phase 3: verification sweep results"`
  - Expected: commit succeeds
  - SC: SC-5

---

### Phase Completion

- [ ] SC-5 PASS with structural evidence (grep sweep)
- [ ] Sweep results documented
- [ ] Commit made
- [ ] Ready for VbC (verification-before-completion) and finishing checks

---

### Common SC-6 — SC Integrity

**Applies to all phases**

- [ ] 23. (**sub-agent**) Verify no SC was weakened or reclassified to evade implementation
  - Command: Audit each SC PASS against its declared evidence type
  - Expected: All SCs achieved PASS with their declared evidence type — no behavioral→structural downgrades
  - SC: SC-6

- [ ] 24. (**sub-agent**) Verify behavioral SCs use test execution, not structural/grep substitution
  - Command: Inspect verification evidence for each behavioral SC
  - Expected: No EVIDENCE_TYPE_MISMATCH findings
  - SC: SC-6

- [ ] 25. (**sub-agent**) Reclassify any SC with mismatched evidence type and re-verify
  - Command: Apply substrate classification gate — if change affects behavior, evidence type MUST be behavioral
  - Expected: All SCs correctly classified and verified
  - SC: SC-6

- [ ] 26. (**sub-agent**) Document SC-6 verification
  - Command: Append SC-6 findings to verification results
  - Expected: SC-6 PASS documented
  - SC: SC-6
