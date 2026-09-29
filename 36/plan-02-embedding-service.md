# Phase 2 — Embedding service substrate (encode + singleton)

**Concern:** Implement the `embedding_service` encode pipeline and the load-once process-wide session singleton — module-level holder inside `embedding_service.py`, streamlit-import-free, race-safe under a one-at-a-time in-flight lock (R-2, R-14, SC-2, SC-12, CG-1 parts 2-3).

**Files:**
- `src/services/embedding_service.py` (new)

**SCs:** SC-2 (behavioral), SC-12 (behavioral)

**Dependencies:** Phase 1 — encode tests exercise the committed byte-identical ONNX + tokenizer.json artifacts. RED/GREEN/COMMIT for both SCs stay inside this phase.

**Entry Conditions:**
- Phase 1 committed: byte-pinned artifacts pass the hash check
- Feature branch clean at Phase 1's commit

**Exit Conditions:**
- `encode(texts, batch≤64)` returns float32 (1,384) unit-norm vectors via tokenize(512) → onnxruntime → attention-mask mean-pool → L2-normalize, with error handling that raises contextually
- `load_model()` returns a process-wide single `onnxruntime.InferenceSession` (module-level holder, streamlit-import-free) and N concurrent calls converge to the identical session handle under the one-at-a-time in-flight lock
- Both pytest suites green; commits per item

**Code Path Coverage:** P3 (encode pipeline: tokenizer(512, truncation) → InferenceSession.Run on the module-level singleton under the in-flight lock → attention-mask mean-pool → L2-normalize → float32 (N,384))

**Cross-Cutting SCs:** SC-2 spans model substrate + numerical correctness + performance; SC-12 spans process lifecycle + concurrency + memory envelope (CC matrix). Encode invariants are reused by SC-5/SC-6/SC-8 callers in later phases.

**Interface Boundaries:** Module import graph — `embedding_service` is a NEW_LEAF_MODULE: imports no streamlit (verified at import time); exposes `encode(texts, batch≤64)` and `load_model() → onnxruntime.InferenceSession` (singleton). Consumers in later phases: `semantic_search_service` (SC-5), `upload_service.populate_search_entries` (SC-8), `table_maintenance` backfill method (SC-9).

**State Transitions:** Embedding model (process): not_loaded → loaded on first `load_model()` call — acquires in-flight lock, session constructed from committed ONNX bytes; loaded session persists for process lifetime, never evicted per-thread/per-session; concurrent `Run()` calls on the shared session are thread-safe (spike-verified 2026-09-29: 8 threads, deterministic outputs).

**Cost frame:** Running the vector and concurrency tests costs minutes. Skipping means malformed or denormalized vectors silently poison every cosine ranking — discovered only through user-visible nonsense results — and a per-session model load multiplies ~128 MB of resident memory per concurrent user until the container OOMs under modest real-user concurrency.

---

- [ ] 10. **pre-cleanup (**direct**).** Remove stale artifacts for the Item 2 RED cycle.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*`
  - Sub-bullet: SC reference — SC-2
- [ ] 11. **RED (**task-card**).** Dispatch `test-driven-development` red task: write the failing pytest asserting `embedding_service.encode` — shape (1,384) float32, norm == 1.0, batch-64 padding path, contextual error raising on invalid input.
  - Sub-bullet: dispatch string — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — encode() absent, wrong dtype/shape, non-unit norm, or a padding path that fails at batch ≤64
  - Sub-bullet: SC reference — SC-2 (behavioral: pytest run asserting the encode pipeline output)
- [ ] 12. **GREEN (**task-card**).** Dispatch `test-driven-development` green task: implement `src/services/embedding_service.py` encode() per the R-2 invariants — tokenize with max length 512 and truncation, onnxruntime inference, attention-mask mean-pool, L2-normalize, float32 output; raise contextual errors on invalid input (fail-fast, no silent skip).
  - Sub-bullet: dispatch string — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: module must remain streamlit-import-free; only the minimum change that makes the RED test pass
  - Sub-bullet: SC reference — SC-2
- [ ] 13. **post-regression + verify (**task-card**).** Dispatch `test-driven-development` phase-4 regression task and the `verification-before-completion` verify task for Item 2 — pytest unit confirms shape (1,384), norm 1.0, batch-64 padding path against the Phase 1 artifacts.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-* ./tmp/issue-36/artifacts/pipeline-verify-*`
  - Sub-bullet: SC reference — SC-2
- [ ] 14. **commit-inline (**direct**).** Commit the Item 2 test and implementation as one atomic slice.
  - Sub-bullet: `git add src/services/embedding_service.py <test file> && git commit -m "issue#36: embedding_service encode pipeline per R-2 invariants (SC-2)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 15. **pre-cleanup + RED — Item 12 (**direct**, then **task-card**).** Clean Item 12 artifacts, then dispatch the red task for the singleton contract.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*`
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — `load_model()` absent, returns distinct sessions across calls, or N concurrent calls produce more than one session handle; import-time streamlit detection also fails the test
  - Sub-bullet: SC reference — SC-12 (behavioral: pytest concurrency, registry count == 1)
- [ ] 16. **GREEN — Item 12 (**task-card**).** Dispatch the green task: implement `load_model()` returning a process-wide singleton session held at module level in `embedding_service.py` with a single one-at-a-time in-flight lock around any (re)load — never per-thread/per-session loads. Verify the encode-invariant companion obligations in the same GREEN (encode exercised against the singleton session).
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: lock idiom — one-at-a-time in-flight `threading.Lock` guarding (re)load, the same idiom the admin backfill requires; no `@st.cache_resource` (module stays streamlit-import-free)
  - Sub-bullet: SC reference — SC-12
- [ ] 17. **post-regression + verify — Item 12 (**task-card**).** Dispatch the phase-4 regression task and the verify task: pytest concurrency confirms N threads calling `load_model()` → identical session handle, registry count == 1; profiler artifact records the measured worst-case resident-set (model load + batch-64 encode) vs the R-14 references and the 1 GiB envelope.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-* ./tmp/issue-36/artifacts/pipeline-verify-*`
  - Sub-bullet: profiler artifact feeds Phase 3 Item 10 (SC-10) evidence
  - Sub-bullet: SC reference — SC-12
- [ ] 18. **commit-inline — Item 12 (**direct**).** Commit the Item 12 test and singleton implementation as one atomic slice.
  - Sub-bullet: `git add src/services/embedding_service.py <test file> && git commit -m "issue#36: load-once process-wide session singleton with in-flight lock (SC-12)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 19. **Item 12 post-regression sweep (**task-card**).** Dispatch the phase-4 regression task once more after the Item 12 commit to confirm both SC-2 and SC-12 suites pass together.
  - Sub-bullet: dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-*`

#### Phase 2 VbC

- Encode contract: pytest confirms float32 (1,384), norm == 1.0, batch-64 padding path, contextual errors — SC-2 behavioral evidence recorded PASS.
- Singleton contract: pytest concurrency confirms identical session handle and registry count == 1 across N threads — SC-12 behavioral evidence recorded PASS.
- Import hygiene: `embedding_service.py` imports no streamlit (asserted at import time).
- Both commits present on the feature branch; profiler artifact available for Phase 3.

**Concern transition:** Leaving embedding service substrate → entering pgvector schema + migrations + manifest. Phase 3 depends on Phase 2's encode/session substrate (the SC-10 profiler evidence consumes the encode path; migration tests need the schema models that consume the pin string).