# Local Development Guide

This guide explains how to run the SNEA Shoebox Editor locally for development and testing.

## Prerequisites

- **Python 3.10+**: Ensure you have a compatible Python version installed.
- **uv**: Dependency management. Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- **Supabase Account**: You'll need a PostgreSQL database. You can use a free Supabase project or a local PostgreSQL instance.
- **Docker & Docker Compose**: For running the containerized environment.
    - **Note**: Ensure BuildKit is enabled to avoid deprecation warnings.
    - **Installation**: If missing, install the buildx plugin: `sudo apt-get update && sudo apt-get install docker-buildx`.
    - **Configuration**: Run `export DOCKER_BUILDKIT=1` and `export COMPOSE_DOCKER_CLI_BUILD=1` in your shell, or add them to your `~/.bashrc`.

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
    *Note: Register a separate GitHub OAuth App for local development with `http://localhost:8501` as the callback URL.*

## Running the App

Start the Streamlit development server:

```bash
uv run streamlit run src/frontend/app.py
```

The app should now be accessible at `http://localhost:8501`.

## Database Management

Since we are using Supabase (PostgreSQL), the application is responsible for initializing its own schema. 

- On startup, the app checks if the required tables exist and creates them if necessary.
- You can inspect the database directly via the Supabase dashboard.

## Running Tests

Run the test suite using `unittest`:

```bash
uv run python -m unittest discover tests
```

## Architecture Details

- **Frontend/Backend**: Streamlit Community Cloud (standard Python server execution).
- **Database**: PostgreSQL (Supabase).
- **Authentication**: GitHub OAuth (`streamlit-oauth`).
- **Data Layer**: MDF (Multi-Dictionary Formatter).
- **Embeddings**: (Future Feature) Hugging Face Inference API.

## Vector Search (Future Feature - Deferred)

The project plans to use semantic search via PostgreSQL and `pgvector` on Supabase. This feature is **currently deferred** and not implemented in the production application due to budget constraints. If implemented in the future, both local development and production will use the Hugging Face Inference API for embedding generation exclusively. The developer Docker environment (`docker-compose.yml`) does not include a local embedding container to ensure perfect parity with production. Ensure your PostgreSQL instance has the `vector` extension enabled.
