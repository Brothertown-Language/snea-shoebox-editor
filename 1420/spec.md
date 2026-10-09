# SPEC: Agent-facing read-only records API — bolted-in GET endpoints with admin-issued key+secret auth

## User Intent / Original Prompt

The developer (2026-10-07) directed, verbatim:

> "an API endpoint managed by the Streamlit app that an agent can PULL from for getting a DB dump for use. An admin view added that allows setting up key+secret pairs for API access. GET requests mainly. Records only (linguistic data)."

Security directive, verbatim: *"Assume we never want agents accessing things via the db from other projects as a major security risk"* — the API is the sole sanctioned remote data surface; it must not expose DB connectivity to other projects.

Binding design decisions from the 2026-10-07 discussion: routes are bolted into the Streamlit server's own Tornado application — *"it would be better to have routes bolted in, all with a single parent api folder so that the actual api endpoints can then be named as needed"*; a FastAPI sidecar is IMPOSSIBLE on Streamlit Community Cloud (single process, one port); GET-only, records-only scope; key+secret pairs issued via an admin view with hashed secret storage and audit events into the existing `system_event_log`.

## Intent / Executive Summary

Add an agent-facing, read-only HTTP API managed by the Streamlit app itself: `GET /api/v1/records` serves the app's linguistic record data (the `records` lexical-entry table) as a single JSON dump for consumption by agents in other projects. Routes are bolted into the Streamlit server's running Tornado application from app code — no sidecar process, one port, Community Cloud compatible — with all API code under a single parent package (`src/api/`) whose per-endpoint route modules name their own paths. Access is gated by key+secret pairs issued through a new admin-gated admin view: secrets are stored hashed (never plaintext), shown exactly once at issuance, and support enable/disable/regenerate/revoke; key lifecycle events and failed-auth attempts are audited into the existing `system_event_log`. The endpoint never exposes DB connectivity — other projects' agents consume only the HTTP API with issued keys.

## Root Cause

The app's linguistic record data lives in PostgreSQL reachable only from inside the app's own process and infrastructure. Agents in other projects (downstream language tools, analysis scripts) currently have no sanctioned way to consume the dataset: the only paths would be direct DB credentials — explicitly forbidden as a major security risk — or manual one-off exports. There is no HTTP surface, no API credential management, and no audit trail for programmatic access.

## Approach

1. **Route bolt-in (verified mechanism).** A registrar module (`src/api/registrar.py`) is invoked from `streamlit_app.py` at first script run (after database initialization). It gc-finds the running `tornado.web.Application` instance(s) and prepends `tornado.web.Rule(tornado.routing.PathMatches(pattern), Handler)` entries to `app.wildcard_router.rules` ahead of Streamlit's catch-all — the specific endpoint rule (`/api/v1/records`) first, then a `/api/.*` catch-all rule serving the JSON 404 contract. Streamlit's own routes remain untouched behind the prepended block. Route handlers run outside Streamlit's script-runner context: they never use `st.*` APIs or session state; they access the database only through the shared engine/session factory.
2. **Single parent API package.** All API code lives under `src/api/`: the registrar, request authentication (`src/api/auth.py`), and per-endpoint route modules (`src/api/routes/*.py`) — each module defines its own path pattern and handler; future endpoints are added as new modules under this parent, each declaring its own path pattern.
3. **Key+secret credentials.** A new `api_keys` table (model + migration on the existing migrations stack) and `src/services/api_key_service.py` implement create / regenerate-secret / enable / disable / revoke. Secrets are generated with the stdlib `secrets` module (≥256-bit) and stored ONLY as PBKDF2-HMAC-SHA256 hashes (per-secret random salt, 600,000 iterations, versioned string format); the plaintext secret is displayed exactly once in the admin view and never persisted, logged, or embedded in audit events.
4. **Admin view.** `src/frontend/pages/api_keys.py` is registered in the Admin section of the navigation tree (admin-gated like the other admin pages): key list, create pair, regenerate secret, enable/disable, revoke with confirmation.
5. **Dump endpoint.** `GET /api/v1/records` serves live (`is_deleted = false`) `records` rows as a single JSON response, ordered by ascending id, serialized against a closed field whitelist with the resolved source name and primary-first language codes embedded so each record is self-contained.
6. **Request hardening.** Constant-time credential comparison; per-key fixed-window rate limit (429 + `Retry-After`); a JSON error contract for 401/403/404/405/429/503; failed-auth attempts logged to `system_event_log`.

## Verified Mechanism (probe evidence, 2026-10-07)

Grounding for R-2 through R-4 — empirically verified live on this project's pinned stack:

