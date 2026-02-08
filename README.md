<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# SNEA Online Shoebox Editor

Collaborative, version-controlled editing of Southern New England Algonquian (SNEA) linguistic records in MDF format.

## Overview

**Live Site:** [https://snea-edit.streamlit.app/](https://snea-edit.streamlit.app/)

The **SNEA Online Shoebox Editor** is a collaborative platform for managing linguistic data. It leverages a 100% Python stack to provide a robust environment for editing records in Multi-Dictionary Form (MDF).

### Goals & Ethics

- **Nation Sovereignty**: Developed with respect for SNEA Nation sovereignty.
- **AI Contributions**: All AI-assisted changes are clearly marked.
- **Inclusive English**: Use of respectful and inclusive language (e.g., "Nation" instead of "Tribal").

## Tech Stack

| Component          | Technology                                                                 |
|--------------------|---------------------------------------------------------------------------|
| Language           | Python 3.12                                                               |
| Framework          | [Streamlit](https://streamlit.io/) (hosted on Streamlit Community Cloud)  |
| Database           | PostgreSQL (Aiven) / local via `pgserver`                                 |
| ORM                | SQLAlchemy 2.x                                                            |
| Authentication     | GitHub OAuth via `streamlit-oauth` (Brothertown-Language team verification) |
| Package Manager    | [uv](https://docs.astral.sh/uv/)                                         |
| Linter / Formatter | Ruff                                                                      |
| Testing            | pytest                                                                    |
| Deployment         | Automatic on push to `main` (Streamlit Community Cloud)                   |

> *Note: The `src/frontend/` folder is a mandatory legacy artifact required by Streamlit Cloud's entry point configuration and cannot be changed.*

## Requirements

- **Python 3.12** — exact version required (`requires-python = "==3.12.*"`).
- **uv** — for dependency management and virtual environment.
- **Aiven Account** — for hosting the PostgreSQL database (production).
- **GitHub Account** — for authentication (OAuth) and deployment.

## Setup & Run

### Quick Start (Local Development)

1. **Install dependencies**:
    ```bash
    uv sync --extra local
    ```

2. **Run the app**:
    ```bash
    ./scripts/start_streamlit.sh
    ```

    If no database URL is configured in secrets or environment, the app automatically starts a local PostgreSQL 16.2 instance using `pgserver` (data stored in `tmp/local_db`).

3. **Stop the app**:
    ```bash
    ./scripts/kill_streamlit.sh
    ```

4. **Configure secrets** (optional): Create `.streamlit/secrets.toml` with your GitHub OAuth credentials to test authentication.

> Always use the start script or `nohup` for background execution. For local development, **always** include `--extra local` in your `uv` commands.

## Environment Secrets

Secrets are managed via `.streamlit/secrets.toml` locally and the Streamlit Cloud "Secrets" UI in production.

| Secret                          | Description                        |
|---------------------------------|------------------------------------|
| `connections.postgresql.url`    | Aiven PostgreSQL connection URI    |
| `github_oauth.client_id`       | GitHub OAuth Client ID             |
| `github_oauth.client_secret`   | GitHub OAuth Client Secret         |
| `github_oauth.redirect_uri`    | App callback URL                   |

> **Do not commit secrets to the repository.** If secrets were accidentally committed, follow the **[Security Rotation Guide](docs/development/SECURITY_ROTATION.md)** immediately.

## Tests

Run the full test suite:

```bash
uv run pytest tests/
```

Run a specific test file:

```bash
uv run pytest tests/test_security_manager.py
```

Test directories mirror the `src/` layout:

| Directory          | Covers                       |
|--------------------|------------------------------|
| `tests/database/`  | Database models & connection |
| `tests/frontend/`  | UI components & pages        |
| `tests/mdf/`       | MDF parser & validator       |
| `tests/services/`  | Service layer                |
| `tests/ui/`        | UI utilities                 |

## Scripts

All utility scripts are in the `scripts/` directory.

| Script                        | Description                                      |
|-------------------------------|--------------------------------------------------|
| `start_streamlit.sh`          | Start the local dev server (background, `nohup`) |
| `kill_streamlit.sh`           | Stop the running Streamlit server                |
| `manage_local_db.py`          | Manage the local `pgserver` database             |
| `clone_db.py`                 | Clone a database                                 |
| `seed_permissions.py`         | Seed permission data                             |
| `dump_permissions.py`         | Dump current permissions                         |
| `clear_permissions.py`        | Clear permission data                            |
| `dump_users.py`               | Dump user records                                |
| `check_db_resolution.py`      | Check database DNS resolution                    |
| `test_db_connection.py`       | Test database connectivity                       |
| `verify_iso639.py`            | Verify ISO 639 language code data                |
| `download_ci_logs.py`         | Download CI log artifacts                        |

Run Python scripts with:

```bash
uv run python scripts/<script_name>.py
```

## Project Structure

```
snea-shoebox-editor/
├── src/
│   ├── frontend/          # Streamlit app entry point & pages
│   │   ├── app.py         # Main application orchestrator
│   │   ├── pages/         # Streamlit multi-page views
│   │   ├── constants.py   # UI constants
│   │   ├── ui_utils.py    # UI helper functions & dialogs
│   │   └── utils.py       # General frontend utilities
│   ├── database/          # SQLAlchemy models & connection
│   │   ├── connection.py  # DB engine creation & init
│   │   ├── migrations.py  # Schema evolution & data seeding
│   │   ├── base.py        # Declarative base
│   │   ├── data/          # Seed data (permissions JSON, ISO 639)
│   │   └── models/        # ORM models (core, identity, workflow, etc.)
│   ├── mdf/               # MDF parser & validator
│   ├── services/          # Business logic services
│   │   ├── identity_service.py       # User sync & GitHub identity
│   │   ├── security_manager.py       # RBAC, session rehydration
│   │   ├── navigation_service.py     # Page registry & routing
│   │   ├── audit_service.py          # Activity logging
│   │   ├── infrastructure_service.py # Aiven API, network & system checks
│   │   └── linguistic_service.py     # Record/Source CRUD (scaffold)
│   └── auth.py            # OAuth integration
├── tests/                 # pytest test suite (mirrors src/ layout)
├── scripts/               # Utility & maintenance scripts
├── launchers/             # PyCharm run configurations
├── docs/                  # Project documentation
├── documentation/         # Active task tracking
├── .junie/                # AI agent guidelines
├── pyproject.toml         # Project metadata & dependencies
├── uv.lock                # Locked dependency versions
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # Contribution guidelines
└── README.md
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Architecture](docs/ARCHITECTURE.md)**: System architecture overview.
- **[Requirements](docs/REQUIREMENTS.md)**: Project requirements.
- **[Roadmap & Setup](docs/development/roadmap.md)**: Deployment phases and detailed setup guide.
- **[Local Development Guide](docs/development/local-development.md)**: Detailed instructions for local setup and testing.
- **[OAuth2 & Deep Link Setup](docs/development/oauth2-deeplink-setup.md)**: Guide for setting up OAuth and deep links.
- **[Database Comparison](docs/database/DB_COMPARISON.md)**: Why Aiven was chosen as the database provider.
- **[Security Rotation](docs/development/SECURITY_ROTATION.md)**: Procedures for rotating compromised keys and secrets.
- **[MDF Guidelines](docs/mdf/mdf-tag-reference.md)**: References for the Multi-Dictionary Form.
- **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project.

## License

- **Code**: Licensed under the [MIT License](LICENSE).
- **Documentation**: Licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

---

*This project is in active development.*
