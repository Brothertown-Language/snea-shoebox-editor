# Local Development Guide

This guide explains how to run the SNEA Shoebox Editor locally for development and testing.

## Prerequisites

- **Python 3.10+**: Ensure you have a compatible Python version installed.
- **uv**: Dependency management. Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Aiven Account**: You'll need a PostgreSQL database. You can use a free Aiven project or a local PostgreSQL instance.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Brothertown-Language/snea-shoebox-editor.git
    cd snea-shoebox-editor
    ```
2.  **Initialize environment**:
    ```bash
    uv venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    uv pip install -e .
    ```
3.  **Configure local secrets**: Create `.streamlit/secrets.toml` in the project root:
    ```toml
    [connections.postgresql]
    url = "postgresql://avnadmin:[YOUR-PASSWORD]@[YOUR-SERVICE-NAME]-[YOUR-PROJECT-NAME].aivencloud.com:[YOUR-PORT]/defaultdb?sslmode=require"

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
    *Note: Register a separate GitHub OAuth App for local development with `http://localhost:8501` as the callback URL.*

## Running the App

Start the Streamlit development server:

```bash
uv run streamlit run src/frontend/app.py
```

The app should now be accessible at `http://localhost:8501`.

## Database Management

Since we are using Aiven (PostgreSQL), the application is responsible for initializing its own schema. 

- On startup, the app checks if the required tables exist and creates them if necessary.
- You can inspect the database directly via the Aiven console.

## Running Tests

Run the test suite using `unittest`:

```bash
uv run python -m unittest discover tests
```

## Architecture Details

- **Folder Structure**: The `src/frontend/` directory is a legacy artifact. Although the app is now a unified Python application, this specific folder structure is required for Streamlit Community Cloud deployment and cannot be changed.
- **Frontend/Backend**: Streamlit Community Cloud (standard Python server execution).
- **Database**: PostgreSQL (Aiven).
- **Authentication**: Simple session-based login.
- **Data Layer**: MDF (Multi-Dictionary Formatter).
- **Embeddings**: (Future Feature) Hugging Face Inference API.

## Vector Search (Future Feature - Deferred)

The project plans to use semantic search via PostgreSQL and `pgvector` on Aiven. This feature is **currently deferred** and not implemented in the production application due to budget constraints. If implemented in the future, both local development and production will use the Hugging Face Inference API for embedding generation exclusively. Ensure your PostgreSQL instance has the `vector` extension enabled.
