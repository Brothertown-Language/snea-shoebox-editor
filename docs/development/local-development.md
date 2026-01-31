<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# Local Development Guide

This document provides instructions for running the SNEA Shoebox Editor locally for development and testing purposes. We prioritize using **Docker** to keep your workstation environment clean and consistent.

## Prerequisites

- **Docker**: Required for the recommended containerized development.
- **Python**: >= 3.11 (Optional, for direct local execution/testing).
- **uv**: Latest version (Optional, for direct local execution/testing).

## Running with Docker (Recommended)

Using Docker ensures that dependencies like `npm`, `wrangler`, and specific Python versions do not pollute your host system.

### 1. Build and Run using Docker Compose

A `docker-compose.yml` file is provided to start both the frontend (Solara) and the backend (Wrangler/D1).

```bash
docker-compose up --build
```

- **Frontend (Solara)**: Exposed on `http://localhost:8765`.
- **Backend (Wrangler/D1)**: Exposed on `http://localhost:8787`.

### 2. Managing the Local Database

The backend container runs Wrangler with `--local --persist`, meaning your local D1 simulation data is stored in the `.wrangler` directory in the project root.

The application automatically handles schema creation and updates on startup. Manual execution of schema files is not required. If you need to inspect the database, you can use the Wrangler CLI through the container:

```bash
docker-compose exec backend wrangler d1 execute snea-shoebox --local --command="SELECT name FROM sqlite_master WHERE type='table';"
```

## Manual Local Environment Setup (Optional)

If you prefer to run tests or code directly on your workstation, you can set up a local Python environment.

1. **Initialize the environment**:
   ```bash
   uv venv
   uv pip install -e .
   # Note: activation (source .venv/bin/activate) is optional when using `uv run`
   ```

2. **Run Tests**:
   ```bash
   uv run python -m unittest discover tests
   ```

## Local Database (Cloudflare D1)

The SNEA Shoebox Editor requires Cloudflare D1 (or its local simulation via Wrangler) for all development. Direct use of local SQLite files without the D1 simulation layer is discouraged to ensure parity with the production environment.

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

## Frontend Development (Solara)

While `docker-compose` is recommended, you can run the Solara frontend with hot-reloading locally if you have the environment set up:

```bash
uv run solara run src/frontend/app.py
```
