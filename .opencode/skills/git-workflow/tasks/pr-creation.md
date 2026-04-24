# Task: pr-creation

## Purpose

Create pull request after explicit user instruction. Squash commits to single commit, push branch, create PR targeting `dev` branch.

## Operating Protocol

1. **User-initiated only:** "create a PR", "make a PR", "push and create PR"
2. **Squash to single commit:** ALL implementation commits combined into ONE clean commit
3. **Target `dev` branch:** Feature PRs merge to `dev` (not `main`)
4. **HALT after PR creation:** Wait for human to merge

## Entry Criteria

- User says "create a PR", "make a PR", "push and create PR", or similar
- Implementation is complete
- Developer has reviewed changes via compare URL

## Exit Criteria

- PR created via GitHub API or GitBucket CLI
- PR URL extracted from API response and reported in chat
- Agent HALTs waiting for human merge

## Procedure

### Step 0-1: Enforcement Gate and PR State Check

**Route to:** `pr-creation/enforcement-gate`

Verifies submodule dependencies, explicit PR instruction, branch push status, existing PR state, and merge conflict detection.

### Step 2-4: Changelog, Squash, Rebase, Push

**Route to:** `pr-creation/squash-push`

Generates changelog (or skips with `[skip changelog]`), squashes commits, rebases on current dev, and pushes to remote with verification.

### Step 5-7: Collect Sub-Issues, Create PR, Extract URL

**Route to:** `pr-creation/create-pr`

Collects sub-issues from parent spec, creates PR with executive summary body, extracts URL from API response, reports in chat and HALTs.

## Sub-Task Files

| Sub-Task | Purpose | Words |
| -- | -- | -- |
| `pr-creation/enforcement-gate` | Verify pre-conditions, submodule deps, PR instruction, conflict detection | ≈650 |
| `pr-creation/squash-push` | Changelog, squash, rebase, push with live verification | ≈600 |
| `pr-creation/create-pr` | Sub-issue collection, PR creation, URL extraction, body format | ≈550 |

## Co-Author Trailers (MANDATORY)

Every squash commit MUST include:
1. AI Trailer: `Co-authored-by: <AgentName> (<ModelId>) <noreply@example.com>`
2. Human Trailer: `Co-authored-by: <dev.name> <dev.email>`

## Review Phase (Mandatory)

After implementation and BEFORE PR creation:

1. Agent pushes feature branch to remote
2. Agent reports compare URL in CHAT ONLY (NEVER to GitHub Issues)
3. Developer reviews changes via GitHub diff viewer
4. Developer decides whether to create PR or request changes
5. If satisfied, developer says "create a PR"
6. Agent creates PR (squash, push, create PR, HALT)

## Context Required

- Related skills: `review-prep`, `conflict-resolution`
- Related tasks: `pr-creation/enforcement-gate`, `pr-creation/squash-push`, `pr-creation/create-pr`