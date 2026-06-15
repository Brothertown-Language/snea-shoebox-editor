STATUS: 1.4 (REVISED - NEEDS APPROVAL)
CREATED: 2026-03-29
REVISED: 2026-06-13 — Added Documentation Sources table per modern spec standards (previous revision: 2026-05-22)
REVISED: 2026-06-13 — Added Decision Ledger, Risk Traceability, Out of Scope, and Constraints sections per modern spec standards

---

## Executive Summary

Add semantic search for English gloss fields using vector embeddings stored in PostgreSQL. Enables finding "round object" when searching "spherical", or locating glosses by related concepts. Constraint: solution must work identically on local `pgserver` (embedded PostgreSQL 16.2) and production PostgreSQL. Both environments already support `pgvector` extension. Requires a small embedding model (~22MB) committed to the repository for offline-first operation.

---

## Problem

Issue #23 provides exact-match search for glosses and headwords, but linguists often search with synonyms or related terms:

- Searching "round" should find records with gloss "spherical object"
- Searching "container" should find records with gloss "vessel"
- Searching "he hunts" should find records with example translation "he hunts deer"

Full-text search (FTS) and LIKE queries cannot capture semantic similarity.

---

## Proposed Solution

Implement vector-based semantic search using:

1. **Embedding model** committed to `models/` directory (22MB)
2. **pgvector extension** for PostgreSQL vector storage and similarity search (already available in pgserver 16.2 and Aiven production)
3. **sentence-transformers** for server-side embedding generation
4. **Vectors on SearchEntry** for granular per-field semantic matching

### Architecture

| Component | Production | Local pgserver |
|-----------|------------|----------------|
| Database | PostgreSQL 17 + pgvector | PostgreSQL 16.2 + pgvector (bundled) |
| Embeddings | `vector(384)` on SearchEntry | `vector(384)` on SearchEntry |
| Model | `models/all-MiniLM-L6-v2` | Same (git-committed) |
| Similarity | `pgvector` cosine search | `pgvector` cosine search |
| Query | Same SQL | Same SQL |

**Key point:** Both environments support pgvector identically. No fallback required.

## Decision Ledger

| DEC-ID | Decision | Rationale | Requirement Key | Affected SCs |
|--------|----------|-----------|-----------------|--------------|
| DEC-1 | Use `vector(384)` with all-MiniLM-L6-v2 model | Small footprint (~22MB), adequate for gloss-level semantic search, works identically on local pgserver and production PostgreSQL | MUST | SC-1, SC-2, SC-3 |
| DEC-2 | Store embeddings on SearchEntry table rather than separate embedding table | Granular per-field semantic matching; same table as exact-match search simplifies query routing | MUST | SC-6, SC-9 |
| DEC-3 | Cosine similarity via pgvector `<=>` operator | Standard similarity metric for sentence embeddings; matches all-MiniLM-L6-v2 training objective | MUST | SC-4, SC-5 |
| DEC-4 | Embedding model committed to `models/` directory | Offline-first operation; no external API dependency at inference time | MUST | SC-7 |
| DEC-5 | sentence-transformers for server-side embedding generation | Well-integrated with all-MiniLM-L6-v2; handles batching, Unicode, and truncation natively | MUST | SC-8 |
| DEC-6 | Semantic search limited to direct gloss fields only | Excludes definitions (`\de`), usage notes (`\ue`), and national language fields — these are not glosses | MUST | SC-1, SC-2, SC-3 |
| DEC-7 | Default similarity threshold 0.7 | Conservative default balances recall vs precision; user-adjustable via UI slider | SHOULD | SC-5 |

---

## Risk Traceability

| RISK-ID | Risk | Likelihood | Impact | Mitigation | Verifying SC |
|---------|------|------------|--------|------------|--------------|
| RISK-1 | Model not found at startup | Low | High | Startup fails with clear error message; model committed to repo | SC-7 |
| RISK-2 | pgvector extension unavailable on target environment | Low | High | Migration checks extension availability; informative error on missing extension | SC-10, SC-11 |
| RISK-3 | Embedding quality too low for useful results | Medium | Medium | Similarity threshold tunable via UI slider; default 0.7 conservatively low | SC-1, SC-4, SC-5 |
| RISK-4 | Long gloss text exceeds model token limit (512) | Medium | Low | Truncate to 512 tokens with warning log | SC-8 |
| RISK-5 | Performance regression on bulk backfill | Medium | Medium | Batch embedding with progress tracking; page-size batching for DB writes | SC-8 |
| RISK-6 | Empty database semantic search crashes | Low | High | Empty query returns empty results, not error | SC-12, SC-13 |

