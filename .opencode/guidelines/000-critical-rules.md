# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated. Sections with full detail in dedicated guidelines are referenced here with one-line pointers — the referenced guideline contains the complete rule, enforcement matrix, and examples.

## Critical Violation: Worktree Bypass — Using stash+checkout Instead of Worktrees

**⚠️ Using `stash + checkout -b` instead of worktrees for ANY feature branch creation is a CRITICAL GUIDELINE VIOLATION.**

Worktrees are ALWAYS mandatory for feature branch creation. **See `using-git-worktrees` skill for the complete worktree creation procedure. See `060-tool-usage.md` §1-2 for tool priority hierarchy and path resolution rules.**

- 🚫 FORBIDDEN: `git checkout -b`, `stash + checkout`, operating in main working directory, ignoring `WORKTREE_FATAL=1`
- ✅ REQUIRED: `using-git-worktrees` skill for every feature branch; HALT if `WORKTREE_FATAL=1` or `WORKTREE_PATH` empty

## Critical Violation: Skipping Git Pre-Check Before ANY Work

**⚠️ Working on files without checking git state is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Starting work without creating a worktree first; operating in main working directory; creating/editing files on `main` or `dev`
- ✅ REQUIRED: See `git-workflow` skill `--task pre-work` for mandatory worktree creation and environment verification

## Critical Violation: Relative File Paths in Worktree Context

**⚠️ Using relative paths with `read`/`edit`/`write`/`glob`/`grep` tools when `WORKTREE_PATH` is set is a CRITICAL GUIDELINE VIOLATION.**

**See `060-tool-usage.md` §2 "Path Rules (ZERO TOLERANCE)" for the complete tool-by-tool table showing wrong vs correct path resolution, and the `using-git-worktrees` skill → "Tool Usage Compliance" section for worktree-specific guidance.**

- 🚫 FORBIDDEN: Relative paths with file operation tools when `WORKTREE_PATH` is set; assuming tools respect `workdir`
- ✅ REQUIRED: Prefix ALL paths with `WORKTREE_PATH` when in worktree context

## Critical Violation: Sub-Agents Ignoring Worktree Context

**⚠️ Sub-agents that modify the main repo instead of the worktree are a CRITICAL GUIDELINE VIOLATION.**

When a main agent is operating in a worktree and dispatches a sub-agent, the sub-agent MUST receive `WORKTREE_PATH` in its dispatch context and use it as the base directory for ALL file operations and git commands.

- 🚫 FORBIDDEN: Spawning sub-agents without `WORKTREE_PATH` when operating in a worktree; sub-agents that stage/commit to the main repo's working directory; skills that perform git or file operations without a "Worktree Mode" section
- ✅ REQUIRED: Pass `WORKTREE_PATH` in ALL sub-agent dispatch prompts when set; sub-agents verify `git rev-parse --show-toplevel` matches `WORKTREE_PATH` before mutating state; all new skills MUST include worktree awareness per `skill-creator` skill requirements

## Critical Violation: Implementing Without Verifying Against Live Documentation

**⚠️ Implementing code without verifying API signatures, environment variables, or function parameters against live documentation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Using unverified APIs, guessed env vars, outdated patterns, or memory-based signatures
- ✅ REQUIRED: Verify API signatures from official docs, confirm env vars from config, use `srclight_get_signature` for code signatures

## Critical Violation: Verification Dishonesty — Reporting Memory as Verified

**⚠️ Reporting unverified information as verified, or using memory recall instead of actual verification, is a CRITICAL GUIDELINE VIOLATION.**

**See `065-verification-honesty.md` for the complete rule, evidence requirements, single exchange window exception, and relationship to other guidelines.**

- 🚫 FORBIDDEN: Reporting from memory without re-verification; claiming "I checked earlier" without current tool call; training knowledge as fact; omitting tool call evidence
- ✅ REQUIRED: Use a tool/command for every verification; show evidence; tag unverified recollections as "(unverified)"

## Critical Violation: Acting on Resources Without Reading All Comments

**⚠️ Acting on a GitHub/GitBucket resource without reading ALL comments is a CRITICAL GUIDELINE VIOLATION.**

**See `067-context-completeness.md` for the complete rule, evidence requirements, staleness rule, single exchange window exception, and reading requirements per resource type.**

- 🚫 FORBIDDEN: Acting after reading only the issue body; reviewing PRs without reading comments; assuming "no new comments"; caching comment state
- ✅ REQUIRED: Read ALL comments before any action; show evidence of having read them; re-read before significant actions; use `github_issue_read` with `method=get_comments`

## Critical Violation: Skipping Post-Implementation Verification Skills

