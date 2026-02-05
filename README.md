<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# SNEA Online Shoebox Editor

Collaborative, version-controlled editing of Southern New England Algonquian (SNEA) linguistic records in MDF format.

## Overview

The **SNEA Online Shoebox Editor** is a collaborative platform for managing linguistic data. It leverages a 100% Python stack to provide a robust environment for editing records in Multi-Dictionary Form (MDF).

### Goals & Ethics
- **Nation Sovereignty**: Developed with respect for SNEA Nation sovereignty.
- **AI Contributions**: All AI-assisted changes are clearly marked.
- **Inclusive English**: Use of respectful and inclusive language (e.g., "Nation" instead of "Tribal").

## Tech Stack

- **Architecture**: Monolithic Streamlit application (Hosted on Streamlit Community Cloud).
    - *Note: The `src/frontend/` folder is a mandatory legacy artifact required by Streamlit Cloud's entry point configuration and cannot be changed.*
- **Database**: Aiven (PostgreSQL).
- **Authentication**: GitHub OAuth via `streamlit-oauth`.
- **Package Manager**: uv.
- **Deployment**: Automatic build and deploy on push to main (via Streamlit Community Cloud).

## Requirements

- **Python 3.12**: Required version for development and production.
- **uv**: For dependency management.
- **Aiven Account**: For hosting the PostgreSQL database.
- **GitHub Account**: For authentication (OAuth) and deployment.

## Setup

Refer to the **[Roadmap & Setup](docs/development/roadmap.md)** for detailed setup instructions.

### Quick Start (Local Development)

1.  **Install dependencies**:
    ```bash
    uv sync --extra local
    ```
2.  **Run the app**:
    ```bash
    ./scripts/start_streamlit.sh
    ```
    *Note: Always use the start script or `nohup` for background execution. If no database URL is configured in secrets or environment, the app will automatically start a local PostgreSQL 16.2 instance using `pgserver` (data stored in `tmp/local_db`).*

3.  **Configure secrets (Optional)**: Create `.streamlit/secrets.toml` with your GitHub OAuth credentials if you want to test authentication.

## Environment Secrets

Secrets are managed via `.streamlit/secrets.toml` locally and the Streamlit Cloud "Secrets" UI in production.

| Secret | Description |
|--------|-------------|
| `connections.postgresql.url` | Aiven PostgreSQL connection URI |
| `github.client_id` | GitHub OAuth Client ID |
| `github.client_secret` | GitHub OAuth Client Secret |
| `github.redirect_uri` | App callback URL |
| `auth.jwt_secret` | Secret for JWT signing |
| `embedding.model_id` | (Future Feature - Deferred) Hugging Face Model ID |
| `embedding.api_key` | (Future Feature - Deferred) Hugging Face API Key |

Note: Semantic searching is an upcoming feature. The database has been prepared with `pgvector` support in both production and local development environments.

Note: Do not commit secrets to the repository. If secrets were accidentally committed, follow the **[Security Rotation Guide](docs/development/SECURITY_ROTATION.md)** immediately.

## Scripts

- `./scripts/start_streamlit.sh`: Starts the local development server in the background using `nohup`.
- `uv run python -m unittest discover tests`: Runs the test suite.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Roadmap & Setup](docs/development/roadmap.md)**: Deployment phases and detailed setup guide.
- **[Database Comparison](docs/database/DB_COMPARISON.md)**: Why Aiven was chosen as the database provider.
- **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project.
- **[Security Rotation](docs/development/SECURITY_ROTATION.md)**: Procedures for rotating compromised keys and secrets.
- **[MDF Guidelines](docs/mdf/)**: References for the Multi-Dictionary Form.

## License

- **Code**: This project's source code is licensed under the [MIT License](LICENSE).
- **Documentation**: All documentation (including AI-generated content) is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

---
*Note: This project is in active development.*
