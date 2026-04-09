# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated.

## Critical Violation: Skipping Git Pre-Check Before ANY Work

**⚠️ Working on files without checking git state is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Starting ANY work (implementation, verification, editing) WITHOUT checking git state first
- Assuming working tree is clean without `git status` verification
- Creating files while on `main` or `dev` branch
- Editing files while on `main` or `dev` branch
- Skipping stash when pending changes exist

### ✅ MANDATORY

**See `git-workflow` skill `--task pre-work` for the mandatory pre-check sequence, stash verification, and branch creation steps.**

### Why This Matters

| Scenario | Consequence |
|----------|-------------|
| Edit files on `main` | Cannot create branch, changes stuck on `main` |
| Skip git status check | Untracked files lost when switching branches |
| Forget `-u` flag | Untracked files NOT stashed, lost forever |
| Skip stash verification | Modifications silently lost |

______________________________________________________________________

## Critical Violation: Implementing Without Documentation Verification

**⚠️ Implementing code without verifying against live documentation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Implementing API calls without verifying parameter names from official docs
- Using environment variables without confirming correct names from config files
- Guessing function signatures from memory or similar libraries
- Using outdated blog posts/tutorials instead of official documentation

### ✅ REQUIRED

- **ALWAYS verify API signatures before implementing**
- Check official documentation for current API usage
- Use `srclight_get_signature` or `pycharm_get_symbol_info` for function signatures
- Read source code and type hints when docs unavailable
- Confirm environment variable names from `.env.example` or config

### Why This Matters

- Assumption-based implementations lead to broken functionality
- API changes between library versions cause silent failures
- Incorrect parameter names waste debugging time
- Outdated patterns accumulate technical debt

______________________________________________________________________

## Critical Violation: Skipping Post-Implementation Verification Skills

**⚠️ Failing to invoke `verification-before-completion` and `finishing-a-development-branch` after implementation is a CRITICAL GUIDELINE VIOLATION.**

This is the same class of failure as skipping `review-prep`: skills exist, dispatch triggers are documented, but the agent skips them because there is no enforcement mechanism blocking progression.

### 🚫 FORBIDDEN

- Claiming "task complete" without invoking `verification-before-completion --task verify`
- Claiming "implementation complete" without invoking `finishing-a-development-branch --task checklist`
- Manually executing skill steps instead of formally invoking the skill
- Skipping verification because "the changes look correct"
- Proceeding to `review-prep` before verification skills pass

### ✅ REQUIRED

**See `verification-before-completion` skill `--task verify` for evidence requirements.**
**See `finishing-a-development-branch` skill `--task checklist` for branch readiness enforcement.**
**See `git-workflow` skill `--task review-prep` for the mandatory post-implementation workflow.**

### Why Manual Execution Is NOT Sufficient

Manual execution of skill steps is PROHIBITED because skills contain enforcement checklists, CRITICAL VIOLATION warnings, and mandatory decision points that inline steps lack.

| Manual Execution | Formal Skill Invocation |
|-------------------|------------------------|
| Skips enforcement checklists | Loads and follows enforcement checklist |
| Agent may skip "obvious" steps | Every step is explicit and mandatory |
| No CRITICAL VIOLATION warnings in context | Skill content includes enforcement warnings |
| Error-prone, agent decides what to skip | No decision points — all steps required |

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| Skip verification | Success criteria not checked, bugs shipped |
| Skip finishing checklist | Uncommitted changes, failing tests, broken PRs |
| Skip both | No evidence of completion, no quality gate |
| Manual execution only | Agent bypasses enforcement, misses steps |

______________________________________________________________________

## Critical Violation: Skipping review-prep After Implementation

