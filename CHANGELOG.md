# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Version Bump Skill**: New AI skill for automatic semantic version management. Analyzes implementation changes to determine version bump type (major/minor/patch), updates all version files atomically (pyproject.toml, setup.py, package.json, Cargo.toml, VERSION), and integrates with the PR creation workflow.

### Changed
- **Streamlined PR Workflow**: Integrated automatic changelog generation into the PR creation process. Changelogs are now automatically created from git commits and included in PR documentation, reducing manual documentation work and ensuring consistent change tracking.

### Added
- **Changelog Integration in PR Workflow**: Automatically generates user-facing changelogs during PR creation. Changelogs are created from git commits and included in the squash commit.
- **Merged PR Detection**: New workflow step detects previously merged PRs before creating new ones, preventing duplicate work.
- **CHANGELOG.md with Keep a Changelog Format**: Initial changelog file added following the industry-standard Keep a Changelog format.
- **Write Task for Changelog Generator**: New task in the changelog-generator skill for writing changelog output directly to CHANGELOG.md.