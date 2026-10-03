## Discovered during
#1401 (search-match highlighting) implementation — SC-8 RED testing. Report-only; NOT fixed in #1403.

## Problem
`LinguisticService.search_records()` (src/services/linguistic_service.py, strategy dispatch around line 458) maps Semantic Gloss / Semantic All modes to `search_semantic(query, search_term)` via the `_search_strategies` table. The Semantic strategies return a `SemanticSearchResult` (src/services/semantic_search_service.py:59), which is not a SQLAlchemy query, so the subsequent paginated-query step (`query.order_by(...)`) raises:

```
AttributeError: 'SemanticSearchResult' object has no attribute 'order_by'
```

## Impact
Currently latent: the production Records page routes Semantic modes through the seam (`search_semantic` -> page-local mirror container), never through `search_records` with a Semantic mode. Any future caller passing a Semantic `search_mode` to `search_records` hits the crash.

## Evidence
Live reproduction during SC-8 RED testing (2026-10-03): `search_records(search_mode='Semantic Gloss', ...)` raises the AttributeError above; FTS/Lexeme/Headword/Gloss modes work normally.

## Suggested fix direction
Either reject Semantic modes in `search_records` with a clear ValueError, or route them through the seam path consistently with the page wiring.

---

## Revision 2026-10-03 — post-#1403 re-verification (fresh live evidence)

The original problem statement above is preserved for provenance but is now PARTIALLY STALE: commit `4eaa891` (SC-8 revision, merged in PR #1403) rewrote the semantic dispatch inside `LinguisticService.search_records` to consume the result container, so the ORIGINAL `SemanticSearchResult`-into-`order_by` crash no longer reproduces for Semantic Gloss. Fresh live verification against the post-#1403 code (2026-10-03) shows a different, still-open defect — revised below.

### Current behavior after #1403 (live evidence, 2026-10-03)

- **Semantic Gloss**: no longer raises the original `order_by` AttributeError. The revised dispatch (src/services/linguistic_service.py ~lines 454–469) unpacks the container via `raw.results` and filters `Record.id.in_([hit.record_id for hit in semantic_hits])`.
- **Semantic All**: STILL raises, with a different variant:

```
AttributeError: 'tuple' object has no attribute 'record_id'
```

### Root cause (verified against src/services/semantic_search_service.py, read 2026-10-03)

The real `search_semantic()` seam returns a `SemanticSearchResult` whose `results` is a list of **plain tuples** `(record_id, score)` (src/services/semantic_search_service.py, `search_semantic()` — rows unpacked as `for record_id, score, term in rows`, appended as `(int(record_id), value)`), plus a `matched_terms: dict[int, set]` keyed by record_id. The container-consumption code in `search_records` (both the id-filter at ~line 469 and the matched_terms loop at ~lines 524–532) instead accesses `hit.record_id` / `hit.term` attribute-style, which only works on the stubbed hit shapes used in the revised SC-8 unit tests — not on the real tuples.

1. **The revised SC-8 unit tests stubbed `_search_strategies` with container-shaped, attribute-bearing hits, masking the real shape.** The tests never exercised the genuine `search_semantic('all')` return contract, so the tuple-shaped hits pass the tests but crash live.
2. **Mode routing is additionally suspect:** the strategy table maps both `"Semantic Gloss"` and `"Semantic All"` to the bare `_search_semantic` function, and the dispatch calls `strategy(query, search_term)` — but `search_semantic`'s signature is `search_semantic(mode="gloss", query="", ...)`. The mode argument is never threaded through, so the caller's intended mode is not what reaches the seam. Any fix must pass the mode explicitly.
3. **The fix must normalize both hit shapes** (attribute-bearing hit objects AND `(record_id, score)` tuples) in the `search_records` semantic consumption path, and populate `matched_terms` from the seam's real `matched_terms` dict rather than re-deriving from hit attributes.

### Revised problem statement

`LinguisticService.search_records()` with `search_mode='Semantic All'` raises `AttributeError: 'tuple' object has no attribute 'record_id'` because the real `search_semantic('all')` hit shape (tuples of `(record_id, score)` plus a `matched_terms` dict) is not what the container-consumption code expects (attribute-bearing hits). Semantic Gloss currently passes only because the live probe path happens to avoid the attribute access; the same shape mismatch is latent for it. The regression coverage that should have caught this was masked by stubbed hit shapes.

### Revised impact
Any caller of `search_records` with `search_mode='Semantic All'` (and, once real hits flow, `'Semantic Gloss'`) crashes. The production Records page still routes around this via the seam, but the service contract is broken and the test suite no longer reflects the real seam contract.

## Revised success criteria

- **SC-1**: `LinguisticService.search_records(search_mode='Semantic Gloss', search_term=...)` does not raise and returns a `RecordSearchResult` whose `matched_terms` is populated from the seam's real per-record matched terms.
- **SC-2**: `LinguisticService.search_records(search_mode='Semantic All', search_term=...)` does not raise and returns a `RecordSearchResult` whose `matched_terms` is populated from the seam's real per-record matched terms.
- **SC-3**: Regression tests exercise the REAL `search_semantic` hit shapes for both modes (container hits and `(record_id, score)` tuples) with only the DB session patched — no stubs for the shape contract.
- **SC-4**: No regression in existing test suites.

## Revised fix direction
Normalize both hit shapes (attribute-bearing hits and tuples) in the `search_records` semantic consumption path; consume the seam's `matched_terms` dict directly; thread the caller's mode (`'gloss'` / `'all'`) explicitly into `search_semantic`; rewrite the SC-8 regression tests against the real seam shape.

## Change control

| Date | Change | Reason | Authorized by |
|------|--------|--------|---------------|
| 2026-10-03 | Revised problem statement, evidence, fix direction, and SCs to reflect post-#1403 live behavior: original crash no longer reproduces for Semantic Gloss; Semantic All raises `'tuple' object has no attribute 'record_id'`; root cause is stubbed SC-8 test shapes masking the real `search_semantic` tuple hit contract; added SC-1..SC-4. | Fresh live evidence gathered 2026-10-03 after the #1403 merge (dispatch context from orchestrator). | Developer (Michael Conrad), spec-revision dispatch |

---
🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)