---

## Indexable Fields (Direct Glosses Only)

Only fields that are **direct glosses for terms or sentences** are indexed:

| Marker | Description | entry_type | Included |
|--------|-------------|------------|----------|
| `\ge` | Gloss (English) - primary | `ge` | ✓ |
| `\ge` in `\se` | Subentry gloss | `ge_subentry` | ✓ |
| `\ge` in `\cf` | Sense gloss | `ge_sense` | ✓ |
| `\ge` in `\sn` | Gloss in sense block | `ge_in_sense` | ✓ |
| `\xe` | Example translation (English) | `xe` | ✓ |
| `\ce` | Cross-ref gloss (English) | `ce` | ✓ |
| `\eg` | Etymology gloss | `eg` | ✓ |

**Excluded (not direct glosses):**
- `\de` — Definition (explanation, not gloss)
- `\ue` — Usage notes (contextual, not gloss)
- `\nt` — General notes (mixed content)
- `\ng` — Grammar notes (technical, not gloss)
- `\dn`, `\gn`, `\xn` — National language fields (non-English)

---

## Search Modes

| Mode | Search Scope | entry_type filter |
|------|--------------|-------------------|
| **Gloss** (exact) | Primary `\ge` only | `ge` |
| **Semantic Gloss** | Primary `\ge` only (vector) | `ge` |
| **Semantic All** | All gloss fields (vector) | `ge`, `ge_subentry`, `ge_sense`, `ge_in_sense`, `xe`, `ce`, `eg` |

---

## Files Affected

| File | Change |
|------|--------|
| `models/all-MiniLM-L6-v2/` | Model files (git-committed) |
| `src/services/embedding_service.py` | New file — model loading, embedding generation |
| `src/services/linguistic_service.py` | Add `search_semantic_primary()`, `search_semantic_all()` |
| `src/services/upload_service.py` | Index gloss fields with embeddings |
| `src/database/models/search.py` | Add `embedding` column (Vector type) |
| `src/database/migrations.py` | Add vector column, enable pgvector |
| `src/frontend/pages/records.py` | Add "Semantic Gloss" and "Semantic All" radio buttons |
| `tests/services/test_embedding.py` | Tests for embedding service |
| `tests/services/test_semantic_search.py` | Tests for semantic search |
| `pyproject.toml` | Add `pgvector`, `sentence-transformers` dependencies |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `sentence-transformers` | ^2.2 | Embedding generation |
| `pgvector` | ^0.2 | PostgreSQL vector operations |

---

## Constraints

| Constraint | Detail |
|------------|--------|
| Offline-first operation | Embedding model must be committed to repo; no external API at inference time |
| Cross-environment parity | Solution must work identically on local pgserver (PostgreSQL 16.2) and production (PostgreSQL 17) |
| Model size limit | Model must be small enough to commit to git repository (~22MB target) |
| Backward compatibility | Existing exact-match search modes must remain unaffected |
| No external API dependency | Embedding generation must not require network access at runtime |

---

## Success Criteria

