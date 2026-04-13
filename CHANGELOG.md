# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

For AI agent infrastructure changes (`.opencode/` directory), see
[`.opencode/CHANGELOG.md`](.opencode/CHANGELOG.md).

## [0.2.0] - Unreleased

### spec/592-submodule-release

- **Submodule Release Coordination** (#592) - Implemented automanaged submodule lifecycle: session-start sync with missing dev auto-creation, automated commit/push in review-prep, SHA validation scripts (validate-submodule-refs.sh, enhanced validate-release-tags.sh with --semver/--branch), PR dependency chain enforcement, automated dev→main release promotion, and cross-platform (GitHub + GitBucket) tag verification.

### spec/batch-apr-13-2026

- **Batch Approval Implementation** (#756, #752, #728, #688, #680, #667, #533, #306, #662, #630, #683, #763, #762, #614, #470, #467) - 17 issues implemented in a single batch, including unified batch workflow, mandatory post-implementation invocation, auto-rebase pending PRs, bug analysis auto-spec, discussion-conclusion non-authorization patterns, label state machine cross-references, spec-auditor auto-fix model, branch-header changelog, identity placeholder cleanup, brainstorming terminal state, session enforcement discussion mode, ruff version sync, stale User import fix, byline format standardization, PR trigger check, and template-driven element removal.

### spec/branch-stacking-prerequisite

- **Branch Stacking Prerequisite** (#771) - Established that feature branch stacking is a prerequisite for code correctness, not a preference. Updated 6 documentation files to reframe parallel execution as opportunistic-only with documented justification required. Added critical violation entry for treating stacking as optional.

### Changed

- **Unified Batch Workflow** (#756) - Renamed batch-approval-analysis to pre-implementation-analysis, removed IMPLEMENT_DIRECTLY dispatch path, and unified single/batch issue handling through divide-and-conquer assemble-batch.
- **Mandatory Post-Implementation Invocation** (#752) - Added mandatory invocation steps to 22 skill files for verification-before-completion and finishing-a-development-branch after implementation completes.
- **Auto-Rebase Pending PRs** (#728) - Added rebase-pending task to git-workflow with intent-based conflict resolution for PRs that fall behind dev.
- **Bug Analysis Auto-Spec** (#688) - Added analyze-and-spec and verify-fix-spec tasks to issue-review skill for automatic fix spec creation from bug reports.
- **Discussion-Conclusion Non-Authorization** (#680) - Added explicit non-authorization patterns for verbal agreement, consensus, and opinion in go-prohibitions guideline.
- **Label State Machine Cross-References** (#667) - Added YAML symbolic state machines to 12 guideline and skill files for authorization lifecycle tracking.
- **Spec-Auditor Auto-Fix Model** (#533) - Added three-tier auto-fix model (auto-fix, conditional, flag-for-review) and executive summary output format to spec-auditor skill.
- **Branch-Header Changelog** (#306) - Implemented branch-header-based changelog with incremental entries, replacing flat category-only format.
- **Byline Format Standardization** (#614) - Standardized AI byline format across 23 skill files to consistent `AgentName (ModelID)` pattern.

### Fixed

- **Identity Placeholder Cleanup** (#662) - Replaced hardcoded org/user/identity values with typed placeholders across 15+ skill and guideline files.
- **Brainstorming Terminal State** (#630) - Added spec-creation path to brainstorming skill terminal state so brainstorming flows into spec creation.
- **Session Enforcement Discussion Mode** (#683) - Added discussion mode declaration to session-enforcement TypeScript plugin.
- **Ruff Version Sync** (#763) - Synchronized ruff version across pyproject.toml, .pre-commit-config.yaml, and normalized formatting in 50+ Python files.
- **Stale User Import** (#762) - Fixed stale User import and missing schema_version table in 4 test files.
- **PR Trigger Check** (#470) - Added PR creation trigger check to git-workflow skill.

### Removed

- **Template-Driven Elements** (#467) - Removed mechanical template files from skill-creator templates directory and fixed 9 broken cross-references.

### Added

- **Divide-and-Conquer Skill** (#734) - New discipline-enforcing skill that mandates pre-flight context-fit assessment before implementation. Tasks that risk context window overflow are decomposed and dispatched to sub-agents. Sub-agents signal OVERFLOW for recursive decomposition up to a configurable depth limit (default 3). Replaces implementation-workflow with a more general decomposition-first approach.

### Changed

### Fixed

- **Mock Import Paths in Frontend Tests** (#761) - Updated 34 `@patch("src.database.get_session")` mock decorators in `test_upload_mdf_page.py` (15) and `test_upload_review_d1.py` (19) to use `@patch("src.database.connection.get_session")`, matching the post-#758 import path structure.

### Added

- **Hard-Delete Unit Tests** (#698) - Added 5 unit tests for `LinguisticService.hard_delete_record()` covering cleanup of all three search tables (SearchEntry, HeadwordSearchEntry, GlossSearchEntry), EditHistory cleanup, nonexistent record edge case, and MatchupQueue suggestion nullification.

- **Database Import Paths** (#758) - Removed all convenience re-exports from `src/database/__init__.py` and `src/database/models/__init__.py`. All consumer files now use concrete import paths (e.g., `from src.database.models.core import Record` instead of `from src.database import Record`), eliminating IDE confusion and "Find Usages" misdirection.
- **Environment Variable Rename** (#759) - Renamed `JUNIE_PRIVATE_DB` to `OPENCODE` and replaced all "Junie" references with "OpenCode" across source, tests, scripts, and docs. Legacy AI tool references no longer appear in the codebase.
- **Database Initialization** (#758) - Added explicit model imports to `init_db()` so SQLAlchemy can resolve foreign keys without relying on `__init__.py` re-exports. Auto-enables `pgvector` extension when using local PostgreSQL (pgserver).

- **PEP 723 Self-Contained Tool Scripts** (#753) - Converted all 13 `.opencode/tools/` entry points (6 dispatchers + 5 standalones + session-init) and 26 impl scripts to self-contained PEP 723 scripts with `#!/usr/bin/env -S uv run --script` shebangs and inline metadata (`requires-python = "~=3.12"`, `dependencies`). Moved session-init from `.opencode/scripts/session_init.py` to `.opencode/tools/session-init`. Removed broken `[project.scripts]` from pyproject.toml. Updated all 6 dispatchers to invoke impl scripts via `uv run` instead of `sys.executable`. Updated session-enforcement.ts plugin to use `uv run .opencode/tools/session-init`. Added PEP 723 mandatory requirement to 070-environment.md. Created validation script `.opencode/tests/test-pep723-tools.sh`.

- **Subagent-Driven-Development** (#734) - Updated to reference divide-and-conquer as primary orchestration skill. Fixed missing YAML frontmatter opening delimiter. Replaced implementation-workflow cross-references.
- **Batch Orchestration Migration** (#734) - Migrated branch-per-issue, merge dependencies, squash-merge, frozen branches, and intent-and-context metadata from implementation-workflow into divide-and-conquer assemble-batch task.
- **Cross-Reference Updates** (#734) - Updated all guidelines and skills referencing implementation-workflow or batch-orchestrate to reference divide-and-conquer and assemble-batch respectively.

### Removed

- **Implementation-Workflow Skill** (#734) - Deleted `.opencode/skills/implementation-workflow/` directory; functionality absorbed by divide-and-conquer skill.

### Fixed

- **FK Cascade on Record Deletion** (#698) - Fixed `[23503] FK violation` crash when deleting records. Added explicit `HeadwordSearchEntry`/`GlossSearchEntry` deletes in `hard_delete_record()`, `populate_search_entries()`, `rollback_session()`, and batch delete paths.
- **Missing Search Entry Index and Constraint** (#698) - Added migration `20260413120000` creating `ix_search_entries_entry_type` index and `ck_search_entries_entry_type` CHECK constraint on `search_entries.entry_type`.
- **Search Entry Reprocessing Logic** (#698) - Updated `populate_search_entries` to handle all three search entry tables (headword, gloss, and generic) during reprocessing, preventing stale entries.
- **spec-creation write task now creates GitHub Issue instead of dumping to chat** (#733) - Fix spec-creation skill's write task to invoke github-issue-creation skill and output exec summary + URL + byline instead of dumping full spec content to chat.
- **Sub-agent worktree dispatch** (#741) - Add worktree awareness to all sub-agent dispatch and skill creation, preventing sub-agents from silently modifying the main repo.

### spec/session-init-batch

- **Session Injection Anti-Hallucination Context + uvx Compatibility + Worktree Detection** (#710, #712, #720, #721, #722, #723) - Rewrite session_init.py output to eliminate LLM hallucination-driven error-retry cycles. Add Remote URL, worktree detection with Working directory/Main repo paths, hooks path (problems-only), and fix bootstrap_worktree_layout for in-worktree execution. Make session_init.py uvx-compatible with proper shebang and pyproject.toml entry point. Switch session-enforcement.ts to uvx invocation. Document env-loader.ts input.$ cwd behavior.
- FIX: session_init.py "Worktrees: available" replaced with actual path (e.g. .worktrees/main/)
- FIX: session_init.py bootstrap_worktree_layout() fails when run inside a worktree
- FIX: session_init.py shebang wrong and no pyproject.toml entry point for uvx
- FIX: session-enforcement.ts hardcoded relative path breaks in worktrees
- ADD: Remote URL line in session output (anti-hallucination)
- ADD: In-worktree detection with Working directory/Main repo paths
- ADD: Hooks path output only when core.hooksPath is non-standard

### spec/724-batch-approval-fix

- **Batch Approval Analysis: Autonomous Execution + Pre-Analysis Screening + Edge Cases** - Fix batch-approval-analysis to proceed autonomously after authorization (no confirmation prompts), add pre-analysis screening for superseded/moot/conflicting/partially-implemented issues, and handle edge cases (cross-issue sub-issues, stale spec assumptions, merge-time conflicts, revision status)
- ADD: Step 0 pre-analysis screening with detection categories (already-implemented, partially-implemented, superseded, moot, stale assumptions, conflicting, meta/non-code)
- UPDATE: Step 5 from confirmation-based to informative-only (agent proceeds immediately)
- ADD: Prohibited Actions section and Developer Involvement Triggers
- ADD: Partial implementation detection with auto-detect (no developer input)
- ADD: Cross-issue sub-issue handling (parent covers default, isolated sub-agent exception)
- ADD: Stale spec assumption detection (same-intent: serialize; different-intent: HALT)
- ADD: Merge-time conflict PR ordering
- ADD: Revision status handling (approval covers revision, flag in plan, remove label)
- ADD: New classification detail sections (superseded, moot, partial implementation, stale assumption, cross-issue sub-issue, merge-time conflict)

### spec/sub-agent-batch-orchestration

- **Sub-Agent-First Implementation with Batch Orchestration** - Make sub-agent dispatch the default pattern for all implementations, with batch orchestration for multi-issue approvals
- NEW: `batch-orchestrate` task in implementation-workflow skill for single and multi-issue dispatch
- UPDATE: `orchestrate` task now dispatches to `batch-orchestrate` instead of implementing directly
- UPDATE: `batch-approval-analysis` task adds batch state file writing and yield to `batch-orchestrate`
- ADD: Batch authorization carry-forward rule to `010-approval-gate.md`
- ADD: "Main Agent Implements Directly" critical violation to `000-critical-rules.md`

### spec/purge-todowrite

- **TodoWrite Purge** - Remove unreliable `todowrite`/`TodoWrite` tracking references from active skills, eliminating stale state issues caused by the tool's unreliable state maintenance

### spec/621-compare-url-base

- **Compare URL Base Branch Fix** - Fix feature branch compare URLs to use `dev` as base instead of `main`, matching the three-branch model (feature→dev→main) and preventing inflated diffs that mislead reviewers
- Add Wrong Compare URL Base Branch critical violation to 000-critical-rules.md

### spec/676-reference-authorization-cascade

- **Reference ≠ Authorization Cascade** - Add rule that only formal sub-issue links (via `github_sub_issue_write`) trigger authorization cascade, not mere text references in issue bodies or comments
- Add mandatory verification step requiring `get_sub_issues` check before cascading authorization
- Add Confirmation ≠ Authorization rule distinguishing observation confirmations from implementation authorization
- Add both critical violations to 000-critical-rules.md and 010-approval-gate.md

### spec/668-batch-approval

- **Batch Approval Orchestration** - Add interdependency analysis for multiple approved issues, classifying them as must-precede, independent, conflict-risk, or meta/non-code, and producing a dependency graph with parallel-safe group identification before implementation begins
- Add `batch-approval-analysis` task to approval-gate skill with classification heuristics and dependency graph output format
- Add `batch-execution` task to subagent-driven-development skill for dispatching subagents according to batch execution plans
- Add critical violation entry for skipping interdependency analysis when multiple issues are approved together
- Update approval-gate and subagent-driven-development SKILL.md frontmatter with batch-related trigger keywords

### spec/664-cleanup-sync

- **Cleanup Local Sync Fix** - Add mandatory dev sync verification (git log check after pull) and make git remote prune origin mandatory in cleanup task, preventing stale local branches and ghost remote-tracking references after PR merges

### spec/659-worktrees-standardization

- **Worktrees Directory Standardization** - Standardize all references from `worktrees/` to `.worktrees/` in session_init.py, removing outdated bare directory references and updating .gitignore to remove the redundant bare `worktrees/` entry

### spec/613-worktree-enforcement

- **Worktree Enforcement Gate** - Make worktree usage mandatory when layout is active instead of advisory, remove OR escape hatch from subagent-driven-development, fix cd command violations in using-git-worktrees skill
- Add Tool Usage Compliance section and verification step to using-git-worktrees skill
- Add Worktree Gate to git-workflow pre-work task that requires worktrees when layout is active

### spec/600-auto-create-changelog-dev

- **Session Init Guard Checks** - Auto-create missing CHANGELOG.md, .opencode/CHANGELOG.md, and dev branch during session initialization, preventing silent failures from dead links and branch errors

### spec/remove-hardcoded-identity-values

- **Identity Value Cleanup** - Replace hardcoded org/user/identity values with typed placeholders in skills, enabling reuse across different repositories

### spec/594-ban-recursive-flag

- **Recursive Flag Ban** - Prohibit --recursive flag from all git submodule commands in guidelines, preventing unintended nested submodule resolution

### spec/593-git-hooks-bypass

- **Git Hook Protection** - Add pre-merge-commit and prepare-commit-msg hooks to block merges on protected branches, move hooks to .opencode/hooks/, and auto-install into submodule dirs

### spec/562-brainstorming-conversational-first

- Redesign brainstorming skill from dimension-based exploration to conversational-first approach
- Enforce strictly one question per message during brainstorming
- Replace dimension-based structured output with internal mental checklist
- Add scope decomposition before diving in for multi-subsystem requests
- Add alternatives analysis for significant decisions only (simple fixes skip to design)
- Make visual companion conditional (offered only when topic involves visual decisions)
- Add spec self-review checklist before user review (placeholder scan, consistency, scope, ambiguity)
- Add source attribution to obra/superpowers brainstorming skill
- Add process flow diagram (Graphviz dot)
- Add change comparison table from previous version
- Update terminal state to invoke writing-plans

### spec/573-isolated-test-env

- Add `.opencode/tests/with-test-home` wrapper script for isolated XDG state during opencode-cli testing
- Refactor `.opencode/tests/test-enforcement.sh` to use with-test-home, removing PREREQUISITE session limitation
- Add `tmp/` to `.opencode/.gitignore` to exclude test artifacts
- Add skill enforcement test commands to AGENTS.md Build/Lint/Test table

### spec/570-context-completeness

- Add `067-context-completeness.md` guideline requiring agents to read ALL comments before acting on any resource (issue, PR, discussion)
- Add critical violation section to `000-critical-rules.md` for acting on resources without reading all comments
- Add `067-context-completeness.md` to `opencode.jsonc` instructions list for session context injection
- Define evidence requirement (cite, count, or summarize comments read)
- Define staleness rule using action-significance (not time estimation)
- Define single exchange window exception consistent with verification honesty (#568)

### spec/subagent-driven-development

- Add `subagent-driven-development` skill adapted from obra/superpowers
- Create implementer, spec-reviewer, and code-quality-reviewer prompt templates
- Implement two-stage review per task (spec compliance then code quality)
- Document model selection guidance for cheap/standard/capable models
- Add implementer status handling (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED)
- Integrate with approval-gate, git-workflow, verification-before-completion, finishing-a-development-branch
- Document when to use subagent-driven-development vs implementation-workflow
- Add cross-references to implementation-workflow, executing-plans, and dispatch-table
- Include source attribution to obra/superpowers in all adapted files

### spec/556-writing-plans-enhancement

- Add TDD step granularity within phases (failing test → verify fail → implement → verify pass → commit)
- Add plan document header with Goal, Architecture, and Tech Stack sections
- Add file structure section for decomposition before tasks
- Enhance no-placeholders rule with 6 additional prohibited patterns from obra/superpowers
- Add self-review checklist (spec coverage, placeholder scan, type consistency)
- Add step granularity rules (2-5 min per step, exact code/commands)
- Add source attribution to obra/superpowers writing-plans skill
- Update enforcement to validate TDD structure, file structure, and header

### spec/fix-session-init-output-format

- Convert session_init.py output from inconsistent `Label: value` / `KEY=value` mix to consistent `KEY=value` format
- Change `Human Developer:` → `DEV_NAME=`, `Human Email:` → `DEV_EMAIL=`, `Git Remote Url:` → `GIT_REMOTE_URL=`, `Repository Owner:` → `GIT_OWNER=`, `Repository:` → `GIT_REPO=`
- Add prominent platform banners with horizontal rules (`# GITHUB REPOSITORY DETECTED` / `# GITBUCKET REPOSITORY DETECTED`)
- Update AGENTS.md to document KEY=value format and add missing `GITHUB_HTML_URL` variable

### spec/adjust-tool-priorities

- Remove 36 superseded ai_bin scripts (nb, plans, py-find, py-structure, start, multi-find)
- Rewrite mcp-tool-usage skill with five-tier tool priority hierarchy (opencode built-in primary, JetBrains MCP fallback)
- Update 10+ guideline/skill/config files to reference new hierarchy and removed tools
- Add notebook swap/reorder workflows to notebook-operations skill
- Add .ipynb zero-tolerance exception table to notebook-operations skill
- Update AGENTS.md MCP Enforcement Gate and Boundaries sections

### spec/prevent-redundant-audit-comments-521

- Remove spec-auditor mandate to post audit findings as GitHub issue comments
- Add audit findings prohibition to github-comments skill decision table
- Clarify in critical-rules that audit findings are internal agent guidance, not progress comments
- Establish workflow: audit → act on findings → comment only for substantive spec revisions

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

### Changed

- **Identity Placeholder Sweep** (#770) - Replaced remaining hardcoded org/user/identity values with typed placeholders across skill and tool files, ensuring repository portability.
- **Mandatory Chat Output in Writing-Plans** (#773) - Added mandatory chat output step to the writing-plans create task, ensuring plan creation always produces a visible executive summary.

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
