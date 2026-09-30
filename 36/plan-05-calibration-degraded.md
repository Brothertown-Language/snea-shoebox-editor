# Phase 5 — Degraded semantics (Item 7 only; Item 6 RETIRED)

**Concern:** ~~Verify the calibration anchor floors against freshly synced real data~~ (RETIRE 2026-09-29, developer directive — the model is vendor-trained and hash-pinned; the Sep 28 spike measurements in `tmp/spike-gte/` stand as the calibration evidence of record; no calibration pytest is delivered) and harden the seam's degraded status edge semantics — every degraded input yields the correct status+message, never an exception (R-7, SC-7, CG-3 part 2).

**Files:**
- ~~calibration module (new) + per-anchor evidence artifact (new)~~ — retired

**SCs:** SC-7 (behavioral) — SC-6 retired

**Dependencies:** Phase 4 — edge-matrix tests exercise the Phase 4 seam. SC-7 RED+GREEN+COMMIT completes inside this phase.

**Entry Conditions:**
- Phase 4 committed and VbC consolidated: seam green, dispatch entries routing
- Feature branch clean at Phase 4's last commit

**Exit Conditions:**
- ~~Calibration module passes on freshly synced real data~~ — RETIRED: spike artifacts (`tmp/spike-gte/`, measured 2026-09-28) stand as SC-6 evidence of record
- Degraded inputs produce empty_query/no_embeddings/stale_model/ok+empty statuses with messages naming the admin backfill remedy — zero exceptions across the edge matrix
- Commits per item

**Code Path Coverage:** P7 (search_semantic edge guards: strip query → empty/whitespace → status empty_query pre-model; no pinned rows → no_embeddings; pinned rows exist but only stale-model rows → stale_model; ranked list empty after threshold → ok + empty results; degraded messages name the admin backfill remedy), P9 (calibration pytest — encode anchors on freshly synced DB → per-anchor floors recorded → threshold 0.80 held)

**Cross-Cutting SCs:** SC-7 spans data exclusions + UX degradation contract + guard ordering — the remedy wording is the contract surface #1385 renders. SC-6 is single-concern (calibration).

**Interface Boundaries:** Seam contract frozen (Phase 4) — degraded status enum and message semantics are part of the same frozen surface #1385 consumes. Degraded messages name the admin backfill remedy; no threshold or widget surface added here.

**State Transitions:** Search query lifecycle degraded legs — received → empty_query (strip → empty/whitespace, checked BEFORE any model invocation, never an exception); received → no_embeddings (no embedded rows in either table); received → stale_model (embedded rows exist exclusively under a non-pinned embedding_model); ranked → ok_empty (all scores below threshold). Invariant: degraded states return designated status+message payloads, never exceptions; stale_model/no_embeddings messages name the admin backfill remedy.

**Cost frame:** Running the calibration and edge-matrix pytest suites costs minutes against real synced data. Skipping means an uncalibrated threshold ships and linguists tune blind — the correctness of the feature itself is unverifiable — and every missing-embedding state becomes a production support ticket, the highest-frequency failure surface.

---

- [ ] 45. **RETIRED — Item 6 steps 45-49 (2026-09-29, developer directive).** No calibration cycle is executed; steps 45-49 are removed. Spike artifacts stand as SC-6 evidence of record.
- [ ] 50. **pre-cleanup + R-12 re-sync + RED — Item 7 (**direct**, then **task-card**).** Clean Item 7 artifacts, re-sync the DB, then dispatch the red task for the degraded-status contract.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*` then `bash scripts/sync_prod_to_local.sh`
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — edge inputs (empty/whitespace query, no embedded rows, only stale-pin rows, all-below-threshold) raise exceptions or return wrong statuses instead of the designated payloads
  - Sub-bullet: SC reference — SC-7 (behavioral: pytest edge-input matrix on the service)
- [ ] 51. **GREEN — Item 7 (**task-card**).** Dispatch the green task: add the edge guards to `src/services/semantic_search_service.py` — guard empty/whitespace before any model invocation; pin-join exclusions for NULL/stale rows; statuses empty_query/no_embeddings/stale_model/ok+empty with messages naming the admin backfill remedy.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: guard order per the state-machine matrix — empty_query check is pre-model; degraded states never raise
  - Sub-bullet: SC reference — SC-7
- [ ] 52. **post-regression + verify — Item 7 (**task-card**).** Dispatch the phase-4 regression task and the verify task: pytest edge matrix vs the synced DB — every input yields the correct status+message, never an exception.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-7
- [ ] 53. **commit-inline — Item 7 (**direct**).** Commit the Item 7 test and edge handling as one atomic slice.
  - Sub-bullet: `git add src/services/semantic_search_service.py <test file> && git commit -m "issue#36: degraded status semantics with backfill remedy messages (SC-7)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 54. **Phase regression sweep (**task-card**).** Dispatch the phase-4 regression task once more after the Item 7 commit to confirm the SC-7 suite passes.
  - Sub-bullet: dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-*`

#### Phase 5 VbC

- ~~Calibration~~ — RETIRED: spike artifacts stand as SC-6 evidence of record; no deliverable.
- Degraded semantics: the edge matrix yields empty_query (pre-model), no_embeddings, stale_model, ok+empty — all with backfill-remedy messages, zero exceptions — SC-7 behavioral evidence recorded PASS.
- ~~Re-baseline procedure available and referenced by the calibration module for future distribution shifts (R-6).~~ — retired with Item 6; R-6 stands as record-of-evidence only.

**Concern transition:** Leaving calibration + degraded semantics → entering the data plane. Phase 6 depends on Phase 5's proven exclusion behavior (backfill recompute semantics) plus the encode substrate and schema.