<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
## Overview

This document outlines the implementation plan for the **SNEA Shoebox Editor**, a 100% Python-based web application for
collaborative, version-controlled editing of linguistic records from across Southern New England Algonquian (SNEA) languages.

---

## Setup & Deployment Flow

To ensure a reliable and free deployment, the project uses **Streamlit Community Cloud** paired with **Supabase**.

### Phase 1: Infrastructure Setup [PENDING]

Before initializing the project, you must set up the hosting and database platforms.

1.  **Supabase Setup (Database)**:
    - Create a free account at [Supabase](https://supabase.com/).
    - Create a new project.
    - Go to **Project Settings > Database** to find your connection string (URI). It should look like `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres`.
    - Save this connection string for the next step.
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
      url = "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres"

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

### Phase 2: Local Development Setup [PENDING]

1.  **Connectivity Checks**:
    - The application now includes built-in DNS and socket reachability checks for the database. 
    - Verify these on the system status page BEFORE troubleshooting SQL connection issues.

2.  **Initialize Environment**:
    - Clone the repository.
    - Create a `.streamlit/secrets.toml` file (ignored by git) and paste the same secrets used in Streamlit Cloud, but with local redirect URIs:
      ```toml
      [connections.postgresql]
      url = "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres"

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
    uv venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    uv pip install -e .
    ```
3.  **Run Locally**:
    ```bash
    uv run streamlit run src/frontend/app.py
    ```

---

## Architecture Details

### 1. Frontend & Backend (Streamlit)

- **Platform**: Streamlit Community Cloud (connected to private GitHub repo).
- **Execution**: Server-side Python execution.
- **UI**: Standard Streamlit components for a responsive, reactive interface.
- **Authentication**: `streamlit-oauth` for GitHub OAuth flow.

### 2. Database (Supabase / PostgreSQL)

- **Platform**: Supabase (PostgreSQL).
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
- Implement schema initialization in Supabase.
- Migrate existing Natick/Trumbull data to the new database.

### Phase 4: GitHub OAuth Integration [IN PROGRESS]
- Implement the login flow using `streamlit-oauth`.
- Verify user membership in authorized teams/orgs.
- Securely store session state.

### Phase 5: Search & Discovery [PENDING]
- Implement full-text search (FTS) using PostgreSQL's native capabilities.
- **[DEFERRED]** Explore pgvector on Supabase for semantic search (Hugging Face integration).
    - *Note: This feature is currently not implemented nor planned for immediate development due to budget constraints regarding dedicated inference hosting.*

### Phase 6: Quality Control & Audit [PENDING]
- Implementation of the 'approved' status to flag records as vetted.
- Admin portal for user management and audit logs.

