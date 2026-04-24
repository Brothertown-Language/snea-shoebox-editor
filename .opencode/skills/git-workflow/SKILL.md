---
name: git-workflow
description: Use when creating a branch, committing changes, pushing work, or creating a PR. Also use when git rebase/merge produces conflicts — invoke conflict-resolution skill for classification. Also use when user says "check pr" or "check prs" to trigger PR state verification and cleanup if merged. Also use when user says "release PR", "promote to main", or "dev to main" — invokes release-promotion task for dev → main promotion. Triggers on: branch, commit, push, PR, pull request, pre-work, review-prep, feature branch, dev branch, squash, conflict, merge conflict, rebase conflict, check pr, check prs, check pull request, check pull requests, release PR, release pr, promote to main, dev to main, release promotion.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: git-workflow

## Overview

Git Workflow Enforcer ensuring all git operations follow the three-branch model: feature → dev → main. AI commits are blocked on protected branches. All feature branches merge to `dev` via PR. Squashing is ONLY at PR creation time, not during implementation.

## Persona

You are a Git Workflow Enforcer. Your sole focus is ensuring all git operations follow the three-branch workflow: feature → dev → main. AI commits are blocked on protected branches. Squashing is ONLY for PR creation, not during feature branch development.

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `pre-work` | Verify authorization, create worktree | ≈420 |
| `implementation` | Handle WIP commits during implementation | ≈400 |
| `review-prep` | Push branch, generate compare URL for review (2 subtasks) | ≈390 |
| `pr-creation` | Squash, push, create PR via GitHub MCP (3 subtasks) | ≈385 |
| `rebase-pending` | Rebase other open PRs after merge, classify conflicts | 1,666 |
| `cleanup` | Verify merge, close issues, delete branches (3 subtasks) | ≈950 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ≈200 |
| `release-promotion` | Automate dev → main promotion and tagging (submodule and non-submodule repos) | ≈500 |
| `check-pr` | List all PRs (open + merged); if merged found, activate cleanup | ≈50 |
| `provenance` | Create provenance issues/PRs in submodule repos after push/promotion (3 subtasks) | ≈460 |
| `pair-pre-work` | Detect pair mode, WIP-commit switch instead of worktree | ≈400 |
| `pair-commit` | Commit with [pair-mode] co-author trailers, issue association | ≈350 |
| `pair-pr-creation` | Squash + PR with [pair-mode] trailers targeting dev | ≈300 |
| `pair-cleanup` | Branch deletion after merge, stash cleanup | ≈350 |
| `pair-mode-resume` | Detect and report on pair-* branch at session start | ≈300 |

## Routing: Feature PR vs Release PR