- **Versions:** Streamlit 1.54.0 and Tornado 6.5.4 (both pinned in `uv.lock`), matching the probe environment exactly.
- **Probe behavior:** a minimal Streamlit app on :8505 executed the bolt at first script run. `gc.get_objects()` filtered to `tornado.web.Application` found exactly 1 instance; `wildcard_router.rules.insert(0, tornado.web.Rule(tornado.routing.PathMatches("/api/probe"), Handler))` prepended successfully (rule count 11 → 12). A real browser then fetched `GET /api/probe` and received `{"bolted": true}` served by the same process. Streamlit's own routes were present and untouched (the prepend landed ahead of the catch-all).
- **Probe artifacts:** `/tmp/opencode/st-api-probe/` (`app.py`, `bolt.log`) — ephemeral probe workspace; not committed to the repository.
- **Encoded constraints:**
  - (a) The bolt is a one-shot at first script run and persists for the server lifetime — and MUST be idempotent (rerun-safe). The probe's `st.session_state` guard is adequate only for a single browser session (session state is per-session, so a second session would re-bolt and stack duplicate rules); the production guard is therefore a module-level latch PLUS a structural route-presence check that scans existing rules for the same path patterns before inserting (R-3).
  - (b) `wildcard_router` is an internal Streamlit/Tornado structure. The spec pins Streamlit 1.54.0 / Tornado 6.5.4 and requires a startup self-check — a route-presence assertion logged at bolt time, including both version numbers (R-4) — plus a documented failure mode: if the structure is missing or changed, log loudly, leave the app running, disable the API; never crash the UI.
  - (c) Community Cloud compatibility follows from the same single-process mechanism. Community Cloud's own constraints are recorded as deployment considerations: the database is configured via the secrets store (works unchanged — the bolted handlers read the same connection factory), no long-running sidecar processes are permitted (the bolted-in design has none — a sidecar was impossible anyway), and the platform runs a single process/instance (consistent with the module-level latch and in-memory rate limiter). HTTPS is terminated by the platform, so key+secret headers travel encrypted.

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| FastAPI (or any) sidecar service | Impossible on Streamlit Community Cloud — single process, single port; a second listening process cannot be hosted. Bolted-in routes are the chosen shape and are empirically proven |
| Direct DB credentials / read replica for other projects | Developer directive: never — agents accessing the DB from other projects is a major security risk; the DB gains no new exposure |
| Public unauthenticated endpoint | Records are the community's curated dataset; unauthenticated pull permits uncontrolled scraping with no audit trail and no revocation path |
| `Authorization: Bearer <token>` | A single token conflates identifier and credential, preventing independent rotation of key vs secret; key+secret headers keep them distinct |
| HMAC request signing (AWS-style) | Unnecessary complexity for a read-only GET surface over platform-terminated HTTPS |
| JSONL response format | A single JSON response is sufficient at ~7,753 records; JSONL adds a second format to test with no consumer requirement yet |
| Streaming / chunked pagination | The dump is small (single response acceptable per developer directive); pagination is a follow-up if dumps grow |
| Write API (POST/PUT/DELETE) | Out of scope — the surface is a read-only dump; write safety and workflow are separate concerns |
| WSGI-mounted Flask/FastAPI inside Tornado | The same bolt-in complexity plus a new framework dependency; Tornado handlers are already available in-process with zero new dependencies |

## Key Decisions

- **Bolted-in Tornado routes over any sidecar** — single process, one port; empirically proven on the pinned versions
- **gc-discovery + rules-prepend** — no public Streamlit extension API exists for arbitrary routes; the registrar finds the live Application instance(s) at first script run
- **Idempotency = module-level latch + structural route-presence check** — the probe's `session_state` guard is per-browser-session and insufficient alone; production requires cross-session rerun safety
- **Graceful degradation over hard coupling** — `wildcard_router` is internal; if it disappears on an upgrade, the API disables with a loud log while the UI continues
- **Version pinning** — the mechanism is specified against Streamlit 1.54.0 / Tornado 6.5.4 (both in `uv.lock`); Phase 0 re-verifies before implementation
- **Single parent package `src/api/`** — all API code (registrar, auth, routes) under one parent; future endpoints are added as new modules under `src/api/routes/`, each declaring its own path pattern
- **`GET /api/v1/records`, one endpoint in v1** — the `/api/v1` prefix leaves room for future endpoints without path ambiguity; no health/probe route is shipped (the self-check is structural)
- **`X-API-Key` + `X-API-Secret` headers** — the key identifies, the secret authenticates; constant-time comparison; uniform 401 message that never distinguishes unknown key from bad secret
- **Password-grade hashing for secrets** — PBKDF2-HMAC-SHA256, per-secret random salt, 600,000 iterations, versioned hash string; plaintext never persisted
- **Records-only payload with resolved references** — closed field whitelist; source name and language codes embedded so the dump is self-contained; the embedding vector, lock state, and internal user-identity columns are excluded
- **`system_event_log` as the audit sink** — the #1332 `EventLogService` infra is reused for key lifecycle and auth-failure events
- **Stdlib-only implementation** — `gc`, `hashlib`, `hmac`, `secrets`, `json`; Tornado already present; no new dependencies
- **Rate-limit-lite included** — per-key fixed window (default 60 requests per 60 seconds), in-memory per process, 429 + `Retry-After`

## Interface Contract

### Endpoints (v1)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/v1/records` | key+secret required | Full dump of live linguistic records |
| any | `/api/.*` (no endpoint matched) | none processed | JSON 404 catch-all — unknown API paths never fall through to the UI |

### Authentication

- Headers: `X-API-Key: <key>` and `X-API-Secret: <secret>` — both required on every API request.
- The key is a unique public identifier (`snea_` prefix + `secrets.token_urlsafe(16)`); the secret is a ≥256-bit credential (`secrets.token_urlsafe(32)`).
- Verification: lookup by key, then constant-time comparison (`hmac.compare_digest`) of the PBKDF2 hash of the presented secret. Header values are compared as received (no trimming or case normalization of values).
- Status semantics: **401** for missing headers / unknown key / wrong secret — one uniform message, never distinguishing unknown key from bad secret; **403** for a known key that is disabled or revoked.

