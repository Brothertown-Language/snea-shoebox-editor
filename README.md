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

## Requirements

- **Python 3.12** — exact version recommended (`requires-python = "==3.12.*"`).
- **uv** — for dependency management and environment orchestration.
- **PostgreSQL 16+** — local development uses `pgserver` (embedded Postgres).
- **GitHub Account** — for authentication and team-based RBAC.

## Setup & Run

### Quick Start (Local Development)

1. **Install dependencies**:
    ```bash
    uv sync --extra local
    ```

2. **Start the local environment**:
    ```bash
    ./scripts/start_streamlit.sh
    ```

    The app automatically manages its own `pgserver` instance and schema. Data is stored in `tmp/local_db`.

3. **Stop the environment**:
    ```bash
    ./scripts/kill_streamlit.sh
    ```

4. **Background Mock Viewer** (optional):
    ```bash
    ./scripts/start_view_mocks.sh
    ```
    This launches the mock component gallery on port 8502. Stop it with `./scripts/stop_view_mocks.sh`.

## Scripts

All utility scripts are in the `scripts/` directory and should be run with `uv run`.

| Script                        | Description                                      |
|-------------------------------|--------------------------------------------------|
| `start_streamlit.sh`          | Start main app on port 8501 (background)         |
| `kill_streamlit.sh`           | Stop main app                                    |
| `start_view_mocks.sh`         | Start mock viewer on port 8502 (background)      |
| `stop_view_mocks.sh`          | Stop mock viewer                                 |
| `manage_local_db.py`          | Inspect or reset local `pgserver`                |
| `verify_iso639.py`            | Refresh ISO 639 reference data                   |
| `seed_permissions.py`         | Load RBAC rules from `permissions.json`          |
| `dump_users.py`               | Inspect synchronized GitHub user accounts        |
| `test_db_connection.py`       | Verify connectivity to Aiven or local DB         |

Run Python scripts with:

```bash
uv run python scripts/<script_name>.py
```

## Project Structure

```
snea-shoebox-editor/
├── streamlit_app.py       # Main application entry point & orchestrator
├── src/
│   ├── frontend/          # Streamlit pages & UI components
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
│   │   ├── upload_service.py         # MDF upload, staging & matchup workflow
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
- **[MDF Upload Plan](docs/plans/mdf-upload-plan.md)**: Implementation plan for the MDF file upload feature.
- **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project.

## License

- **Code**: Licensed under the [MIT License](LICENSE).
- **Documentation**: Licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

---

*This project is in active development.*
