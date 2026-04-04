# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Implementation Quality Skill**: New AI skill for verifying pattern compliance during implementation. Includes concern-based task files for file locations, code structure, environment patterns, and data integrity. Automatic invocation at workflow boundaries ensures consistent pattern verification before creating files, during implementation, and before running commands.

### Changed
- **URL-Last Format for Executive Summaries**: Executive summaries in GitHub comments now place URLs at the end, making it easier to scan the summary content before accessing the link. This improves readability and establishes a consistent visual pattern across all AI-generated progress comments.
- **Mandatory Push Before HALT**: AI agents now automatically push feature branches to remote before halting after implementation, eliminating a common workflow violation where developers couldn't review changes. This ensures the compare URL is always available for code review.
- **Compound Command Recognition**: Added explicit pattern matching rules to verify that approval tokens (`approved`, `go`) must be standalone words separated by whitespace to constitute valid authorization. Compound phrases like `#196approvedcheck pr` are no longer incorrectly parsed as approvals. This prevents authorization errors when approval tokens appear adjacent to other text.
- **AI Attribution Identity Detection**: AI agents must now detect their actual runtime identity (name, model ID, email) dynamically instead of using hardcoded placeholder values. Example values in guidelines are explicitly illustrative only. When identity is unknown, agents must stop and ask for clarification rather than guessing. This ensures AI co-authored attribution reflects the actual AI assistant that created the content, preventing misattribution from copied example values.

### Added
- **Review Phase Enforcement**: Mandatory review phase after all implementations. Branches must be pushed and a compare URL generated before any PR can be created, ensuring all changes are visible for developer review. This prevents accidental PRs and enforces a clear boundary between "implementation complete" and "PR requested."

### Added
- **Version Bump Skill**: New AI skill for automatic semantic version management. Analyzes implementation changes to determine version bump type (major/minor/patch), updates all version files atomically (pyproject.toml, setup.py, package.json, Cargo.toml, VERSION), and integrates with the PR creation workflow.

### Changed
- **Streamlined PR Workflow**: Integrated automatic changelog generation into the PR creation process. Changelogs are now automatically created from git commits and included in PR documentation, reducing manual documentation work and ensuring consistent change tracking.

### Added
- **Changelog Integration in PR Workflow**: Automatically generates user-facing changelogs during PR creation. Changelogs are created from git commits and included in the squash commit.
- **Merged PR Detection**: New workflow step detects previously merged PRs before creating new ones, preventing duplicate work.
- **CHANGELOG.md with Keep a Changelog Format**: Initial changelog file added following the industry-standard Keep a Changelog format.
- **Write Task for Changelog Generator**: New task in the changelog-generator skill for writing changelog output directly to CHANGELOG.md.