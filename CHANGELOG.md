# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Changelog Integration in PR Workflow**: Automatically generates user-facing changelogs during PR creation. Changelogs are created from git commits and included in the squash commit.
- **Merged PR Detection**: New workflow step detects previously merged PRs before creating new ones, preventing duplicate work.
- **CHANGELOG.md with Keep a Changelog Format**: Initial changelog file added following the industry-standard Keep a Changelog format.
- **Write Task for Changelog Generator**: New task in the changelog-generator skill for writing changelog output directly to CHANGELOG.md.

### Changed
- **Restructured PR Creation Workflow**: Steps reorganized to include Step 0 (merged PR detection) and integrated changelog writing (Step 3). Squash commits now include CHANGELOG.md changes (Step 4).