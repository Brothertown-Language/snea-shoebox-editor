<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
<!-- Licensed under CC BY-SA 4.0 -->
<!-- 
CRITICAL MAINTENANCE RULES:
1. This file must NEVER be altered except when expressly instructed to do so by the user.
2. It is MANDATORY to never mark issues or roadmap items as complete in this document (e.g., changing [PENDING] to [COMPLETED]) unless specifically requested and approved by the user.
3. If an edit appears necessary but has not been explicitly requested, the AI agent MUST stop and query the user with details.
-->
## Overview

This document outlines the implementation plan for the **SNEA Shoebox Editor**, a 100% Python-based web application for
collaborative, version-controlled editing of linguistic records from across Southern New England Algonquian (SNEA) languages.

---

## Setup & Deployment Flow

To ensure a reliable and free deployment, the project uses **Streamlit Community Cloud** paired with **Aiven**.

### Phase 1: Infrastructure Setup [COMPLETED]

Before initializing the project, you must set up the hosting and database platforms.

1.  **Aiven Setup (Database)**:
    - Create a free account at [Aiven](https://aiven.io/).
    - Create a new PostgreSQL service.
    - Select a free plan (available in various regions including AWS US-East-1). Note that the PostgreSQL 17 free tier (EOL: 8 November 2029) includes 1 CPU, 1 GB RAM, 1 GB storage, and is limited to 20 maximum connections. Maintenance is scheduled for Wednesdays after 06:10:45 UTC.
    - Once the service is running, find your **Connection URI** in the Aiven console.
    - Save this connection string for the next step.
    - **Capability Check**: The `vector` (pgvector) extension has been enabled in the production instance.
2.  **GitHub OAuth Setup**:
    - Go to your GitHub [**Developer settings > OAuth Apps > New OAuth App**](https://github.com/settings/applications/new).
    - **Application Name**: `SNEA Shoebox Editor`
    - **Homepage URL**: `https://snea-edit.streamlit.app/`
    - **Authorization callback URL**: `https://snea-edit.streamlit.app/component/streamlit_oauth.authorize_button`
    - Generate a **Client Secret** and save both the **Client ID** and **Client Secret**.
    - In the app settings, go to **Secrets** and paste the content of **`.streamlit/secrets.toml.production`**:
      ```toml
      [connections.postgresql]
      url = "YOUR_DATABASE_URL"

      [github_oauth]
      client_id = "YOUR_CLIENT_ID"
      client_secret = "YOUR_CLIENT_SECRET"
      redirect_uri = "https://snea-edit.streamlit.app/component/streamlit_oauth.authorize_button"
      authorize_url = "https://github.com/login/oauth/authorize"
      token_url = "https://github.com/login/oauth/access_token"
      user_info_url = "https://api.github.com/user"
      ```

### Phase 2: Local Development Setup [COMPLETED]

1.  **Connectivity Checks**:
    - The application now includes built-in DNS and socket reachability checks for the database, including both IPv4 and IPv6 support.
    - Note: IPv6 connectivity might fail on local networks that do not fully support IPv6 or have specific firewall rules, while still working in the Streamlit Cloud environment.
    - Verify these on the system status page BEFORE troubleshooting SQL connection issues.

2.  **Initialize Environment**:
    - Clone the repository.
    - **Local PostgreSQL**: The app will automatically start a local PostgreSQL 16.2 instance using `pgserver` if no `DATABASE_URL` or secret is provided. Data is stored in `tmp/local_db`. All development must target PostgreSQL 16.2 compatibility.
    - (Optional) If you want to use a specific database, create a `.streamlit/secrets.toml` file (ignored by git):
      ```toml
      [connections.postgresql]
      # For Aiven or existing local DB
      url = "YOUR_DB_CONNECTION_URI"

      [github_oauth]
      client_id = "YOUR_LOCAL_GITHUB_CLIENT_ID"
      client_secret = "YOUR_LOCAL_GITHUB_CLIENT_SECRET"
      redirect_uri = "http://localhost:8501/component/streamlit_oauth.authorize_button"
      authorize_url = "https://github.com/login/oauth/authorize"
      token_url = "https://github.com/login/oauth/access_token"
      user_info_url = "https://api.github.com/user"
      ```
    - Note: You should create a separate GitHub OAuth App for local development with `http://localhost:8501/component/streamlit_oauth.authorize_button` as the callback URL.
2.  **Install Dependencies**:
    ```bash
    uv sync --extra local
    ```
3.  **Run Locally**:
    ```bash
    ./scripts/start_streamlit.sh
    ```
    - **MANDATORY RULE:** Always use the start script `./scripts/start_streamlit.sh` or `nohup uv run --extra local ...` for background execution. For local development and testing, **ALWAYS** include `--extra local` to ensure that `pgserver` and other local dependencies are available. If no database URL is configured in secrets or environment, the app will automatically start a local PostgreSQL 16.2 instance using `pgserver` (data stored in `tmp/local_db`).
    - **PyCharm Launchers**: Pre-configured run configurations for PyCharm are available in the `launchers/` directory. Copy them to your `.idea/runConfigurations/` folder to use them. These launchers automatically handle process management (killing old sessions) and ensure `pgserver` is started.

---

## Architecture Details

### 1. Frontend & Backend (Streamlit)

- **Platform**: Streamlit Community Cloud (connected to private GitHub repo).
- **Execution**: Server-side Python execution.
- **UI**: Standard Streamlit components for a responsive, reactive interface.
- **Authentication**: `streamlit-oauth` for GitHub OAuth flow.

### 2. Database (Aiven / PostgreSQL)

- **Platform**: Aiven (PostgreSQL).
- **Connection**: `st.connection("postgresql", type="sql")`.
- **Persistence**: Data survives app reboots and is shared across all users.

### 3. Data Layer

- **Format**: MDF (Multi-Dictionary Formatter).
- **Schema**: Tables for `sources`, `records`, `languages`, `search_entries`, `matchup_queue`, `users`, `permissions`, `edit_history`, `user_activity_log`.
- **NFD Sorting**: Records are sorted by their extracted headword (\lx) using NFD normalization.

---

## Feature Roadmap (Upcoming)

### Phase 3: Migration to PostgreSQL [COMPLETED]
- Port existing SQLite/D1 logic to SQLAlchemy/PostgreSQL.
- Implement schema initialization in Aiven.
- Migrate existing Natick/Trumbull data to the new database.

### Phase 4: GitHub OAuth [COMPLETED]
- Implement the login flow using `streamlit-oauth`.
- Securely store session state in Streamlit's `st.session_state`.

### Phase 5: Navigation & Access Control [COMPLETED]
- Implement persistent session rehydration using browser cookies. [COMPLETED]
- Implement deep link navigation support for authenticated users. [COMPLETED]
- **Route Protection**: Implement granular access controls based on user roles and source-specific permissions. [COMPLETED]
    - **admin**: Automatic full access to all resources and administrative functions.
    - **editor**: Authorized to edit, update, and manage MDF records ONLY.
    - **viewer**: Read-only access to records. **MAY NEVER** edit or modify any data (HARD BLOCK).
- **Refactor: Identity Service** (`src/services/identity_service.py`): Centralized user synchronization and identity data fetching. [COMPLETED]
- **Refactor: Security Manager** (`src/services/security_manager.py`): Centralized authentication middleware, session rehydration, and route protection. [COMPLETED]
- **Refactor: Navigation Service** (`src/services/navigation_service.py`): Centralized Streamlit page definitions and navigation logic. [COMPLETED]
- **Refactor: Audit Service** (`src/services/audit_service.py`): Standardized activity logging via `UserActivityLog`. [COMPLETED]
- **Refactor: Linguistic Service** (`src/services/linguistic_service.py`): Scaffolded data-access layer for `Record`, `Source`, and `Language` models (stubs only; full CRUD deferred). [COMPLETED]
- **Refactor: Infrastructure Service** (`src/services/infrastructure_service.py`): Consolidated Aiven API, network diagnostics, and system inspection. [COMPLETED]
- **Refactor: Database Migrations** (`src/database/migrations.py`): Centralized schema evolution, extension management, and data seeding via `MigrationManager`. [COMPLETED]
- **Cleanup**: Removed deprecated `auth_utils.py`. Simplified `app.py` to orchestration-only (~100 lines). All HTML injections standardized via `ui_utils.py`. [COMPLETED]

### MDF Upload Feature 🔄 [IN PROGRESS]
- **MDF Parser Enhancements**: Extended parser for `\nt Record:`, `\va`, `\se`, `\cf`, `\ve` fields and normalization helpers. [COMPLETED]
- **Upload Service** (`src/services/upload_service.py`): Full backend for MDF upload workflow — parse, stage to `matchup_queue`, suggest matches (exact + base-form + record-id), auto-remove duplicates, flag mismatches, bulk/single approve, commit matched/new/homonym records, populate search entries. [COMPLETED]
- **Upload Page** (`src/frontend/pages/upload_mdf.py`): File uploader, source selector with create-new option, parse summary, Stage & Match, pending batch selector, Re-Match. Role-guarded to `editor`/`admin`. [COMPLETED]
- **Review & Confirm UI**: Match review table with status selectors, default status logic, side-by-side MDF comparison, bulk approval buttons, per-record Apply Now. [IN PROGRESS — batch apply buttons, manual match override, download pending, and results summary pending]
- **Detailed plan**: See [MDF Upload Plan](../plans/mdf-upload-plan.md).

### Phase 6: Search & Discovery ⏳ [PENDING]
- Implement full-text search (FTS) using PostgreSQL's native capabilities.
- Leverage `pgvector` on Aiven for semantic cross-reference lookup.
    - *Note: Vector capability (pgvector) has been enabled in both local and production environments for future use in linking semantically related records.*
- **D.R.Y. Service**: Centralize embedding generation and semantic search logic into a reusable `SearchService` to ensure consistency between bulk uploads and UI search.

### Phase 7: Quality Control & Audit ⏳ [PENDING]
- Implementation of the 'approved' status to flag records as vetted.
- **Audit Infrastructure**: Establish a backend service layer to encapsulate logging logic (`UserActivityLog`, `EditHistory`) for cross-module consistency.
- **Admin Dashboard**: Frontend UI for viewing audit logs and managing permissions.

---

## Technical Documentation

- [OAuth2 and Deep Link Setup Guide](oauth2-deeplink-setup.md)

