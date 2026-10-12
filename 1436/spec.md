# Spec — full-suite `SNEA_E2E=1` invocation races the unbolted API (#1436, class 1)

## Problem

Running the full suite (`uv run pytest -q --ignore=tmp`) with `SNEA_E2E=1` against a freshly started live app on :8501 turns 22 API-class tests red across six files — `test/test_api_auth_matrix_sc5.py` (10), `test/test_api_records_dump_sc6.py` (4), `test/test_api_encoding_sc11.py` (3), the live class of `test/test_api_error_exposure_sc12.py` (2), the live class of `test/test_api_key_audit_sc9.py` (2), `test/test_api_rate_limit_burst_sc10.py` (1) — each failing with an HTTP 200 where 401/403/404/405/429 is expected. The supported invocations (plain `pytest test/` serverless; per-file `SNEA_E2E=1` E2E after the documented warmup) show none of these failures. Surfaced 2026-10-11 by the #1434 suite-green gate; recorded in `.pytest_cache/v/cache/lastfailed` and the issue filing.

Triage (2026-10-12) refuted the filing's hypothesized mechanism — the test-only auth bypass is not involved:

- API authentication reads only request headers against the database (`src/api/auth.py:98-117`); the `SNEA_E2E` bypass writes only `st.session_state` inside the app process (`src/services/security_manager.py:85-146`); no API handler touches session state (`src/api/context.py:8`).
- `test_valid_pair_returns_200` — valid credentials — failed in the same runs (`lastfailed`); a bypass that authenticated everything would have made it pass.
- The encoding file's 3-of-4 failure pattern byte-matches Streamlit's static `index.html` (IPA marker present, zero `\u` escapes, non-JSON body), fingerprinting the response source.

Root cause — bolt-warmup race. The agent-facing API is a Tornado bolt installed on the running server during the app's first browser script run (`streamlit_app.py:225-229`, inside `_initialize_database()`; `src/api/registrar.py:108`; idempotent latch `registrar.py:119-150`). The API test docstrings state the dependency — "the bolt requires a first browser session; run the Playwright warmup before this suite" — but it exists only as prose; no executable gate enforces it. In the full-suite collection `test/test_api_*` sorts before `test/ui/`, the app is headless (`.streamlit/config.toml` `headless = true`) so no browser connects on its own, and `/_stcore/health` answers ok as soon as the runtime leaves its initial state — with no script run required. The API tests therefore run against an app that has never executed its script: the bolt is absent, and every `/api/*` request falls through to Streamlit's static catch-all, which serves `index.html` with status 200 (GET) or 405 HTML (POST) — the observed 200s. The filing's failure-count variation (5 vs 23 across two runs) is this class's health-gate timing plus the #1438 semantic trio, not additional defects.

## Design direction (triage recommendation, 2026-10-12 — approval pending)

Two test-side mechanisms close the race and make the invocation trustworthy:

1. **Executable warmup.** A new `test/conftest.py` (none exists today) carries a session-scoped autouse fixture that, only when `SNEA_E2E=1` is set and the app answers health, opens one throwaway browser session against the app to trigger the first script run, then waits until a no-credential probe of the API returns 401 JSON — the bolt-installed signal — before releasing the suite. Idempotent by the registrar's existing latch.
2. **Bolt-presence gate.** The live API test classes share one setUpClass-stage gate (after today's health check): a no-credential probe must return 401 with a JSON error body; any other response — 200 text/html is the unbolted catch-all — fails the class loudly with a message naming the uninstalled bolt and the warmup requirement.

Together: the warmup makes the full-suite invocation deterministic; the gate converts any residual unbolted state (warmup breakage, app restart mid-run, ad-hoc invocations) from 22 uninterpretable reds into one diagnosable failure.

Rejected alternatives:

- The filing's two fix directions. Env scrubbing cannot affect the separate app process, and pre-import scrubbing merely flips the skipIf gates into silent skips — coverage loss disguised as green. Scoping the bypass away from API auth changes nothing: no code path couples them (proofs above).
- App-side decoupling of bolt installation from browser sessions: crosses the `registrar`/`context` design surface (never-crash-the-UI semantics, fail-closed 503 on a missing session factory, existing bolt SC coverage) and rewrites working production-path code to fix a test-invocation defect — maximal blast radius on the problem's smallest surface.

## Requirements

- **SC-1 (behavioral; the reported failure):** under the full-suite invocation (`uv run pytest -q --ignore=tmp`, `SNEA_E2E=1`, live app on :8501, freshly synced database), every test in the six API files listed above passes.
- **SC-2 (behavioral; supported per-file path preserved):** with the warmed live app, each of the six API files passes under its per-file `SNEA_E2E=1` invocation.
- **SC-3 (behavioral; serverless path preserved):** a plain serverless run of `test/` (`uv run pytest test/ -q`, `SNEA_E2E` unset) produces the six files' pre-change outcomes — live classes skip by design, already-green tests stay green — and the run opens no browser session.
- **SC-4 (structural; race closed by construction, failure diagnosable):** the warmup mechanism activates only when `SNEA_E2E=1` is set and the app answers health, with that gate preceding any browser or Playwright use; the shared bolt-presence gate fails loudly — naming the uninstalled bolt and the warmup requirement — whenever the no-credential probe response is not 401 JSON.
- **SC-5 (structural; fix is test-side):** the change touches no `src/` code, no app entrypoint, and no dependency manifests; the `SNEA_E2E` bypass and API auth code are untouched.

## Verification instruments

Per the regression protocol, `bash scripts/sync_prod_to_local.sh` runs before the verification cycle, and all runs execute on the feature branch under test.

- **SC-1:** one pre-fix reproduction of the API-class reds on the branch under test (the recorded 2026-10-11 `lastfailed` plus a fresh run), then one post-fix full-suite run — the six files' nodeid outcomes are all green; run output recorded under `tmp/1436/artifacts/`. Other reds in the same run (the #1438 semantic trio; any #1426 order-dependence failures) are documented out-of-scope defects and do not bar SC-1.
- **SC-2:** six executed per-file invocations, one per file, against the warmed live app — all green; recorded under `tmp/1436/artifacts/`.
- **SC-3:** executed serverless runs before and after the change — the six files' nodeid outcomes identical in both (live classes SKIP); recorded under `tmp/1436/artifacts/`.
- **SC-4, SC-5:** fact-decidable inspection — the conftest gate order and the shared gate's failure message in the diff; the diff's path scope.

## Out of scope

- App-side decoupling of bolt installation from browser sessions (rejected above).
- The semantic zero-result E2E failures — carved out to sub-issue #1438; they co-occur in the same full-suite run.
- The serverless suite's order-dependent DB contamination — #1426.
- Marker alignment of the live API classes with the deck's `playwright_e2e` contract, and any change to the tests' assertions, thresholds, or coverage — the fix is invocation integrity; the production auth path's test surface is unchanged.

## Impact

- **Scope:** one new `test/conftest.py`, one shared bolt-presence gate helper, and setUpClass touch points in the six API files; no application code, no data, no dependencies.
- **Risk:** the warmup adds one browser session per E2E run (seconds); a warmup that cannot reach the app must fail or skip loudly rather than hang the suite — its wait bound is a plan decision. The gate's loud-failure path must not fire in correctly warmed runs: the probe expects the same 401 the auth matrix itself asserts.
- **Test impact:** API-class outcomes under the supported invocations are unchanged; the full-suite `SNEA_E2E=1` invocation becomes a trustworthy gate.

🤖 Co-authored with AI: OpenCode (huggingface/zai-org/GLM-5.3-Flash)
