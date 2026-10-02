# Phase 2 — Seam default-floor semantics (threshold=None) + all-below-floor outcome

**Concern:** seam

**Files:**
- `src/services/semantic_search_service.py` — `search_semantic()`, `_candidate_sql()` threshold filter, post-query result assembly
- new/extended pytest seam test modules (seam contract + edge-input matrix)

**SCs:** SC-2, SC-3, SC-4, SC-5, SC-6, SC-7

**Dependencies:** Phase 1 (module-level calibration constant published)

**Entry Conditions:**
- Phase 1 complete: calibration constant published with provenance
- Phase 1 VbC passed; both Phase 1 commits landed

**Exit Conditions:**
- `search_semantic(threshold=None)` filters on the calibrated default floor
- Explicit threshold values override the default; `None` after an override re-engages the default
- All-below-floor outcome returns `status=ok` with empty `results` and a deficiency message — no exception, no below-floor rows served
- Signature and status enum unchanged (R-3); all prior tests pass

**Code Path Coverage:**
- SC-2: `search_semantic()` — `threshold` is not `None` currently sets the SQL filter; `threshold=None` currently returns the FULL ranked list. The default-on-`None` change lands here: `None` resolves the module calibration constant and filters on it
- SC-3: same seam path — explicit threshold continues to flow through the threshold parameter unmodified (override precedence)
- SC-4: same seam path — seam is stateless per call (threshold is a parameter, no module state); the test guards against future sticky-state regression
- SC-5: post-query result assembly — the empty-results branch already returns `status=ok` with a message when pinned embeddings exist; below-floor filtering maps onto this same outcome shape (R-3, `.issues/36` R-7 pattern)
- SC-6: status machine — no new exception path; the all-below-floor case is handled in the normal return flow
- SC-7: `_candidate_sql()` threshold filter — the `has_threshold` branch adds a score cutoff in SQL; the default floor must actually apply for the default path, not only for explicit thresholds

**Cross-Cutting SCs:**
- SC-2 spans calibration and seam concerns — the constant must exist (Phase 1) before the seam can engage it (here)
- SC-5, SC-6, SC-7 are simultaneously threshold-filtering changes and status-machine mappings constrained by R-3

**Interface Boundaries:**
- `search_semantic(mode, query, threshold, source_id, limit) -> SemanticSearchResult` — signature PRESERVED (R-3); only `threshold=None` semantics change
- `SemanticSearchResult` statuses (`ok`/`empty_query`/`no_embeddings`/`stale_model`) — PRESERVED; no new status value
- Consumers (`linguistic_service.py` dispatch alias, `records.py` calls) pass threshold by name only — no consumer relies on the old `None` behavior
- Named calibration constant (R-2, no magic number) consumed from Phase 1

**State Transitions:**
- `threshold=None` → floor-engaged filtering (prior: unfiltered full ranked list)
- Explicit threshold → override preserved; `None` → default restored (stateless per call — no sticky state to migrate)
- All ranked scores below floor → `status=ok`, `results=[]`, deficiency message (prior: no floor for the default path; low-confidence rows served as ranked results). No status-enum transition added (R-3)

**Cost frame:** Running the seam pytest battery costs minutes of execution time. Skipping the below-floor outcome tests costs the core user-facing defect shipping unchanged — "no reasonable match" stays indistinguishable from "match" in every query, and the fix costs a full re-review cycle at 100× the discovery-latency cost.

---

## Step-by-step

### Item 4 — SC-2: default-on-None engages the calibrated floor

- [ ] 18. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing seam test asserting `search_semantic(threshold=None)` filters on the module-level calibrated default floor constant. The test FAILS because `None` currently bypasses filtering entirely. **→ SC-2**
- [ ] 19. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: implement `threshold=None` → resolve the calibration constant and filter (named constant, no magic number). Minimum change only. **→ SC-2**
- [ ] 20. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: existing seam tests (explicit-threshold paths, status machine) must still pass. **→ non-regression for SC-2**
- [ ] 21. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify the default is engaged exactly when `threshold=None` and the constant is the named calibration constant. **→ SC-2**
- [ ] 22. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-2**