**⚠️ Failing to invoke `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Marking implementation complete WITHOUT committing, pushing, and generating URL
- Skipping `review-prep` because "no changes were made"
- Skipping `review-prep` because "already pushed"
- Skipping `review-prep` for documentation/guideline changes
- Proceeding to next phase without URL in chat

### ✅ REQUIRED

**See `git-workflow` skill `--task review-prep` for the mandatory post-implementation workflow including commit, push, compare URL generation, and HALT protocol.**

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| No commit | Changes lost, no tracking |
| No push | Remote has no branch, compare URL fails |
| No URL | Developer cannot review changes |
| No HALT | Premature PR creation or issue closure |
| Wrong format | Developer lacks context before URL |

______________________________________________________________________

## Critical Violation: Wrong Chat Output Format

**⚠️ Posting URL before executive summary in chat is a CRITICAL GUIDELINE VIOLATION.**

The executive summary MUST appear BEFORE the URL in chat output. URL must be LAST.

**See `git-workflow` skill → "Chat Output Format (CRITICAL)" section for complete format requirements and examples.**

______________________________________________________________________

## Critical Violation: Wrong PR Body Format

**⚠️ Writing implementation details instead of executive summary in PR bodies is a CRITICAL GUIDELINE VIOLATION.**

PR bodies MUST use the executive summary format (Summary/Outcome/Fixes). Implementation details do NOT belong in PR bodies.

**See `git-workflow` skill → `pr-creation` task → "PR Body Requirements" section for complete format specification and examples.**

______________________________________________________________________

## Critical Violation: Uncommitted/Unpushed Changes After Implementation

**⚠️ Marking implementation complete WITHOUT committing and pushing is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Marking task complete when `git status` shows uncommitted changes
- Skipping `git commit` because "changes are small"
- Skipping `git push` because "branch exists"
- Proceeding to review-prep without push verification

### ✅ REQUIRED

**See `finishing-a-development-branch` skill `--task checklist` for the complete commit/push verification procedure and enforcement checklist.**

______________________________________________________________________

## Critical Violation: Fabricating URLs — ZERO TOLERANCE

**⚠️ Generating URLs from memory, guesswork, or hardcoded patterns is a CRITICAL GUIDELINE VIOLATION.**

All URLs must be constructed exclusively from values provided by the session-enforcement plugin output. No exceptions.

### 🚫 FORBIDDEN

- Hard-coding domain names, hostnames, or URL paths in any output
- Using "known correct" URLs from previous sessions, specs, or documentation as source
- Guessing URL patterns from git remote URLs or other indirect sources
- Caching URL base values across sessions
- Including example URLs in guidelines/skills that might be copied as fact
- **Constructing URLs from the git remote hostname** (e.g., `tomcat-0002.newsrx.com` ≠ `gitbucket.newsrx.com`)

### ✅ REQUIRED

1. Values are automatically injected by the session-enforcement plugin (`.opencode/plugins/session-enforcement.ts` via `.opencode/scripts/session_init.py`)
1. Extract `GITBUCKET_HTML_URL` (preferred) or `GITBUCKET_URL` (legacy) from session init output
1. Construct ALL URLs using that base URL + `GIT_OWNER` + `GIT_REPO`
1. If session init does not provide a required URL component → HALT and report

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| Hardcoded domain | Wrong server, broken links, eroded trust |
| Cached from prior session | Stale after infrastructure changes |
| Guessed from remote URL | Fragile, often incorrect |
| Example URL copied as fact | Propagates errors across specs/docs |

### Session Init Unavailable

If session init has not been run or does not provide URL components:

1. **REFUSE** to generate any URL
1. Report: "Cannot generate URLs — session init not run or missing URL components"
1. HALT and wait for user to run session init

______________________________________________________________________

## Critical Violation: Inferring GitHub Owner from File Paths/Usernames

**⚠️ Inferring GitHub owner from file paths or usernames is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Inferring `owner=XXXX` from file path `/home/XXXX/git/...`
- Inferring owner from `$USER` environment variable
- Inferring owner from git username (`git config user.name`)
- Using cached/stale owner values from previous sessions
- Making ANY GitHub MCP call without session init values being available

### ✅ REQUIRED

1. Values are automatically injected by the session-enforcement plugin (`.opencode/plugins/session-enforcement.ts` via `.opencode/scripts/session_init.py`)
1. Store ALL output values (`DEV_NAME`, `DEV_EMAIL`, `GIT_OWNER`, `GIT_REPO`, `GIT_HOOKS_PATH`, `GIT_REMOTE_URL`) for session duration
1. Use `GIT_OWNER` and `GIT_REPO` for EVERY GitHub MCP call
1. NEVER assume or hardcode owner/repo values

### Why This Matters

- File paths vary across machines (`/home/<user>/` vs `/home/<other>/` )
- `$USER` returns local username, NOT GitHub owner
- `git config user.name` returns human name, NOT GitHub owner
- Cached values become stale across sessions
- Incorrect owner causes GitHub API failures

______________________________________________________________________

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.**

AI co-authorship applies to **original content authored by AI**, NOT copy-pasted content.

### What Requires Attribution

- **Python files**: Module docstring with `Co-authored with AI: AI-Name (model-id)`
- **README files**: Footer section with `## Co-Authored With AI`
- **New repositories**: README MUST include AI co-authored section
- **Original docs**: Footer with `*Co-authored with AI: AI-Name (model-id)*`