### Success response (200)

```json
{
  "count": 7753,
  "records": [
    {
      "id": 123,
      "lx": "…",
      "sort_lx": "…",
      "hm": 1,
      "ps": "…",
      "ge": "…",
      "source_id": 2,
      "source_page": "…",
      "status": "approved",
      "mdf_data": "…",
      "current_version": 4,
      "is_deleted": false,
      "updated_at": "2026-10-07T12:00:00+00:00",
      "source": "…",
      "languages": ["<primary-code>", "…"]
    }
  ]
}
```

- The field whitelist is CLOSED — exactly the 15 fields above; no other `records` column is ever serialized. Excluded by design: `embedding` (derived search vector, not linguistic data), `is_locked`/`locked_by`/`locked_at`/`lock_note` (operational lock state), `updated_by`/`reviewed_by`/`reviewed_at` (internal user identities).
- `source` is the resolved `sources.name`; `languages` is the record's language codes ordered primary-first.
- Ordering: ascending `id`. Only live records (`is_deleted = false`) are served.
- Timestamps: ISO 8601 UTC. `count` equals the number of records in the response.

### Error contract

All API responses carry `Content-Type: application/json; charset=utf-8`. Error body shape: `{"error": {"code": "<code>", "message": "<generic message>"}}` — messages are static/generic and never include DB connection details, host names, SQL, or stack traces.

| Status | `code` | When |
|---|---|---|
| 401 | `unauthorized` | missing headers, unknown key, wrong secret |
| 403 | `key_disabled` | key known but disabled or revoked |
| 404 | `not_found` | path under `/api/` matching no endpoint |
| 405 | `method_not_allowed` | non-GET on a defined API route |
| 429 | `rate_limited` | per-key window exceeded; includes `Retry-After` header |
| 503 | `service_unavailable` | database unavailable |

### Response encoding

- JSON serialized with `ensure_ascii=False` — Unicode (ə, ŋ, ã, č, ꝏ, combining diacritics) is emitted as raw UTF-8, never `\u`-escaped, and never normalized (project data-integrity rules).
- Success responses are a single JSON document (no pagination in v1).

## Not Included

- **Write paths** — no POST/PUT/DELETE/PATCH on any API route; the surface is read-only.
- **Tables beyond linguistic records** — `users`, `permissions`, `user_activity_log`, `system_event_log`, `edit_history`, `matchup_queue`, the search/FTS index tables, `schema_version`, and any secrets/config storage are never served; the closed whitelist in the Interface Contract is the entire data surface.
- **Cross-project DB access** — the endpoint never exposes connection strings, hosts, ports, or sockets; other projects consume only the HTTP API with issued keys; the DB gains no new exposure of any kind.
- **Pagination, streaming, JSONL** — single JSON response; revisit only if the dump outgrows it.
- **Query parameters / filters** — the dump is the whole live dataset; unexpected query parameters are ignored (no 400 path).
- **OAuth/JWT/token infrastructure** — key+secret pairs are the only credential type.
- **Key expiry dates** — revocation covers the lifecycle; expiring keys are a follow-up if needed.
- **Per-endpoint or per-IP rate limiting** — one per-key limit applies uniformly.
- **A health/probe endpoint** — the startup self-check is structural (logged route-presence assertion); no unauthenticated liveness route is shipped, and the feasibility probe's `/api/probe` endpoint is not part of the deliverable.
- **A FastAPI or other sidecar process** — impossible on Community Cloud and superseded by the bolted-in mechanism.

## Dependencies

