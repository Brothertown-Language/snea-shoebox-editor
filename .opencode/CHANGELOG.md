# Changelog

All notable changes to AI agent infrastructure (`.opencode/`) will be
documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.2.0] - Unreleased

### feature/approval-cleanup

- **Fixed: Authorization Cleanup is SILENT**: Removed "Post authorization comment"
  step from cleanup workflow. Authorization cleanup is state management (label
  removal, STATUS suffix clearing, todo clearing) and does not warrant GitHub
  comments. Only implementation progress (review-prep, PR creation) requires
  GitHub comments AND chat updates.
- **Changed Files**:
  - `010-approval-gate.md`: Removed comment posting step from cleanup process
  - `123-github-ai-identity.md`: Removed Authorization Cleanup Comments section
  - `approval-gate/SKILL.md`: Updated cleanup workflow to remove comment posting
- **Addresses**: GitHub issue #384

### skill/todowrite-progress-tracking

- **Added: Progress Tracking to Git Workflow Tasks**: All git workflow
  tasks now include TodoWrite progress tracking so developers can see
  which step the agent is on during complex git operations.
- **Changed Files**:
  - `git-workflow/tasks/pre-work.md`: Track Steps 0-2 (verify branch,
    create feature branch, report ready)
  - `git-workflow/tasks/review-prep.md`: Track Steps 0-6 (temp cleanup,
    lint verification, verify push, clear TODOs, generate URL, verify,
    report, HALT)
  - `git-workflow/tasks/commit-prep.md`: Track Steps 1-4 (discovery,
    summarize, create script, HALT)
  - `git-workflow/tasks/pr-creation.md`: Track Steps 0-9 (clear todos,
    check PR state, collect sub-issues, version bump, changelog, stage,
    squash, push, create PR, report)
  - `git-workflow/tasks/cleanup.md`: Track Steps 1-7 (verify PR merge,
    hotfix ticket, switch to dev, delete branch, clean branches, verify,
    clear todos)
- **Developer Experience**: Each task initializes TodoWrite at the start
  with all steps showing pending/in_progress/completed status, updating
  after each step completes for real-time visibility.
- **Addresses**: GitHub issue #438 (Phase 2: Add TodoWrite to Tasks)

### spec/435-ruff-markdown-prohibition

- **Fixed: Pre-Lint File Type Verification**: Added mandatory file type
  verification before running linters to prevent running Python tools
  (ruff, pyright, vulture) on Markdown files. This is a CRITICAL guideline
  violation that causes noise and wastes time.
- **Added: Enforcement in Multiple Locations**:
  - `070-environment.md`: Added Pre-Lint File Type Verification section
    with verification steps and cross-check table
  - `060-tool-usage.md`: Added mandatory verification with tool selection table
  - `080-code-standards.md`: Added linting section with file type verification
    and prohibited misuse table
  - `git-workflow/tasks/review-prep.md`: Added lint tool verification step
  - `mcp-tool-usage/SKILL.md`: Added Pre-Lint File Type Verification task
- **Changed: Tool Selection Enforcement**: Added explicit prohibitions
  against running ruff/pyright/vulture on .md files, and pymarkdownlnt/mdformat
  on .py files. Verification MUST happen before each lint command.
- **Addresses**: GitHub issue #435.

### spec/ai-agent-workflow-fixes

- **Added: PR Creation Skill Enforcement (015-mcp-preference.md)**: Added mandatory
  skill invocation table for PR creation trigger patterns. Prohibits bypassing
  git-workflow skill with direct `github_create_pull_request` calls or manual git
  commands. All PR creation must go through `/skill git-workflow --task pr-creation`.
- **Changed: Executive Summary URL Placement (113-git-pr-workflow.md)**: Added URL
  placement table specifying that GitHub Issue comments must NOT contain URLs
  while Chat output must contain URLs. URLs must appear as the last line after
  the agent byline. Executive summaries focus on stakeholder value, not file lists.
- **Added: Todo Tracking for Multi-Phase Specs (git-workflow/tasks/implementation.md)**:
  Added todo cleanup section for clearing stale todos when authorization received
  after workflow interruption. Includes detection of interruption types and
  mandatory todo clearing before implementation.
