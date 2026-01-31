<!-- Copyright (c) 2026 Brothertown Language -->
<!-- Licensed under CC BY-SA 4.0 -->
# Contributing to SNEA Online Shoebox Editor

Thank you for your interest in contributing to the SNEA Online Shoebox Editor. We welcome contributions from the community to help preserve and manage Southern New England Algonquian (SNEA) linguistic records.

## Ethics and Sovereignty

- **Nation Sovereignty**: This project is developed with respect for SNEA Nation sovereignty.
- **Terminology**: Use "Nation" instead of "Tribal" when referring to indigenous communities.
- **Inclusive Language**: Use respectful and inclusive English in all documentation and code comments.
- **AI Contributions**: All AI-assisted changes must be clearly marked.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally.
3. **Follow the Local Development Guide** in [docs/development/local-development.md](docs/development/local-development.md) for setting up your local environment using Docker. **Cloudflare D1 access (local simulation) is mandatory for development.**
4. **Follow the Setup instructions** in the [README.md](README.md) if you need to deploy or bootstrap infrastructure.
    - **Note**: You only need to perform the "Initialization" (Docker-based setup) step. The "Infrastructure Bootstrapping" step is not required if you are contributing to an existing repository where infrastructure is already set up.

## Development Workflow

- We use `uv` for dependency management.
- Frontend is built with [Solara](https://solara.dev/).
- Backend runs on Cloudflare Workers (Python).
- Data must strictly follow MDF (Multi-Dictionary Form) standards.
- We use `ruff` for code linting and formatting. It is recommended to install the `ruff` plugin in your IDE (e.g., PyCharm, VS Code).
- Code is automatically formatted on commit via `pre-commit`. To set this up, run:
  ```bash
  docker-compose exec web pre-commit install
  ```

## Testing

Before submitting a Pull Request, ensure all tests pass. Tests should be run within the Docker environment:

```bash
docker-compose exec web python -m unittest discover tests
```

## Pull Request Process

1. Create a new branch for your feature or bugfix.
2. Ensure your code follows the existing style and conventions.
3. Update documentation if your changes introduce new features or change existing behavior. Note that all documentation contributions are licensed under CC BY-SA 4.0.
4. Submit a Pull Request to the `main` branch.
5. All PRs will be reviewed by the maintainers.

## Documentation

- **Roadmap & Setup**: [docs/development/roadmap.md](docs/development/roadmap.md)
- **Local Development**: [docs/development/local-development.md](docs/development/local-development.md)
- **MDF Guidelines**: [docs/mdf/](docs/mdf/)
- **AI Guidelines**: [.junie/guidelines.md](.junie/guidelines.md)