### Item 5 — SC-3: explicit threshold overrides the default

- [ ] 23. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing test asserting an explicit threshold value passed by the caller overrides the calibrated default. The test FAILS because the override-vs-default precedence is not yet distinguished. **→ SC-3**
- [ ] 24. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: preserve/verify the explicit-value override path wins over the default. **→ SC-3**
- [ ] 25. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: explicit-threshold consumers and prior SC-2 test unaffected. **→ non-regression for SC-3**
- [ ] 26. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify explicit value reaches the SQL filter unchanged and wins over the default. **→ SC-3**
- [ ] 27. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-3**

### Item 6 — SC-4: None after override re-engages the default

- [ ] 28. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing test asserting `threshold=None` restores the calibrated default after a prior explicit-override call. The test FAILS because no default exists to re-engage (pre-SC-2 state in the test's view) — the sticky-state guard is untested. **→ SC-4**
- [ ] 29. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: verify per-call statelessness — `None` re-engages the default after any override. **→ SC-4**
- [ ] 30. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: regression batch unaffected. **→ non-regression for SC-4**
- [ ] 31. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify override-then-`None` sequence re-engages the default with no sticky state. **→ SC-4**
- [ ] 32. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-4**

### Item 7 — SC-5: all-below-floor → ok + empty + deficiency message

- [ ] 33. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing edge-input test asserting that when all scores fall below the calibrated floor the seam returns `status=ok`, empty `results`, and the pinned deficiency message exactly: "No gloss results meet the sensitivity floor." (message text is a pinned constant, not an example). The test FAILS because below-floor rows are currently served as ranked results. **→ SC-5**
- [ ] 34. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: route the all-below-floor set through the existing empty-results branch shape (`ok` + message), consistent with the `.issues/36` R-7 pattern. **→ SC-5**
- [ ] 35. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: existing empty-results and status-machine tests unaffected. **→ non-regression for SC-5**
- [ ] 36. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify the below-floor outcome shape (ok + empty + message) against the edge-input matrix. **→ SC-5**
- [ ] 37. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-5**

### Item 8 — SC-6: all-below-floor never raises

- [ ] 38. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing edge-input test asserting the all-below-floor outcome never raises an exception. The test FAILS because the below-floor path is not yet handled in the normal return flow. **→ SC-6**
- [ ] 39. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: ensure the below-floor path returns normally (no exception) for any below-floor score distribution. **→ SC-6**
- [ ] 40. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: no new exception path introduced; prior tests pass. **→ non-regression for SC-6**
- [ ] 41. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify zero above-floor rows produce a normal return in the edge-input matrix. **→ SC-6**
- [ ] 42. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-6**

### Item 9 — SC-7: below-floor rows never served as ranked results

- [ ] 43. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing edge-input test asserting the all-below-floor outcome never serves below-floor rows as ranked results. The test FAILS because the default floor does not yet apply in the SQL filter path. **→ SC-7**
- [ ] 44. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: guarantee below-floor rows are excluded from results under the default path — the floor filter must actually apply for the default, not only for explicit thresholds. **→ SC-7**
- [ ] 45. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: full seam regression batch passes. **→ non-regression for SC-7**
- [ ] 46. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify results are empty whenever all scores are below the floor in the edge-input matrix. **→ SC-7**
- [ ] 47. **Commit (**direct**).** Stage and commit test + implementation together. **→ SC-7**

---

## Phase 2 VbC Completion Block

- [ ] Verify SC-2..SC-4: default-on-`None`, override precedence, override-then-`None` all verified against the seam contract.
- [ ] Verify SC-5..SC-7: below-floor outcome is ok + empty + message, exception-free, with no below-floor rows served.
- [ ] Verify R-3: signature and status enum unchanged; consumers untouched.
- [ ] Verify every commit is an atomic test+implementation slice and all prior tests pass.

**Concern transition:** Leaving seam semantics → entering UI threshold plumbing. Phase 3 syncs the UI default to the published floor engaged by the seam and verifies override passthrough against Phase 2 seam semantics.