| SC | Test | Expected Result | Evidence Type |
|-----|------|-----------------|----------------|
| SC-1 | `test_semantic_primary_finds_synonyms` # SC-1 | Search "round" in Semantic Gloss mode finds records with "spherical", "circular" glosses | behavioral |
| SC-2 | `test_semantic_all_finds_cross_field` # SC-2 | Search "container" in Semantic All mode finds records with "vessel" in any gloss field | behavioral |
| SC-3 | `test_semantic_all_finds_example_translation` # SC-3 | Search "hunt" in Semantic All mode finds records with "he hunts" in `\xe` field | behavioral |
| SC-4 | `test_synonym_similarity_threshold` # SC-4 | Exact synonym match has similarity > 0.8 | behavioral |
| SC-5 | `test_unrelated_term_low_similarity` # SC-5 | Unrelated term has similarity < 0.5 | behavioral |
| SC-6 | `test_empty_gloss_no_embedding` # SC-6 | Empty gloss field results in no embedding stored, excluded from search | structural |
| SC-7 | `test_embedding_service_loads_model` # SC-7 | `get_model()` loads and returns SentenceTransformer from `models/all-MiniLM-L6-v2` | structural |
| SC-8 | `test_embed_text_returns_vector` # SC-8 | `embed_text("test")` returns list of 384 floats | structural |
| SC-9 | `test_pgvector_migration_creates_column` # SC-9 | Migration adds `vector(384)` column to `search_entries` table | structural |
| SC-10 | `test_pgvector_extension_enabled` # SC-10 | `CREATE EXTENSION IF NOT EXISTS vector` succeeds on local pgserver | structural |
| SC-11 | `test_pgvector_missing_raises_informative_error` # SC-11 | When pgvector extension is unavailable, migration raises a clear error message (not silent failure) | behavioral |
| SC-12 | `test_malformed_semantic_query_returns_empty` # SC-12 | Empty or malformed semantic query returns empty results without crash | behavioral |
| SC-13 | `test_no_embeddings_returns_empty_with_status` # SC-13 | When no embeddings exist in DB, semantic search returns empty results with a status message (not an error/exception) | behavioral |

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| **Empty database** | Semantic search returns empty result. Search function handles gracefully without error. |
| **Model not found** | Startup fails with clear error: "Model not found at models/all-MiniLM-L6-v2. Run setup script." |
| **pgvector not installed** | Migration fails with error message. Document in README: ensure pgvector extension available. |
| **Long glosses (>512 tokens)** | Truncate to first 512 tokens before embedding (model max). Log warning for truncated glosses. |
| **Unicode/non-ASCII glosses** | sentence-transformers handles Unicode. Embeddings generated normally. |
| **Empty gloss string** | Skip embedding, set `embedding = NULL`. Excluded from vector search via `WHERE embedding IS NOT NULL`. |
| **Threshold too strict** | Returns empty results. Document default threshold 0.7 is conservative. User can adjust via UI. |
| **Existing records without embeddings** | Backfill script processes all records. Newly uploaded records auto-generate embeddings. |
| **pgvector extension missing** | Migration raises informative error identifying missing extension; does not silently fail or skip. |
| **Malformed/empty semantic query** | Returns empty results list without raising exception; no crash on blank or whitespace-only input. |
| **No embeddings in database** | Returns empty results with a status/message indicating no indexed content; does not raise an error. |

---

## Migration Path

### New Records
Automatically generate embeddings during upload for all gloss fields.

### Existing Records
Create migration script:

```python
# scripts/backfill_embeddings.py
async def backfill():
    records = await get_all_records()
    for record in records:
        for entry_type, text in extract_gloss_fields(record.mdf_data):
            embedding = embed_text(text)
            session.add(SearchEntry(
                record_id=record.id,
                entry_type=entry_type,
                term=text,
                normalized_term=normalize(text),
                embedding=embedding
            ))
        await session.commit()
```

---

## Performance Considerations

| Operation | Time |
|-----------|------|
| Model load (startup) | ~500ms |
| Single embedding (384 dim) | ~20-50ms CPU |
| Single record indexing (~5-10 gloss fields) | ~100-500ms |
| Vector similarity (indexed) | ~1ms |
| Bulk backfill (1000 records) | ~2-5 minutes |

---

## Integration with #23 and #400

Issues #23 and #400 add exact-match search modes. This issue adds semantic search modes:

| Issue | Mode Type | Scopes |
|-------|-----------|--------|
| #23, #400 | Exact match | Headword (`\lx`), Gloss (primary `\ge`), Lexeme, FTS |
| #36 | Semantic vector | Semantic Gloss (primary `\ge`), Semantic All (all gloss fields) |

Both use the same `SearchEntry` table — #23/#400 use `term`/`normalized_term` columns, #36 adds `embedding` column.

---

## Related

- Issue #23: Headword and Gloss exact-match search modes
- Issue #400: Headword and Gloss search modes (new spec, supersedes #23)
- Issue #14: Original search requirements

