# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Auto-Issue Creation for Workflow Violations**: When AI agents bypass critical workflow steps like review-prep or PR creation, the system now automatically creates GitHub issues to track the violations. This creates accountability for workflow compliance and enables systematic improvement of guidelines.
- **Post-Implementation Pattern Enforcement**: A new post-implementation task in the implementation-quality skill now ensures review-prep is invoked after every implementation. This mandatory gate prevents workflow bypass and ensures all code changes are properly reviewed before PR creation.
- **Mandatory Skill Invocation Enforcement**: AI agents must now invoke skills at critical workflow points (file creation, implementation start, command execution, data handling) via the implementation-quality skill. Automatic pattern verification prevents guideline violations before they occur, ensuring consistent code structure, file locations, and data integrity throughout all implementations.

### Changed
- **Authority Source Rule Added**: New guideline in `130-authority-source.md` enforces checking for superseding issues before implementing specs. This prevents wasted work on outdated specifications by requiring verification that no later `[SPEC]`, `[SPEC-FIX]`, or `[SPEC-ENHANCEMENT]` issues exist, and that referenced code locations haven't been modified since spec creation. Specs found to be stale must be revised before implementation proceeds.

### Fixed
- **PR Workflow Enforcement**: Added critical violation warning for bypassing the git-workflow skill during PR operations. All PR-related commands ("pr", "update PR", "push and create PR") must now invoke the skill, which handles GitHub API verification and branch cleanup automatically. This prevents manual git command errors and ensures consistent PR handling.
- **Spec Audit Chain Enforcement**: Added mandatory architectural review as the third auditor in the spec review process. All specs must now pass concern structure, content quality, AND architectural correctness checks before approval. This prevents incomplete or poorly-architected specifications from being approved.

### Changed
- **Dev-Architect Review-Spec Task Rewritten**: Review-spec task now uses comprehensive violation mapping with 100% auto-revise for format violations (boilerplate phases, missing elements), incomplete context (file references, success criteria), and content quality (vague/untestable criteria). Prompt-only mode is reserved for catastrophic failures like circular dependencies and architecture conflicts. This makes spec review more predictable and thorough.
- **Mandatory PR Skill Invocation**: Added explicit CRITICAL VIOLATION warning for bypassing the git-workflow skill when handling PR commands. Commands like "pr", "update PR", and "push and create PR" MUST invoke the pr-creation task. Manual PR updates are FORBIDDEN. The skill now handles existing PR detection automatically, checking for both open and merged PRs before proceeding.

### Fixed
- **Existing PR Detection**: Changed `--state merged` to `--state all` in PR checks to catch all PR states. Added decision tree: update open PRs, create new branch for merged PRs. This prevents updating merged PRs (would lose changes) and prevents creating duplicate PRs when an open PR already exists.

### Added
- **Authorization Recognition Protocol**: New explicit authorization patterns in AGENTS.md and scope-autonomy guidelines. Defines compound commands like "fix X while you're at it" and "implement #227 and include in this branch" as valid authorization. Clarifies that questions like "should I do X?" and conditionals like "if you think X..." are NOT authorization. This prevents authorization confusion and ensures consistent AI behavior.
- **Implementation Quality Skill**: New AI skill for verifying pattern compliance during implementation. Includes concern-based task files for file locations, code structure, environment patterns, and data integrity. Automatic invocation at workflow boundaries ensures consistent pattern verification before creating files, during implementation, and before running commands.
- **Review Phase Enforcement**: Mandatory review phase after all implementations. Branches must be pushed and a compare URL generated before any PR can be created, ensuring all changes are visible for developer review. This prevents accidental PRs and enforces a clear boundary between "implementation complete" and "PR requested."
- **Version Bump Skill**: New AI skill for automatic semantic version management. Analyzes implementation changes to determine version bump type (major/minor/patch), updates all version files atomically (pyproject.toml, setup.py, package.json, Cargo.toml, VERSION), and integrates with the PR creation workflow.
- **Changelog Integration in PR Workflow**: Automatically generates user-facing changelogs during PR creation. Changelogs are created from git commits and included in the squash commit.
- **Merged PR Detection**: New workflow step detects previously merged PRs before creating new ones, preventing duplicate work.
- **CHANGELOG.md with Keep a Changelog Format**: Initial changelog file added following the industry-standard Keep a Changelog format.
- **Write Task for Changelog Generator**: New task in the changelog-generator skill for writing changelog output directly to CHANGELOG.md.
- **Completion Reporting Format Clarified**: Fixed issue where PR URLs were incorrectly included in GitHub issue completion comments. PR URLs now appear only in chat output, with GitHub issues focusing on summary and outcome without redundant URLs. Review-prep and pr-creation tasks have explicit tables showing correct placement for each format element.
- **URL-Last Format Enforcement Added**: Added critical warnings and verification checklists to git-workflow skills (review-prep.md and pr-creation.md). Executive summaries must place URLs at the end for better scannability. Includes pre-post verification checklists to ensure compliance before posting.
- **URL-Last Format for Executive Summaries**: Executive summaries in GitHub comments now place URLs at the end, making it easier to scan the summary content before accessing the link. This improves readability and establishes a consistent visual pattern across all AI-generated progress comments.
- **Mandatory Push Before HALT**: AI agents now automatically push feature branches to remote before halting after implementation, eliminating a common workflow violation where developers couldn't review changes. This ensures the compare URL is always available for code review.
- **Compound Command Recognition**: Added explicit pattern matching rules to verify that approval tokens (`approved`, `go`) must be standalone words separated by whitespace to constitute valid authorization. Compound phrases like `#196approvedcheck pr` are no longer incorrectly parsed as approvals. This prevents authorization errors when approval tokens appear adjacent to other text.
- **AI Attribution Identity Detection**: AI agents must now detect their actual runtime identity (name, model ID, email) dynamically instead of using hardcoded placeholder values. Example values in guidelines are explicitly illustrative only. When identity is unknown, agents must stop and ask for clarification rather than guessing. This ensures AI co-authored attribution reflects the actual AI assistant that created the content, preventing misattribution from copied example values.
- **Streamlined PR Workflow**: Integrated automatic changelog generation into the PR creation process. Changelogs are now automatically created from git commits and included in PR documentation, reducing manual documentation work and ensuring consistent change tracking.

### Fixed
- **Issue vs Chat Format Separation**: Fixed completion reporting to use different formats for GitHub issues (summary and outcome only) versus chat (includes PR URL). Previously, PR URLs were incorrectly appearing in both locations, creating redundancy and confusion.