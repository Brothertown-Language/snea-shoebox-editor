<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
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
    - **Homepage URL**: `https://snea-edit.streamlit.app`
    - **Authorization callback URL**: `https://snea-edit.streamlit.app`
    - Generate a **Client Secret** and save both the **Client ID** and **Client Secret**.
3.  **Streamlit Community Cloud Setup**:
    - Sign in to [Streamlit Community Cloud](https://share.streamlit.app/) with your GitHub account.
    - Click **Create app** and select your private GitHub repository.
    - In the app settings, go to **Secrets** and paste the following (replacing with your actual values):
      ```toml
      [connections.postgresql]
      url = "postgresql://avnadmin:[YOUR-PASSWORD]@[YOUR-SERVICE-NAME]-[YOUR-PROJECT-NAME].aivencloud.com:[YOUR-PORT]/defaultdb?sslmode=require"

      [github_oauth]
      client_id = "YOUR_GITHUB_CLIENT_ID"
      client_secret = "YOUR_GITHUB_CLIENT_SECRET"
      redirect_uri = "https://snea-edit.streamlit.app"
      cookie_secret = "a-random-secret-string"

      # [FUTURE FEATURE]
      # [embedding]
      # model_id = "BAAI/bge-m3"
      # api_key = "hf_your_token_here"
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
      redirect_uri = "http://localhost:8501"
      cookie_secret = "a-random-secret-string"

      # [FUTURE FEATURE]
      # [embedding]
      # model_id = "BAAI/bge-m3"
      # api_key = "hf_your_token_here"
      ```
    - Note: You should create a separate GitHub OAuth App for local development with `http://localhost:8501` as the callback URL.
2.  **Install Dependencies**:
    ```bash
    uv sync --extra local
    ```
3.  **Run Locally**:
    ```bash
    uv run streamlit run src/app.py
    ```

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
- **Schema**: Tables for `sources`, `records`, `users`, `permissions`.
- **NFD Sorting**: Records are sorted by their extracted headword (\lx) using NFD normalization.

---

## Feature Roadmap (Upcoming)

### Phase 3: Migration to PostgreSQL [PENDING]
- Port existing SQLite/D1 logic to SQLAlchemy/PostgreSQL.
- Implement schema initialization in Aiven.
- Migrate existing Natick/Trumbull data to the new database.

### Phase 4: GitHub OAuth Integration [IN PROGRESS]
- Implement the login flow using `streamlit-oauth`.
- Verify user membership in authorized teams/orgs.
- Securely store session state.

### Phase 5: Search & Discovery [PENDING]
- Implement full-text search (FTS) using PostgreSQL's native capabilities.
- **[IN PROGRESS]** Leverage `pgvector` on Aiven for semantic search (Hugging Face integration).
    - *Note: Semantic search capability (pgvector) has been enabled in both local and production environments.*

### Phase 6: Quality Control & Audit [PENDING]
- Implementation of the 'approved' status to flag records as vetted.
- Admin portal for user management and audit logs.

