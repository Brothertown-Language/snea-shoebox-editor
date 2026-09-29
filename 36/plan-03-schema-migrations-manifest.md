# Phase 3 — pgvector schema + DDL migrations + dependency manifest

**Concern:** Add the additive two-table pgvector schema models, append the two DDL-only versioned migrations with the pgvector extversion assertion, and correct the runtime dependency manifest with the memory-envelope profiler evidence (R-3, R-4, R-10, SC-3, SC-4, SC-10, CG-2).

**Files:**
- `src/database/models/search.py`
- `src/database/migrations.py`
- `pyproject.toml`
- profiler evidence artifact (batch-64 RSS vs 1 GiB envelope)

**SCs:** SC-3 (structural), SC-4 (behavioral), SC-10 (structural)

**Dependencies:** Phase 2 — migrations (SC-4) create the schema the ORM models (SC-3) declare; SC-10's profiler evidence consumes the Phase 2 encode path; the dependency manifest check unblocks every later runtime test cycle (`uv sync` with onnxruntime + tokenizers available).

**Entry Conditions:**
- Phase 2 committed: encode + singleton substrate green
- Phase 2 profiler artifact exists (worst-case resident-set references)

**Exit Conditions:**
- `models/search.py` declares GlossSearchEntry +3 columns and the new SemanticSearchEntry model + SemanticSearchResult dataclass, additive-only
- Two registry entries appended (YYYYMMDDSSSSS format) — CREATE TABLE semantic_search_entries, ALTER TABLE gloss_search_entries ADD COLUMN ×3 — with pgvector extversion assertion and reversible drops documented
- pyproject.toml runtime dependencies gain onnxruntime + tokenizers; sentence-transformers stays dev-only
- Profiler evidence artifact records batch-64 load+encode RSS vs the 1 GiB envelope
- Commits per item

**Code Path Coverage:** P6 (startup schema check → _MIGRATIONS version compare → apply pending in order → DDL → pgvector extversion assertion → idempotency via SchemaVersion row), P8 (dependency resolution → runtime group gains onnxruntime + tokenizers → RSS profile vs 1 GiB envelope)

**Cross-Cutting SCs:** None — SC-3 (schema concern only) and SC-4 (migrations concern only) are single-concern per the CC matrix; SC-10 is envelope verification riding substrate completion (CG-1 evidence).

**Interface Boundaries:** Schema boundary — ADDITIVE_COLUMNS + NEW_TABLE. `gloss_search_entries`: +embedding vector(384), +entry_type, +embedding_model (4 existing columns untouched, RESTRICT FK untouched); `semantic_search_entries`: id, record_id FK CASCADE, entry_type, term, embedding vector(384), embedding_model. The new table's CASCADE-vs-RESTRICT difference vs the live sibling is documented in the spec FK policy note — not altered. CREATE TABLE + ALTER TABLE DDL must match ORM column definitions exactly (schema/model parity for introspection tests).

**State Transitions:** Migration registry (SchemaVersion): pre-migration → table-created (apply entry N+1, CREATE TABLE, pgvector extversion asserted first) → columns-added (apply entry N+2, ALTER TABLE ×3); apply-in-order, rerun is a no-op, DDL-only — no data writes, no renumbering. Dependency manifest: pre-change → post-change (add onnxruntime + tokenizers).

**Cost frame:** Running schema introspection and the isolated migration test costs minutes. Skipping means a schema/model mismatch breaks every semantic query at runtime in production, and a non-idempotent or wrongly-versioned migration bricks startup for every environment simultaneously.

---

