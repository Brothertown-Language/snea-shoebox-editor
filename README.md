<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# SNEA Online Shoebox Editor

Collaborative, version-controlled editing of Southern New England Algonquian (SNEA) linguistic records in MDF format.

## Overview

The **SNEA Online Shoebox Editor** is a collaborative platform for managing linguistic data. It leverages a 100% Python stack to provide a robust, "Zero-Touch" deployment environment for editing records in Multi-Dictionary Form (MDF).

### Goals & Ethics
- **Nation Sovereignty**: Developed with respect for SNEA Nation sovereignty.
- **AI Contributions**: All AI-assisted changes are clearly marked.
- **Inclusive English**: Use of respectful and inclusive language (e.g., "Nation" instead of "Tribal").

## Tech Stack

- **Unified Worker**: Cloudflare Workers (Python/WASM runtime) serves both frontend and backend.
- **Frontend**: stlite (Streamlit compiled to WebAssembly) runs in the browser, served as static assets by the Worker.
- **Backend**: Python API endpoints in the same Worker handle authentication, database operations, and business logic.
- **Database**: Cloudflare D1 (SQL database) bound to the Worker.
- **Package Manager**: uv.
- **Deployment**: Cloudflare git integration (automatic build and deploy on push to main).

## Requirements

- **Docker**: Required for local development.
- **Docker Compose**: Required to run the full stack locally.
- **Cloudflare Account**: With Workers and D1 access for production deployment.
- **GitHub Account**: For authentication (OAuth) and deployment.

## Setup

Refer to the **[Local Setup Guide](docs/development/SETUP.md)** for setting up your local development environment. For infrastructure bootstrapping, see the **[Production Setup Guide](docs/development/PROD_SETUP.md)**.

### Quick Start (Local Development)

If you are already a contributor and just need to run the app locally:

1.  Refer to the **[Local Development Guide](docs/development/local-development.md)**.
2.  Start the backend (Worker + local D1) and optional example frontend per guide.

## Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `CF_API_TOKEN` | Cloudflare Account API Token (Custom Token) | Manual |
| `GH_TOKEN` | GitHub Personal Access Token | Manual |
| `JWT_SECRET` | Secret for JWT signing | Wrangler secret |
| `SNEA_GITHUB_CLIENT_ID` | GitHub OAuth Client ID | Wrangler secret |
| `SNEA_GITHUB_CLIENT_SECRET` | GitHub OAuth Client Secret | Wrangler secret |

Note: For local development you may also set non-`SNEA_` fallbacks (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`) via a `.env` file. In production, use Wrangler secrets; do not commit secrets. If your `.env` file was accidentally committed, follow the **[Security Rotation Guide](docs/development/SECURITY_ROTATION.md)** immediately.

## Scripts

- `bootstrap_env.py`: **Production Only.** Automates Cloudflare and GitHub infrastructure setup (D1 database, Secrets). Run locally with `uv`.
- `docker-compose up --build`: Starts the local Worker (backend) and optional dev tooling.
- `uv run python3 -m unittest discover tests`: Runs the test suite.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Setup Guide](docs/development/SETUP.md)**: Consolidated initial setup instructions.
- **[Architecture](docs/ARCHITECTURE.md)**: Technical overview and stack details.
- **[Roadmap](docs/development/roadmap.md)**: Detailed deployment phases and development roadmap.
- **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project.
- **[Local Development](docs/development/local-development.md)**: Guide for running the Worker with local D1 and an example Pages frontend.
- **[Security Rotation](docs/development/SECURITY_ROTATION.md)**: Procedures for rotating compromised keys and secrets.
- **[MDF Guidelines](docs/mdf/)**: References for the Multi-Dictionary Form.

## License

- **Code**: This project's source code is licensed under the [MIT License](LICENSE).
- **Documentation**: All documentation (including AI-generated content) is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

---
*Note: This project is in active development.*
