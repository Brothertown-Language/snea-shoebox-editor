<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# Local Development Guide

This document provides instructions for running the SNEA Shoebox Editor locally for development and testing purposes. We prioritize using **Docker** to keep your workstation environment clean and consistent.

## Prerequisites

- **Docker**: Required for containerized development.
- **Docker Compose**: Required to run the full stack.

## Running with Docker

Using Docker ensures that dependencies like `npm`, `wrangler`, and specific Python versions do not pollute your host system.

### 1. GitHub OAuth for Local Development

To enable authentication locally, you must create a separate GitHub OAuth application as described in the **[Local Setup Guide](SETUP.md#1-local-github-oauth-setup)**. If you are recovering from a credential leak, refer to the **[Security Rotation Guide](SECURITY_ROTATION.md)**.

### 2. Build and Run using Docker Compose

A `docker-compose.yml` file is provided to start the unified app (Wrangler/D1 + Stlite Bundler).

```bash
docker-compose up --build
```

- **Unified App**: Exposed on `http://localhost:8787`. Both the frontend and backend are served from this single port.

### 3. Interactive Live Development

The Docker environment is configured for **Pure Unified Dev Mode (Strict Parity)**:

- **Frontend**: The container automatically watches `src/frontend/app.py`. When you save changes, it re-bundles the Stlite frontend into `dist/`. Simply refresh your browser at `http://localhost:8787` to see changes.
- **Backend**: Wrangler's local development mode (`wrangler dev`) automatically watches changes in `src/backend/` and reloads the Worker.
- **Tests**: Run tests from your host or within a container.

To run tests interactively:
```bash
uv run python3 -m unittest discover tests
```

### 4. Authentication Flow

When developing locally with the unified architecture:
- Both the frontend and backend live on `http://localhost:8787`.
- **GitHub OAuth Callback**: Your GitHub OAuth Application **Authorization callback URL** must be set to `http://localhost:8787`.
- The backend handles the OAuth exchange and session management.
- You must be a member of the `proto-SNEA` team in the `Brothertown-Language` organization to log in, even locally.

### 5. Managing the Local Database

The backend container runs Wrangler with `--local --persist`, meaning your local D1 simulation data is stored in the `.wrangler` directory in the project root.

The application automatically handles schema creation and updates on startup. Manual execution of schema files is not required. If you need to inspect the database, you can use the Wrangler CLI through the container:

```bash
docker-compose exec backend wrangler d1 execute snea-shoebox --local --command="SELECT name FROM sqlite_master WHERE type='table';"
```

## Local Database (Cloudflare D1)

The SNEA Shoebox Editor requires Cloudflare D1 (or its local simulation via Wrangler) for all development.

### D1 Simulation in Docker

The `backend` service in `docker-compose.yml` automatically starts a local D1 simulation.

1. **Automatic Schema Initialization**:
   The application is designed to create its own schema and update existing tables (using `ALTER`) automatically upon startup. You do not need to manually run `schema.sql`.

2. **Persistence**:
   Data is persisted in the `.wrangler` directory. Do not delete this directory unless you wish to reset your local database state.

### Why D1 Access is Required

By using the D1 simulation via Wrangler, we ensure that:
- All database queries are compatible with Cloudflare D1.
- The authentication and binding logic matches the production Worker environment.
- The "Zero-Touch" deployment remains consistent between local and production.

---

## Local Embedding Service (Docker-based)

**This is the source of truth for local development.** The SNEA Shoebox Editor uses embeddings for semantic search. For local development, we run the same BGE-M3 model used in production via Docker with GPU acceleration.

### Prerequisites

- **NVIDIA GPU**: Minimum 8GB VRAM (16GB+ recommended)
- **NVIDIA Container Toolkit**: Required for GPU access in Docker
- **Docker Compose**: Already required for the project

### Check GPU Availability

Before starting the embedding service, verify your system has the required GPU support:

```bash
bash scripts/check_gpu.sh
```

This script checks for:
1. NVIDIA GPU and drivers
2. Docker installation
3. NVIDIA Container Toolkit
4. Docker Compose

If any component is missing, the script provides installation instructions.

### Starting the Embedding Service

The embedding service is defined in `docker-compose.yml` and starts automatically with the full stack:

```bash
# Start all services including embeddings
docker-compose up --build

# Or start only the embedding service
docker-compose up -d embeddings
```

**First Run Notes:**
- The container downloads the BGE-M3 model (~2GB) on first start
- Initial startup takes 2-5 minutes for model loading
- Requires ~5GB disk space for model and cache
- Model uses ~4GB VRAM when loaded

### Testing the Embedding Service

Verify the service is working correctly:

```bash
# Wait for service to be ready
curl --retry 10 --retry-delay 5 http://localhost:8080/health

# Run comprehensive tests
uv run python scripts/test_embeddings.py
```

The test script verifies:
- Service health and availability
- Embedding generation with various texts (including Algonquian words)
- Correct dimensionality (1024 dimensions for BGE-M3)
- Consistency and uniqueness of embeddings

### Configuration

The embedding service is configured via environment variables in `.env`:

```env
# Enable local embeddings
USE_LOCAL_EMBEDDINGS=true

# Embedding service URL (Docker internal network)
EMBEDDING_SERVICE_URL=http://embeddings:80
```

See `.env.example` for a complete configuration template.

### Architecture

- **Model**: `BAAI/bge-m3` (same as Cloudflare `@cf/baai/bge-m3`)
- **Dimensions**: 1024 (matches production)
- **Container**: Hugging Face Text Embeddings Inference (TEI) with CUDA support
- **API**: REST API at `http://localhost:8080` (host) or `http://embeddings:80` (Docker network)

### Fallback Options

If GPU is unavailable:
1. **Unit Tests**: Use mock embeddings (fast, deterministic, no GPU required)
2. **Integration Tests**: Deploy a dev worker to Cloudflare and use remote embeddings

See **[EMBEDDINGS.md](EMBEDDINGS.md)** for detailed configuration and alternative approaches.

---

## Plan to resolve GitHub OAuth: Token exchange failed (non-2xx)

This plan addresses the 404 HTML page from GitHub during token exchange and standardizes the local OAuth flow.

Summary:
- Use a single frontend-initiated flow: frontend GETs /api/oauth/login to obtain authorize_url, then handles the code on its URL and POSTs to /api/oauth/callback. No GET callbacks are used (GET returns 405).
- Ensure env vars are injected into the backend container at runtime via `env_file: ../.env`.
- Enforce redirect_uri parity (what was sent to authorize is echoed and also sent in the token exchange).

Steps:
1) Verify environment
   - .env must define:
     - GITHUB_CLIENT_ID=...
     - GITHUB_CLIENT_SECRET=...
   - Optional: JWT_SECRET=dev-secret (defaults to "change-me")
   - The application automatically handles FRONTEND_URL and BACKEND_URL for local Docker dev.