| Dependency | Purpose | Version/Constraint | Availability Requirement |
|---|---|---|---|
| Streamlit | Host server whose Tornado app receives the bolted routes | 1.54.0 (`uv.lock`) — the verified mechanism is pinned to this version | Already the app framework |
| Tornado | Routing/HTTP layer receiving the prepended rules | 6.5.4 (`uv.lock`) — pinned | Already a Streamlit dependency |
| Python stdlib (`gc`, `hashlib`, `hmac`, `secrets`, `json`) | Registrar, hashing, credential generation, serialization | Python 3.12+ | No new dependency |
| PostgreSQL / SQLAlchemy | `api_keys` table, records query, audit writes | Existing stack | Existing |
| `EventLogService` (#1332) | Audit sink for key lifecycle + auth failures | Existing | `system_event_log` table present |

## Terminology

Terms the spec relies on, defined against the repository at `main@289bb8a`:

- **Admin section of the navigation tree** — the `Admin` section built by `NavigationService` (`src/services/navigation_service.py:78-80`): `nav_tree["Admin"]` is populated only when `user_role == "admin"`. "Admin-gated like the other admin pages" (Approach item 4, R-8) means the established in-page guard pattern of the existing admin pages (e.g. `src/frontend/pages/table_maintenance.py:129-130`, `src/frontend/pages/batch_rollback.py:294-295`): a non-admin role receives the permission error and no page content.
- **Shared engine/session factory** — the `get_engine()` / `get_session()` accessors in `src/database/connection.py:600` and `src/database/connection.py:710`; "the shared engine/session factory" (Approach item 1, R-2) means database access exclusively through these functions.
- **The existing migrations stack** — the versioned `MigrationManager` (`src/database/migrations.py:100`, `run_all()` at `src/database/migrations.py:199`), invoked by `init_db()` after `Base.metadata.create_all` (`src/database/connection.py:691-694`); "migration via the existing migrations stack" (R-6) means adding a versioned migration there, recorded in the `schema_version` table.
- **Primary-first language codes** — the language codes of a record's `record_languages` join rows (`src/database/models/core.py:46-56`: `record_id`, `language_id`, `is_primary`), ordered with the row whose `is_primary` is true first, then the remaining rows' codes; this is the resolution path the app already uses for primary-language filtering (`src/services/linguistic_service.py:428-431`, `RecordLanguage.is_primary == True`). SC-6 and SC-11 verify the payload's `languages` bytes against this ordering.
- **Module-level latch** — expanding R-3's inline definition: a module-scoped boolean in the registrar, set once the bolt has run; because a module object is created once per interpreter import, the latch persists across Streamlit script reruns and distinct browser sessions within the process and only resets on interpreter restart or module reload — the structural route-presence check (R-3) independently prevents duplicate rules on module reload, where the latch state would be recreated.
- **The established `SNEA_E2E=1` role-selection sessions** — the project's test-only E2E authentication (established 2026-10-02; `docs/development/ui_testing_standard.md:36-41`): with `SNEA_E2E=1` the app authenticates via the test-only bypass hook `rehydrate_session` (`src/services/security_manager.py:64`) using a synthetic test-only identity; the role under test is selected with the `SNEA_E2E_ROLE` environment variable (`E2E_ROLE_ENV_VAR` at `src/services/security_manager.py:23`, read under the bypass at `src/services/security_manager.py:123`), values `admin` / `editor` / `viewer`. SC-7's Playwright runs start one such session per role.

## Documentation Sources

Provenance for the factual assertions used above (repository facts checked against `main@289bb8a`; external pages verified live 2026-10-09):

- **Records dataset size (~7,753; Alternatives Considered JSONL row, Interface Contract example):** verified against the local synced replica during pre-analysis — 7,753 total rows in the `records` table, 7,750 live (3 soft-deleted) — recorded in `.issues/1420/artifacts/state-analysis.yaml:109` and `.issues/1420/artifacts/state-analysis.yaml:147`. The endpoint serves only the live subset (R-9), so `count` reflects live records.
- **Community Cloud constraints (User Intent, Verified Mechanism (c), Alternatives Considered):** HTTPS termination by the platform is documented by Streamlit — "HTTPS support" (https://docs.streamlit.io/develop/concepts/configuration/https-support): "Streamlit Community Cloud uses this approach" (SSL termination in a reverse proxy/load balancer) and "Community Cloud already serves your app with TLS". The single-process / one-port constraint is recorded as a decided deployment assumption from the developer's binding 2026-10-07 design decision (quoted verbatim in User Intent and Change Control); the official Community Cloud "Status and limitations" page (https://docs.streamlit.io/deploy/streamlit-community-cloud/status) was checked 2026-10-09 and does not state that constraint verbatim.
- **PBKDF2-HMAC-SHA256 with 600,000 iterations (Approach item 3, Key Decisions, R-6):** OWASP Password Storage Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) — "use PBKDF2 with a work factor of 600,000 or more and set with an internal hash function of HMAC-SHA-256". The spec's value matches that guidance; no in-app precedent exists (Change Control, initial entry).
- **Second-session re-bolt (Verified Mechanism (a), Key Decisions):** grounded in Streamlit's documented session-state semantics — "Session State is a way to share variables between reruns, for each user session" (https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) — and the probe's structural evidence: the probe bolt appends one rule per invocation (`app[0] PREPENDED ok (rules now 12)`, `/tmp/opencode/st-api-probe/bolt.log`) and the probe's only guard is `st.session_state`-keyed (`/tmp/opencode/st-api-probe/app.py:37-40`), so a distinct browser session starts with an empty `st.session_state` and would re-bolt, stacking duplicate rules.
- **No public Streamlit extension API for arbitrary routes (Key Decisions — gc-discovery rationale):** package-source check recorded 2026-10-09 against the installed pinned stack — Streamlit 1.54.0 (`uv.lock:1399`; installed dist-info `streamlit-1.54.0.dist-info`, METADATA `Version: 1.54.0`) and Tornado 6.5.4 (`uv.lock:1558`; installed `tornado-6.5.4.dist-info`): grep of `.venv/lib/python3.12/site-packages/streamlit/` for public route-registration APIs (`def add_route`, `def register_route`, `def expose`, `def add_handler`) returns no matches, and `wildcard_router` appears nowhere in the Streamlit package — it is a Tornado `Application` attribute defined at `.venv/lib/python3.12/site-packages/tornado/web.py:2236`, reachable only on the live Application instance via gc-find (the bolt mechanism verified in the Verified Mechanism section; probe artifacts `/tmp/opencode/st-api-probe/`).
- **Audit sink provenance (Key Decisions, R-7, R-13):** `EventLogService` is the #1332 unified system-event entry point writing to the `system_event_log` table — header at `src/services/event_log_service.py:3` ("issue #1332"), class at `src/services/event_log_service.py:22`; table at `src/database/models/event_log.py:27`.

## Preconditions

- Phase 0 re-verification has passed: the bolt probe re-run against the current pinned versions confirms rule-prepend and same-process serving before implementation begins.
- The `system_event_log` table and `EventLogService` are available (existing #1332 infra).
- The local database is synced from production before regression testing, per the repository's regression-test protocol.

## Requirements

### SHALL Requirements

- **R-1. Single parent API package.** All API code SHALL live under one parent package `src/api/`: the registrar (`src/api/registrar.py`), request authentication (`src/api/auth.py`), and per-endpoint route modules (`src/api/routes/*.py`) — each route module defines its path pattern and handler; new endpoints are added as new modules under this parent.
- **R-2. Bolt mechanism.** At first script run of the app, `streamlit_app.py` SHALL invoke the registrar, which gc-finds the running `tornado.web.Application` instance(s) and prepends routing rules to `wildcard_router.rules` ahead of Streamlit's catch-all — specific endpoint rules first, then the `/api/.*` JSON-404 catch-all — per the verified mechanism. Route handlers run outside Streamlit's script-runner context and SHALL NOT use `st.*` APIs or `st.session_state`; they access the database only through the shared engine/session factory.
- **R-3. Idempotency.** The bolt SHALL be a no-op when the routes are already present: a module-level latch plus a structural route-presence check (scanning existing rules for the same path patterns) SHALL prevent duplicate rules across script reruns, distinct browser sessions, and module reloads.
- **R-4. Startup self-check + failure mode.** After bolting, the registrar SHALL log a route-presence assertion (rules found/inserted, order, pattern list, Application instance count) including the Streamlit and Tornado version numbers. If the Application or `wildcard_router.rules` structure is not found, the registrar SHALL log a loud error naming the mismatch, leave the API disabled, and the app SHALL continue running normally — no exception may propagate into the UI script path.
- **R-5. Credential scheme.** Requests SHALL authenticate via `X-API-Key` + `X-API-Secret` headers; verification SHALL use constant-time comparison; 401 SHALL be returned for missing/unknown/invalid credentials with a single uniform message, 403 for a known key that is disabled or revoked.
- **R-6. Key storage.** A new `api_keys` table (migration via the existing migrations stack) SHALL store: `id`, `key` (unique), `secret_hash`, `label`, `created_by`, `created_at`, `enabled`, `revoked_at`, `last_used_at`. Secrets SHALL be generated with the stdlib `secrets` module (≥256-bit entropy) and stored ONLY as PBKDF2-HMAC-SHA256 hashes (per-secret random salt, 600,000 iterations, versioned string format `pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>`); plaintext secrets SHALL never be persisted, logged, or embedded in audit events. `last_used_at` SHALL be updated on successful authentication.
- **R-7. Key lifecycle + audit.** The key service SHALL support create, regenerate-secret (replaces the stored hash; the old secret is invalid immediately), enable, disable, and revoke (soft mark via `revoked_at`; rows retained for audit). Each lifecycle operation SHALL be audited into `system_event_log` via `EventLogService` with event types `api_key_created`, `api_key_regenerated`, `api_key_enabled`, `api_key_disabled`, `api_key_revoked` — details identifying the key and acting admin, never containing secret material.
- **R-8. Admin view.** A new page (`src/frontend/pages/api_keys.py`) SHALL be registered in the Admin section of the navigation (admin-gated like the other admin pages) and SHALL provide: the key list (label, key identifier, created, last used, status), create pair (secret displayed exactly once), regenerate secret (displayed exactly once), enable/disable, and revoke with confirmation. It SHALL never redisplay an existing secret.
- **R-9. Dump endpoint scope.** `GET /api/v1/records` SHALL serve the live records (`is_deleted = false`) of the `records` table as a single JSON response, ordered by ascending id, each record serialized with EXACTLY the closed 15-field whitelist defined in the Interface Contract (including the resolved `source` name and primary-first `languages` codes); no other column, table, or derived index (`embedding`) is ever serialized.
- **R-10. Response encoding.** All API responses SHALL be `application/json; charset=utf-8` serialized with `ensure_ascii=False`; linguistic content SHALL be preserved byte-exact from the database — no normalization, stripping, or re-encoding of Unicode; timestamps SHALL be ISO 8601 UTC.
- **R-11. Error contract.** Every API error response SHALL use the JSON error body shape defined in the Interface Contract with static generic messages; no error response SHALL include DB connection details, hosts, SQL, or stack traces.
- **R-12. Method + path scoping.** Non-GET methods on defined API routes SHALL receive 405 (JSON); paths under `/api/` matching no endpoint SHALL receive the JSON 404 catch-all; Streamlit's own routes and UI behavior SHALL remain unchanged.
- **R-13. Auth-failure logging.** Every failed authentication attempt (401 and 403 outcomes) SHALL be logged into `system_event_log` via `EventLogService` as `api_auth_failure` with the presented key identifier (if parseable), the outcome, and the client address — never the presented secret.
- **R-14. Rate-limit-lite.** Each key SHALL be limited to a fixed window of 60 requests per 60 seconds (default; overridable via the `api.rate_limit_per_minute` secrets key); exceeding the window SHALL return 429 with a `Retry-After` header; the limiter SHALL be in-memory per process (consistent with single-process hosting).

## Success Criteria

| ID | Criterion | Evidence Type | Verification Method | Cost Frame |
|----|-----------|---------------|---------------------|------------|
| SC-1 | With the app running, `GET /api/v1/records` on the Streamlit server's port is served by the same process: an unauthenticated request returns 401 with the JSON error body, proving the bolted route is live ahead of Streamlit's catch-all | `behavioral` | Start the live app locally; issue `GET /api/v1/records` with no credentials; assert HTTP 401 with the JSON error shape; correlate with the bolt self-check log line from the same process | Running the live-app request check costs minutes of execution time — a bounded delay that surfaces a routing or bolt defect before it reaches consumers. Skipping this verification means an API route that never gets served (or breaks the UI's catch-all) ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-2 | At startup the registrar logs the route-presence self-check naming the inserted patterns in order and the Streamlit + Tornado versions | `behavioral` | Start the app; capture logs; assert the self-check line lists `/api/v1/records` ahead of the `/api/.*` catch-all and includes both version numbers | Reading the startup log costs seconds of execution time — a bounded delay that surfaces a silent mis-bolt before it reaches consumers. Skipping this verification means a bolt that quietly failed (or landed in the wrong position) ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-3 | When the Application or `wildcard_router` structure is absent (registrar exercised against a structure-less Application), the registrar logs a loud error naming the mismatch, reports the API disabled, and raises nothing; a Playwright session completes an authenticated UI page load against the live app while the API returns no responses (no `/api/` rule is registered — the API is disabled) | `behavioral` | Unit-exercise the registrar against a structure-less Application fixture (assert loud log + no exception); Playwright against the live app asserting normal UI operation | Running the failure-path fixture and UI check costs minutes of execution time — a bounded delay that surfaces a crash-the-UI defect before it reaches users. Skipping this verification means a Streamlit upgrade that changes the internal structure takes the whole app down instead of just the API, which costs 1000× more to fix. Correctness is the only metric. |
| SC-4 | The bolt is idempotent: invoking the registrar repeatedly (reruns, distinct sessions, reloads) leaves exactly one rule per API pattern — no duplicates | `behavioral` | Unit-test: invoke the registrar repeatedly against the same Application fixture and assert the rule count is unchanged after the first bolt; corroborate with the self-check log across two distinct browser sessions | Running the repeated-bolt assertions costs seconds of execution time — a bounded delay that surfaces a duplicate-rule defect before it reaches consumers. Skipping this verification means session reruns quietly stack duplicate rules and degrade routing, which ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-5 | The auth + method matrix holds: valid pair → 200; unknown key → 401; wrong secret → 401 (uniform message); disabled key → 403; revoked key → 403; missing headers → 401; POST to the endpoint → 405; unknown `/api/` path → JSON 404 | `behavioral` | HTTP-level test suite against the live app with seeded keys covering the full matrix; assert status codes, the uniform 401 message, and JSON error bodies | Running the request-matrix suite costs minutes of execution time — a bounded delay that surfaces an auth-bypass or status-code defect before it reaches consumers. Skipping this verification means a wrongly-accepted credential class (or an HTML error page leaking framework details) ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-6 | The dump payload matches the database exactly: count equals the live-record count, every record matches the DB row on every whitelisted field, ordering is by ascending id, and no excluded column appears | `behavioral` | Script: query the DB for live records; fetch the endpoint with a valid pair; compare every record field against the DB values and assert each record's field-key set equals the closed whitelist | Running the full-payload comparison costs minutes of execution time — a bounded delay that surfaces a dropped, corrupted, or over-exposed record defect before it reaches consumers. Skipping this verification means a dump that silently misses records or leaks excluded columns ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-7 | The admin view is admin-gated with the per-action observable outcomes from R-8: the page renders for an admin session while a viewer or editor session receives the permission-denied block; create pair renders the new plaintext secret exactly once and no later view renders it; regenerate renders the new secret exactly once; enable and disable flip the key's status in the list to enabled/disabled; revoke (after confirmation) sets the key's status to revoked in the list; no existing secret is ever redisplayed | `behavioral` | Playwright real-browser tests against the live app per `docs/development/ui_testing_standard.md` with the established `SNEA_E2E=1` role-selection sessions (admin / editor / viewer); assert gating and each lifecycle action's observable behavior | Running the role-variant Playwright suite costs minutes of test execution time — a bounded delay that surfaces a role-gating or credential-exposure defect before it reaches users. Skipping this verification means a viewer reaching key management (or a secret redisplayable after issuance) ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-8 | Secrets exist only as PBKDF2 hashes at rest: after issuing keys, a database inspection finds no plaintext secret value and finds the versioned `pbkdf2_sha256$` hash format for every key | `behavioral` | Issue a key with a known secret; query the `api_keys` table (full-table scan); assert the plaintext secret appears nowhere and every `secret_hash` matches the versioned format; verify the known secret authenticates (hash correctness) | Running the storage-inspection check costs minutes of execution time — a bounded delay that surfaces a plaintext-credential defect before it reaches production. Skipping this verification means a database compromise exposes every API consumer's credentials, which costs 1000× more to remediate. Correctness is the only metric. |
| SC-9 | Key lifecycle and auth failures are audited: create/regenerate/enable/disable/revoke events and every failed-auth attempt appear in `system_event_log` with the specified event types, key identifiers, and no secret material | `behavioral` | Perform each lifecycle operation and trigger failed auths; query `system_event_log`; assert the event types and that no secret value appears in any event row | Running the audit-trail verification costs minutes of execution time — a bounded delay that surfaces a missing-audit defect before it reaches operations. Skipping this verification means credential misuse with no forensic trail ships to production and costs 1000× more to untangle. Correctness is the only metric. |
| SC-10 | The per-key rate limit holds: bursting one key past the configured window returns 429 with a `Retry-After` header on every request past the window, while a second key's concurrent requests return 200; the request count that triggers the first 429 equals the configured limit | `behavioral` | Configure a low test limit; burst requests with one key past the window; assert 429 + `Retry-After` and that a second key's concurrent requests still succeed | Running the burst test costs minutes of execution time — a bounded delay that surfaces a missing or non-per-key limiter defect before it reaches consumers. Skipping this verification means a single consumer can starve the endpoint (or the limiter throttles unrelated keys), which ships to production and costs 1000× more to fix. Correctness is the only metric. |
| SC-11 | Response encoding is UTF-8 JSON with unescaped Unicode: `Content-Type` is `application/json; charset=utf-8`, Unicode-bearing headwords/glosses appear as raw UTF-8 (no `\u` escapes), and linguistic content is byte-identical to the database | `behavioral` | Fetch the endpoint; assert `Content-Type`; select records known to contain IPA/diacritic characters (ə, ŋ, ã, ꝏ) and compare raw response bytes against the database values | Running the encoding check costs seconds of execution time — a bounded delay that surfaces a mojibake or normalization defect before it reaches consumers. Skipping this verification means silently corrupted linguistic data ships to downstream projects and costs 1000× more to fix. Correctness is the only metric. |
| SC-12 | No DB exposure through the API: every error response body for every status code contains only the generic JSON error shape — no connection strings, hosts, ports, SQL, or stack traces | `string + behavioral` | Unit-assert every error formatter's output against a blocklist pattern set (`postgres://`, host/port tokens, traceback markers); live spot-checks of 401/404/429 bodies | Running the exposure checks costs minutes of execution time — a bounded delay that surfaces an information-disclosure defect before it reaches attackers. Skipping this verification means infrastructure details leak to external API consumers, which costs 1000× more to remediate after exposure. Correctness is the only metric. |

## Edge Cases

- **Missing headers / unknown key / wrong secret** → uniform 401 JSON, logged as `api_auth_failure` (no distinction revealed in the response)
- **Disabled or revoked key** → 403 JSON, logged
- **Unknown path under `/api/`** → JSON 404 catch-all, never the UI's 404 page
- **Bolt-structure change on a Streamlit upgrade** → loud error log, API disabled, UI unaffected, no crash (SC-3)
- **Duplicate bolt attempts** (script reruns, second browser session, module reload) → no-op via the module latch + structural check (SC-4)
- **Multiple Application instances found by gc** → every instance exposing `wildcard_router.rules` is bolted; the instance count is logged in the self-check
- **Empty database / zero live records** → 200 with `{"count": 0, "records": []}`
- **Database unavailable after the bolt** → 503 JSON (auth lookup and record query both fail closed); the failure is logged
- **Unexpected query parameters** → ignored (dump semantics; no 400 path)
- **Header value edge cases** → values compared as received; no trimming; empty header values fail as missing
- **Soft-deleted records** → never served (the `is_deleted` filter is part of the query, not the payload)
- **Key revoked mid-request** → the next request fails closed; auth decisions are not cached beyond the request

## Implementation Phases

### Phase 0: Feasibility re-verification (gate)
- RED: the bolt mechanism is not yet re-verified in the current environment.
- Re-run the bolt probe (artifact pattern under `/tmp/opencode/`) against the current pinned versions: assert the rule is prepended ahead of the catch-all and a real HTTP GET to the bolted path is served by the same process.
- Record the probe output as the implementation baseline; if the mechanism no longer holds, HALT — the spec's mechanism requires revision before any implementation.

### Phase 1: API parent package + registrar + bolt
- Implement `src/api/` (registrar with latch + structural check + self-check logging + failure mode; routes package; JSON-404 catch-all module; error formatters per the Interface Contract)
- Wire the registrar invocation into `streamlit_app.py` after database initialization
- Verify: SC-1, SC-2, SC-3, SC-4

### Phase 2: Key storage + admin view
- `api_keys` model + migration; `src/services/api_key_service.py` (create/regenerate/enable/disable/revoke, PBKDF2 hashing discipline); admin page + navigation entry; lifecycle audit events
- Verify: SC-7, SC-8, SC-9 (lifecycle events)

### Phase 3: Dump endpoint + scoping
- `src/api/routes/records.py` (closed field whitelist, live filter, resolved source/languages, id ordering); `src/api/auth.py` (headers, constant-time verification, 401/403 semantics); method scoping (405) and catch-all wiring; response encoding (`ensure_ascii=False`, UTF-8)
- Verify: SC-5, SC-6, SC-11, SC-12

### Phase 4: Audit + hardening + tests
- Failed-auth logging (R-13); per-key rate limiter (R-14); full test suites — unit tests (registrar idempotency/failure mode, hashing/storage discipline, error-formatter exposure blocklist, rate limiter), the HTTP matrix suite, and Playwright E2E for the admin view
- Verify: SC-9 (auth-failure events), SC-10, and a full re-run of all SCs

## Requirements → SCs → Phases Traceability

| Requirement | SCs | Phases |
|---|---|---|
| R-1 (single parent API package) | SC-1 | Phase 1 |
| R-2 (bolt mechanism) | SC-1, SC-2 | Phase 0, Phase 1 |
| R-3 (idempotency) | SC-4 | Phase 1 |
| R-4 (self-check + failure mode) | SC-2, SC-3 | Phase 1 |
| R-5 (credential scheme) | SC-5 | Phase 3 |
| R-6 (key storage/hashing) | SC-8 | Phase 2 |
| R-7 (lifecycle + audit) | SC-9 | Phase 2 |
| R-8 (admin view) | SC-7 | Phase 2 |
| R-9 (dump scope) | SC-6 | Phase 3 |
| R-10 (response encoding) | SC-11 | Phase 3 |
| R-11 (error contract) | SC-12 | Phase 1, Phase 3 |
| R-12 (method + path scoping) | SC-5 | Phase 1, Phase 3 |
| R-13 (auth-failure logging) | SC-9 | Phase 4 |
| R-14 (rate limit) | SC-10 | Phase 4 |

## Affected Files

- New: `src/api/__init__.py`, `src/api/registrar.py` (gc-find + bolt + idempotency + self-check + failure mode), `src/api/auth.py` (header authentication, hash verification, rate limiter)
- New: `src/api/routes/__init__.py`, `src/api/routes/records.py` (dump endpoint), `src/api/routes/api_not_found.py` (JSON 404 catch-all)
- New: `src/database/models/api_keys.py` (`ApiKeys` model); Modified: `src/database/migrations.py` (create `api_keys` table)
- Modified: `src/database/connection.py` (register the `ApiKeys` model in `init_db()`'s `Base.metadata` import list — the repo's `init_db()` (`src/database/connection.py:678-687`) explicitly imports every model to register it with `Base.metadata` before `create_all` (`src/database/connection.py:691`), so R-6's new `ApiKeys` model requires this registration)
- New: `src/services/api_key_service.py` (lifecycle operations + hashing + audit events)
- New: `src/frontend/pages/api_keys.py` (admin view); Modified: `src/services/navigation_service.py` (Admin section entry)
- Modified: `streamlit_app.py` (registrar invocation after database initialization)
- New: unit tests under `test/` (registrar idempotency + failure mode, hashing/storage discipline, error-formatter exposure blocklist, rate limiter) and Playwright E2E under `test/ui/` (admin view, `playwright_e2e` marked)

## Type

SPEC (new capability: agent-facing read-only records HTTP API with admin-issued key+secret authentication, bolted into the Streamlit server's Tornado application)

## Enforcement Gate

This spec is enforced by the project's approval gate and verification-before-completion gates. Implementation may not begin until the spec is approved and a plan is created. Each SC must be verified by its declared verification method before the branch is considered complete; no SC may be skipped, weakened, deferred, or removed. Verification evidence must be produced per the declared evidence type for each SC.

> **Enforcement gate:** All success criteria MUST pass before this spec is considered complete. Partial implementation is not permitted.

---

## Change Control

| Date | Change | Reason | Authorized By |
|------|--------|--------|---------------|
| 2026-10-07 | Initial spec created. Developer directives, verbatim: "an API endpoint managed by the Streamlit app that an agent can PULL from for getting a DB dump for use. An admin view added that allows setting up key+secret pairs for API access. GET requests mainly. Records only (linguistic data)." Security directive: "Assume we never want agents accessing things via the db from other projects as a major security risk" — the API is the sole sanctioned remote data surface. Hosting shape: "it would be better to have routes bolted in, all with a single parent api folder so that the actual api endpoints can then be named as needed." Deterministic choices made under the developer's decide-in-spec instruction, flagged for visibility: `X-API-Key`/`X-API-Secret` headers (vs bearer); single JSON response (vs JSONL); PBKDF2-HMAC-SHA256 600k hashing (the app is OAuth-only, so no existing password-hash precedent to mirror); idempotency strengthened beyond the probe's `session_state` guard (session state is per-browser-session; production requires a module-level latch + structural route-presence check); `/api/v1` path prefix; closed 15-field whitelist excluding `embedding`, lock state, and internal user-identity columns; resolved source name + language codes embedded for a self-contained dump; rate limit fixed at 60 requests/60 s default with secrets override; JSON 404 catch-all + 405 semantics; `last_used_at` tracking. Bolt mechanism grounded in the live probe of 2026-10-07 (artifacts `/tmp/opencode/st-api-probe/`) on Streamlit 1.54.0 / Tornado 6.5.4 | Feature request with binding design decisions from the 2026-10-07 discussion | Developer (Michael Conrad) |
| 2026-10-07 | Spec audit returned DRAFT — 6/11 holistic criteria FAIL (HD-1/2/3/5/6/7); all remediated with deterministic rewrites, Affected-Files addition, terminology definitions, hatch removal, and a Documentation Sources section; no requirement, SC, or decision changed | Spec audit DiMo chain (investigator→validator→evaluator→arbiter) on the same fixed criteria set | AI agent (remediation per audit) |
