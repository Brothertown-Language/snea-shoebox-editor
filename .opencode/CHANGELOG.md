# Changelog

All notable changes to AI agent infrastructure (`.opencode/`) will be
documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - Unreleased

### spec/engineering-methodology-enforcement

- **Added: Verification-First Response Protocol**: AI agents must verify
  session init, superseding issues, codebase state, and sub-issues BEFORE
  responding to ANY user input. Enforces mandatory MCP probes and
  prevents incorrect responses based on outdated assumptions.
- **Added: Critical Violation for Bypassing Verification Gates**: Added
  enforcement rules for checking session init, MCP availability, and
  conflict detection before any response. Violations trigger mandatory
  checks at workflow entry points.
- **Added: Questions Are Not Bypass Authorization**: Clarified that
  answering questions does NOT authorize implementation. Questions
  require verification first, then response. Authorization is a separate
  check.
- **Changed: Session Init is Mandatory First Step**: Agents cannot
  respond to user input before completing session init. Stores
  GIT_OWNER, GIT_REPO, DEV_NAME, DEV_EMAIL for session duration.

### spec/audit-main-branch-refs

- **Fixed: Branch Reference Standardization**: Updated all git workflow
  skills and guidelines to use `dev` as the base branch for feature
  branches instead of `main`. Changes include:
  - Replaced `origin/main` with `origin/dev` in git diff/log commands
  - Updated branch creation workflow to start from `dev`
  - Fixed squash operations to reset against `origin/dev`
  - Corrected changelog generation to compare against `dev` branch

### spec/changelog-organization

- Establish dual changelog workflow separating AI agent changes from
  project changes
- Reference version numbers from `pyproject.toml` in changelog headers
- Update changelog-generator skill to support dual changelog workflow
- Add version extraction logic from pyproject.toml for consistent
  versioning

### spec/comment-format-enforcement-275

- **Fixed: URLs in GitHub Issue Comments**: Added critical violation rule
  forbidding URLs in GitHub issue comments. Comments are now reserved for
  historic context (WHAT/WHY), while chat receives actionable URLs.
  Includes complete comment format requirements in github-comments skill.

### spec/ai-assistant-task-loop-prevention

- **Added: Task Loop Prevention Guideline**: Documents AI assistant task
  loop/recursion patterns and prevention strategies. Covers loop detection
  heuristics, exit strategies, and mandatory MCP enforcement points.
- **Fixed: Task invocation MUST check for self-referential calls** before
  entering subtask to prevent infinite recursion.
- **Added: Summary loop, question loop, and status update loop patterns**
  with detection and recovery procedures.

### spec/sub-issue-status-check-before-parent-closure

- **Fixed: Sub-issue Verification Before Parent Closure**: Added mandatory
  pre-close checklist requiring all agents to call `get_sub_issues` before
  closing any issue. Prevents violations where parent issues were closed
  while children remained open.

### spec/closed-issue-audit

- **Added: Closed-Issue Remediation Workflow**: When a closed issue is
  targeted for implementation, agents must audit sub-issues and verify
  code exists before proceeding. Includes direct inspection requirements
  and remediation decision tree.

### spec/post-impl-workflow-gate

- **Added: Post-Implementation Pattern Enforcement**: New task in
  implementation-quality skill ensures review-prep is invoked after every
  implementation. Mandatory gate prevents workflow bypass and ensures
  proper code review before PR creation.

### spec/skills-check-subissues

- **Fixed: Check Sub-issues When Verifying Task Completion**: Agents must
  verify all sub-issues are closed (or legitimately unimplemented) before
  closing parent issues. Includes double-check workflow after PR merge.

### spec/mandatory-skill-invocation

- **Added: Mandatory Skill Invocation Enforcement**: AI agents must invoke
  skills at critical workflow points (file creation, implementation start,
  command execution, data handling) via implementation-quality skill.
  Automatic pattern verification prevents guideline violations.

### spec/issue-first-workflow

- **Changed: Authority Source Rule Added**: Enforces checking for
  superseding issues before implementing specs. Prevents wasted work on
  outdated specifications by requiring verification that no later
  `[SPEC]`, `[SPEC-FIX]`, or `[SPEC-ENHANCEMENT]` issues exist.