2) Docker compose
   - Compose passes the .env into the `backend` service via `env_file: ../.env`. This ensures wrangler dev receives GitHub OAuth vars inside the container.
   - After editing .env, restart containers:
     - `docker compose -f docker/docker-compose.yml restart backend`

3) Backend behavior
   - GET /api/oauth/login returns JSON:
     - authorize_url: https://github.com/login/oauth/authorize?...&redirect_uri=http://localhost:8787
     - state: signed state
     - redirect_uri: http://localhost:8787 (echoed)
     - pkce: false (or true if OAUTH_USE_PKCE=1)
   - POST /api/oauth/callback accepts { code, state } only. GET is 405.
   - Token exchange uses application/x-www-form-urlencoded with client_id, client_secret, code, and redirect_uri. If PKCE enabled, includes code_verifier.
   - On non-2xx from GitHub, backend returns 502 JSON including upstream status and body to aid debugging.

4) Frontend behavior
   - Stlite (served at :8787) GETs /api/oauth/login, then redirects to authorize_url.
   - After redirect back to http://localhost:8787 with ?code&state, Stlite POSTs these to /api/oauth/callback.
   - On 200, store token/user in session; on error, display backend JSON (which includes upstream details when applicable).

5) Troubleshooting
   - If GitHub returns 404/HTML on token exchange, most likely client_id/secret or redirect_uri mismatch. Confirm:
     - GitHub OAuth App → Authorization callback URL points to http://localhost:8787 (for local dev).
     - /api/oauth/login shows redirect_uri=http://localhost:8787
     - .env values are non-empty inside backend container (wrangler dev). Restart containers after changes.
   - If backend says "Invalid state": ensure the frontend POSTs the same `state` GitHub sent to the frontend URL.

6) Single endpoint policy
   - Frontend uses only POST /api/oauth/callback (no GET). This avoids ambiguity and aligns with CORS and CSRF best practices.

OAuth token exchange with GitHub
--------------------------------

Our backend posts to https://github.com/login/oauth/access_token using
application/x-www-form-urlencoded and Accept: application/json as required by GitHub.

Do NOT send JSON in the body for this endpoint. GitHub expects
form-encoded fields: client_id, client_secret, code and (recommended)
redirect_uri, and code_verifier if PKCE was used. Using JSON may work in
some libraries but is not the documented contract and may yield 404/HTML
responses.

Reference example (Python requests – correct):

```
import requests

def exchange_code(client_id, client_secret, code, redirect_uri=None, code_verifier=None):
    url = "https://github.com/login/oauth/access_token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "snea-shoebox-backend/1.0",
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }
    if redirect_uri:
        data["redirect_uri"] = redirect_uri
    if code_verifier:
        data["code_verifier"] = code_verifier

    r = requests.post(url, data=data, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()
```

This matches the backend implementation in src/backend/worker.py (see
form_data and urlencode(...)).

If you see a 404 HTML page from GitHub during exchange, check that:
1) client_id/client_secret are set in the backend container env
2) redirect_uri in the exchange matches what was used at authorize
3) POST body is form-encoded (not JSON)
4) Accept header requests JSON