### What Does NOT Require Attribution

- **Standard licenses** (MIT, Apache, GPL) - established legal templates
- **Copy-pasted code/docs** - original source holds copyright, NOT AI co-authorship
- **Auto-generated files** (lock files, `__pycache__`)
- **Framework boilerplate** (default configs, project structures)
- **Minor edits** (typo fixes, formatting)

### Attribution Format

`Co-authored with AI: <AI-Name> (<model-id>)`

Example: `Co-authored with AI: OpenCode (ollama-cloud/glm-5)`

**See `.opencode/guidelines/080-code-standards.md` for complete attribution requirements (file types, formats, exceptions).**

## Critical Violation: Missing Progress Comments

**⚠️ Failing to post progress comments to the associated issue is a CRITICAL GUIDELINE VIOLATION.**

Every implementation task MUST be documented with progress comments on the GitHub issue.

**See `github-comments` skill for complete progress comment format, emoji guide, and byline requirements.**

### 🚫 FORBIDDEN in Progress Comments

- **File lists** — Redundant (visible in git commits)
- **"Next" field** — Dialog prompt (violates AGENTS.md)
- **Punch-list format** — Use executive summary paragraphs
- **"Awaiting authorization"** — Use HALT protocol, not comments
- **Technical changelog** — Focus on impact, not file-by-file changes

### Audit Findings Are NOT Progress Comments

**⚠️ Posting spec-audit findings as GitHub comments is FORBIDDEN.**

Audit findings from `spec-auditor` are internal agent guidance — equivalent to linter output. They inform the agent what to fix, not what to announce to stakeholders.

| Action | Post Comment? |
|--------|---------------|
| Agent completes implementation task | ✅ YES — progress comment with executive summary |
| Agent revises spec substantively after audit | ✅ YES — one revision comment per `github-comments` skill |
| Agent makes non-substantive spec changes (STATUS, typos, cross-refs) after audit | ❌ NO |
| Agent posts audit findings report | 🚫 FORBIDDEN — act on findings, don't post the report |

### ⚠️ Chat Output Rule (CRITICAL)

**Progress executive summaries go to BOTH GitHub comments AND chat.**

**See `github-comments` skill for complete requirements.**

______________________________________________________________________

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

Users communicating via GitHub Issues cannot see your internal analysis, are not mind readers, and expect responses where they asked the question.

**MANDATORY: Read issue comments and respond publicly. See `github-comments` skill → "Responding to User Comments (MANDATORY)" section for complete protocol.**

______________________________________________________________________

## Critical Violation: Acting on Resources Without Reading All Comments

**⚠️ Acting on a GitHub/GitBucket resource without reading ALL comments is a CRITICAL GUIDELINE VIOLATION.**

The issue body or PR description alone is NEVER sufficient context. Comments may contain authorizations, direction changes, clarifications, blockers, or scope changes that alter the correct action.

### 🚫 FORBIDDEN

- Acting on an issue after reading only the issue body
- Reviewing a PR without reading review comments
- Checking authorization without reading recent comments
- Assuming "no new comments" without actually checking
- Caching comment state from a previous session
- Skipping comment reads because "I checked earlier"

### ✅ REQUIRED

- Read ALL comments before ANY action on a resource (issue, PR, discussion)
- Show evidence of having read comments (count, summarize, or cite specific comments)
- Re-read before significant actions even if recently read
- Use `github_issue_read` with `method=get_comments` to fetch comments

**See `067-context-completeness.md` for the complete rule, evidence requirements, staleness rule, and single exchange window exception.**

______________________________________________________________________

## Critical Violation: Sub-issue Structure Bypass — Multi-task Specs

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**

- Implementing a phase that exists only as text in the parent issue body
- Proceeding **to implementation** when `get_sub_issues` returns empty array for multi-task specs **without creating sub-issues first**
- Assuming markdown checkboxes = task tracking
- Creating step-level sub-issues instead of phase-level

**✅ REQUIRED:**