- **Addresses**: GitHub issues #429 and #431.

### spec/git-workflow-compare-url-fix

- **Fixed: Compare URL Base Branch**: Corrected compare URL generation in
  git-workflow skills and guidelines to use `dev` as base branch for
  feature branches instead of `main`. Feature branches merge to `dev`
  first, then `dev` merges to `main` via release PRs. Updated 6 files:
  `000-critical-rules.md`, `125-github-issue-comments.md`,
  `approval-gate/SKILL.md`, `approval-gate/tasks/post-implementation.md`,
  `git-workflow/tasks/review-prep.md`,
  `implementation-quality/tasks/post-implementation.md`.

### skill/wording-remediation

- **Changed: Standardized Skill Trigger Format**: All 29 skills now use explicit
  `/skill X --task Y` commands in master trigger table. Replaced ambiguous
  trigger descriptions with precise invocation commands for better agent
  clarity. All skills follow consistent workflow trigger format.
- **Fixed: Removed Junie Language**: Replaced all "invoked automatically" and
  similar passive construction with explicit "is invoked at these triggers"
  format. Removed "Automatic Invocation" headings replaced with "Workflow
  Triggers" or "Enforcement Points".
- **Changed: Terminology Standardization**: Replaced "Entry/Exit Criteria" with
  "Preconditions/Postconditions" across all task files and templates. Replaced
  "Operating Protocol" with "Workflow" section to match skill convention.
- **Fixed: Hardcoded Identity References**: Removed hardcoded "OpenCode (ollama-cloud/glm-5)"
  example values from skill files. Guidelines now explicitly state these are
  illustrative examples and agents must detect their own identity at runtime.
- **Added: Verification Tool**: Moved verify-skill-wording.sh to .opencode/scripts/
  for ongoing enforcement of linguistic standards. The tool detects Junie
  patterns and terminology violations.
- **Changed: Master Trigger Table**: AGENTS.md now has single source-of-truth
  trigger table with explicit /skill invocations. All skills reference this
  table instead of duplicating trigger information.

### skill/audit-chain-clean-room

- **Fixed: Clean-Room Draft Generation as First Auditor**: Corrected the
  mandatory audit chain to include clean-room draft generation as the
  FIRST step. The spec-auditor now has a `generate-independent-spec` task
  that creates a complete, implementable spec draft WITHOUT viewing the
  live spec. This prevents pollution where the agent's view of existing
  content influences its draft. The audit chain now runs in this order:
  1) clean-room draft generation, 2) concern-separation audit (phase
  structure), 3) spec-audit (content quality), 4) dev-architect review
  (architectural correctness).

### spec/anchor-based-references

- **Added: Anchor Infrastructure for Stable References**: Created verification
  script (`verify-anchor-refs.py`) that detects fragile references (section
  numbers, step numbers, gate numbers, phase numbers) in guidelines and
  skills. Added comprehensive style guide (`150-anchor-references.md`) for
  converting fragile references to stable anchor-based format.
- **Changed: Guidelines Use Stable Anchors**: Converted 113 fragile references
  in 20 files to stable anchor-based references using section names and
  anchor IDs instead of line numbers or section numbers. This prevents
  broken cross-references when files are edited.

### skill/pr-creation-changelog-fix

- **Fixed: Changelog Step Order in PR Creation Workflow**: Replaced fragile
  step number references with stable anchor names in the pr-creation task.
  The Execute Squash section now references `[Generate Changelog](#generate-changelog)`
  and `[Stage Changelog](#stage-changelog)` anchors instead of "Step 3" and
  "Step 4", ensuring the documentation remains correct even if step order
  changes. This eliminates confusion where the skill documentation stated
  changelog should be included before squash but referenced steps that ran
  after squash.

### skill/verification-gates-enforcement

- **Added: Verification Gates in All Skills**: Added mandatory
  verification checkpoints to 29 skill SKILL.md files ensuring
  engineering methodology is enforced at critical workflow points.
- **Added: Question-Response Protocol**: Guidelines now require
  verification before answering any user questions, preventing agents
  from acting on outdated assumptions.
- **Added: Exemption Conditions per Skill**: Each skill documents
  specific exemption conditions for its verification gates.

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