---

## Phase 1: Database Schema Setup (Gated)

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|------|------------------|-------------------|----------|--------|
| 1 | `test_pgvector_extension_enabled` # SC-10 — assert `vector` extension can be enabled | Enable pgvector extension in PostgreSQL (migration script) | Clean up migration script, verify model imports | Commit Phase 1 with reference to phase number |
| 1 | `test_pgvector_migration_creates_column` # SC-9 — assert `search_entries` has `embedding` column of type `vector(384)` after migration | Add `vector(384)` column to SearchEntry table (migration script) | Verify column type and model field | (same commit) |
| 1 | `test_ivfflat_index_exists` — assert `idx_search_entries_embedding` index exists after migration | Create ivfflat index for similarity search on embedding column | Verify index parameters | (same commit) |
| 1 | `test_entry_type_gin_index_exists` — assert `idx_search_entries_type` index exists after migration | Create GIN index for entry_type filtering | Verify index coverage | (same commit) |
| 1 | `test_pgvector_missing_raises_informative_error` # SC-11 — assert migration raises clear error when pgvector extension unavailable | Add extension-availability check in migration with descriptive error message | Verify error message clarity | (same commit) |

**Verify all RED tests FAIL:** `uv run pytest tests/database/test_migration_manager.py -k "pgvector or embedding or ivfflat or entry_type_index" -v`

**After GREEN, verify all Phase 1 tests PASS**, then REFACTOR + COMMIT.

**Migration script example:**
```sql
-- Enable pgvector extension (already available in pgserver and production)
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column to search_entries
ALTER TABLE search_entries ADD COLUMN embedding vector(384);

-- Create index for similarity search
CREATE INDEX idx_search_entries_embedding ON search_entries 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create GIN index for entry_type filtering
CREATE INDEX idx_search_entries_type ON search_entries(entry_type);
```

**Updated model:**
```python
# src/database/models/search.py
from pgvector.sqlalchemy import Vector

class SearchEntry(Base):
    __tablename__ = 'search_entries'
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, ForeignKey('records.id'), nullable=False)
    term = Column(String, nullable=False)              # Original text
    normalized_term = Column(String, nullable=False)    # Normalized for exact search
    entry_type = Column(String, nullable=False)         # 'ge', 'ge_subentry', 'xe', etc.
    embedding = Column(Vector(384))                     # Semantic vector
```

---

## Phase 2: Core Services Implementation (Gated)

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|------|------------------|-------------------|----------|--------|
| 2 | `test_embedding_service_loads_model` # SC-7 — assert `get_model()` returns SentenceTransformer instance | Download and commit all-MiniLM-L6-v2 model to `models/` directory (22MB) | Clean up model path config | Commit Phase 2 with reference to phase number |
| 2 | `test_embed_text_returns_vector` # SC-8 — assert `embed_text("test")` returns list of 384 floats | Create `src/services/embedding_service.py` with `get_model()`, `embed_text()`, `embed_batch()` | Verify function signatures | (same commit) |
| 2 | `test_embed_batch_returns_vectors` — assert `embed_batch(["a", "b"])` returns list of 2 lists of 384 floats | (included in embedding service above) | Verify batch performance | (same commit) |
| 2 | `test_empty_gloss_no_embedding` # SC-6 — assert empty gloss entry has `embedding = NULL` | Modify `src/services/upload_service.py` to skip embedding for empty gloss fields | Verify NULL handling in search queries | (same commit) |
| 2 | `test_semantic_primary_finds_synonyms` # SC-1 — assert search "round" finds records with "spherical" gloss | Add `search_semantic_primary()` to `src/services/linguistic_service.py` | Verify query performance | (same commit) |
| 2 | `test_semantic_all_finds_cross_field` # SC-2 — assert search "container" finds records with "vessel" in any gloss field | Add `search_semantic_all()` to `src/services/linguistic_service.py` | Verify multi-field query correctness | (same commit) |
| 2 | `test_semantic_all_finds_example_translation` # SC-3 — assert search "hunt" finds `\xe` entries | (covered by `search_semantic_all()` above) | Verify entry_type filtering | (same commit) |
| 2 | `test_synonym_similarity_threshold` # SC-4 — assert similarity > 0.8 for exact synonyms | (threshold enforced in SQL WHERE clause) | Verify threshold parameter | (same commit) |
| 2 | `test_unrelated_term_low_similarity` # SC-5 — assert similarity < 0.5 for unrelated terms | (threshold filtering excludes low-similarity results) | Verify edge-case thresholds | (same commit) |
| 2 | `test_malformed_semantic_query_returns_empty` # SC-12 — assert empty or malformed query returns empty results without crash | Add input validation in search functions to gracefully handle blank/whitespace queries | Verify no exception raised | (same commit) |
| 2 | `test_no_embeddings_returns_empty_with_status` # SC-13 — assert search returns empty with status message when no embeddings in DB | Add zero-results-status path in search functions: return empty list with status indicator when no rows match | Verify status message returned | (same commit) |

