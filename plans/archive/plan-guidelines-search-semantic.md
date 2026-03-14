# Plan: `ai_bin/guidelines-search` — Hybrid Re-Ranking Search (BM25 + Semantic)

## Overview

Redesign `ai_bin/guidelines-search` so that **hybrid re-ranking (BM25 + semantic) is the default
search mode**. Add `--bm25` and `--semantic` flags to opt into a single-mode search when needed.
Semantic encoding uses `sentence-transformers` declared as an inline `uv` script dependency
(~500 MB first download). Hybrid scoring: `alpha * bm25_norm + (1 - alpha) * semantic_sim`
with a tunable `--alpha` flag (default `0.5`).

**Why**: BM25 alone misses conceptually related content; semantic alone misses exact-term
precision. Combining them at negligible extra cost (<5 ms BM25 overhead on top of semantic)
gives the best results by default. The semantic encoding cost dominates either way.

**Scope**: `ai_bin/guidelines-search` only. No `src/` changes.

---

## Mode Summary

| Invocation | Behaviour |
|---|---|
| `guidelines-search "query"` | Hybrid (default): BM25 + semantic, weighted sum |
| `guidelines-search --bm25 "query"` | BM25 only (fast, no model load) |
| `guidelines-search --semantic "query"` | Semantic only (cosine similarity) |
| `--bm25` + `--semantic` together | Error: mutually exclusive |

---

## Steps

### Phase 1 — Preparation

1. ✔️ Completed — Confirmed: no existing `# /// script` header; shebang is `#!/usr/bin/env -S uv run python` which supports PEP 723 inline deps. Package: `sentence-transformers`. Model: `all-MiniLM-L6-v2`.

### Phase 2 — Implementation

2. ✔️ Completed — Added `sentence-transformers` inline `uv` dep header; import gated inside `semantic_scores()` so `--bm25` runs never load the model.

3. ✔️ Completed — Added flag parsing to `main()`:
   - `--bm25`: BM25-only mode.
   - `--semantic`: semantic-only mode.
   - `--alpha <float>`: hybrid weight (default `0.5`); ignored in single-mode runs.
   - Error if both `--bm25` and `--semantic` are supplied.
   - Default (no mode flag): hybrid.

4. ✔️ Completed — Implemented `semantic_scores()` function:
   - Accepts corpus lines and query string.
   - Loads `SentenceTransformer` model, encodes corpus + query.
   - Returns a list of cosine similarity floats (one per line).

5. ✔️ Completed — Implemented `hybrid_scores()` function:
   - Calls existing BM25 logic to get raw scores; min-max normalise to `[0, 1]`.
   - Calls `semantic_scores()` (already `[0, 1]` from cosine).
   - Returns `alpha * bm25_norm + (1 - alpha) * semantic_sim` per line.

6. ✔️ Completed — Refactored `main()` dispatch:
   - `--bm25`: use existing BM25 scoring path unchanged.
   - `--semantic`: use `semantic_scores()`.
   - default: use `hybrid_scores()`.
   - Reuse existing result-printing block for all three paths.

7. ✔️ Completed — Updated module docstring to document all three modes, `--alpha`, cold-start warning, and default model name.

### Phase 3 — Verification

8. ✔️ Completed — Hybrid default smoke test passed; top result: `01-approval-gate.md:1` (score=0.99).

9. ✔️ Completed — BM25-only mode works; fast, no model load; top result: `guidelines.md:59` (score=10.41).

10. ✔️ Completed — Semantic-only mode works; top result: `01-approval-gate.md:1` (score=0.75).

11. ✔️ Completed — Mutual exclusion error confirmed; exit code 2.

12. ✔️ Completed — Exit code 1 confirmed for BM25 no-matches; semantic always returns scores (cosine > 0 by nature).

### Phase 4 — Housekeeping

13. ✔️ Completed — TODO.md item marked `[x]` with date 2026-03-12.

14. ✔️ Completed — memory.md `last_task` updated.

15. ✔️ Completed — Plan archived.

---

## Checklist

- [ ] Verify correctness with smoke tests (steps 8–12).
- [ ] Verify completion with a deep code dive (steps 8–12).
- [ ] Automatically archive completed plan (step 15).