**⚠️ Failing to invoke `verification-before-completion` and `finishing-a-development-branch` after implementation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Claiming complete without invoking verification skills; manually executing skill steps; skipping verification because "changes look correct"
- ✅ REQUIRED: See `verification-before-completion` skill `--task verify` for evidence requirements; `finishing-a-development-branch` skill `--task checklist` for branch readiness; `git-workflow` skill `--task review-prep` for post-implementation workflow

## Critical Violation: Skipping review-prep After Implementation

**⚠️ Failing to invoke `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Marking complete without commit/push/URL; skipping review-prep for any reason; proceeding without URL in chat
- ✅ REQUIRED: See `git-workflow` skill `--task review-prep` for mandatory commit, push, compare URL, and HALT protocol

## Critical Violation: Wrong Chat Output Format

**⚠️ Posting URL before executive summary in chat is a CRITICAL GUIDELINE VIOLATION.** Executive summary first, URL last, AI byline LAST after URL.

**See `git-workflow` skill → "Chat Output Format (CRITICAL)" for complete format requirements and examples.**

## Critical Violation: Wrong PR Body Format

**⚠️ Writing implementation details instead of executive summary in PR bodies is a CRITICAL GUIDELINE VIOLATION.** PR bodies use Summary/Outcome/Fixes format.

**See `git-workflow` skill → `pr-creation` task → "PR Body Requirements" for complete format specification.**

## Critical Violation: Uncommitted/Unpushed Changes After Implementation

**⚠️ Marking implementation complete WITHOUT committing and pushing is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Marking complete with uncommitted changes; skipping commit/push because "changes are small"
- ✅ REQUIRED: See `finishing-a-development-branch` skill `--task checklist` for complete commit/push verification

## Critical Violation: Wrong Compare URL Base Branch

**⚠️ Using `main` as base branch in compare URLs for feature branches is a CRITICAL GUIDELINE VIOLATION.**

Feature branches target `dev`. Compare URLs: `compare/dev...<branch-name>`. Only release PRs use `compare/main...dev`.

## Critical Violation: Fabricating URLs — ZERO TOLERANCE

**⚠️ Generating URLs from memory, guesswork, or hardcoded patterns is a CRITICAL GUIDELINE VIOLATION.** All URLs must be constructed from session-enforcement plugin output. No exceptions.

- 🚫 FORBIDDEN: Hard-coding domains; using "known correct" URLs from previous sessions; guessing from git remotes; caching URL bases across sessions
- ✅ REQUIRED: Extract `GITBUCKET_HTML_URL`/`GITBUCKET_URL` from session init; construct all URLs from those values; HALT if session init missing

## Critical Violation: Inferring GitHub Owner from File Paths/Usernames

**⚠️ Inferring GitHub owner from file paths or usernames is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Inferring owner from file paths, `$USER`, `git config user.name`, cached values; making GitHub MCP calls without session init values
- ✅ REQUIRED: Use `GIT_OWNER` and `GIT_REPO` from session init for EVERY GitHub MCP call

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.** Applies to original AI-authored content, NOT copy-pasted content.

- **Requires attribution**: Python docstrings, READMEs, new repos, original docs
- **Exempt**: Standard licenses, copy-pasted code, auto-generated files, framework boilerplate, minor edits
- **Format**: `Co-authored with AI: <AI-Name> (<model-id>)`

**See `080-code-standards.md` for complete attribution requirements (file types, formats, exceptions).**

## Critical Violation: Missing Progress Reports

**⚠️ Failing to report progress in chat after implementation is a CRITICAL GUIDELINE VIOLATION.**

Progress executive summaries go to **chat ONLY**, not GitHub Issue comments. Issue comments are for **substantive, stakeholder-meaningful information** only.

Chat output order (mandatory): 1) Executive summary, 2) URL (if exists), 3) AI byline LAST — `🤖 <AgentName> (<ModelID>) <status>`

**See `github-comments` skill for Issue comment requirements and the complete channel routing table.**

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

**MANDATORY: Read issue comments and respond publicly. See `github-comments` skill → "Responding to User Comments (MANDATORY)".**

## Critical Violation: Sub-issue Structure Bypass — Multi-task Specs

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Implementing phases without sub-issue structure; assuming markdown checkboxes = tracking; creating step-level sub-issues
- ✅ REQUIRED: Sub-issues at PHASE level; each linked via `github_sub_issue_write method=add`; single-task specs exempt; auto-create as pre-implementation setup

**See `github-sub-issues` skill for complete workflow including single-task exemption, auto-create workflow, and database ID requirement.**

## Critical Violation: Stopping After Single Phase in Multi-Task Spec

**⚠️ Halting after completing a single phase of a multi-task spec is a CRITICAL GUIDELINE VIOLATION.** Authorization cascades to ALL sub-issues. Complete ALL phases, report ONCE, HALT ONCE.

**See `approval-gate` skill → "Multi-Task Spec Authorization" for complete cascade workflow and enforcement matrix.**

## Critical Violation: Sub-issue Closure Timing — ZERO TOLERANCE

**⚠️ Closing sub-issues before PR merge is a CRITICAL GUIDELINE VIOLATION.**

🚫 FORBIDDEN: Closing sub-issues after implementation but before PR merge; closing without verifying PR merge via GitHub API

**See `git-workflow` skill `--task cleanup` for complete post-merge verification and closure workflow.**

## Critical Violation: Scope Creep — NEVER Do Things Outside the Spec

**⚠️ Implementing changes not explicitly called for in the spec is a CRITICAL GUIDELINE VIOLATION.** The spec defines EXACTLY what to implement.

🚫 FORBIDDEN: Helper functions, improving nearby code, refactoring adjacent things, fixing similar issues, any change not in the spec

If you think something ELSE should be changed: 1) STOP, 2) Comment on the issue, 3) Wait for explicit approval.

## Critical Violation: Spec Without Investigation

**⚠️ Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION.**

🚫 FORBIDDEN: Specs from vague requirements; skipping codebase analysis; finalizing without edge cases; proceeding without success criteria

**See `brainstorming` skill for investigation requirements and completion criteria.**

## Critical Violation: Implementing Stale or Superseded Specs

**⚠️ Implementing a stale or superseded spec without revision is a CRITICAL GUIDELINE VIOLATION.**

**See `github-issue-creation` skill `--task pre-creation` for the complete superseded/stale spec check procedure.**

- If superseding issue exists: SILENTLY HALT, report conflict, wait for direction
- If stale: REVISE spec, report revision, HALT for approval — never implement stale without revision

## Critical Violation: Main Agent Implements Directly

**⚠️ The main agent implementing files directly instead of dispatching to sub-agents is a CRITICAL GUIDELINE VIOLATION.**

**See `divide-and-conquer` skill `--task assemble-batch` for the complete sub-agent dispatch workflow.**

- 🚫 FORBIDDEN: Main agent editing implementation files directly during batch orchestration
- 🚫 FORBIDDEN: Bypassing assemble-batch for single-issue dispatch
- 🚫 FORBIDDEN: Code-path divergence between single and batch issue handling
- ✅ REQUIRED: All implementation dispatches through `assemble-batch` — single issue is a single-item batch
- ✅ REQUIRED: Main agent only orchestrates — never edits implementation files
- ✅ REQUIRED: Context window stays clean for orchestration decisions

## Auditor Skills Enforcement

**⚠️ MANDATORY: Run `spec-auditor` when auditing specs. NO SKIPPING.**

Trigger words: "audit this spec", "review this issue", "revisit this task", "check this [SPEC]", "validate the spec"

**See `spec-auditor` skill for the complete orchestration model, baseline subtasks, conditional subtasks, and invocation commands.**

| Trigger | Action |
| -- | -- |
| Spec created | REQUIRED: `spec-auditor --issue N` |
| "Audit/review/revisit this spec" | REQUIRED: `spec-auditor --issue N` |
| Before implementation approval | REQUIRED: Verify no critical issues |
| Guideline change proposed | Optional: `guideline-auditor` |

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.** PRs require "create a PR", "make a PR", "push and create PR", "let's get a PR up", "PR" (bare), or "PR #NNN".

**See `pr-creation-workflow` skill for the full PR timing workflow including authorization boundary.**

## Critical Violation: Bug Discovery Does NOT Authorize Bug Fixing

**⚠️ Finding a bug during analysis does NOT authorize fixing it.** Bug discovery is a reporting action, NOT an implementation authorization.

**See `approval-gate` skill for the complete discovery protocol and authorization matrix.**

- 🚫 FORBIDDEN: Editing source code after discovering a bug; creating branches without approved spec; treating discovery as authorization
- ✅ REQUIRED: Create bug report issue (permitted without auth); perform read-only analysis; HALT and wait for authorization

## Critical Violation: Conflating Issue References with Authorization Cascade

**⚠️ Treating issue references as sub-issue relationships that trigger authorization cascade is a CRITICAL GUIDELINE VIOLATION.**

- 🚫 FORBIDDEN: Cascading authorization based on mentions in body/comments; assuming `#NNN` creates authorization links
- ✅ REQUIRED: Only formal sub-issue links via `github_sub_issue_write` trigger cascade; verify with `github_issue_read(method=get_sub_issues)`