**Verify all RED tests FAIL:** `uv run pytest tests/services/test_embedding.py tests/services/test_semantic_search.py -v`

**After GREEN, verify all Phase 2 tests PASS**, then REFACTOR + COMMIT.

**Embedding service:**
```python
from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load model once at startup."""
    return SentenceTransformer('models/all-MiniLM-L6-v2')

def embed_text(text: str) -> list[float]:
    """Generate embedding for single text."""
    return get_model().encode(text).tolist()

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts."""
    return get_model().encode(texts).tolist()
```

**Indexing integration:**
```python
GLOSS_FIELDS = {'ge', 'ge_subentry', 'ge_sense', 'ge_in_sense',  # Glosses
                'xe', 'ce', 'eg'}                                  # Example translations, cross-refs

async def index_gloss_fields(record: Record, mdf_text: str, session: Session):
    """Extract and index all gloss fields with embeddings."""
    entries = []
    for entry_type, text in extract_gloss_fields(mdf_text):
        entries.append(SearchEntry(
            record_id=record.id,
            term=text,
            normalized_term=normalize(text),
            entry_type=entry_type,
            embedding=embed_text(text) if text.strip() else None
        ))
    session.add_all(entries)
```

**Search functions:**
```python
GLOSS_TYPES = {'ge', 'ge_subentry', 'ge_sense', 'ge_in_sense', 'xe', 'ce', 'eg'}

async def search_semantic_primary(
    query: str,
    limit: int = 50,
    threshold: float = 0.7
) -> list[Record]:
    """Semantic search on primary gloss only (\\ge in headword block)."""
    query_vec = embed_text(query)
    results = await db.execute(text("""
        SELECT DISTINCT r.*, 
               1 - MIN(se.embedding <=> :vec) AS similarity
        FROM records r
        JOIN search_entries se ON se.record_id = r.id
        WHERE se.entry_type = 'ge'
          AND se.embedding IS NOT NULL
          AND 1 - (se.embedding <=> :vec) > :threshold
        GROUP BY r.id
        ORDER BY similarity DESC
        LIMIT :limit
    """), {"vec": str(query_vec), "threshold": threshold, "limit": limit})
    return results.fetchall()

async def search_semantic_all(
    query: str,
    limit: int = 50,
    threshold: float = 0.7
) -> list[Record]:
    """Semantic search across all gloss fields."""
    query_vec = embed_text(query)
    results = await db.execute(text("""
        SELECT DISTINCT r.*, 
               1 - MIN(se.embedding <=> :vec) AS similarity
        FROM records r
        JOIN search_entries se ON se.record_id = r.id
        WHERE se.entry_type IN :types
          AND se.embedding IS NOT NULL
          AND 1 - (se.embedding <=> :vec) > :threshold
        GROUP BY r.id
        ORDER BY similarity DESC
        LIMIT :limit
    """), {"types": tuple(GLOSS_TYPES), "vec": str(query_vec), 
           "threshold": threshold, "limit": limit})
    return results.fetchall()
```

---

## Phase 3: UI Integration (Gated)

### TDD Cycle

