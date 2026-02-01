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

- **Frontend**: Cloudflare Pages (static site or SPA). Any JS framework (or vanilla JS) can be used; example OAuth flow provided.
- **Backend**: Cloudflare Workers (Python/WASM runtime).
- **Database**: Cloudflare D1 (SQL database) bound to the Worker.
- **Package Manager**: uv.
- **Deployment**: GitHub Actions + Wrangler.

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
| `JWT_SECRET` | Secret for JWT signing | Wrangler secret (`JWT_SECRET`) |
| `SNEA_GITHUB_CLIENT_ID` | GitHub OAuth Client ID | Wrangler secret / Pages Project Var |
| `SNEA_GITHUB_CLIENT_SECRET` | GitHub OAuth Client Secret | Wrangler secret / Pages Project Var |
| `SNEA_FRONTEND_URL` | Public Pages URL used as `redirect_uri` | Pages Project Var |

Note: For local development you may also set non-`SNEA_` fallbacks (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `FRONTEND_URL`) via a `.env` file. In production, use Wrangler secrets and Pages Project Variables; do not commit secrets.

## Scripts

- `bootstrap_env.py`: **Production Only.** Automates Cloudflare and GitHub infrastructure setup (D1 database, Secrets). Run locally with `uv`.
- `bootstrap_domains.py`: **Production Only.** Specifically initializes custom domains on Cloudflare for both the Worker (Backend) and Pages (Frontend).
- `docker-compose up --build`: Starts the local Worker (backend) and optional dev tooling.
- `python3 -m unittest discover tests`: Runs the test suite.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Setup Guide](docs/development/SETUP.md)**: Consolidated initial setup instructions.
- **[Architecture](docs/ARCHITECTURE.md)**: Technical overview and stack details.
- **[Roadmap](docs/development/roadmap.md)**: Detailed deployment phases and development roadmap.
- **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project.
- **[Local Development](docs/development/local-development.md)**: Guide for running the Worker with local D1 and an example Pages frontend.
- **[MDF Guidelines](docs/mdf/)**: References for the Multi-Dictionary Form.

## License

- **Code**: This project's source code is licensed under the [MIT License](LICENSE).
- **Documentation**: All documentation (including AI-generated content) is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

---
*Note: This project is in active development.*