- Sub-issues at PHASE level, not step level
- Each phase as separate GitHub Issue linked via `github_sub_issue_write method=add`
- Single-task specs are exempt from sub-issue requirement
- Auto-create sub-issues as a pre-implementation setup step when `get_sub_issues` returns empty for an approved multi-task spec

**The prohibition is against implementing phases without sub-issue structure, NOT against auto-creating sub-issues as a setup step.** Sub-issue creation is a tracking/setup action covered by the parent spec's authorization — no separate authorization is required.

**See `github-sub-issues` skill for complete workflow including single-task vs multi-task exemption, auto-create workflow, database ID requirement, and phase-level structure.**

**Note:** Sub-issue auto-creation is NOT a violation of this prohibition. Auto-creating sub-issues and then proceeding to implementation is the CORRECT workflow. The prohibition is against implementing phases while sub-issues are still missing, NOT against the auto-creation step itself.

______________________________________________________________________

## Critical Violation: Stopping After Single Phase in Multi-Task Spec

**⚠️ Halting after completing a single phase of a multi-task spec is a CRITICAL GUIDELINE VIOLATION.**

When a parent issue has sub-issues, authorization cascades to ALL sub-issues. The agent must complete ALL phases before HALTing.

### 🚫 FORBIDDEN

- Completing Phase 2, then HALTing expecting re-authorization for Phase 3
- Treating sub-issues as separate authorization units
- Asking for "approved" between phases of multi-task spec
- Reporting completion after each phase instead of after ALL phases

**See `approval-gate` skill → "Multi-Task Spec Authorization" for the complete authorization cascade workflow and enforcement matrix.**

Authorization cascades to ALL sub-issues. Complete ALL phases, then report ONCE and HALT ONCE.

**Exception:** User explicitly restricts authorization (e.g., "approved: Phase 2 only") → complete that phase ONLY, then HALT.

## Critical Violation: Sub-issue Closure Timing — ZERO TOLERANCE

**⚠️ Closing sub-issues before PR merge is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- **Closing sub-issues after implementation but BEFORE PR merge**
- **Closing sub-issues when PR is created but not merged**
- **Manually closing sub-issues that have "Fixes #N" in PR description**
- **Closing sub-issues without verifying PR merge via GitHub API**

**See `git-workflow` skill `--task cleanup` for the complete post-merge verification workflow, sub-issue closure, and parent issue closure.**

## Critical Violation: Scope Creep — NEVER Do Things Outside the Spec

**⚠️ Implementing changes not explicitly called for in the spec is a CRITICAL GUIDELINE VIOLATION.**

The spec defines EXACTLY what to implement. Nothing more. Nothing less.

**🚫 FORBIDDEN:**

- Adding "helper" functions not requested
- Improving "nearby" code while you're there
- Refactoring things adjacent to the change
- Adding tests for unrequested functionality
- Modifying related files "just to be safe"
- Fixing "similar issues" in the same area
- Any change not explicitly stated in the issue/PR description

**If you think something ELSE should be changed:**

1. STOP — do not implement it
1. Comment on the issue noting the additional concern
1. Wait for explicit approval before implementing anything outside the spec

**When in doubt: ASK, don't assume.**

______________________________________________________________________

## Critical Violation: Spec Without Investigation

**⚠️ Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**

- Creating specs from vague requirements without exploration
- Skipping codebase analysis before planning
- Finalizing specs before investigating edge cases
- Proceeding without success criteria defined
- Running test code against production systems during investigation

**See `brainstorming` skill for investigation requirements and completion criteria.**

______________________________________________________________________

## Critical Violation: Implementing Stale or Superseded Specs

**⚠️ Implementing a stale or superseded spec without revision is a CRITICAL GUIDELINE VIOLATION.**

**See `github-issue-creation` skill `--task pre-creation` for the complete superseded/stale spec check procedure.**

### If Superseding Issue Exists

- SILENTLY HALT and report the conflict to the issue
- Do NOT proceed with the superseded spec
- Wait for user direction

### If Staleness Detected

**🚫 FORBIDDEN:**

- Implementing a stale spec as-is
- Assuming "the spec is still valid" without verification
- Skipping revision to "save time"

**✅ REQUIRED:**

- REVISE the spec to reflect current reality
- Report the revision via comment on the issue
- HALT — wait for user approval before proceeding
- Never implement a stale spec without revision

______________________________________________________________________

## Auditor Skills Enforcement