### spec/fix-mandatory-pr-skill-invocation

- **Fixed: PR Workflow Enforcement**: Added critical violation warning for
  bypassing git-workflow skill during PR operations. All PR-related
  commands must invoke the skill, which handles GitHub API verification
  and branch cleanup automatically.

### skill/audit-chain-fix

- **Fixed: Spec Audit Chain Enforcement**: Added mandatory architectural
  review as third auditor. All specs must pass concern structure, content
  quality, AND architectural correctness checks before approval.

### spec/223-dev-architect-auto-revise

- **Fixed: Dev-Architect Review-Spec Task Rewritten**: Review-spec task
  uses comprehensive violation mapping with 100% auto-revise for format
  violations, incomplete context, and content quality issues. Prompt-only
  mode reserved for catastrophic failures.
- **Added: Authorization Recognition Protocol**: Defines compound commands
  like "fix X while you're at it" as valid authorization. Clarifies that
  questions and conditionals are NOT authorization.
- **Fixed: URL-Last Format for Executive Summaries**: Executive summaries
  place URLs at the end for better scannability.

### spec/fix-review-prep-invocation

- **Added: Post-Implementation Verification Checklist**: Added mandatory
  post-implementation checklist to approval-gate skill ensuring
  review-prep is invoked after implementation.

### spec/implementation-quality

- **Changed: Restructured Engineering Approach**: Split
  engineering-approach into implementation-quality skill with concern-based
  task files (file locations, code structure, environment, data
  integrity).

### docs/pr-shortcut

- **Added: PR Shortcut Documentation**: Documented 'pr' as valid shortcut
  for 'create a PR' in skills.

### spec/import-opencode-agent-skills

- **Added: Skill Import from External Repository**: Imported opencode
  agent skills from opencode-agents-hub repository with licensing and
  compatibility verification.

### spec/executive-summary-url-formatting

- **Added: URL-Last Format Enforcement**: Added critical warnings and
  verification checklists to git-workflow skills. Executive summaries must
  place URLs at the end.

### spec/review-prep-enforcement-199

- **Fixed: Mandatory Push Before HALT**: AI agents automatically push
  feature branches to remote before halting after implementation.
  Eliminates workflow violation where developers couldn't review changes.

### spec/compound-command-parsing

- **Fixed: Compound Command Recognition**: Added explicit pattern matching
  rules verifying that approval tokens must be standalone words separated
  by whitespace. Compound phrases like `#196approvedcheck pr` no longer
  incorrectly parsed as approvals.

### spec/dynamic-identity-detection

- **Added: AI Attribution Identity Detection**: AI agents must detect
  actual runtime identity (name, model ID, email) dynamically instead of
  using hardcoded placeholder values. Example values in guidelines are
  explicitly illustrative only. When identity unknown, agents must stop
  and ask for clarification.

### spec/impl-workflow-enhancement

- **Fixed: Issue vs Chat Format Separation**: Fixed completion reporting
  to use different formats for GitHub issues (summary and outcome only)
  versus chat (includes PR URL). URLs now appear only in chat output,
  preventing redundancy.
- **Added: Streamlined PR Workflow**: Integrated automatic changelog
  generation into PR creation process. Changelogs automatically created
  from git commits and included in PR documentation.
- **Fixed: Existing PR Detection**: Changed PR state checks to catch all
  PR states. Added decision tree: update open PRs, create new branch for
  merged PRs.
- **Added: Mandatory Push Before HALT**: AI agents automatically push
  feature branches before halting, ensuring compare URL is always
  available.

### spec/version-bump-skill-impl

- **Added: Version Bump Skill**: New AI skill for automatic semantic
  version management. Analyzes implementation changes, determines
  version bump type, updates all version files atomically.

### spec/changelog-subtask-in-pr-creation

- **Added: Changelog Integration in PR Workflow**: Automatically
  generates user-facing changelogs during PR creation from git commits.
- **Added: Write Task for Changelog Generator**: New task writes
  changelog output directly to CHANGELOG.md.
- **Added: Initial CHANGELOG.md**: Project changelog following Keep a
  Changelog format.

[0.2.0]: https://github.com/Brothertown-Language/snea-shoebox-editor/compare/v0.1.0...HEAD
