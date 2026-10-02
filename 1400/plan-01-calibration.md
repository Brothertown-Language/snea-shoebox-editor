# Phase 1 — Real-data calibration of the semantic-seam default floor

**Concern:** calibration (SC-1); recall-regression (SC-8, SC-8a) — per concern-map.yaml

**Files:**
- calibration evidence artifact (new — per-anchor floors + provenance)
- `src/services/semantic_search_service.py` (module-level named calibration constant only; seam behavior unchanged in this phase)
- new pytest calibration test module (calibration module per SC evidence test)

**SCs:** SC-1, SC-8, SC-8a

**Dependencies:** None (first phase)

**Entry Conditions:**
- Plan coherence gate (step 1) and baseline check (step 2) PASS
- Production replica synced and freshly verified (6,681 embedded glosses, pin `thenlper/gte-small`)
- Feature branch exists; existing seam tests pass (baseline)

**Exit Conditions:**
- Calibration evidence artifact published with per-anchor floor values and full provenance (query battery, corpus pin, date) for both in-corpus and out-of-corpus batteries; no synthetic queries
- Named calibration constant published in the seam module: float strictly in (0.9018, 0.9753)
- Floor-clearing in-corpus battery anchors (water / beaver / money / gun / book) rank at rank 1 with cosine ≥ published floor under the default threshold (no recall regression); anchor "how many" (0.8917) returns the below-floor empty outcome per SC-5 semantics (documented measured behavior, not regression)

**Code Path Coverage:**
- SC-1: calibration module (pytest) + calibration evidence artifact — calibration runs on the production replica via the same encode/query path the seam uses (`embedding_service` encode → cosine ranking); no `src/` behavior change in this phase
- SC-8: calibration evidence artifact + production replica probe — recall regression battery over in-corpus floor-clearing anchors (water / beaver / money / gun / book) asserted at rank 1 with cosine ≥ published floor
- SC-8a: calibration evidence artifact + production replica probe — "how many" (0.8917) asserted to return the below-floor empty outcome (SC-5 semantics, pinned message), not a rank-1 serve

**Cross-Cutting SCs:**
- SC-2 spans calibration and seam concerns — the Phase 2 seam change consumes the constant published here
- SC-8/SC-8a span calibration and seam concerns — the regression battery exercises the seam under the default floor while evidence lives in the calibration artifact

**Interface Boundaries:**
- `embedding_service.encode()` / PIN `thenlper/gte-small` — read-only dependency, untouched
- Seam public signature untouched in this phase; the calibration constant is additive

**State Transitions:**
- Unmeasured → measured/published calibration constant with provenance (durable evidence artifact replaces the removed session-local probe scratch)

**Cost frame:** Deriving and committing the calibration evidence artifact costs one calibration battery run plus pytest execution — minutes. Skipping provenance recording costs unauditability: every downstream SC rests on an untraceable number and the calibration must be re-derived from scratch when challenged, at 10×–100× the discovery-latency cost.

---

## Step-by-step

### Item 1 — SC-1: calibration anchors with per-anchor floors and provenance

- [ ] 3. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing test asserting the calibration evidence artifact exists with per-anchor floor values plus source provenance (query battery, corpus pin, date) for both the in-corpus and out-of-corpus batteries — no synthetic queries. The test FAILS because no calibration evidence artifact exists yet. **→ SC-1**
- [ ] 4. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: derive calibration anchors from real corpus queries against the production replica; record per-anchor floors with provenance in the calibration evidence artifact and publish the named calibration constant (strictly between 0.9018 and 0.9753, per the measured probe `tmp/1400/artifacts/verification-probe.yaml`). Minimum change only. **→ SC-1**
- [ ] 5. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: run existing regression patterns — the seam module gained only an additive constant; all prior seam/UI tests must still pass. **→ non-regression for SC-1**
- [ ] 6. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify the evidence artifact carries per-anchor floors + provenance and the constant respects the interval constraint. **→ SC-1**
- [ ] 7. **Commit (**direct**).** Stage and commit the test, the evidence artifact, and the calibration constant together as one atomic slice (no co-author trailers). **→ SC-1**

### Item 2 — SC-8: floor-clearing anchors recall regression under the default floor

- [ ] 8. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing calibration-battery check asserting floor-clearing in-corpus anchors (water / beaver / money / gun / book) rank at rank 1 with cosine ≥ published floor under the default threshold. The test FAILS because the default-floor engagement does not exist yet. **→ SC-8**
- [ ] 9. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: run the battery over the published constant; confirm every floor-clearing in-corpus anchor (water / beaver / money / gun / book) lands at rank 1 with cosine ≥ published floor; record baseline-vs-post-change evidence in the calibration artifact. **→ SC-8**
- [ ] 10. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: full regression batch — no existing behavior regressed by the published constant. **→ non-regression for SC-8**
- [ ] 11. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify battery evidence shows rank 1 with cosine ≥ published floor per floor-clearing anchor, sourced from the production replica probe. **→ SC-8**
- [ ] 12. **Commit (**direct**).** Stage and commit the battery test and artifact update together. **→ SC-8**

### Item 3 — SC-8a: below-floor anchor "how many" returns the honest empty outcome

- [ ] 13. **RED (**task-card**).** Dispatch the red task from test-driven-development: write a failing calibration-battery check asserting anchor "how many" (0.8917) returns the below-floor empty outcome under the default floor (`ok` + empty results + pinned SC-5 message "No gloss results meet the sensitivity floor.") — not a rank-1 serve. The test FAILS because the below-floor outcome is not yet implemented. **→ SC-8a**
- [ ] 14. **GREEN (**task-card**).** Dispatch the green task from test-driven-development: run the battery over the published constant; confirm "how many" returns the below-floor empty outcome with the pinned message; record the documented-overlap evidence in the calibration artifact. **→ SC-8a**
- [ ] 15. **Post-regression (**task-card**).** Dispatch the phase-4 task from test-driven-development: full regression batch — no existing behavior regressed. **→ non-regression for SC-8a**
- [ ] 16. **Verify (**task-card**).** Dispatch the verify task from verification-before-completion: verify battery evidence shows "how many" below-floor empty with pinned message, sourced from the production replica probe. **→ SC-8a**
- [ ] 17. **Commit (**direct**).** Stage and commit the battery test and artifact update together. **→ SC-8a**

---

## Phase 1 VbC Completion Block

- [ ] Verify SC-1: evidence artifact exists with per-anchor floors + provenance, zero synthetic queries.
- [ ] Verify SC-8: battery regression check passes — rank 1, cosine ≥ published floor for every floor-clearing in-corpus anchor under the default.
- [ ] Verify SC-8a: "how many" (0.8917) returns the below-floor empty outcome with the pinned SC-5 message — documented measured behavior, not recall regression.
- [ ] Verify no `src/` seam behavior changed in this phase (constant is additive; signature untouched).
- [ ] Verify both commits contain test + artifact + constant as atomic slices.

**Concern transition:** Leaving calibration → entering seam default-floor semantics. Phase 2 consumes the module-level calibration constant published by Phase 1; its RED tests fail without it.