**⚠️ MANDATORY AUDIT: Run `spec-auditor` orchestrator when auditing specs. NO SKIPPING.**

**Trigger words that require the auditor:** "audit this spec", "review this issue", "revisit this task", "check this [SPEC]", "validate the spec", "audit the issue", or any request involving spec quality or structure.

**See `spec-auditor` skill for the complete orchestration model, baseline subtasks, conditional subtasks, and invocation commands.**

### Enforcement Flow

| Trigger | Action |
|---------|--------|
| Spec created | REQUIRED: Invoke `spec-auditor --issue N` |
| "Audit/review/revisit this spec" | REQUIRED: Invoke `spec-auditor --issue N` |
| Before implementation approval | REQUIRED: Verify spec-auditor found no critical issues |
| Guideline change proposed | Optional: `/skill guideline-auditor` |
| Post-implementation | Optional: Re-run spec-auditor to verify no new issues |

______________________________________________________________________

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.**

PRs require the developer to say one of these EXACT phrases: "create a PR", "make a PR", "push and create PR", "let's get a PR up".

**🚫 FORBIDDEN:**

- Creating a PR after "approved" or "go" — these authorize implementation ONLY
- Creating a PR after completing implementation — completion does NOT authorize PR creation
- Asking "Ready for a PR?" or "Should I create a PR?" — just STOP and report completion
- **Pushing branch to remote without "create a PR" instruction** — pushing is part of PR creation, NOT implementation

**See `pr-creation-workflow` skill for the full PR timing workflow including authorization boundary, developer testing, and HALT after PR creation.**

______________________________________________________________________

## Critical Violation: Bug Discovery Does NOT Authorize Bug Fixing

**⚠️ Finding a bug during analysis or any other activity does NOT authorize fixing it. This is a systemic behavioral violation, not a one-off mistake.**

### 🚫 FORBIDDEN

- Editing source code after discovering a bug — even if the fix seems trivial
- Creating branches for bug fixes without an approved spec
- Treating bug discovery as implicit authorization to modify code
- Implementing "quick fixes" or "obvious corrections" discovered during other work
- Starting implementation after reporting a bug (reporting ≠ authorization)
- Conflating bug reporting (always appropriate) with bug fixing (requires spec + auth)

### ✅ REQUIRED — Bug Discovery Protocol

1. **STOP all code changes immediately** upon discovering a bug during unrelated work
2. **Report the bug** — create a GitHub/GitBucket issue documenting the bug
3. **HALT** — wait for explicit `approved` or `go` before any code changes
4. **If the bug blocks current work**: document the blocker, report it, and HALT — do not fix it
5. **Self-correction**: If you catch yourself editing code without a spec, immediately `git checkout` the affected files and HALT

### Bug Discovery Authorization Matrix

| Action | Requires Spec? | Requires Auth? | Permitted Without Auth? |
|--------|---------------|----------------|--------------------------|
| Create bug report issue | NO | NO | ✅ YES — always permitted |
| Analyze bug (read-only) | NO | NO | ✅ YES — read-only only |
| Edit source code to fix bug | ✅ YES | ✅ YES | 🚫 NO — NEVER |
| Create branch for bug fix | ✅ YES | ✅ YES | 🚫 NO — NEVER |
| Commit bug fix code | ✅ YES | ✅ YES | 🚫 NO — NEVER |
| Create PR for bug fix | ✅ YES | ✅ YES | 🚫 NO — NEVER |

### Self-Correction Protocol

When the agent catches itself about to edit code without an approved spec:

1. **STOP** — do not proceed with the edit
2. **REVERT** — `git checkout -- <affected-files>` to undo any unauthorized changes
3. **REPORT** — document what happened as a factual observation
4. **HALT** — wait for explicit authorization before proceeding

### Why This Matters

| Scenario | Consequence |
|----------|-------------|
| Fix bug without spec | Unauthorized code changes pollute branch |
| "Quick fix" during other work | Scope creep, introduces new bugs |
| Treat reporting as authorization | Wastes human time reverting changes |
| Skip spec for "obvious" fixes | No documentation, no review, no traceability |
| Continue after bug discovery | Branch contamination, lost work |

**See `approval-gate` skill for the complete discovery protocol and authorization boundaries, including the analysis → implementation authorization decision table.**

______________________________________________________________________

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues BEFORE the PR is merged is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**