| Request Type | Target Skill | Branch Pattern |
|---|---|---|
| Feature PR (feature/* → dev) | `pr-creation-workflow` | Feature branch to `dev` |
| Release PR (dev → main) | `git-workflow --task release-promotion` | `dev` to `main` |

## Invocation

- `/skill git-workflow --task pre-work` - BEFORE implementation starts (MUST invoke after approval-gate passes)
- `/skill git-workflow --task implementation` - During implementation work
- `/skill git-workflow --task review-prep` - AFTER implementation done (MUST invoke, no decision point)
- `/skill git-workflow --task pr-creation` - When user says "create a PR"
- `/skill git-workflow --task rebase-pending` - After PR merge, before cleanup
- `/skill git-workflow --task cleanup` - After PR merge confirmed
- `/skill git-workflow --task release-promotion` - When promoting dev → main (submodule repos: lock SHAs, promote each submodule; non-submodule repos: merge dev → main, tag, push, create release), or explicit "promote/push submodule" instruction
- `/skill git-workflow --task check-pr` - When user says "check pr" / "check prs" / "check pull request(s)"
- `/skill git-workflow --task provenance` - Create provenance tracking in submodule repos
- `/skill git-workflow --task completion` - Invoke when workflow halts at any point
- `/skill git-workflow --task pair-pre-work` - Detect pair mode from branch prefix, WIP-commit switch
- `/skill git-workflow --task pair-commit` - Commit with [pair-mode] co-author trailers
- `/skill git-workflow --task pair-pr-creation` - Squash + create PR with [pair-mode] trailers
- `/skill git-workflow --task pair-cleanup` - Cleanup after pair-mode PR merge
- `/skill git-workflow --task pair-mode-resume` - Resume pair mode session on existing pair-* branch
- `/skill git-workflow` - Overview only

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (status report, URL, verification gates) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** pre-work is invoked after approval-gate passes; review-prep is invoked after implementation completes — the agent MUST invoke both at the appropriate time, never skip them, and never prompt for invocation.
2. **Phase sequence:** Pre-work (Phase 1) → Implementation (user-driven) → review-prep (Phase 3, MANDATORY, MUST invoke after implementation) → pr-creation (explicit instruction only) → cleanup (after merge).
3. **review-prep is mandatory:** Skipping it after implementation is a CRITICAL GUIDELINE VIOLATION. The agent MUST invoke `/skill git-workflow --task review-prep` after implementation completes.
4. **PR requires explicit instruction OR pipeline scope:** "approved"/"go" authorizes implementation ONLY — not PR creation. **Exception:** When `authorization_scope >= for_pr` or `pr_only`, the user's pipeline instruction authorizes PR creation as part of the scope. When `pr_strategy == none` or `halt_at < pr_created`, do NOT create PR regardless of explicit instruction.
5. **Chat output order:** Executive summary FIRST, URL LAST. Never put URL before summary.
6. **Compare URLs use `dev` as base:** Feature branches target `dev`, not `main`.
7. **Squash to single commit before any PR:** No exceptions.
8. **Never merge PRs:** Human-only operation.
9. **Post-merge cleanup is MANDATORY:** Skipping `git-workflow --task cleanup` after confirming PR merge is a CRITICAL GUIDELINE VIOLATION. The cleanup task is the sole mechanism for branch deletion, issue closure, and dev sync. Every merged PR MUST be followed by `cleanup`.

### PR Body Keyword Discipline

**`Fixes`/`Closes` auto-close issues on merge — bypassing verification gates.** For plans with sub-issues, use `Implements` instead. See `review-prep.md` → "PR Body Keyword Discipline" for the complete rules.

## Role in Orchestration Architecture

Git-workflow handles **pure git operations only**. Implementation logic is handled by `divide-and-conquer` orchestration layer.

**What git-workflow DOES:** Git operations (worktree, branch, commit, push), git state checks, git cleanup.
**What git-workflow DOES NOT do:** Implementation decisions, file editing, spec reading, authorization checks (handled by approval-gate + orchestration layer).

## Edge Case: Already Implemented (No Changes)

When spec investigation reveals ZERO file modifications: skip branch creation, skip PR workflow, close issue directly with verification comment. ANY file modified (including docs/guidelines) requires full PR workflow.

## Critical Workflow Sequence

```
Implementation complete
    ↓
review-prep MUST be invoked (Phase 3)
    ↓
Push branch → Generate compare URL → HALT
    ↓
(Developer reviews via GitHub diff)
    ↓
Developer says "create a PR"
    ↓
pr-creation: Squash → Push → Create PR → HALT
    ↓
(Developer merges PR)
    ↓
Developer confirms "PR merged"
    ↓
cleanup: Verify merge via API → Close issues (MANDATORY — Skipping is a CRITICAL VIOLATION)
```

## Sub-Agent Tasks

### Sub-Agent Tasks

| Task | Words |
|------|-------|
| `cleanup` (routing) | ≈950 |
| → `cleanup/verify-merge` | ≈760 |
| → `cleanup/issue-closure` | ≈710 |
| → `cleanup/branch-cleanup` | ≈680 |
| `pr-creation` (routing) | ≈385 |
| → `pr-creation/enforcement-gate` | ≈475 |
| → `pr-creation/squash-push` | ≈490 |
| → `pr-creation/create-pr` | ≈615 |
| `review-prep` (routing) | ≈390 |
| → `review-prep/push-and-cleanup` | ≈555 |
| → `review-prep/report-url` | ≈625 |
| `provenance` (routing) | ≈460 |
| → `provenance/platform-detection` | ≈415 |
| → `provenance/dev-push-provenance` | ≈540 |
| → `provenance/promotion-provenance` | ≈610 |
| `pre-work` | 1,898 |
| `release-promotion` | 1,811 |
| `rebase-pending` | 1,666 |
| `implementation` | ≈400 |
| `pair-pre-work` | ≈400 |
| `pair-commit` | ≈350 |
| `pair-pr-creation` | ≈300 |
| `pair-cleanup` | ≈350 |
| `pair-mode-resume` | ≈300 |
| `completion` | ≈200 |
| `check-pr` | ≈50 |

### Result Contracts (Sub-Agent Tasks)

#### pre-work

```yaml
status: DONE | BLOCKED
task: pre-work
worktree_path: <path>
branch_name: <str>
branch_created: bool
setup_complete: bool
tests_passing: bool
```

#### review-prep

```yaml
status: DONE
task: review-prep
branch_pushed: bool
compare_url: <url>
commits_count: <int>
worktree_handoff: bool
```

#### pr-creation

```yaml
status: DONE | BLOCKED
task: pr-creation
pr_number: <N|null>
pr_url: <url|null>
squash_performed: bool
```

#### cleanup

```yaml
status: DONE
task: cleanup
branches_deleted: [<name>]
issues_closed: [<N>]
stashes_preserved: [<name>]
sub_issues_verified: bool
```

#### provenance

```yaml
status: DONE
task: provenance
tier_used: 1 | 2 | 3
issues_created: [<N>]
prs_created: [<N>]
submodules_processed: [<name>]
```

#### release-promotion

```yaml
status: DONE | BLOCKED
task: release-promotion
tag_created: bool
tag_name: <str>
release_url: <url|null>
submodules_promoted: [<name>]
```

#### rebase-pending

```yaml
status: DONE | BLOCKED
task: rebase-pending
rebased_prs: [<N>]
conflicts_detected: [{pr: <N>, tier: 1|2|3}]
conflicts_resolved: [<N>]
```

#### pair-pre-work

```yaml
status: DONE | BLOCKED
task: pair-pre-work
pair_mode: bool
branch_name: <str>
wip_commit_created: bool
working_directory: <path>
```

#### pair-commit

```yaml
status: DONE | BLOCKED
task: pair-commit
commit_hash: <sha>
issue_referenced: <N|null>
pair_mode: true
```

#### pair-pr-creation

```yaml
status: DONE | BLOCKED
task: pair-pr-creation
pr_number: <N|null>
pr_url: <url|null>
squash_performed: bool
pair_mode: true
```

#### pair-cleanup

```yaml
status: DONE
task: pair-cleanup
branches_deleted: [<name>]
stashes_preserved: [<name>]
pr_merge_verified: bool
```

#### pair-mode-resume

```yaml
status: DONE | SKIP
task: pair-mode-resume
pair_branch: <str|null>
issue_number: <N|null>
changes_summary: <str>
uncommitted_count: <int>
unpushed_count: <int>
```

### Dispatch Context Schema

```yaml
branch_name: <str>
worktree_path: <path>
session_vars:
  github.owner: <from-session>
  github.repo: <from-session>
  dev.name: <from-session>
  dev.email: <from-session>
  worktree.path: <from-session>
```

## Sub-Agent Spawning

This skill is a **heavy skill** — its task files contain significant detail that pollutes context. When the main agent needs git-workflow execution, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (≈570 words)
2. Main agent identifies the needed task (e.g., `pre-work`, `cleanup`)
3. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use git-workflow skill --task <task-name> with context: <session-context>")`
4. Sub-agent loads: this SKILL.md + relevant task file + required guidelines
5. Sub-agent executes task in isolation, returns structured result
6. Main agent receives result summary — no full git-workflow content in main context

**Sub-agent context parameters:** Pass `<worktree.path>`, `branch`, `<github.owner>`, `<github.repo>`, `<dev.name>`, `<dev.email>` from session init.

**⚠️ Worktree pass-through is MANDATORY:** When spawning sub-agents from a worktree context, `worktree.path` MUST be included in the dispatch prompt. Sub-agents that perform git operations without `worktree.path` will silently modify the main repo — this is a CRITICAL GUIDELINE VIOLATION (see #741).

## Live Verification Requirements

**🚫 CRITICAL: Every git-workflow task MUST verify actual git/GitHub state via tool calls before acting on claims. Do NOT trust cached values, assumed branch names, or claimed merge status without direct evidence.**

### Verification Matrix

| Verification Point | Tool Call | Expected Evidence | Applies To |
| -- | -- | -- | -- |
| **Branch state** | `git branch --show-current` | Current branch name matches expected | pre-work, implementation, rebase-pending |
| **Working tree cleanliness** | `git status --porcelain` | Empty output (no uncommitted changes) | review-prep, pr-creation |
| **Worktree location** | `git rev-parse --show-toplevel` | Returns worktree path (not main repo) | pre-work, implementation |
| **Commit/push state** | `git log dev..HEAD --oneline` | At least one commit ahead of dev | review-prep, pr-creation |
| **Tracking branch** | `git branch -vv` | `[origin/<branch>]` tracking exists | review-prep |
| **Unpushed commits** | `git diff @{u} HEAD` | Empty diff (all commits pushed) | review-prep |
| **PR merge status** | `github_pull_request_read(method=get)` | `merged_at` is not None | cleanup |
| **Sub-issue closure** | `github_issue_read(method=get_sub_issues)` | All sub-issues state=closed | cleanup |
| **File existence** | `git status --porcelain` | No uncommitted files (all committed) | pr-creation, implementation |
| **Staged state** | `git diff --staged` | Expected changes are staged | commit-prep, pr-creation |
| **Unstaged changes** | `git diff` | Empty (no unstaged changes) | pr-creation |
| **Worktree environment** | `echo $WORKTREE_PATH` | Non-empty path matching worktree dir | pre-work, implementation |
| **Stash state** | `git stash list` | Expected number of stashes (usually 0) | cleanup |

### Adversarial Verification Principles

1. **No cached trust:** Re-verify git state before every state-modifying operation (commit, push, squash, rebase)
2. **Evidence required:** Each verification point MUST produce a tool-call artifact — assertions without evidence are VERIFICATION-GAP findings
3. **Contradiction detection:** If actual state contradicts expected state, classify as a finding before proceeding

### Finding Classification

| Finding | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Branch name doesn't match expected | STRUCTURE-VIOLATION | auto-fix | Report actual branch, verify worktree context |
| Working tree dirty when should be clean | VERIFICATION-GAP | conditional | Commit or stash before proceeding |
| `merged_at` is None (no merge) | CONFLICTING | flag-for-review | HALT — do not close issues |
| Tracking branch missing | MISSING-ELEMENT | auto-fix | Push with `-u` to establish tracking |
| Unpushed commits detected | VERIFICATION-GAP | conditional | Push before generating compare URL |
| worktree.path empty/not set | STRUCTURE-VIOLATION | auto-fix | HALT — fatal error, cannot proceed safely |
| Staged changes differ from expected | CONFLICTING | flag-for-review | Verify staging matches intent before commit |
| Sub-issue closed without merged PR | VERIFICATION-GAP | flag-for-review | Investigate closure reason, may need reopen |

## Submodule Provenance

### Three-Tier Model

When a submodule is pushed or promoted from the parent repo, provenance tracking creates a traceable record in the submodule repository. The tier used depends on API availability:

| Tier | Method | When Available | Provenance Record |
| -- | -- | -- | -- |
| 1 | Issue + PR in submodule repo | Full API access | Full issue + PR with `Fixes #N` and cross-links |
| 2 | Issue only in submodule repo | API available, PR creation fails | Issue documenting the change |
| 3 | Commit message provenance | No API access | Structured commit message with parent context |

### When Each Tier Applies

| Condition | Tier |
| -- | -- |
| API responds successfully, full access | Tier 1: Create issue + PR |
| API responds but PR endpoint fails (403, 405) | Tier 2: Create issue only |
| API returns 403/404/auth error, or platform is `unknown` | Tier 3: Commit message only |

### Integration Points

| Integration | When Provenance Runs |
| -- | -- |
| `review-prep` (Step 0, Submodule Push Automation) | After each submodule is pushed to dev — provenance tracks the dev-push |
| `release-promotion` (Step 2h) | After each submodule is promoted dev → main — provenance tracks the promotion |

### Fire-and-Forget Semantics

Provenance operations are **fire-and-forget** — they never block git operations:

- All fallbacks are **silent** — no HALT, no developer intervention required
- If Tier 1 fails, automatically downgrade to Tier 2
- If Tier 2 fails, automatically downgrade to Tier 3
- The parent repo push/promotion proceeds **regardless** of provenance outcome
- Cross-reference comments on the parent issue are non-blocking — failures are logged, not raised

### Platform Detection

Before provenance tracking, each submodule's host platform is detected from its remote URL:

- `github.com` → GitHub API
- Known GitBucket host patterns → GitBucket API
- Unknown → Tier 3 (no API available)

Detection results are cached for the session to avoid redundant API calls.

## Pair Mode

### Mode Detection

Pair mode is detected from the branch name prefix:

| Branch Pattern | Mode | Working Directory |
|---|---|---|
| `pair-feature/123-xyz` | Dev-pair | Main project dir |
| `pair-spec/456-abc` | Dev-pair | Main project dir |
| `feature/789-xyz` | Autonomous | `.worktrees/` |
| `spec/789-abc` | Autonomous | `.worktrees/` |
| `dev` or `main` | None | Prompt to create/switch |

The `pair-` prefix IS the mode signal. No state files needed — branch name carries everything.

### Pair Mode vs Autonomous Mode

| Aspect | Autonomous Mode | Pair Mode |
|--------|----------------|-----------|
| Branch prefix | `feature/`, `spec/` | `pair-` |
| Working directory | `.worktrees/` | Main project dir |
| Branch switching | Worktree per branch | WIP commit + checkout |
| Worktree safety | Tier 1 mandate | Tier 2 — developer present |
| Commit trailers | Standard co-author | `[pair-mode]` tag |
| PR workflow | Same squash workflow | Same squash workflow |

### Pair Mode Branch Discipline

1. **Always use `pair-` prefix** — no exceptions
2. **Never operate in `.worktrees/`** when pair mode is active
3. **WIP commits before branch switches** — never leave uncommitted changes on a branch switch
4. **Commit trailers always include `[pair-mode]`** — distinguishes from autonomous commits
5. **PR body uses `Implements #N`** — never `Fixes` or `Closes` (avoids premature closure)

### Pair Mode Session Start

The `session_context.py` plugin detects pair mode at session start and injects context:
- Identity section (always): github.owner, github.repo, github.platform, credential status
- Pair mode resume context: branch name, related issue, diff summary
- Trigger warnings: on_main_branch, protected_branch_with_changes, uncommitted_work

### Pair Mode Task Sequence

```
Session start → pair-mode-resume detects pair-* branch
    ↓
pair-pre-work: WIP-commit switch (no worktree)
    ↓
(pair-commits as needed during work)
    ↓
pair-pr-creation: Squash → Push → Create PR
    ↓
(Developer merges PR)
    ↓
pair-cleanup: Delete branch, clean stashes
```

## Cross-References

- Related skills: `approval-gate` (authorization), `pr-creation-workflow` (PR timing), `changelog-generator` (changelog generation), `conflict-resolution` (conflict classification during rebase/merge)
- Related guidelines: `000-critical-rules.md`, `115-branch-naming.md`
- Authorization classification: See `010-approval-gate.md` §Action Authorization Classification
- Related skill tasks: `git-workflow --task pre-work` (branch creation), `git-workflow --task cleanup` (post-merge), `git-workflow --task pr-creation` (PR workflow), `git-workflow --task provenance` (submodule provenance tracking)

```yaml+symbolic
schema_version: "1.0"
last_updated: "2026-04-15T00:00:00Z"
rules:
  - id: git-workflow-provenance-001
    title: "Submodule provenance tracking after push or promotion"
    conditions:
      all:
        - "submodule_pushed == true OR submodule_promoted == true"
    actions:
      - INVOKE(git-workflow --task provenance)
    conflicts_with: []
    requires: []
    triggers: [release-promotion, review-prep]
    source: "git-workflow/SKILL.md Tasks table"
```
