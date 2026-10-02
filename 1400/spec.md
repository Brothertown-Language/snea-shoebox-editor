> **Full spec and artifacts: [`.issues/1400/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1400/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> Remote issue: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1400

# [SPEC] Gloss-space semantic threshold calibration (backend/seam)

## Problem

The gloss-space semantic search seam (`search_semantic()`, #36) returns results for every query regardless of whether a reasonable match exists in the corpus. Measured on the freshly synced production replica (6,681 embedded glosses, pin `thenlper/gte-small`, 2026-10-02):

- Ranked-cosine distribution is badly saturated: p50 ≈ 0.75–0.77, p90 ≈ 0.73–0.75, in-corpus exact matches land at 0.93–1.00.
- An out-of-corpus query ("maple syrup" — no maple/sugar glosses exist in the corpus) returns top hits at 0.83, shape-identical to in-corpus hits at 0.99. No floor currently separates "no reasonable match" from "match".
- Because the UI (`src/frontend/pages/records.py` `st.session_state.semantic_threshold`) and the seam `threshold` parameter scale by the same saturated metric, users always see confident-looking hits even when the corpus contains nothing relevant.

Root cause: gte-small's short-text embedding space compresses cosine similarity into ~0.7–1.0; #36 calibrated per-anchor floors for its SC-6 calibration anchors but no default threshold behavior was established for "no reasonable match exists" queries, and the current default serves all ranks unconditionally.

## User Intent

A user searching glosses with a term that genuinely exists in the corpus expects it at the top of the results. A user searching a term that does not exist in the corpus (e.g. "maple syrup") expects an honest "nothing found" response — not a list of confident-looking but irrelevant hits. Users who want to tune sensitivity keep explicit control via the threshold control; the calibrated floor is only the default.

## Approach Chosen

Calibrate a real-data default threshold for the gloss-space seam from the live corpus and make the seam (and default UI state) apply it:

1. Probe the full production-replica gloss corpus with a battery of real queries spanning in-corpus targets and out-of-corpus targets (provenance-recorded in the calibration evidence artifact — no synthetic data).
2. Derive a measured separation boundary between in-corpus and out-of-corpus score distributions; record per-anchor evidence (mirroring the #36 SC-6 per-anchor floor pattern).
3. Set the calibrated default threshold and apply it: when all ranked scores fall below the floor → `ok` with empty results plus a message, instead of serving low-confidence noise.
4. Preserve explicit user threshold control: a user-provided `threshold` overrides the default; the default engages only when `threshold=None`.

Derived-index-only: no production record data is mutated; embeddings and thresholds are calibration constants, not data changes.

### Calibrated Floor Value Definition (determinism anchor)

The measured probe evidence (session-local `tmp/1400/` scratch, 2026-10-02, production replica, 6,681 embedded glosses) establishes:

| Population | Measured value |
|---|---|
| In-corpus exact-match hits | cosine 0.93–1.00, all at rank 1 |
| Out-of-corpus max hit ("maple syrup" battery) | cosine 0.84 |
| Out-of-corpus bulk distribution | p50 ≈ 0.75–0.77 |

The **calibrated default floor** is the published calibration constant derived by the calibration evidence artifact: a value strictly greater than the measured out-of-corpus maximum (0.84) and strictly less than the measured in-corpus minimum (0.93). The constant carries provenance (query battery, corpus pin, date) and lives as a named calibration constant — not a magic number (R-2). Numeric thresholds in the success criteria below (0.90, ±0.01) are anchored to these measured distributions, not chosen arbitrarily.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Default-on-`None` semantics (`threshold=None` → calibrated floor) | Preserves existing seam signature (R-3); explicit values remain full overrides |
| Below-floor maps onto `status=ok` + empty results + message | Consistent with #36 R-7 pattern; avoids new status values, keeps exception behavior unchanged |
| Per-anchor floor evidence artifact (not a blanket hardcoded number) | Mirrors #36 SC-6 pattern; keeps R-1 provenance and R-2 no-magic-number mandates |
| Floor derived between measured distributions, not fixed a priori | Data-driven; re-derivable if the corpus or embedding pin changes |

## Alternatives Considered

- **Serve all ranks with a warning banner only** — rejected: still surfaces noise as ranked results; users see confident-looking hits for absent terms.
- **Reuse #1386 e5 calibration floors** — rejected: e5 floors are not transferable to gte-small gloss space (different embedding geometry); measured distributions differ.
- **Add a new status value (e.g. `no_match`)** — rejected: violates R-3 (signature-unchanged status machine) and diverges from the #36 R-7 pattern.
- **Re-embed with enriched gloss text** — rejected: explicitly ruled out of scope by the developer (2026-10-02); see Not Included.

## Not Included

- Embedding text enrichment / re-embedding (explicitly ruled out of scope by the developer, 2026-10-02).
- The #1399 limit-binding bug — fixed under its own issue, not here.
- #1386 vernacular term space calibration — separate space, separate issue.
- Any mutation of production record data.

## Success Criteria

| SC | Description | Evidence type | Evidence source | Evidence test | Documentation Sources |
|----|-------------|---------------|-----------------|---------------|----------------------|
| SC-1 | Calibration anchors derived from real corpus queries (in-corpus and out-of-corpus batteries) with per-anchor floor values recorded with source provenance in a calibration evidence artifact; no synthetic queries as evidence | behavioral | calendar-time-synced production replica probe output, provenance-recorded | pytest calibration module producing per-anchor evidence artifact | `src/services/semantic_search_service.py`; `.issues/36/` SC-6 floor pattern |
| SC-2 | `search_semantic()` consumes the calibrated default floor when the caller passes `threshold=None` | behavioral | `semantic_search_service.py` seam contract | pytest seam: default engaged at `threshold=None` | `src/services/semantic_search_service.py` |
| SC-3 | An explicit `threshold` value provided by the caller overrides the calibrated default | behavioral | `semantic_search_service.py` seam contract | pytest seam: explicit override wins over default | `src/services/semantic_search_service.py` |
| SC-4 | An explicit `threshold=None` restores the calibrated default after a prior explicit override call | behavioral | `semantic_search_service.py` seam contract | pytest seam: override-then-None re-engages default | `src/services/semantic_search_service.py` |
| SC-5 | When all ranked scores fall below the calibrated floor, the seam returns `status=ok` with empty `results` and a message naming the deficiency (e.g. "no gloss results meet the sensitivity floor") | behavioral | seam status machine per #36 R-7 pattern | pytest edge-input matrix: below-floor stub → ok + empty + message | `src/services/semantic_search_service.py`; `.issues/36/` R-7 |
| SC-6 | The all-below-floor outcome never raises an exception | behavioral | seam status machine per #36 R-7 pattern | pytest edge-input matrix: zero above-floor rows → no exception | `src/services/semantic_search_service.py`; `.issues/36/` R-7 |
| SC-7 | The all-below-floor outcome never serves below-floor rows as ranked results | behavioral | seam status machine per #36 R-7 pattern | pytest edge-input matrix: results empty when all scores < floor | `src/services/semantic_search_service.py`; `.issues/36/` R-7 |
| SC-8 | Under the default threshold, in-corpus targets in the calibration battery rank at rank 1 with cosine score ≥ 0.90 (no recall regression vs the measured pre-calibration baseline of 0.93–1.00 at rank 1) | behavioral | calibration evidence artifact baseline vs post-change probe | pytest regression battery incl. battery examples like water / how many / beaver | calibration evidence artifact; production replica probe |
| SC-9 | The UI default threshold state (`st.session_state.semantic_threshold`) equals the published calibrated default floor within ±0.01 | behavioral | `records.py` threshold plumbing | Playwright live-app UI check per ui_testing_standard | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-10 | A user override in the UI threshold control is preserved (override value is used by the seam, not silently replaced by the default) | behavioral | `records.py` threshold plumbing | Playwright live-app UI check per ui_testing_standard | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |

### Per-SC Cost Frame (dark-prose-007)

Each SC's failure cost, stated so the evidence test is worth its price:

- **SC-1**: without provenance-recorded anchors, every downstream SC rests on an untraceable number — the entire calibration is unauditable.
- **SC-2**: without default-on-`None`, the floor never engages in practice; the seam keeps serving noise for absent terms.
- **SC-3**: without override precedence, users lose the ability to tune sensitivity — the floor becomes a ceiling on usefulness.
- **SC-4**: without None-restores-default, a single override leaks into subsequent unrelated calls — sticky-state bug class.
- **SC-5**: without the honest empty+message outcome, "no reasonable match" remains indistinguishable from "match" — the core user-facing defect.
- **SC-6**: without the no-exception guarantee, every empty-result query becomes a crash path in the UI.
- **SC-7**: without the no-noise guarantee, the floor filters nothing — SC-1..SC-6 are dead code.
- **SC-8**: without the recall regression check, a mis-calibrated (too-high) floor silently hides real in-corpus matches — worse than the original defect.
- **SC-9**: without UI-default parity, the seam floor and the UI threshold disagree — user-visible behavior contradicts calibration.
- **SC-10**: without override preservation, UI users have no recourse when the default floor is wrong for their query.

## Requirements (condensed)

- R-1. Calibration SHALL run exclusively on real, provenance-recorded corpus data (Global Absolute Prohibition: no synthetic/fabricated query batteries).
- R-2. The threshold default SHALL be a recorded calibration constant with provenance, not a magic number in code.
- R-3. The seam contract (`SemanticSearchResult` statuses incl. `ok`/`empty_query`/`no_embeddings`/`stale_model`) SHALL be signature-unchanged; the all-below-floor outcome maps onto `status=ok` + empty results, consistent with #36 R-7.
- R-4. Out of scope: embedding text enrichment / re-embedding; the #1399 limit-binding bug is fixed under its own issue, not here.

## Edge Cases

| Case | Expected behavior | SC coverage |
|---|---|---|
| All ranked scores below floor | `ok`, empty results, deficiency message; no exception; no noise | SC-5, SC-6, SC-7 |
| `threshold=None` after explicit override | Default floor re-engages | SC-4 |
| Explicit threshold equals the calibrated floor value | Treated as explicit override, not default | SC-3 |
| Out-of-corpus query ("maple syrup") | Below-floor → honest empty response | SC-5 |
| In-corpus anchor query (water / how many / beaver) | Rank 1, cosine ≥ 0.90 | SC-8 |
| UI default state on fresh session | `semantic_threshold` = published floor ±0.01 | SC-9 |

## Dependencies

| Dependency | Status |
|---|---|
| Production replica sync (`scripts/sync_prod_to_local.sh`) | Available — synced 2026-10-02 (6,681 embedded glosses) |
| #36 gloss-space backbone (`search_semantic()` seam, R-7 status pattern) | Merged — in `src/services/semantic_search_service.py` |
| #1399 limit-binding fix | Separate issue — not a blocker for this spec (independent seam parameter) |
| #1386 e5 vernacular floors | Explicitly NOT a dependency (non-transferable) |
| Playwright live-app auth state (SC-9/SC-10) | Per ui_testing_standard — one-time OAuth login procedure when missing |

## Traceability

| Requirement / source | Covered by SCs |
|---|---|
| R-1 (no synthetic calibration data) | SC-1 |
| R-2 (provenance-recorded constant, no magic number) | SC-1, SC-2 |
| R-3 (signature-unchanged status machine) | SC-5, SC-6, SC-7 |
| Problem: default serves all ranks unconditionally | SC-2, SC-5 |
| Problem: user override behavior | SC-3, SC-4, SC-10 |
| Problem: UI default reflects floor | SC-9 |
| Problem: no recall regression for real queries | SC-8 |
| #36 R-7 / SC-6 patterns | SC-1, SC-5, SC-6, SC-7 |

## Enforcement Gate

- Per-SC evidence tests are executed under the per-item TDD cycle (RED → GREEN → REFACTOR → COMMIT) per guideline `091-incremental-build.md`; each SC maps to exactly one cycle.
- SC-9/SC-10 require Playwright real-browser evidence against the live app per `docs/development/ui_testing_standard.md` — `streamlit.testing.v1.AppTest` smoke checks are insufficient for these user-visible-behavior criteria on their own.
- E2E-marked tests skip unless `SNEA_E2E=1` + live app on :8501; skipping is reported as skipped, never silently as PASS.
- Every data/calibration artifact mutation is traceable to its source (provenance fields) per guideline `090-data-integrity.md`.

## References

- Measured probe evidence: session-local `tmp/` scratch (removed post-analysis; per-anchor floors re-derived durably by the calibration evidence artifact in this spec).
- Related: #36 (gloss-space backbone), #1399 (limit binding bug — separate fix), #1386 (vernacular term space; its e5 calibration floors are NOT transferable to gte-small gloss space).

## Change Control

| Date | Change | Reason | Authorized by |
|---|---|---|---|
| 2026-10-02 | Initial spec | Spec creation for gloss-space threshold calibration | Pipeline (spec-creation) |
| 2026-10-02 | Revision: added structure-standard sections (User Intent, Key Design Decisions, Alternatives Considered, Not Included, Per-SC Cost Frame, Edge Cases, Dependencies, Traceability, Enforcement Gate); fixed nonexistent documentation-source paths (`backend/seam/semantic_search_service.py` → `src/services/semantic_search_service.py`, `src/app/records.py` → `src/frontend/pages/records.py`); decomposed compound SC-2/SC-3/SC-5 into atomic SCs (renumbered SC-1..SC-10); quantified SC "at or near rank 1" → rank 1 with cosine ≥ 0.90 and "reflects the calibrated floor" → equals published floor within ±0.01, anchored to measured tmp/1400 probe distributions (in-corpus 0.93–1.00, out-of-corpus max 0.84, p50 0.75–0.77); added Calibrated Floor Value Definition section | Aggregate FAIL from holistic validate (completeness, provenance/feasibility, compound-SC, determinism, per-SC cost frame findings) | Validation findings via spec-creation pipeline |

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
🤖 Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
