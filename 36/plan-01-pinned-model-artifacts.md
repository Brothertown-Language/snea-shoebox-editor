# Phase 1 — Pinned model artifacts substrate

**Concern:** Commit the byte-pinned gte-small INT8 ONNX artifact and tokenizer at `models/gte-small/` byte-identical to the recorded SHA256 pins, with a hash check that fails on absence or mismatch (R-1, SC-1, CG-1 part 1).

**Files:**
- `models/gte-small/onnx/model_qint8_avx512_vnni.onnx` (new, committed bytes)
- `models/gte-small/tokenizer.json` (new, committed bytes)
- `scripts/` — artifact hash check (verification script)

**SCs:** SC-1 (structural)

**Dependencies:** None — first phase of the strict chain.

**Entry Conditions:**
- Coherence gate and baseline check passed (plan index pre-implementation steps)
- Pre-regression baseline captured and verified
- The recorded pins are: ONNX 34,118,638 bytes, SHA256 `c9434b8d71617919a3ef61f1fafea4b15b4e02d782cc287623158713881e34cd`; tokenizer.json 711,661 bytes, SHA256 `da0e79933b9ed51798a3ae27893d3c5fa4a201126cef75586296df9b4d2c62a0`

**Exit Conditions:**
- Both artifacts exist at `models/gte-small/` with the exact recorded sizes and SHA256 digests
- Hash check exits 0 against the recorded pins and exits non-zero on absent or mismatched artifacts
- Test and change committed as one atomic slice

**Code Path Coverage:** P9 (hash script half — sha256 of `models/gte-small/*` vs recorded pins)

**Cross-Cutting SCs:** None — SC-1 is single-concern (model substrate / artifact hash integrity).

**Interface Boundaries:** Models/gte-small/* committed bytes → consumed by the `embedding_service.py` load path in Phase 2; load errors must name the missing path.

**State Transitions:** None in this phase (dependency manifest and DB states begin in Phase 3).

**Cost frame:** Running the hash check costs seconds. Skipping means a corrupted or silently substituted model artifact ships — every embedding in the database is then wrong or irreproducible and weeks of calibration drift get diagnosed downstream.

---

- [ ] 5. **pre-cleanup (**direct**).** Remove stale artifacts for this step and downstream steps before starting the RED cycle.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-* ./tmp/issue-36/artifacts/pipeline-green-* ./tmp/issue-36/artifacts/pipeline-post-regression-* ./tmp/issue-36/artifacts/pipeline-verify-*`
  - Sub-bullet: SC reference — SC-1
- [ ] 6. **RED (**task-card**).** Dispatch `test-driven-development` red task: write the failing enforcement test for SC-1 — the hash check must FAIL when `models/gte-small/` artifacts are absent or byte-mismatched against the recorded pins.
  - Sub-bullet: dispatch string — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — absent artifacts, size drift, or any SHA256 mismatch vs the two 64-hex pins above
  - Sub-bullet: SC reference — SC-1 (structural: hash check script + exit-0 evidence)
- [ ] 7. **GREEN (**task-card**).** Dispatch `test-driven-development` green task: commit the ONNX artifact (34,118,638 B) and tokenizer.json (711,661 B) under `models/gte-small/` as byte-identical bytes, and add the `scripts/` hash check comparing sha256 digests against the recorded pins.
  - Sub-bullet: dispatch string — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: scope discipline — only the minimum change that makes the RED hash check pass; no tokenizer config, no service code
  - Sub-bullet: SC reference — SC-1
- [ ] 8. **post-regression + verify (**task-card**).** Dispatch `test-driven-development` phase-4 regression task, then dispatch `verification-before-completion` verify task to confirm the hash check exits 0 vs the recorded pins and produces the structural evidence artifact.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-*`
  - Sub-bullet: verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-verify-*`
  - Sub-bullet: SC reference — SC-1
- [ ] 9. **commit-inline (**direct**).** Stage and commit the test and change together as one atomic slice.
  - Sub-bullet: `git add models/gte-small/ scripts/ <test file> && git commit -m "issue#36: commit byte-pinned gte-small artifacts + SHA256 hash check (SC-1)"`
  - Sub-bullet: no co-author trailers during implementation commits — those are added during squash at PR time

#### Phase 1 VbC

- Artifact presence: `models/gte-small/onnx/model_qint8_avx512_vnni.onnx` and `models/gte-small/tokenizer.json` committed with exact recorded byte sizes.
- Hash integrity: hash check exit 0 vs both 64-hex pins; deliberate mismatch path still produces a non-zero exit (RED condition never silently disappears).
- SC-1 verdict recorded as PASS with structural evidence before Phase 2 begins.

**Concern transition:** Leaving pinned artifact substrate → entering embedding service substrate. Phase 2 depends on Phase 1's committed byte-pinned artifacts (the load path reads them; RED tests in Phase 2 exercise encode against these bytes).