**See `approval-gate` skill → "Reference ≠ Authorization Cascade" for the complete verification procedure.**

## Critical Violation: Confirmation ≠ Authorization

**⚠️ User confirmation of an observation does NOT constitute implementation authorization.**

- Only "approved", "go", "#NNN approved" authorize implementation
- "Yes, that's correct" = confirmation of observation, NOT authorization

**See `approval-gate` skill → "Confirmation ≠ Authorization" for the complete enforcement table.**

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues BEFORE the PR is merged is a CRITICAL GUIDELINE VIOLATION.**

🚫 FORBIDDEN: Closing after implementation; closing when PR created but not merged; closing parents while children open; closing without "merge confirmed"

**See `git-workflow` skill `--task cleanup` for complete post-merge verification.**

## Critical Violation: Skipping PR for Documentation/Guideline Changes

**⚠️ Documentation and guideline changes are NOT exempt from PR workflow.** ALL file modifications require full PR workflow. The only exceptions: ZERO files modified, or already-implemented specs (verified by `verify-already-implemented` task).

## Critical Violation: Parent/Child Issue Closure

**⚠️ Closing a parent issue while child issues remain open is a CRITICAL GUIDELINE VIOLATION.** Only close the child corresponding to the merged PR. Parent stays open until ALL children are closed.