- Closing issues immediately after implementation
- Closing issues when PR is created but not merged
- Closing parent issues while child issues remain open
- Closing issues without explicit "merge confirmed" from human
- Closing issues based on `git pull` fast-forward alone (MUST use GitHub API)

**See `git-workflow` skill `--task cleanup` for complete post-merge verification.**

______________________________________________________________________

## Critical Violation: Skipping PR for Documentation/Guideline Changes

**⚠️ Documentation and guideline changes are NOT exempt from the PR workflow.**

**🚫 FORBIDDEN:**

- Treating documentation changes as "minor" and closing issues directly
- Skipping review-prep for `.md` file changes
- Closing issues without PR when guidelines, docs, or configs were modified
- Assuming "no code changes" allows skipping PR workflow

**✅ REQUIRED:**

- **ALL file modifications** (code, docs, guidelines, configs) require full PR workflow
- Branch-first rule applies to ALL file types
- review-prep is MANDATORY before any issue closure
- PR merge verification is required before closing ANY issue

| File Type | PR Required? | Reason |
|-----------|--------------|--------|
| Code (`.py`, `.java`, etc.) | ✅ YES | Code changes |
| Guidelines (`.opencode/`) | ✅ YES | Changes to rules |
| Documentation (`docs/`, `*.md`) | ✅ YES | Changes to docs |
| Config (`*.toml`, `*.yaml`) | ✅ YES | Config changes |
| **NO files modified** | ❌ NO | Already implemented |

**The only exception is when ZERO files were modified.**

______________________________________________________________________

## Critical Violation: Parent/Child Issue Closure

**⚠️ Closing a parent issue while child issues remain open is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**

- Closing a parent `[SPEC]` issue when ANY child `[Task]` issues are still open
- Closing a parent after PR merge if other child tasks are incomplete
- Assuming "the PR covers everything" when sub-issues exist

**✅ REQUIRED:**

- Only close the child issue that corresponds to the merged PR
- Parent issue remains open until ALL child issues are closed
- After closing a child: check if other children remain open
- If all children are closed, then (and only then) close the parent

**See `git-workflow` skill `--task cleanup` for the complete parent/child closure workflow and sub-issue double-check procedure.**

______________________________________________________________________

## Critical Violation: Deleting Branches/Stashes Improperly

**⚠️ Improper branch deletion is a CRITICAL GUIDELINE VIOLATION.**

**MERGED branches must be deleted IMMEDIATELY after merge confirmation.**

**🚫 FORBIDDEN:**

- `git branch -D <branch>` on unmerged branches without explicit request
- `git stash drop` without explicit request
- Preserving merged branches "just in case"
- Asking "should I delete this merged branch?" — just delete it
- Deleting `main` or other protected branches

**✅ REQUIRED:**

- **MERGED branches**: Delete IMMEDIATELY after merge confirmation — no asking, no waiting
- **UNMERGED branches with work**: Preserve until explicitly asked to delete
- **Stashes**: Preserve until explicitly asked to delete

| Branch Status | Action |
|---------------|--------|
| Merged PR | **DELETE IMMEDIATELY** — no confirmation needed |
| Unmerged with commits | **PRESERVE** — wait for explicit delete request |
| Stashes | **PRESERVE** — wait for explicit delete request |
| `main` branch | **NEVER DELETE** |

______________________________________________________________________

## Critical: Engineering Mindset Required

**⚠️ All work must be approached with proper engineering discipline.**

See `.opencode/guidelines/085-engineering-approach.md` for complete requirements.

### Core Engineering Principles

1. **Understand Before Solving** — Read all relevant code before proposing changes
2. **Design Before Implementing** — Document approach and obtain approval before coding
3. **Verify Before Declaring Complete** — Run tests, check edge cases, validate success criteria
4. **Communicate Changes** — Post comments when changes occur (NOT when creating issues)

### No Feature Creep

- Implement ONLY what is in the approved spec
- No additions, enhancements, or "improvements" beyond scope
- No refactoring unless explicitly requested
- File separate issues for unrelated fixes discovered during work

### No Unapproved Work

- Never start implementation without explicit authorization
- "Should I do X?" is a question, not authorization
- Wait for clear "approved" or "go" before starting
- If unclear, ask — do not assume

______________________________________________________________________

**Search guidelines:** Use `srclight_search_symbols` or `grep` to find relevant guidelines.