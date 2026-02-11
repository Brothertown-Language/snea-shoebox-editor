<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
# Local Development Guide

This guide explains how to run the SNEA Shoebox Editor locally for development and testing.

## Prerequisites

- **Python 3.12**: Required version for development and production.
- **uv**: Dependency management. Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Aiven Account**: You'll need a PostgreSQL database. You can use a free Aiven project or a local PostgreSQL instance.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Brothertown-Language/snea-shoebox-editor.git
    cd snea-shoebox-editor
    ```
2.  **Initialize Environment**:
    ```bash
    uv sync --extra local
    ```
3.  **Configure local secrets**: Create `.streamlit/secrets.toml` in the project root:
    ```toml
    [connections.postgresql]
    url = "postgresql://avnadmin:[YOUR-PASSWORD]@[YOUR-SERVICE-NAME]-[YOUR-PROJECT-NAME].aivencloud.com:[YOUR-PORT]/defaultdb?sslmode=require"

    [github_oauth]
    client_id = "YOUR_LOCAL_GITHUB_CLIENT_ID"
    client_secret = "YOUR_LOCAL_GITHUB_CLIENT_SECRET"
    redirect_uri = "http://localhost:8501/component/streamlit_oauth.authorize_button"
    ```
    *Note: Register a separate GitHub OAuth App for local development with `http://localhost:8501/component/streamlit_oauth.authorize_button` as the callback URL.*

## Running the App

Start the Streamlit development server using the provided script:

```bash
./scripts/start_streamlit.sh
```

Alternatively, you can run it directly:

```bash
uv run --extra local streamlit run src/frontend/app.py
```

*Note: Always use the start script or `nohup` for background execution. For local development and testing, **ALWAYS** include `--extra local` to ensure that `pgserver` and other local dependencies are available. If no database URL is configured in secrets or environment, the app will automatically start a local PostgreSQL 16.2 instance using `pgserver` (data stored in `tmp/local_db`).*

The app should now be accessible at `http://localhost:8501`.

## Database Management

The app now automatically handles its own schema initialization. If you are using the local `pgserver` (default), the data is stored in `tmp/local_db`.

- On startup, the app checks if the required tables exist and creates them if necessary.
- You can inspect the database directly via the Aiven console if using a remote instance.

## Running Tests

Run the test suite with local dependencies:

```bash
uv run --extra local python -m unittest discover tests
```

## Architecture Details

- **Folder Structure**: The `src/frontend/` directory is a legacy artifact. Although the app is now a unified Python application, this specific folder structure is required for Streamlit Community Cloud deployment and cannot be changed.
- **Frontend/Backend**: Streamlit Community Cloud (standard Python server execution).
- **Database**: PostgreSQL (Aiven).
- **Authentication**: GitHub OAuth via `streamlit-oauth`.
- **Data Layer**: MDF (Multi-Dictionary Formatter).