**See `git-workflow` skill `--task cleanup` for the complete parent/child closure workflow.**

## Critical Violation: Deleting Branches/Stashes Improperly

**⚠️ Improper branch deletion is a CRITICAL GUIDELINE VIOLATION.** Merged branches: DELETE IMMEDIATELY. Unmerged branches with work: PRESERVE. Stashes: PRESERVE until asked.

- 🚫 FORBIDDEN: `git branch -D` on unmerged without request; `git stash drop` without request; keeping merged branches
- Merged PR → DELETE IMMEDIATELY | Unmerged → PRESERVE | Stashes → PRESERVE | `main` → NEVER DELETE

## Critical Violation: Blind Conflict Resolution

**⚠️ Resolving git conflicts using "ours"/"theirs" heuristics without classifying conflict tier is a CRITICAL GUIDELINE VIOLATION.**

**See `conflict-resolution` skill for the complete procedural workflow including classification, notification, and verification.**

Three tiers: **Tier 1 (Trivial)**: whitespace/formatting → auto-resolve, silent. **Tier 2 (Textual but safe)**: same intent, different text → auto-resolve, note in chat. **Tier 3 (Intent conflict)**: different goals or spec compliance at risk → HALT, flag for developer review.

## Critical: Engineering Mindset Required

**⚠️ All work must be approached with proper engineering discipline.** See `085-engineering-approach.md` for complete requirements.

1. Understand Before Solving — Read all relevant code before proposing changes
2. Design Before Implementing — Document approach and obtain approval before coding
3. Verify Before Declaring Complete — Run tests, check edge cases, validate success criteria
4. Communicate Changes — Post comments when substantive changes occur (NOT when creating issues, NOT for status updates)

No feature creep: implement ONLY what is in the approved spec. No unapproved work: wait for explicit "approved" or "go".

## Critical Violation: Skipping Completion Guarantee on Workflow Halt

**⚠️ Halting a skill workflow without invoking `--task completion` is a CRITICAL GUIDELINE VIOLATION.** When a state-modifying skill halts at any point — including error, failure, or early termination — the completion subtask MUST be invoked before halting.

- 🚫 FORBIDDEN: Halting mid-workflow without invoking `--task completion`; skipping completion because "nothing was done"; assuming cleanup happens automatically
- ✅ REQUIRED: Invoke `--task completion` on the current skill before halting; completion tasks are idempotent and safe to invoke multiple times

**See per-skill `tasks/completion.md` files and `.opencode/skills/completion-core/completion-core.md` for the shared completion operations.**

## Critical Violation: Skipping Interdependency Analysis for Batch Approvals

**⚠️ Processing multiple approved issues without interdependency analysis is a CRITICAL GUIDELINE VIOLATION.**

**See `approval-gate` skill → `batch-approval-analysis` task for the complete procedure, classification heuristics, and output format.**

- 🚫 FORBIDDEN: Processing issues one-by-one without analysis; assuming independence without checking; hiding analysis in reasoning
- ✅ REQUIRED: Invoke `batch-approval-analysis` for 2+ approvals; classify each issue; build dependency graph; present analysis in chat; execute in dependency order

______________________________________________________________________

**Search guidelines:** Use `srclight_search_symbols` or `grep` to find relevant guidelines.
