# Phase 4 — Search semantic seam + mode dispatch

**Concern:** Implement the `search_semantic()` v1 contract service and the additive `SearchMode` widening with dispatch entries routing the two new modes to the seam (R-5, R-13, SC-5, SC-11, CG-3 part 1).

**Files:**
- `src/services/semantic_search_service.py` (new)
- `src/services/linguistic_service.py`

**SCs:** SC-5 (behavioral), SC-11 (behavioral)

**Dependencies:** Phases 1, 2, 3 — seam tests need the schema columns/table (Phase 3) and encode (Phase 2). SC-11 widening and SC-5 seam GREEN both live here; no triplet split.

**Entry Conditions:**
- Phase 3 committed and VbC consolidated: migrations applied on the synced DB, ORM models current
- `uv sync` state current (onnxruntime + tokenizers installed)

**Exit Conditions:**
- `search_semantic(mode ∈ {'gloss','all'}, query, threshold=None, source_id=None, limit=None) → SemanticSearchResult` returns the full ranked list desc cosine with record_id-asc tie-break, threshold-filtered (None → 0.80), excluding NULL/stale rows via the pin join; service never imports streamlit
- `SearchMode` Literal widened additively with 'Semantic Gloss'/'Semantic All'; both dispatch entries route to `search_semantic()`; existing four modes, `search_records` signature, and `RecordSearchResult` return type unchanged
- Both pytest suites green; commits per item

**Code Path Coverage:** P1 (search_records(mode='Semantic Gloss'|'Semantic All') → _search_strategies dispatch → search_semantic; anchors: SearchMode Literal and _search_strategies map in `linguistic_service.py`), P2 (search_semantic → load_model() singleton session → encode(query) → cosine rank over gloss_search_entries ∪ semantic_search_entries with the embedding_model == pin join guard → threshold filter → SemanticSearchResult)

**Cross-Cutting SCs:** SC-5 spans data access + ranking correctness + contract design (consumes the Phase 2 singleton + Phase 3 schema; the SemanticSearchResult dataclass is the surface #1385 binds to). SC-11 is single-concern (dispatch seam).

**Interface Boundaries:** search_semantic() seam — NEW_ADDITIVE: `search_semantic(mode: 'gloss'|'all', query: str, threshold: float|None=None, source_id: int|None=None, limit: int|None=None) → SemanticSearchResult{results: list[(record_id, score)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message: str}`. SearchMode Literal — EXTEND_ONLY: Literal['Lexeme','FTS','Headword','Gloss','Semantic Gloss','Semantic All'], additive widening, no removals, existing four modes dispatch unchanged. Consumers: `_search_strategies` dispatch entries, UI spec #1385 (cross-spec: the field list and degraded status enum are frozen here).

**State Transitions:** Search query lifecycle (ranked leg): received → ranked when pinned rows exist and the query is non-empty — encode + cosine rank desc, tie-break record_id asc, threshold filter (None → 0.80). Degraded legs are Phase 5 scope.

**Cost frame:** Running the seam and dispatch pytest suites costs minutes. Skipping means the contract the whole UI spec binds to is wrong — cross-spec rework — and 'Semantic Gloss'/'Semantic All' modes exist in the type but are unreachable (or route to a wrong strategy), silently dead for every consumer.

---

- [ ] 35. **pre-cleanup + R-12 re-sync — Item 5 (**direct**).** Clean Item 5 artifacts and re-sync the regression database from production before the SC-5 test cycle.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*` then `bash scripts/sync_prod_to_local.sh` (from the branch under test)
  - Sub-bullet: R-12 gate — sync replication carries embeddings; local DB never re-embeds during tests
  - Sub-bullet: SC reference — SC-5
- [ ] 36. **RED — Item 5 (**task-card**).** Dispatch the red task: write the failing pytest asserting the seam — `search_semantic` absent, incorrect status enum, wrong ranking order/tie-break, missing pin-join exclusion, or a streamlit import in the service module.
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — seam absent or any v1 contract deviation (field list exact: results, status, message; status values ok/empty_query/no_embeddings/stale_model)
  - Sub-bullet: SC reference — SC-5 (behavioral: service-layer pytest vs freshly synced DB)
- [ ] 37. **GREEN — Item 5 (**task-card**).** Dispatch the green task: implement `src/services/semantic_search_service.py` — encode the query via the singleton session, cosine rank over both tables with the pin join (embedding_model == pin), threshold filter (None → 0.80), full ranked list desc with record_id-asc tie-break, returning SemanticSearchResult; no streamlit imports.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: both tables ranked together (gloss + semantic entries); NULL and stale-pin rows excluded identically at query time
  - Sub-bullet: SC reference — SC-5
- [ ] 38. **post-regression + verify — Item 5 (**task-card**).** Dispatch the phase-4 regression task and the verify task: pytest service-layer confirms ranked order, tie-break, threshold default, pin-join exclusion, and the exact contract field list against the freshly synced DB.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-5
- [ ] 39. **commit-inline — Item 5 (**direct**).** Commit the Item 5 test and seam service as one atomic slice.
  - Sub-bullet: `git add src/services/semantic_search_service.py <test file> && git commit -m "issue#36: search_semantic v1 seam per contract (SC-5)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 40. **pre-cleanup + RED — Item 11 (**direct**, then **task-card**).** Clean Item 11 artifacts, then dispatch the red task for the dispatch-routing contract.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*`
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — 'Semantic Gloss'/'Semantic All' absent from the SearchMode Literal or unmatched by the dispatch map
  - Sub-bullet: SC reference — SC-11 (behavioral: pytest dispatch routing)
- [ ] 41. **GREEN — Item 11 (**task-card**).** Dispatch the green task: widen the SearchMode Literal in `src/services/linguistic_service.py` additively with 'Semantic Gloss'/'Semantic All' and add the dispatch entries routing both modes to `search_semantic()` — existing strategies, the `search_records` signature, and the `RecordSearchResult` return type unchanged.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: additive only — the companion contract obligations (existing modes unchanged, no signature/return-type change) are verified in this same GREEN
  - Sub-bullet: SC reference — SC-11
- [ ] 42. **post-regression + verify — Item 11 (**task-card**).** Dispatch the phase-4 regression task and the verify task: pytest dispatch-routing confirms the two semantic modes route to `search_semantic()` and the existing four modes route unchanged (Lexeme/FTS/Headword/Gloss strategies untouched; search_records signature unchanged).
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-11
- [ ] 43. **commit-inline — Item 11 (**direct**).** Commit the Item 11 test and widening change as one atomic slice.
  - Sub-bullet: `git add src/services/linguistic_service.py <test file> && git commit -m "issue#36: additive SearchMode widening + semantic dispatch entries (SC-11)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 44. **Phase regression sweep (**task-card**).** Dispatch the phase-4 regression task once more after the Item 11 commit to confirm SC-5 and SC-11 suites pass together.
  - Sub-bullet: dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-*`

#### Phase 4 VbC

- Seam contract: full ranked list desc cosine, record_id-asc tie-break, None → 0.80 threshold, pin-join exclusion, exact SemanticSearchResult field list, zero streamlit imports — SC-5 behavioral evidence recorded PASS.
- Dispatch contract: both semantic modes present in the widened Literal and routed to `search_semantic()`; four existing modes route unchanged; signature/return type intact — SC-11 behavioral evidence recorded PASS.
- Cross-spec surface frozen: the seam field list + status enum #1385 consumes are exactly the implemented contract.

**Concern transition:** Leaving search semantic seam + dispatch → entering calibration + degraded semantics. Phase 5 depends on Phase 4's seam — calibration runs the anchors through it and edge guards harden it.