| Phase | RED (Test First) | GREEN (Implement) | REFACTOR | COMMIT |
|------|------------------|-------------------|----------|--------|
| 3 | `test_semantic_gloss_radio_exists` — assert "Semantic Gloss" option exists in search mode selector | Add "Semantic Gloss" radio button to search mode selector in `src/frontend/pages/records.py` | Review UI layout consistency | Commit Phase 3 with reference to phase number |
| 3 | `test_semantic_all_radio_exists` — assert "Semantic All" option exists in search mode selector | Add "Semantic All" radio button to search mode selector | Verify label text matches spec | (same commit) |
| 3 | `test_semantic_results_rendered_in_ui` — assert semantic search results display record list with similarity scores | Integrate semantic search functions with existing search flow; render results with similarity display | Verify result card layout | (same commit) |
| 3 | `test_mode_switching_keyword_to_semantic` — assert switching from keyword to semantic mode updates search behavior (does not use old mode) | Wire mode selector to toggle between exact-match and semantic search paths | Verify mode state persists correctly | (same commit) |
| 3 | `test_threshold_adjustment_updates_results` — assert changing similarity threshold re-filters results with new threshold | Add threshold/similarity slider to UI; wire to search function threshold parameter | Verify slider range and default value | (same commit) |

**Verify all RED tests FAIL:** `uv run pytest tests/frontend/test_records_ui.py -k "semantic" -v`

**After GREEN, verify all Phase 3 tests PASS**, then REFACTOR + COMMIT.

**UI Labels:**
| Button | Description |
|--------|-------------|
| Headword | Exact match on `\lx` only |
| Gloss | Exact match on primary `\ge` only |
| Semantic Gloss | Vector search on primary `\ge` |
| Semantic All | Vector search on all gloss fields |
| Lexeme | Exact match on `\lx`, `\va`, `\se`, `\cf`, `\ve` |
| FTS | Full-text search on all fields |

---

## Documentation Sources

| Source | Description | Version/Date | URL |
|--------|-------------|--------------|-----|
| Spec #400 — Headword/Gloss Search Modes | Search mode dispatch architecture, UI integration dependency | Active | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/400 |
| pgvector | PostgreSQL vector extension for cosine similarity search | ^0.2 | https://github.com/pgvector/pgvector |
| sentence-transformers (all-MiniLM-L6-v2) | Embedding model for semantic search | ^2.2 | https://www.sbert.net/ |
| Spec #23 — Original Search Requirements | Headword/gloss exact-match search, SearchEntry table schema | 2026-03-29 | https://github.com/Brothertown-Language/snea-shoebox-editor/issues/23 |
| Extant Linguistic Service | Existing FTS/exact-match search for pattern reference | Current | `src/services/linguistic_service.py` |

---

## Out of Scope

| Concern | Rationale |
|---------|-----------|
| Multilingual embedding models | Only English glosses are indexed; cross-language semantic search is not required |
| Real-time embedding updates | Embeddings generated on upload/migration only; no streaming or incremental update pipeline |
| Cross-lingual search (Algonquian → English semantic) | Semantic search is English-gloss-to-English-query only; headword semantic search is not required |
| GPU acceleration for embeddings | CPU-based inference is sufficient (~20-50ms per embedding); no GPU dependency |
| Alternative similarity metrics (dot product, Euclidean) | Cosine similarity is the standard for sentence-transformers; alternative metrics add complexity without demonstrated need |

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI:  ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

🤖 *[AI: OpenCode/glm-5] on behalf of Michael Conrad ✨ Created*
🤖 📝 Updated by OpenCode (ollama-cloud/glm-5): Concern Separation Refactor

---

AI: OpenCode ollama-cloud/glm-5 📝 Spec Audit: Added Edge Cases

## Summary
- Issues Found: 1
- Issues Fixed: 1
- Issues Skipped: 0

## Changes Applied

Added Edge Cases section identifying:
- Empty database handling
- Model not found error handling
- pgvector extension availability check
- Long gloss truncation
- Unicode/non-ASCII support
- Empty gloss field handling
- Threshold tuning documentation
- Existing records backfill

**Standard:** docs/specs/how-to-write-good-spec-ai-agents.md - Fresh-Start Context Requirements

---

AI: OpenCode ollama-cloud/glm-5 📝 Spec Revision v1.3: Added Evidence Type column to all SCs; added SC-11/SC-12/SC-13; expanded Phase 3 TDD to 5 RED tests; standardized TDD cycle table format across all phases
