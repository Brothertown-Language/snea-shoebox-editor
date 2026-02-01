# Plan: Resolve “Login failed: Token exchange failed (non-2xx)”

Goal: Make the GitHub OAuth web flow succeed locally (Streamlit on http://localhost:8501) using a single POST callback endpoint and provide clear diagnostics if anything fails. This plan corresponds to the issue “Login failed: Token exchange failed (non-2xx)” where GitHub returned an HTML 404 page for the access_token exchange.

## Ground truth (local)
- Frontend runs at: `http://localhost:8501`
- Single OAuth callback endpoint: `POST /api/oauth/callback`
- Backend issues authorize URLs via: `GET /api/oauth/login`
- Backend uses `application/x-www-form-urlencoded` to exchange the code at `https://github.com/login/oauth/access_token` and sets `Accept: application/json`.

## Environment
Ensure `.env` (project root) contains:

```
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
FRONTEND_URL=http://localhost:8501
JWT_SECRET=dev-secret
# Optional: enable PKCE end-to-end
# GITHUB_OAUTH_PKCE=1
```

Notes:
- docker-compose passes these into the backend with `env_file: ../.env`.
- If you edit `.env`, restart containers (see below).

## Single callback method
- Only `POST /api/oauth/callback` is supported. `GET` returns 405 (already enforced in backend).
- The frontend collects `code` and `state` from the URL and POSTs JSON:

```json
{"code":"...","state":"..."}
```

## Redirect URI parity
- Backend sets `redirect_uri` when building the authorize URL, and echoes it in the JSON from `/api/oauth/login`.
- The same `redirect_uri` is also included in the token exchange request.
- Locally this must be exactly `http://localhost:8501` and must match the GitHub OAuth App’s Authorization callback URL.

## Restart after env changes
```
docker compose -f docker/docker-compose.yml restart backend
docker compose -f docker/docker-compose.yml restart web
```

## Validation checklist
1) Sanity check the login endpoint:
   ```bash
   curl -sS -H 'User-Agent: snea-dev/1.0' \
     http://localhost:8787/api/oauth/login | jq
   ```
   - Confirm `redirect_uri` is `http://localhost:8501`.
   - Optional: with `AI_DEBUG=1`, send `-H 'X-AI-Debug: 1'` to see `__ai_debug` events in the JSON.

2) Run the browser flow from the Streamlit app. On success, backend returns:
   ```json
   { "token": "...", "user": {"id":..., "email":"...", "username":"...", "name":"..."} }
   ```

3) If it fails, the backend responds with structured JSON, surfacing upstream GitHub details:
   ```json
   {
     "error": "Token exchange failed (non-2xx)",
     "status": 404,
     "body": "<html>...GitHub page not found...</html>"
   }
   ```
   - A 404 HTML from GitHub typically indicates a mismatch in `redirect_uri` or missing/incorrect `client_id`/`client_secret`.

## Typical causes of non‑2xx from GitHub
- Redirect mismatch: GitHub App Authorization callback URL ≠ `redirect_uri` (fix the GitHub app setting to `http://localhost:8501`).
- Invalid secret: `GITHUB_CLIENT_SECRET` wrong or not passed into the backend (confirm `.env` and restart containers).
- Expired/invalid `code`: the code is single‑use and short‑lived; repeat from `/api/oauth/login`.
- PKCE mismatch (if enabled): ensure `GITHUB_OAUTH_PKCE=1` and that the authorize call includes `code_challenge` and the callback exchange includes the matching `code_verifier` (the backend already carries this in signed state when enabled).

## Implementation notes (repo)
- Backend: `/api/oauth/login` echoes `redirect_uri` and returns an `authorize_url`; `/api/oauth/callback` only accepts POST and exchanges the code via `application/x-www-form-urlencoded` (adds `redirect_uri` and optional `code_verifier` for PKCE).
- The worker uses Cloudflare Workers’ Python interop: `from js import Response, JSON, fetch, AbortSignal`. Local static analysis may flag unresolved symbols; they are provided by the runtime.
- Frontend (Streamlit) uses a single flow: it opens `authorize_url` and POSTs code/state to `/api/oauth/callback`.

## Deep diagnostics (optional)
- Set `AI_DEBUG=1` in `.env` and send header `X-AI-Debug: 1` while testing. The backend will include a `__ai_debug` array in the JSON with step‑by‑step events (scrubbed of secrets).
- The backend requires an inbound `User-Agent` header; missing it returns 400. All sample curls include one.

## Out of scope
- Production/public URL alignment and Cloudflare Pages/Wrangler secrets can be set later. This plan focuses only on local dev at port 8501.
