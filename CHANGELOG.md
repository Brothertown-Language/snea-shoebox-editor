# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

For AI agent infrastructure changes (`.opencode/` directory), see
[`.opencode/CHANGELOG.md`](.opencode/CHANGELOG.md).

## [0.2.0] - Unreleased

### feature/git-workflow-restructure

- Restructure git workflow to main/dev/feature branch strategy with
  squash merges for feature PRs and merge commits for release PRs

### main (initial)

- Initial project infrastructure setup
- Streamlit-based web application for SNEA linguistic record editing
- PostgreSQL database integration with pgvector support
- OAuth authentication via Streamlit OAuth
- Session management and cookie handling

## [0.1.0]

### main (initial)

- Project initialization with `pyproject.toml` for dependency management
- Core dependencies: PyGithub, Streamlit, SQLAlchemy, psycopg2-binary,
  pgvector
- Development dependencies: ruff, pytest, pre-commit
- Python 3.12 requirement
- MIT License

[0.2.0]: https://github.com/Brothertown-Language/snea-shoebox-editor/compare/v0.1.0...HEAD

[0.1.0]: https://github.com/Brothertown-Language/snea-shoebox-editor/releases/tag/v0.1.0
