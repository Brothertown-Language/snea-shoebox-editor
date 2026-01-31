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

To enable authentication locally, you must create a separate GitHub OAuth application:

1.  Go to GitHub **Settings** > **Developer settings** > **OAuth Apps** > **New OAuth App**.
2.  **Application Name**: `SNEA Shoebox Editor (Local)`
3.  **Homepage URL**: `http://localhost:8765`
4.  **Authorization callback URL**: `http://localhost:8787/auth/callback`
5.  Create a `.env` file in the project root:
    ```env
    GITHUB_CLIENT_ID=your_local_client_id
    GITHUB_CLIENT_SECRET=your_local_client_secret
    ```

### 2. Build and Run using Docker Compose

A `docker-compose.yml` file is provided to start both the frontend (Solara) and the backend (Wrangler/D1).

```bash
docker-compose up --build
```

- **Frontend (Solara)**: Exposed on `http://localhost:8765`.
- **Backend (Wrangler/D1)**: Exposed on `http://localhost:8787`.

### 3. Authentication Flow & CORS

When developing locally:
- The frontend (`:8765`) will redirect to GitHub.
- GitHub will redirect to the backend's callback (`:8787`).
- The backend must handle CORS to allow the frontend to communicate with it across different ports.
- You must be a member of the `proto-SNEA` team in the `Brothertown-Language` organization to log in, even locally.

### 4. Managing the Local Database

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

