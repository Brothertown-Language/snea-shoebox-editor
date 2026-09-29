# [SPEC] Algonquian term-space semantic search — end-user interface (records page modes, threshold, scores, pagination, empty states)

**Stub — pending full spec body generation.** This issue is the UI half of the term-space split; the full spec body (Intent / Not-Included / SC table / requirements / traceability) will be generated via the spec-creation pipeline and replace this stub.

**Sibling specs:**

- #1385 — gloss-space end-user interface (records page modes UI; the pattern this stub extends for term-space)
- #1386 — term-space backend/db spec; this stub binds to its `search_terms` seam contract

**Binding contract (from #1386):** `search_terms` seam — `TermSearchResult{results: list[(record_id, score, entry_type, language_code, source_id, term)], status ∈ {ok, empty_query, no_embeddings, stale_model}, message}`

**Scope (UI layer only — summary; full scope at spec generation):**

- Two new mode entries in the records-page search mode radio
- Per-user threshold preference via PreferenceService
- Score display on term-space modes only
- Pagination slicing of the full ranked list
- Empty-state rendering per status, incl. `stale_model` naming the term-space admin backfill remedy

**Constraint:** No pgvector/ORM imports in the UI layer — the UI consumes only the `search_terms` seam.

🤖 OpenCode (ollama-cloud/glm-5.3-flash) created