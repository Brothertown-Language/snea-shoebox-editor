<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# Local Development Setup Guide

This guide provides a step-by-step walkthrough for setting up the **SNEA Online Shoebox Editor** for local development using Docker.

**If you are an Administrator looking to setup the production infrastructure (Cloudflare/GitHub Secrets), please follow the [Infrastructure & Production Setup Guide](PROD_SETUP.md) instead.**

## 1. Local GitHub OAuth Setup

To enable authentication during local development, you must register a local GitHub OAuth Application.

*   **Purpose**: Used when running via Docker at `localhost`.
*   **Registration**: [GitHub **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**](https://github.com/settings/applications/new).
*   **Application Name**: `SNEA Shoebox Editor (Local)`
*   **Application Description**: `Local development environment for the SNEA Online Shoebox Editor.`
*   **Homepage URL**: your local frontend dev URL (e.g., `http://localhost:8501`)
*   **Authorization callback URL**: same as Homepage (e.g., `http://localhost:8501`)
*   **Configuration**: Add the `Client ID` and `Client Secret` to your local `.env` file (see Step 2). The Worker reads `SNEA_GITHUB_CLIENT_ID`/`SNEA_GITHUB_CLIENT_SECRET` (with fallbacks to `GITHUB_CLIENT_ID`/`GITHUB_CLIENT_SECRET`).

## 2. Local Environment Initialization

We prioritize using **Docker** to keep your workstation environment clean and consistent.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Brothertown-Language/snea-shoebox-editor.git
    cd snea-shoebox-editor
    ```
2.  **Create `.env` File**:
    In the project root, create a `.env` file with your local OAuth credentials (from Step 1) and set your frontend dev URL. **Crucial:** Never commit this file to the repository. If you accidentally committed it, see the **[Security Rotation Guide](SECURITY_ROTATION.md)**.
    ```env
    # GitHub OAuth (Local Development)
    SNEA_GITHUB_CLIENT_ID=your_local_client_id
    SNEA_GITHUB_CLIENT_SECRET=your_local_client_secret

    # Frontend dev server URL (e.g., Streamlit default)
    FRONTEND_URL=http://localhost:8501
    ```
3.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
    *Note: Environment variables are loaded from the `.env` file automatically by the application.*

    **PRO TIP**: You do **NOT** need to run `bootstrap_env.py` for local development. The local database is a Wrangler D1 simulation.
    *   **Frontend (Pages dev server or static)**: e.g., `http://localhost:8501`
    *   **Backend (Worker + local D1)**: `http://localhost:8787`

## 3. Usage & Development

*   **Initial Login**: You may be required to be in a specific GitHub org/team depending on permissions data.
*   **Database**: The local database is a simulation of Cloudflare D1. Data is persisted in the `.wrangler` directory.
*   **Seeding**: On first startup, the application will automatically seed the database with linguistic records (e.g., Natick dictionary).

---
For more detailed information, refer to:
*   **[Local Development Guide](local-development.md)** (Advanced Usage)
*   **[Infrastructure & Production Setup Guide](PROD_SETUP.md)** (Admins Only)
*   **[Roadmap & Deployment Phases](roadmap.md)**

## Quick plan to resolve “Login failed: Token exchange failed (non-2xx)”

This summarizes the minimal actions needed for local dev (Streamlit on :8501):

1) Environment
   - In project `.env` make sure you have:
     - `GITHUB_CLIENT_ID=...`
     - `GITHUB_CLIENT_SECRET=...`
     - `FRONTEND_URL=http://localhost:8501`
     - `JWT_SECRET=dev-secret`

2) Compose env propagation
   - The backend service uses `env_file: ../.env` so wrangler dev receives these values inside the container. After editing `.env`, restart containers:
     - `docker compose -f docker/docker-compose.yml restart backend`
     - `docker compose -f docker/docker-compose.yml restart web`

3) One callback method
   - Only `POST /api/oauth/callback` is supported (GET returns 405). The frontend should always POST `{code, state}`.

4) Redirect URI parity
   - `GET /api/oauth/login` returns `authorize_url` and `redirect_uri`. The latter must be `http://localhost:8501` locally and must match what GitHub has configured for the OAuth app. The backend also sends this same value in the token exchange.

5) Verify quickly
   - `curl -sS -H 'User-Agent: snea-dev/1.0' http://localhost:8787/api/oauth/login`
     - Check `redirect_uri` is `http://localhost:8501`.
   - Complete the browser login flow. On success, backend returns `{ token, user }`.
   - On failure, backend will surface GitHub’s upstream `status` and `body` to help diagnose.

6) If you still see 404 HTML from GitHub
   - Re-check that the GitHub OAuth app Authorization callback URL is exactly `http://localhost:8501`.
   - Ensure the backend is sending `client_id`, `client_secret`, `code`, and `redirect_uri` (done by worker). Restart containers after any env change.

## Local OAuth checklist (GitHub)

Use this checklist to prevent/resolve the “Token exchange failed (non-2xx)” and GitHub HTML 404 responses during login.

1) Ports and URLs
   - Frontend runs at: `http://localhost:8501` (Streamlit default in this repo)
   - Set `FRONTEND_URL=http://localhost:8501` in your `.env` (already present in this project)
   - In your GitHub OAuth App (Settings → Developer settings → OAuth Apps):
     - Homepage URL: `http://localhost:8501`
     - Authorization callback URL: `http://localhost:8501`

2) Environment → docker-compose
   - We pass `.env` into both containers via `env_file: ../.env`.
   - Ensure these are defined in `.env`:
     - `GITHUB_CLIENT_ID=...`
     - `GITHUB_CLIENT_SECRET=...`
     - `FRONTEND_URL=http://localhost:8501`
     - `JWT_SECRET=some-dev-secret`
   - After changes: restart containers
     - `docker compose -f docker/docker-compose.yml restart backend`
     - `docker compose -f docker/docker-compose.yml restart web`

3) Flow and endpoints (single callback verb)
   - Backend issues `authorize_url` from `GET /api/oauth/login`.
   - Frontend exchanges the returned `code`+`state` by POSTing JSON to a single endpoint:
     - `POST /api/oauth/callback` with body `{ "code": "...", "state": "..." }`
   - `GET /api/oauth/callback` is disabled (returns 405) to avoid confusion.

4) Token exchange details (backend)
   - Backend sends `application/x-www-form-urlencoded` to `https://github.com/login/oauth/access_token` with `Accept: application/json`.
   - The POST includes: `client_id`, `client_secret`, `code`, and `redirect_uri=http://localhost:8501` (plus `code_verifier` if PKCE is enabled).
   - If GitHub returns non‑2xx, backend responds 502 and includes the upstream `status` and `body` to aid debugging.

5) Quick validation
   - `curl -H 'User-Agent: test' http://localhost:8787/api/oauth/login` → verify `redirect_uri=http://localhost:8501` in JSON.
   - Perform browser login. On success frontend receives `{ token, user }` from backend.
   - On failure, expand error details in the Streamlit UI to view backend’s upstream body.
