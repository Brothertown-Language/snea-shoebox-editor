> **Full spec and artifacts: [`.issues/1400/`](https://github.com/Brothertown-Language/snea-shoebox-editor/tree/issues-data/.issues/1400/)** — this issue is a condensed exec summary; the authoritative spec lives in the `issues-data` branch.
>
> Remote issue: https://github.com/Brothertown-Language/snea-shoebox-editor/issues/1400

# [SPEC] Gloss-space semantic threshold calibration (backend/seam)

## Problem

The gloss-space semantic search seam (`search_semantic()`, #36) returns results for every query regardless of whether a reasonable match exists in the corpus. Measured on the freshly synced production replica (6,681 embedded glosses, pin `thenlper/gte-small`, 2026-10-02):

- Ranked-cosine distribution is badly saturated: p50 ≈ 0.75–0.77, p90 ≈ 0.73–0.75, in-corpus exact hits land at 0.99–1.00 (e.g. money 0.997, gun 0.996, book 0.994) but in-corpus anchors spread widely — beaver 0.9753, "how many" 0.8917.
- Out-of-corpus queries (no matching gloss exists) return top hits up to a measured battery max of 0.9018 ("light bulb"; battery minimum observed 0.8471, "telephone") across a broad real battery. The distributions OVERLAP: out-of-corpus max 0.9018 exceeds the in-corpus anchor "how many" (0.8917). No floor currently separates "no reasonable match" from "match", and given the overlap, any constant floor necessarily trades suppressing out-of-corpus noise against suppressing low-scoring in-corpus anchors.
- Because the UI (`src/frontend/pages/records.py` `st.session_state.semantic_threshold`) and the seam `threshold` parameter scale by the same saturated metric, users always see confident-looking hits even when the corpus contains nothing relevant.

Root cause: gte-small's short-text embedding space compresses cosine similarity into ~0.7–1.0; #36 calibrated per-anchor floors for its SC-6 calibration anchors but no default threshold behavior was established for "no reasonable match exists" queries, and the current default serves all ranks unconditionally.

## User Intent

A user searching glosses with a term that genuinely exists in the corpus expects it at the top of the results. A user searching a term that does not exist in the corpus (e.g. "light bulb") expects an honest "nothing found" response — not a list of confident-looking but irrelevant hits. Users who want to tune sensitivity keep explicit control via the threshold control; the calibrated floor is only the default. Because the measured score distributions overlap, an in-corpus anchor that scores below the floor ("how many", 0.8917) returns the same honest empty outcome under the default — the threshold control is the user's recourse for such queries.

## Approach Chosen

Calibrate a real-data default threshold for the gloss-space seam from the live corpus and make the seam (and default UI state) apply it:

1. Probe the full production-replica gloss corpus with a battery of real queries spanning in-corpus targets and out-of-corpus targets (provenance-recorded in the calibration evidence artifact — no synthetic data).
2. Derive a measured separation boundary between in-corpus and out-of-corpus score distributions; record per-anchor evidence (mirroring the #36 SC-6 per-anchor floor pattern).
3. Set the calibrated default threshold and apply it: when all ranked scores fall below the floor → `ok` with empty results plus a message, instead of serving low-confidence noise.
4. Preserve explicit user threshold control: a user-provided `threshold` overrides the default; the default engages only when `threshold=None`.

Derived-index-only: no production record data is mutated; embeddings and thresholds are calibration constants, not data changes.

### Calibrated Floor Value Definition (determinism anchor)

The measured probe evidence (verification artifact `tmp/1400/artifacts/verification-probe.yaml`, 2026-10-02, production replica, 6,681 embedded glosses, pin `thenlper/gte-small`, 20-query real battery) establishes:

| Population | Measured value (probe artifact) |
|---|---|
| In-corpus exact-match anchors — water (rank 1, 1.0000), money (0.9970), gun (0.9959), book (0.9936) | cosine 0.99–1.00, all rank 1 |
| In-corpus anchor beaver (rank 1) | cosine 0.9753 |
| In-corpus anchor "how many" (rank 1, record 3400 "One.") | cosine 0.8917 — falls BELOW any floor that clears the out-of-corpus max |
| Out-of-corpus battery max ("light bulb", record 3939 "Light.") | cosine 0.9018 |
| Out-of-corpus battery range | 0.8471 ("telephone") to 0.9018 ("light bulb") |
| Out-of-corpus bulk distribution (earlier probe, session-local scratch) | p50 ≈ 0.75–0.77 |

**Measured reality — overlapping distributions:** the out-of-corpus maximum (0.9018) is strictly greater than the in-corpus anchor "how many" (0.8917). There is therefore no constant floor that both suppresses every out-of-corpus hit and serves every real in-corpus anchor. Honest outcome semantics follow:

- The **calibrated default floor** is the published calibration constant derived by the calibration evidence artifact, constrained to the interval **strictly greater than the measured out-of-corpus max (0.9018) and strictly less than the smallest floor-clearing in-corpus anchor (beaver, 0.9753)** — i.e. floor ∈ (0.9018, 0.9753). The constant carries provenance (battery, corpus pin, date, verification artifact path) and lives as a named calibration constant — not a magic number (R-2).
- Under the default floor, in-corpus anchors that measurably clear the floor (water 1.0000, beaver 0.9753, money 0.9970, gun 0.9959, book 0.9936) are served; the anchor "how many" (0.8917) legitimately falls below the floor and returns the below-floor empty outcome (SC-5 semantics) rather than a guaranteed rank-1 serve.
- Out-of-corpus queries — including the battery max "light bulb" — return the below-floor empty outcome under the default floor.
- Explicit threshold control (SC-3/SC-10) is the documented recourse for queries like "how many" whose real in-corpus targets score below the default floor.

Numeric thresholds in the success criteria below (±0.01) are anchored to these measured distributions and the probe artifact provenance, not chosen arbitrarily.

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
| SC-1 | Calibration anchors derived from real corpus queries (in-corpus battery: water / beaver / how many / money / gun / book; out-of-corpus battery: coffee, telephone, airplane, electricity, car, radio, television, computer, internet, light bulb, clock, school, hospital, train, camera, battery, refrigerator) with per-anchor floor values recorded with source provenance in a calibration evidence artifact; no synthetic queries as evidence | behavioral | calendar-time-synced production replica probe output, provenance-recorded (measured probe: `tmp/1400/artifacts/verification-probe.yaml`) | pytest calibration module producing per-anchor evidence artifact | `src/services/semantic_search_service.py`; `.issues/36/` SC-6 floor pattern |
| SC-2 | `search_semantic()` consumes the calibrated default floor when the caller passes `threshold=None` | behavioral | `semantic_search_service.py` seam contract | pytest seam: default engaged at `threshold=None` | `src/services/semantic_search_service.py` |
| SC-3 | An explicit `threshold` value provided by the caller overrides the calibrated default | behavioral | `semantic_search_service.py` seam contract | pytest seam: explicit override wins over default | `src/services/semantic_search_service.py` |
| SC-4 | An explicit `threshold=None` restores the calibrated default after a prior explicit override call | behavioral | `semantic_search_service.py` seam contract | pytest seam: override-then-None re-engages default | `src/services/semantic_search_service.py` |
| SC-5 | When all ranked scores fall below the calibrated floor, the seam returns `status=ok` with empty `results` and the fixed deficiency message exactly: "No gloss results meet the sensitivity floor." (message text is a pinned constant, not an example) | behavioral | seam status machine per #36 R-7 pattern | pytest edge-input matrix: below-floor stub → ok + empty + pinned message | `src/services/semantic_search_service.py`; `.issues/36/` R-7 |
| SC-6 | The all-below-floor outcome never raises an exception | behavioral | seam status machine per #36 R-7 pattern | pytest edge-input matrix: zero above-floor rows → no exception | `src/services/semantic_search_service.py`; `.issues/36/` R-7 |
| SC-7 | Whenever a threshold is active (the calibrated default OR an explicit user threshold), rows scoring below the active floor are excluded from the returned `results` — per-row filtering, not just the all-below-floor edge case: under an explicit user threshold with a PARTIALLY-below-floor score distribution, floor-clearing rows are served in the same result set while below-floor rows are excluded from it (the seam must never mix served and below-floor rows in one response) | behavioral | seam filtering behavior per #36 R-7 pattern | pytest per-row filtering test: mixed above/below-floor stub under an explicit threshold → result contains ONLY floor-clearing rows; below-floor rows excluded from the same result set | `src/services/semantic_search_service.py`; `.issues/36/` R-7 |
| SC-8 | Under the default threshold, in-corpus calibration anchors that measurably clear the floor — water (1.0000), beaver (0.9753), money (0.9970), gun (0.9959), book (0.9936) — rank at rank 1 with cosine score ≥ the published floor (no recall regression for floor-clearing anchors) | behavioral | calibration evidence artifact baseline vs post-change probe (measured probe: `tmp/1400/artifacts/verification-probe.yaml`) | pytest regression battery: floor-clearing anchors water / beaver / money / gun / book asserted at rank 1 with cosine ≥ published floor | calibration evidence artifact; production replica probe |
| SC-8a | The in-corpus anchor "how many" (0.8917) falls below the default floor by measurement and MUST return the below-floor empty outcome (SC-5 semantics), not a rank-1 serve — this is documented measured behavior, not recall regression | behavioral | calibration evidence artifact baseline vs post-change probe (measured probe: `tmp/1400/artifacts/verification-probe.yaml`) | pytest regression battery: "how many" asserted below-floor empty (ok + empty results + pinned SC-5 message) | calibration evidence artifact; production replica probe |
| SC-9 | The UI default threshold state (`st.session_state.semantic_threshold`) equals the published calibrated default floor within ±0.01 | behavioral | `records.py` threshold plumbing | Playwright live-app UI check per ui_testing_standard | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-10 | A user override in the UI threshold control is preserved (override value is used by the seam, not silently replaced by the default) | behavioral | `records.py` threshold plumbing | Playwright live-app UI check per ui_testing_standard | `src/frontend/pages/records.py`; `docs/development/ui_testing_standard.md` |
| SC-11 | The Playwright E2E UI test harness authenticates headlessly via the pinned test-only mechanism — a `SNEA_E2E`-gated test-only auth bypass hook in the app's auth path (`src/services/security_manager.py` auth resolution) — such that E2E tests execute authenticated WITHOUT any headed GitHub OAuth login and WITHOUT fabricating real GitHub credentials | behavioral | E2E suite executes authenticated without headed login | Playwright E2E run with `SNEA_E2E=1` + live app on :8501 completing authentication via the bypass hook without any headed OAuth login or saved-credentials capture step | `src/services/security_manager.py`; `test/ui/AGENTS.md`; `docs/development/ui_testing_standard.md` |
| SC-11a | The test-only auth bypass is inert outside `SNEA_E2E=1`: with `SNEA_E2E` unset, the auth path in `src/services/security_manager.py` behaves identically to production (no bypass branch taken, real GitHub API token validation unchanged) — verified by test | behavioral | auth-path behavior with `SNEA_E2E` unset vs production baseline | pytest auth-path test: with `SNEA_E2E` unset the auth resolution follows the production path (no bypass) | `src/services/security_manager.py`; `test/ui/AGENTS.md`; `docs/development/ui_testing_standard.md` |

**Pinned mechanism (single, no alternatives):** the ONLY authorized test-only authentication mechanism for SC-11 is the `SNEA_E2E`-gated test-only auth bypass hook in the app's auth path (`src/services/security_manager.py` auth resolution). Direct cookie/context injection is NOT an authorized alternative — it cannot work because the app sets the session token server-side and validates tokens against the live GitHub API, so a Playwright-injected cookie would fail server-side validation.

### Per-SC Cost Frame (dark-prose-007)

Each SC's failure cost, stated so the evidence test is worth its price:

- **SC-1**: without provenance-recorded anchors, every downstream SC rests on an untraceable number — the entire calibration is unauditable.
- **SC-2**: without default-on-`None`, the floor never engages in practice; the seam keeps serving noise for absent terms.
- **SC-3**: without override precedence, users lose the ability to tune sensitivity — the floor becomes a ceiling on usefulness.
- **SC-4**: without None-restores-default, a single override leaks into subsequent unrelated calls — sticky-state bug class.
- **SC-5**: without the honest empty+message outcome, "no reasonable match" remains indistinguishable from "match" — the core user-facing defect.
- **SC-6**: without the no-exception guarantee, every empty-result query becomes a crash path in the UI.
- **SC-7**: without the per-row filtering invariant, a partially-below-floor result set under an explicit threshold would mix served floor-clearing rows with below-floor noise rows in one response — the floor filters nothing per-row and the seam serves noise alongside real matches.
- **SC-8**: without the recall regression check, a mis-calibrated (too-high) floor silently hides real in-corpus matches — worse than the original defect.
- **SC-8a**: without the documented below-floor outcome for "how many", the overlapping-distribution behavior is undefined — implementers would silently serve or silently drop the anchor with no spec-mandated contract.
- **SC-9**: without UI-default parity, the seam floor and the UI threshold disagree — user-visible behavior contradicts calibration.
- **SC-10**: without override preservation, UI users have no recourse when the default floor is wrong for their query.
- **SC-11**: without a test-only auth bypass, every E2E UI run requires a developer to sit through a headed GitHub OAuth login whose token capture has proven unreliable (the app sets the token server-side, so Playwright cannot capture the cookie) — E2E verification of SC-9/SC-10 becomes unrunnable in unattended runs and the E2E tier regresses into manual-only testing.
- **SC-11a**: without a verified-inert bypass, a test-only auth hook that leaks into non-test runs would silently weaken production authentication — a security regression far worse than the original test-infrastructure defect.

## Missing Items (per-SC TDD item enumeration)

Each SC maps to exactly one implementation item with its own RED/GREEN/verify/commit cycle per guideline `091-incremental-build.md`:

| Item | SC | RED | GREEN | Verify | Commit |
|---|---|---|---|---|---|
| 1 | SC-1 | Failing calibration test: per-anchor evidence artifact missing for battery anchors | Calibration module produces provenance-recorded per-anchor artifact | Verify artifact provenance fields (battery, pin, date) against production replica | Test + artifact committed together |
| 2 | SC-2 | Failing seam test: `threshold=None` does not filter by calibrated floor | Default floor engaged in seam at `threshold=None` | Verify default engagement via seam test output | Test + seam change committed together |
| 3 | SC-3 | Failing seam test: explicit threshold ignored in favor of default | Explicit override precedence implemented | Verify override wins over default | Test + seam change committed together |
| 4 | SC-4 | Failing seam test: `None` after override keeps prior explicit value | `None` restores default after override | Verify override-then-None re-engages default | Test + seam change committed together |
| 5 | SC-5 | Failing edge-input test: below-floor stub raises or serves noise | `ok` + empty results + pinned deficiency message | Verify pinned message text exact match | Test + seam change committed together |
| 6 | SC-6 | Failing edge-input test: zero above-floor rows raises exception | No-exception path for all-below-floor | Verify no exception across edge matrix | Test + seam change committed together |
| 7 | SC-7 | Failing per-row filtering test: under an explicit threshold with a mixed above/below-floor stub, below-floor rows are served alongside floor-clearing rows | Per-row filtering implemented — below-floor rows excluded from `results` whenever a threshold is active; floor-clearing rows still served | Verify mixed-distribution result contains ONLY floor-clearing rows (below-floor rows excluded) | Test + seam change committed together |
| 8 | SC-8 | Failing regression battery: floor-clearing anchors not at rank 1 / below floor | Published floor serves floor-clearing anchors at rank 1 | Verify rank 1 + cosine ≥ floor per anchor from probe evidence | Test + calibration artifact committed together |
| 9 | SC-8a | Failing regression battery: "how many" served as rank-1 hit | "how many" returns below-floor empty outcome (SC-5 semantics) | Verify below-floor empty outcome from probe evidence | Test + calibration artifact committed together |
| 10 | SC-9 | Failing Playwright check: fresh-session `semantic_threshold` ≠ published floor | UI default synced to published floor ±0.01 | Verify via live-app Playwright screenshot evidence | Test + UI change committed together |
| 11 | SC-10 | Failing Playwright check: UI override silently replaced by default | Override passthrough preserved to seam | Verify override value reaches the seam | Test + UI change committed together |
| 12 | SC-11 | Failing E2E run: `SNEA_E2E=1` Playwright suite cannot authenticate without headed OAuth login | `SNEA_E2E`-gated test-only auth bypass hook in `src/services/security_manager.py` auth resolution makes E2E tests authenticate headlessly | Verify E2E suite completes authenticated with no headed-login step and no fabricated credentials | Test + bypass change committed together |
| 13 | SC-11a | Failing auth-path test: with `SNEA_E2E` unset, bypass branch is taken (or auth path diverges from production behavior) | Bypass hook inert when `SNEA_E2E` is unset — auth resolution follows production path | Verify via pytest auth-path test that with `SNEA_E2E` unset the auth path behaves identically to production | Test + bypass change committed together |

## Documentation Sources

| Source | Type | Location | Verification |
|---|---|---|---|
| Semantic search seam implementation | Source code | `src/services/semantic_search_service.py` | Read directly; seam contract per #36 R-7 |
| UI threshold plumbing | Source code | `src/frontend/pages/records.py` | Read directly; `st.session_state.semantic_threshold` |
| UI testing standard | Project doc | `docs/development/ui_testing_standard.md` | Read directly; Playwright/E2E gating rules |
| Gloss-space backbone spec (floor pattern, R-7) | Prior spec | `.issues/36/` (issues-data branch) | Read directly from local issue store |
| e5 calibration floors (non-transferable reference) | Prior spec | `.issues/1386/` (issues-data branch) | Read directly from local issue store |
| Measured probe evidence | Verification artifact | `tmp/1400/artifacts/verification-probe.yaml` | Read directly; provenance fields 2026-10-02, 6,681 glosses, pin `thenlper/gte-small` |
| Calibration evidence artifact (to be produced) | Evidence artifact | `tmp/1400/artifacts/` (path recorded at calibration) | Produced by SC-1 item; provenance-recorded |

## Requirements (condensed)

- R-1. Calibration SHALL run exclusively on real, provenance-recorded corpus data (Global Absolute Prohibition: no synthetic/fabricated query batteries).
- R-2. The threshold default SHALL be a recorded calibration constant with provenance, not a magic number in code.
- R-3. The seam contract (`SemanticSearchResult` statuses incl. `ok`/`empty_query`/`no_embeddings`/`stale_model`) SHALL be signature-unchanged; the all-below-floor outcome maps onto `status=ok` + empty results, consistent with #36 R-7.
- R-4. Out of scope: embedding text enrichment / re-embedding; the #1399 limit-binding bug is fixed under its own issue, not here.

## Edge Cases

| Case | Expected behavior | SC coverage |
|---|---|---|
| All ranked scores below floor | `ok`, empty results, pinned deficiency message; no exception; no noise | SC-5, SC-6, SC-7 |
| Mixed result set under an explicit threshold (some rows below floor, some clearing it) | Floor-clearing rows served; below-floor rows excluded from the same result set — never mixed | SC-7 |
| `threshold=None` after explicit override | Default floor re-engages | SC-4 |
| Explicit threshold equals the calibrated floor value | Treated as explicit override, not default | SC-3 |
| Out-of-corpus query (e.g. "light bulb", battery max 0.9018) | Below-floor → honest empty response | SC-5 |
| In-corpus anchor clearing the floor (water / beaver / money / gun / book) | Rank 1, cosine ≥ published floor | SC-8 |
| In-corpus anchor below the floor ("how many", 0.8917) | Below-floor → honest empty response (documented overlap behavior) | SC-5, SC-8a |
| UI default state on fresh session | `semantic_threshold` = published floor ±0.01 | SC-9 |
| E2E run without saved OAuth auth state / without developer present | E2E tests authenticate headlessly via the pinned `SNEA_E2E`-gated bypass hook; production auth path unchanged | SC-11 |
| App run outside `SNEA_E2E=1` | Auth bypass hook inert — production OAuth behavior unchanged | SC-11a |

## Dependencies

| Dependency | Status |
|---|---|
| Production replica sync (`scripts/sync_prod_to_local.sh`) | Available — synced 2026-10-02 (6,681 embedded glosses) |
| #36 gloss-space backbone (`search_semantic()` seam, R-7 status pattern) | Merged — in `src/services/semantic_search_service.py` |
| #1399 limit-binding fix | Separate issue — not a blocker for this spec (independent seam parameter) |
| #1386 e5 vernacular floors | Explicitly NOT a dependency (non-transferable) |
| Playwright live-app auth state (SC-9/SC-10) | Superseded for E2E runs — SC-11 test-only auth bypass removes the headed-login dependency; one-time OAuth login procedure remains documented for manual/interactive sessions per ui_testing_standard |
| Test-only auth bypass mechanism (SC-11/SC-11a) | To be implemented as a `SNEA_E2E`-gated test-only auth bypass hook in the app's auth path (`src/services/security_manager.py` auth resolution); SC-11a requires test-verified inertness when `SNEA_E2E` is unset |

## Traceability

| Requirement / source | Covered by SCs |
|---|---|
| R-1 (no synthetic calibration data) | SC-1 |
| R-2 (provenance-recorded constant, no magic number) | SC-1, SC-2 |
| R-3 (signature-unchanged status machine) | SC-5, SC-6, SC-7 |
| Problem: below-floor rows never served whenever a threshold is active (per-row filtering, incl. partial distributions under explicit thresholds) | SC-7 |
| Problem: default serves all ranks unconditionally | SC-2, SC-5 |
| Problem: user override behavior | SC-3, SC-4, SC-10 |
| Problem: UI default reflects floor | SC-9 |
| Problem: no recall regression for real queries | SC-8 |
| Problem: honest outcome for below-floor in-corpus anchors (overlap) | SC-8a |
| Developer directive 2026-10-02: E2E UI tests unrunnable without headed OAuth login (stale auth-state regression) | SC-11 |
| Developer directive 2026-10-02: bypass must not alter production auth (inertness requirement) | SC-11a |
| #36 R-7 / SC-6 patterns | SC-1, SC-5, SC-6, SC-7 |

## Enforcement Gate

**All success criteria MUST pass for this spec to be satisfied. Partial implementation is not permitted.**

- Per-SC evidence tests are executed under the per-item TDD cycle (RED → GREEN → REFACTOR → COMMIT) per guideline `091-incremental-build.md`; each SC maps to exactly one cycle (see Missing Items enumeration).
- SC-9/SC-10 require Playwright real-browser evidence against the live app per `docs/development/ui_testing_standard.md` — `streamlit.testing.v1.AppTest` smoke checks are insufficient for these user-visible-behavior criteria on their own.
- SC-11 requires the E2E Playwright suite to authenticate headlessly via the pinned test-only mechanism (the `SNEA_E2E`-gated auth bypass hook in `src/services/security_manager.py`; no headed OAuth login, no fabricated real GitHub credentials).
- SC-11a requires pytest evidence that the bypass is inert with `SNEA_E2E` unset (production auth behavior unchanged).
- E2E-marked tests skip unless `SNEA_E2E=1` + live app on :8501; skipping is reported as skipped, never silently as PASS.
- All 13 success criteria — enumerated unambiguously as SC-1, SC-2, SC-3, SC-4, SC-5, SC-6, SC-7, SC-8, SC-8a, SC-9, SC-10, SC-11, SC-11a — MUST pass — partial implementation is not permitted.
- Every data/calibration artifact mutation is traceable to its source (provenance fields) per guideline `090-data-integrity.md`.

## References

- Measured probe evidence (provenance): `tmp/1400/artifacts/verification-probe.yaml` — 20-query real battery, production replica 6,681 embedded glosses, pin `thenlper/gte-small`, 2026-10-02; per-anchor floors re-derived durably by the calibration evidence artifact in this spec.
- Related: #36 (gloss-space backbone), #1399 (limit binding bug — separate fix), #1386 (vernacular term space; its e5 calibration floors are NOT transferable to gte-small gloss space).

## Change Control

**Historical note:** numeric values mentioned in change-control entries below (e.g. "cosine ≥ 0.90", "0.84") reflect superseded revisions retained as history only; the authoritative measured values are in the Calibrated Floor Value Definition section above.

| Date | Change | Reason | Authorized by |
|---|---|---|---|
| 2026-10-02 | Initial spec | Spec creation for gloss-space threshold calibration | Pipeline (spec-creation) |
| 2026-10-02 | Revision: added structure-standard sections (User Intent, Key Design Decisions, Alternatives Considered, Not Included, Per-SC Cost Frame, Edge Cases, Dependencies, Traceability, Enforcement Gate); fixed nonexistent documentation-source paths (`backend/seam/semantic_search_service.py` → `src/services/semantic_search_service.py`, `src/app/records.py` → `src/frontend/pages/records.py`); decomposed compound SC-2/SC-3/SC-5 into atomic SCs (renumbered SC-1..SC-10); quantified SC "at or near rank 1" → rank 1 with cosine ≥ 0.90 and "reflects the calibrated floor" → equals published floor within ±0.01, anchored to measured tmp/1400 probe distributions (in-corpus 0.93–1.00, out-of-corpus max 0.84, p50 0.75–0.77); added Calibrated Floor Value Definition section | Aggregate FAIL from holistic validate (completeness, provenance/feasibility, compound-SC, determinism, per-SC cost frame findings) | Validation findings via spec-creation pipeline |
| 2026-10-02 | Revision: recalibrated Calibrated Floor Value Definition against measured reality — verification probe (`tmp/1400/artifacts/verification-probe.yaml`, 2026-10-02, production replica 6,681 embedded glosses) shows in-corpus anchor "how many" tops at 0.8917 (NOT 0.93–1.00) and out-of-corpus battery max "light bulb" at 0.9018 (NOT 0.84); measured distributions OVERLAP, so the prior floor interval strictly in (0.84, 0.93) admits no honest constant. Floor interval restated as strictly (0.9018, 0.9753); in-corpus battery anchor list expanded (water 1.0000, beaver 0.9753, how many 0.8917, money 0.9970, gun 0.9959, book 0.9936); out-of-corpus battery restated as broad 17-query real battery with measured max 0.9018; SC-8 restated to guarantee recall only for floor-clearing anchors with "how many" documented as below-floor empty outcome (SC-5 semantics); SC intent unchanged — no SC removed or weakened. Per guideline 130 (spec misstates measured state → revise spec, not code) | Developer revision request (spec-creation revise dispatch, for_pr scope), verified live against production replica 2026-10-02 |
| 2026-10-02 | Revision (structure/decomposition only, no scope or intent change): split compound SC-8 into atomic SC-8 (floor-clearing anchors rank 1 with cosine ≥ published floor) and SC-8a ("how many" returns below-floor empty outcome), each with its own evidence row; added Missing Items per-SC TDD item enumeration (RED/GREEN/verify/commit per SC); added standalone Documentation Sources table (Source/Type/Location/Verification); added all-or-nothing statement to Enforcement Gate ("All success criteria MUST pass… Partial implementation is not permitted"); pinned SC-5 deficiency message text (replaced "e.g." with fixed message "No gloss results meet the sensitivity floor."); added historical note marking prior change-control numeric values as history. Floor interval (0.9018, 0.9753) and all measured-distribution content unchanged; no SC removed or weakened | Validation findings from spec-creation validate (compound-SC, missing-items, missing-documentation-sources, enforcement-gate all-or-nothing; warnings: unpinned message text, historical numbers) | Validation findings via spec-creation pipeline |
| 2026-10-02 | Revision: added atomic SC-11 — the Playwright E2E UI test harness MUST authenticate via a test-only mechanism (SNEA_E2E-gated test-only auth bypass hook in the app's auth path, or direct cookie/context injection accepted by the local app) such that E2E tests execute authenticated WITHOUT any headed GitHub OAuth login and WITHOUT fabricating real GitHub credentials; bypass inert outside `SNEA_E2E=1`; production auth behavior unchanged. Added Missing Items item 12 (per-SC TDD cycle), SC-11 Cost Frame entry, Edge Cases rows, Traceability row, Enforcement Gate bullet + explicit SC count, updated Dependencies row (Playwright auth state dependency superseded for E2E runs). No existing SC removed or weakened | Developer directive (2026-10-02, current session, chat): "the E2E tier's dependency on a real headed GitHub OAuth login (one-time auth-state regeneration) is a REGRESSION in test infrastructure — E2E UI tests have become unrunnable without developer presence (SC-9/SC-10 Playwright tiers blocked on stale tmp/issue-36/auth-state.json lacking the gh_auth_token cookie; two headed-login capture attempts failed to capture any cookie because the app sets the token server-side). Add ONE new atomic SC (SC-11) fixing this regression: the E2E UI test harness MUST authenticate via a test-only monkey-patched login … real production auth behavior remains unchanged and the bypass is inert outside SNEA_E2E=1 test runs." | Developer directive (Michael Conrad, 2026-10-02, chat), for_pr scope |
| 2026-10-02 | Revision (SC-11 disambiguation + atomicity split, no scope or intent change): (1) pinned SC-11 to EXACTLY ONE test-only authentication mechanism — the `SNEA_E2E`-gated test-only auth bypass hook in the app's auth path (`src/services/security_manager.py` auth resolution) — removing the "or direct cookie/context injection" alternative entirely, with rationale recorded (direct cookie injection cannot work because the app sets the token server-side and validates tokens against the live GitHub API); (2) split compound SC-11 into atomic SC-11 (E2E harness authenticates headlessly via the pinned bypass; no headed OAuth login; E2E tests run authenticated) and SC-11a (bypass inert outside `SNEA_E2E=1` — auth path behaves identically to production, verified by pytest test); (3) corrected the Enforcement Gate SC count with an unambiguous full enumeration (SC-1..SC-8, SC-8a, SC-9, SC-10, SC-11, SC-11a — 13 criteria; note: the validation finding stated "12 SCs" but its own enumeration contains 13 members, and the Missing Items table maps 13 items, so the enumerated count of 13 is authoritative); updated Per-SC Cost Frame (SC-11 entry rewritten, SC-11a entry added), Missing Items (item 12 rewritten for pinned SC-11; item 13 added for SC-11a), Edge Cases rows (SC-11/SC-11a coverage split), Dependencies row, Traceability row (SC-11a added). No existing SC removed or weakened | Validation findings from spec-creation validate (SC-11 disjunctive ambiguity, SC-11 compound, Enforcement Gate SC miscount) | Validation findings via spec-creation pipeline |
| 2026-10-02 | Revision (SC-7 validation finding + cosmetic fix, no scope or intent change): (1) SC-7 restated from the all-below-floor edge case (set-entailed by SC-5's empty-results requirement over the identical scenario) to the non-entailed per-row filtering invariant: below-floor rows are excluded from `results` whenever a threshold is active (default or explicit), verified via the PARTIALLY-below-floor mixed-distribution case under an explicit user threshold (floor-clearing rows served, below-floor rows excluded from the same result set) — the only reading under which SC-7 adds a verification signal over SC-5; SC-7's evidence method, Missing Items entry 7, Per-SC Cost Frame entry, Edge Cases row (new mixed-distribution row; all-below-floor row re-pointed to SC-5/SC-6), and Traceability row (new per-row filtering row) updated accordingly; (2) cosmetic: Problem preamble out-of-corpus range wording "0.85–0.90" replaced with the precise measured max 0.9018 (aligning with the Calibrated Floor Value Definition). SC-5 and all other SCs unchanged — nothing removed or weakened. The four analytical artifacts at tmp/1400/artifacts/ (blast-radius, concern-map, interface-compatibility, testability-assessment) refreshed to cover the SC-11/SC-11a additions (src/services/security_manager.py; e2e-auth-bypass concern) since they predate those SCs | Validation findings from spec-creation validate (SC-7 covered-by-prior; cosmetic range wording) | Validation findings via spec-creation pipeline |

🤖 Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
🤖 Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
