# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

For AI agent infrastructure changes (`.opencode/` directory), see
[`.opencode/CHANGELOG.md`](.opencode/CHANGELOG.md).

## [0.2.0] - Unreleased

### feature/overwrite-skills-503

- Restructure guidelines to rules-only: delete 15 procedural guideline files, move content to skills
- Add 12 new guideline files: planning series (141-144), error handling series (200-203), srclight preference (016), open questions (045), branch naming (115), scripting (210)
- Add 8 critical violation sections to 000-critical-rules.md: git pre-check, docs verification, review-prep, chat output format, uncommitted changes, fabricated URLs, owner inference, sub-issue bypass
- Expand 000-session-init.md with GitBucket platform detection, .env credential loading, structured output
- Replace placeholder references (`<project-db>`, `<archived-db>`) with actual names (`pubmed_data_3`, `pubmed_data_2`)
- Delete 14 obsolete skills: code-review, commit-writer, context7-lookup, debugger, dev-architect, file-organizer, git-conventions, implementation-quality, mcp-builder, pr-writer, release-notes, task-writer, version-bump, webapp-testing
- Add 14 new skills: brainstorming, engineering-approach, executing-plans, finishing-a-development-branch, fragment-manager, gitbucket-api (with tools and tests), github-issue-creation, implementation-workflow, receiving-code-review, requesting-code-review, systematic-debugging, test-driven-development, verification-before-completion, writing-plans
- Restructure 16 existing skills with task decomposition (SKILL.md task pattern)
- Add .opencode/.guidelines/ registry system (README.md, ai-identity.md, branch-first-protocol.md, commit-workflow.md, registry.yaml)
- Add .opencode/dispatch-table.yaml for skill trigger mapping
- Archive previous guideline/skill versions to .opencode.legacy/
- Expand ai_bin/session_init.py with GitBucket URL parsing and .env support
- Add 21 ai_bin/ implementation scripts for notebook and plans operations
- Remove plans/ directory (70+ archived plan files superseded by GitHub Issues)

### feature/hotfix-backport-dev-authoritative-422

- Add "Hotfix Backport: Dev as Authoritative Source" section to `112-git-merge-protocol.md`
- Add conflict resolution matrix for hotfile-specific vs non-hotfix files
- Update `115-git-hotfix-workflow.md` with reference to new conflict resolution procedure
- Create `scripts/hotfix_backport.py` - automated backport script with intelligent conflict resolution
- Add testing documentation for hotfix backport workflow

### feature/skills-wording-unit14

- Fix skill verification script to exclude CHANGELOG.md from "Automatic Invocation" check (historical documentation)
- Fix skill verification script to exclude lines with "→ Example only" (educational markers)
- Fix AGENTS.md to include "pr" trigger in Master Trigger Table for PR creation

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