- [ ] 20. **pre-cleanup — Item 3 (**direct**).** Remove stale artifacts for the Item 3 cycle.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*`
  - Sub-bullet: SC reference — SC-3
- [ ] 21. **RED — Item 3 (**task-card**).** Dispatch the red task: write the failing schema introspection test asserting the `gloss_search_entries` +3 columns and the `semantic_search_entries` table (with record_id FK CASCADE) are absent from the synced DB.
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — columns/table absent or ORM declarations missing when introspecting against the model definitions
  - Sub-bullet: SC reference — SC-3 (structural: schema introspection after migration on synced DB)
- [ ] 22. **GREEN — Item 3 (**task-card**).** Dispatch the green task: extend `src/database/models/search.py` — GlossSearchEntry gains embedding vector(384), entry_type, embedding_model; add the SemanticSearchEntry model (record_id FK CASCADE, entry_type, term, embedding vector(384), embedding_model) and the SemanticSearchResult dataclass — additive-only, existing columns and RESTRICT FK untouched.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: only the minimum model additions; no migration logic changes in this item
  - Sub-bullet: SC reference — SC-3
- [ ] 23. **post-regression + verify — Item 3 (**task-card**).** Dispatch the phase-4 regression task and the verify task: schema introspection on the synced DB confirms the declared schema (structural evidence).
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: R-12 re-sync note — introspection runs against a DB where migrations have applied; final introspection evidence lands with Item 4's applied migrations
  - Sub-bullet: SC reference — SC-3
- [ ] 24. **commit-inline — Item 3 (**direct**).** Commit the Item 3 test and model additions as one atomic slice.
  - Sub-bullet: `git add src/database/models/search.py <test file> && git commit -m "issue#36: additive pgvector schema models (SC-3)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 25. **pre-cleanup + RED — Item 4 (**direct**, then **task-card**).** Clean Item 4 artifacts, then dispatch the red task for the migrations contract.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*`
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — migration version rows absent, target objects absent, or rerun non-idempotent
  - Sub-bullet: SC reference — SC-4 (behavioral: isolated migration test, #1346 flake-isolation pattern)
- [ ] 26. **GREEN — Item 4 (**task-card**).** Dispatch the green task: append 2 registry entries (YYYYMMDDSSSSS format) to `src/database/migrations.py` — CREATE TABLE semantic_search_entries and ALTER TABLE gloss_search_entries ADD COLUMN ×3 — with the pgvector extversion assertion and reversible DROP statements documented; DDL-only, no data writes, no renumbering.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: append-only registry per the in-file directive; DDL must match the ORM column definitions exactly (schema/model parity)
  - Sub-bullet: SC reference — SC-4
- [ ] 27. **post-regression + verify — Item 4 (**task-card**).** Dispatch the phase-4 regression task and the verify task: isolated migration test confirms the migrations applied once in order, version rows advanced, objects created, and rerun is a no-op.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-4
- [ ] 28. **commit-inline — Item 4 (**direct**).** Commit the Item 4 test and migration entries as one atomic slice.
  - Sub-bullet: `git add src/database/migrations.py <test file> && git commit -m "issue#36: DDL-only versioned migrations with pgvector extversion assert (SC-4)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 29. **pre-cleanup + RED — Item 10 (**direct**, then **task-card**).** Clean Item 10 artifacts, then dispatch the red task for the dependency manifest contract.
  - Sub-bullet: `rm -f ./tmp/issue-36/artifacts/pipeline-red-*`
  - Sub-bullet: dispatch — `task(..., prompt: "execute red task from test-driven-development")`
  - Sub-bullet: RED describes what fails — onnxruntime/tokenizers absent from the runtime dependency group, sentence-transformers present in runtime deps, or the profiler evidence artifact absent
  - Sub-bullet: SC reference — SC-10 (structural: dependency manifest check + profiler evidence artifact)
- [ ] 30. **GREEN — Item 10 (**task-card**).** Dispatch the green task: edit `pyproject.toml` to add onnxruntime + tokenizers to the runtime `dependencies` (version pins verified against the live registry at implementation time per guideline 070); sentence-transformers stays dev-only (already verified live — no change); produce the profiler evidence artifact measuring batch-64 load+encode RSS against the 1 GiB envelope using the Phase 2 singleton session.
  - Sub-bullet: dispatch — `task(..., prompt: "execute green task from test-driven-development")`
  - Sub-bullet: measured reference for the profile is 312 MiB RSS; R-2 worst-case resident-set references (~128 MB gte-small INT8 / ~472 MB e5-small / ~520 MB both-resident) recorded as evidence context — the 1 GiB envelope assertion itself is unchanged
  - Sub-bullet: SC reference — SC-10
- [ ] 31. **post-regression + verify — Item 10 (**task-card**).** Dispatch the phase-4 regression task and the verify task: manifest check confirms onnxruntime + tokenizers in runtime deps and sentence-transformers dev-only; profiler artifact confirms the envelope fit. Run `uv sync` so the corrected runtime deps are installed for Phase 4+ test cycles.
  - Sub-bullet: regression dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; verify dispatch — `task(..., prompt: "execute verify task from verification-before-completion")`; pre-clean both artifact sets
  - Sub-bullet: SC reference — SC-10
- [ ] 32. **commit-inline — Item 10 (**direct**).** Commit the Item 10 test/manifest change and evidence as one atomic slice.
  - Sub-bullet: `git add pyproject.toml <test file> <evidence artifact> && git commit -m "issue#36: runtime deps onnxruntime + tokenizers, profiler envelope evidence (SC-10)"`
  - Sub-bullet: no co-author trailers during implementation commits
- [ ] 33. **Phase regression sweep (**task-card**).** Dispatch the phase-4 regression task once more after the Item 10 commit to confirm SC-3, SC-4, and SC-10 suites pass together.
  - Sub-bullet: dispatch — `task(..., prompt: "execute phase-4 task from test-driven-development")`; pre-clean: `rm -f ./tmp/issue-36/artifacts/pipeline-post-regression-*`
- [ ] 34. **Phase VbC consolidation (**direct**).** Confirm the SC-3 introspection evidence, SC-4 migration evidence, and SC-10 manifest+profiler evidence are all recorded PASS before Phase 4 begins.
  - Sub-bullet: any missing evidence artifact re-runs its verify dispatch before proceeding

#### Phase 3 VbC

- Schema parity: introspection shows exactly the declared +3 columns and new table with CASCADE FK; existing 4 columns and RESTRICT FK untouched — SC-3 structural evidence recorded PASS.
- Migration behavior: apply-in-order, version rows advanced, rerun no-op, extversion assertion present — SC-4 behavioral evidence recorded PASS.
- Dependency envelope: onnxruntime + tokenizers in runtime deps, sentence-transformers dev-only, profiler artifact under 1 GiB — SC-10 structural evidence recorded PASS.
- `uv sync` state current for all later phases.

**Concern transition:** Leaving pgvector schema + migrations + manifest → entering the search semantic seam + mode dispatch. Phase 4 depends on Phase 3's applied schema (seam queries the columns/table) and Phase 2's encode/session substrate.