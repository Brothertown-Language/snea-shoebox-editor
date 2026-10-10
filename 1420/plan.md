# Implementation Plan — #1420 Agent-facing read-only records API

Spec source: `.issues/1420/spec.md` (approved 2026-10-09, terminal authorization `approved for pr`).
Branch: `feature/1420-agent-records-api`, base tip `289bb8a`.

Derivation guard: every item below traces to a spec SC (Item 0 traces to the spec's Preconditions / Phase 0 gate). No item without an SC anchor.

Naming/test conventions per repo: unit tests `test/test_<topic>_sc<N>.py`; Playwright under `test/ui/` with `playwright_e2e` marks, run under `SNEA_E2E=1` role sessions per `docs/development/ui_testing_standard.md`.

## Item 0 — Phase 0 gate: bolt-mechanism re-verification

- **Deliverable:** re-run the bolt probe (pattern: minimal Streamlit app on a scratch port; gc-find the Application; prepend a `tornado.web.Rule(PathMatches(...))` to `wildcard_router.rules`; real HTTP GET served by the same process) against the current pinned Streamlit 1.54.0 / Tornado 6.5.4. Artifacts under `/tmp/opencode/`.
- **RED:** the mechanism is not yet re-verified in this environment — no current probe artifact exists.
- **GREEN:** probe log shows rule count increment, prepend landing ahead of the catch-all, and a real GET returning the probe handler's body.
- **Instrument:** run the probe script; assert exit 0 and grep the bolt log for `PREPENDED ok` and the HTTP fetch result. HALT if the mechanism no longer holds (spec: mechanism requires revision before implementation).

## Item 1 — SC-1: bolted route serves 401 on the live app

- **Deliverable:** `src/api/` package skeleton (`__init__.py`, `registrar.py` with gc-find + rules-prepend + module latch + structural route-presence check + self-check logging + failure mode, `routes/api_not_found.py`, error formatters per Interface Contract); registrar invocation wired into `streamlit_app.py` after database initialization; `GET /api/v1/records` route stub that authenticates (401 without credentials is the SC-1 observable).
- **RED:** with the app running, `GET /api/v1/records` returns Streamlit's HTML catch-all (404 HTML), not a JSON 401.
- **GREEN:** bolted rule ahead of the catch-all serves the API handler; unauthenticated request → 401 JSON `{"error": {"code": "unauthorized", ...}}`.
- **Instrument:** start the live app locally; `curl -i http://localhost:8501/api/v1/records`; assert HTTP 401, `Content-Type: application/json; charset=utf-8`, JSON error shape; correlate with the registrar self-check log line from the same process (shared evidence with Item 2).

## Item 2 — SC-2: startup self-check log

- **Deliverable:** registrar logs the route-presence assertion at bolt time: rules found/inserted, order, pattern list (`/api/v1/records` then `/api/.*`), Application instance count, Streamlit + Tornado version numbers.
- **RED:** no self-check line exists at startup.
- **GREEN:** startup log contains the assertion listing both patterns in order with both version numbers.
- **Instrument:** start the app, capture logs, grep for the self-check line; assert `/api/v1/records` appears before `/api/.*` and both version numbers are present.

## Item 3 — SC-3: failure mode — structure absent → API disabled, UI unharmed

- **Deliverable:** the registrar's failure path: when the Application or `wildcard_router.rules` structure is not found → loud error log naming the mismatch, "API disabled" report, no exception propagation into the UI script path, no `/api/` rules registered.
- **RED:** no failure path exists; a missing structure raises or crashes.
- **GREEN:** structure-less fixture → loud log + no exception; live app runs normally with the API absent.
- **Instrument:** unit test `test/test_api_registrar_failure_sc3.py` exercising the registrar against a structure-less Application fixture (assert loud log record + no raised exception); Playwright session completing an authenticated UI page load against the live app while `/api/` routes return nothing.

## Item 4 — SC-4: bolt idempotency

- **Deliverable:** idempotency proof: module-level latch + structural route-presence scan prevent duplicate rules across script reruns, distinct browser sessions, module reloads.
- **RED:** repeated registrar invocation stacks duplicate rules (the probe's per-session `st.session_state` guard behavior).
- **GREEN:** repeat invocations leave exactly one rule per API pattern.
- **Instrument:** unit test `test/test_api_registrar_idempotent_sc4.py`: invoke the registrar N times against one Application fixture; assert rule count unchanged after first bolt. Corroborate: self-check log across two distinct browser sessions.

## Item 5 — SC-8: key storage — hashed secrets at rest

- **Deliverable:** `src/database/models/api_keys.py` (`ApiKeys`: `id`, `key` unique, `secret_hash`, `label`, `created_by`, `created_at`, `enabled`, `revoked_at`, `last_used_at`); versioned migration in `src/database/migrations.py`; `ApiKeys` registered in `init_db()`'s Base.metadata import list (`src/database/connection.py`); `src/services/api_key_service.py` with PBKDF2-HMAC-SHA256 hashing (per-secret random salt, 600,000 iterations, `pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>`), stdlib `secrets` generation (key `snea_` + `token_urlsafe(16)`, secret `token_urlsafe(32)` ≥256-bit).
- **RED:** no `api_keys` table exists; issuing produces no hash-verified storage.
- **GREEN:** key issuance stores only the versioned hash; the known plaintext secret later authenticates via hash verification.
- **Instrument:** unit test `test/test_api_key_storage_sc8.py`: issue a key with a known secret; full-table-scan the `api_keys` table; assert plaintext appears nowhere and every `secret_hash` matches the versioned format; verify the known secret authenticates.

## Item 6 — SC-7: admin view (admin-gated, lifecycle actions)

- **Deliverable:** `src/frontend/pages/api_keys.py` registered in the Admin section (`src/services/navigation_service.py`) — key list (label, key identifier, created, last used, status), create pair (secret shown exactly once), regenerate secret (shown exactly once), enable/disable, revoke with confirmation; never redisplay an existing secret.
- **RED:** no API-keys admin page exists in the navigation; admin sees nothing to manage.
- **GREEN:** admin renders the page and each lifecycle action produces its R-8 observable outcome; viewer/editor sessions get the permission-denied block.
- **Instrument:** Playwright real-browser tests per `docs/development/ui_testing_standard.md` with the established `SNEA_E2E=1` role sessions (`SNEA_E2E_ROLE` = admin / editor / viewer), `playwright_e2e`-marked; assert gating + each action's observable outcome. **Before authoring/running: read `docs/development/ui_testing_standard.md` and `test/ui/AGENTS.md`.**

## Item 7 — SC-9: lifecycle + auth-failure audit trail

- **Deliverable:** lifecycle audit events via `EventLogService` into `system_event_log` (`api_key_created`, `api_key_regenerated`, `api_key_enabled`, `api_key_disabled`, `api_key_revoked` — key identifier + acting admin, never secret material); auth-failure logging `api_auth_failure` (presented key identifier if parseable, outcome, client address — never the presented secret).
- **RED:** no API-key events appear in `system_event_log`.
- **GREEN:** each lifecycle op and each failed auth (401 + 403) writes its event with the specified type and no secret value.
- **Instrument:** unit test `test/test_api_key_audit_sc9.py`: perform each lifecycle operation + trigger failed auths; query `system_event_log`; assert event types and absence of the secret value in every event row.

## Item 8 — SC-5: auth + method matrix

- **Deliverable:** `src/api/auth.py` (`X-API-Key` + `X-API-Secret` headers, lookup by key, `hmac.compare_digest` of the PBKDF2 hash, values compared as received — no trimming/case normalization, `last_used_at` update on success, 401 uniform message vs 403 disabled/revoked semantics); method scoping (non-GET on defined routes → 405 JSON); `/api/.*` catch-all wiring (unknown API paths → JSON 404).
- **RED:** none of the matrix outcomes exist (endpoint is absent or unguarded).
- **GREEN:** full matrix holds — valid pair 200; unknown key 401; wrong secret 401 (same message); disabled 403; revoked 403; missing headers 401; POST → 405; unknown `/api/` path → JSON 404.
- **Instrument:** HTTP-level test suite `test/test_api_auth_matrix_sc5.py` against the live app with seeded keys covering the full matrix; assert status codes, the single uniform 401 message, and JSON error bodies.

## Item 9 — SC-6: dump payload matches the database

- **Deliverable:** `src/api/routes/records.py` — `GET /api/v1/records` serving live records (`is_deleted = false`) ordered by ascending `id`, each record EXACTLY the closed 15-field whitelist with resolved `source` name and primary-first `languages` codes; `count` equals record count; timestamps ISO 8601 UTC.
- **RED:** the endpoint returns no records (auth stub only).
- **GREEN:** payload equals the database: count, field-for-field values, ordering, and no excluded column key ever appears.
- **Instrument:** comparison script `test/test_api_records_dump_sc6.py`: query the DB for live records; fetch the endpoint with a valid pair; compare every record on every whitelisted field; assert each record's field-key set equals the closed whitelist.

## Item 10 — SC-11: UTF-8 JSON, unescaped Unicode, byte-exact

- **Deliverable:** response encoding: `application/json; charset=utf-8`, `ensure_ascii=False`, linguistic content preserved byte-exact from the DB (no normalization/stripping/re-encoding).
- **RED:** no responses are produced by the endpoint yet (or would be ASCII-escaped by default `json.dumps`).
- **GREEN:** raw response bytes carry Unicode (ə, ŋ, ã, ꝏ) unescaped and byte-identical to DB values.
- **Instrument:** `test/test_api_encoding_sc11.py`: fetch the endpoint; assert `Content-Type`; select records known to contain IPA/diacritics; compare raw response bytes against database values.

## Item 11 — SC-12: no DB exposure in error surfaces

- **Deliverable:** error formatters produce only the generic JSON shape; static/generic messages for every status code; no connection strings, hosts, ports, SQL, or stack traces anywhere in error output.
- **RED:** error formatters don't exist (or would echo framework/DB detail).
- **GREEN:** every error body for every status code matches the generic shape and passes the blocklist.
- **Instrument:** unit test `test/test_api_error_exposure_sc12.py` asserting every error formatter's output against the blocklist pattern set (`postgres://`, host/port tokens, traceback markers); live spot-checks of 401/404/429 bodies.

## Item 12 — SC-10: per-key rate limit

- **Deliverable:** in-memory per-process fixed-window limiter (default 60 req/60 s, overridable via `api.rate_limit_per_minute` secrets key); exceeding window → 429 + `Retry-After`; per-key isolation.
- **RED:** no limiter exists; a burst never receives 429.
- **GREEN:** burst past the configured window → 429 + `Retry-After` on every request past the window; a second key's concurrent requests still 200; first-429 request count equals the configured limit.
- **Instrument:** `test/test_api_rate_limit_sc10.py` with a low test limit: burst one key past the window; assert 429 + `Retry-After` + second-key isolation + exact trigger count.

## Item 13 — Full SC re-run + regression protocol

- **Deliverable:** complete verification pass across SC-1…SC-12 per the spec's evidence types (behavioral evidence for behavioral SCs — live-app HTTP checks and Playwright, never claims from reading code).
- **RED:** the full suite has not yet run end-to-end on the completed feature.
- **GREEN:** every SC's instrument passes; pre-existing test suite shows no regression.
- **Instrument:** run all new test files + the project's existing test suite (after `bash scripts/sync_prod_to_local.sh` per the repository regression-test protocol); collect outputs as PR evidence.

## Dependency order

Item 0 gates everything (HALT on failure). Items 1–4 (bolt + scoping skeleton) precede 5–7 (storage + admin + audit). Item 8 (auth) requires Item 5 (keys to authenticate). Item 9 requires Items 1 + 8 (routed + authenticated). Items 10–12 refine the endpoint. Item 13 is last.

## Phasing (spec § Implementation Phases)

- Phase 0 → Item 0
- Phase 1 → Items 1–4 (SC-1..4)
- Phase 2 → Items 5–7 (SC-7, SC-8, SC-9 lifecycle)
- Phase 3 → Items 8–11 (SC-5, SC-6, SC-11, SC-12)
- Phase 4 → Items 7 (auth-failure events), 12 (SC-10), 13 (full re-run)
