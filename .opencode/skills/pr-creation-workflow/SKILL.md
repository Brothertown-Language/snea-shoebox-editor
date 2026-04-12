---
name: pr-creation-workflow
description: Use when asking about when to create a PR or whether PR creation is authorized. Triggers on: create PR, make PR, pull request, PR timing, when to PR, PR authorized.
type: technique
license: MIT
compatibility: opencode
---

# PR Creation Workflow Skill

## Overview

PR creation is a DISTINCT phase requiring EXPLICIT instruction — it is NOT automatic after implementation. "Approved" and "go" authorize implementation ONLY, not PR creation. The developer MUST explicitly say "create a PR" or equivalent.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-pr-checklist` | Mandatory checks before PR creation (squash, changelog, branch state) | ~500 |
| `sub-issue-collection` | Fetch and include sub-issues in PR body for autoclose | ~300 |

## Invocation

- `/skill pr-creation-workflow --task pre-pr-checklist` - Run mandatory pre-PR checks
- `/skill pr-creation-workflow --task sub-issue-collection` - Collect sub-issues for PR body
- `/skill pr-creation-workflow` - Overview only

## Authorization Boundary (CRITICAL)

### What Authorizes Implementation (BUT NOT PR)

| Authorization | Meaning | PR Authorized? |
|---------------|---------|----------------|
| `approved` | Begin implementation | ❌ NO |
| `go` | Proceed to next task | ❌ NO |
| `approved: 1` | Implement Phase 1 | ❌ NO |
| `proceed` | Continue with plan | ❌ NO |

### What Authorizes PR Creation

"create a PR", "make a PR", "push and create PR", "let's get a PR up", "create a pull request", "PR" (bare), "PR #NNN"

## Operating Protocol

1. **After implementation completes:** Report completion, HALT. Do NOT ask about PRs.
2. **When developer says "create a PR":** Run pre-PR checklist, squash, push, create PR, report URL, HALT.
3. **Never merge PRs:** Merging is HUMAN-ONLY operation.
4. **Never create PR without explicit instruction:** "approved" does NOT authorize PR creation.

## Pre-PR Creation Checklist (MANDATORY)

- Squash verification: EXACTLY ONE commit on branch
- Changelog generated (all platforms, no exceptions)
- Branch state: working tree clean
- Push verification: no unpushed commits
- Co-author trailers: both AI and human trailers included
- Issue references: `Fixes #<parent>` for single-task, `Fixes #<parent>` AND `Fixes #<child>` for each sub-issue

## After PR Creation

1. Report URL in chat (NEVER to GitHub Issues)
2. HALT — wait for human to merge
3. Never merge PRs — HUMAN-ONLY operation
4. Delete merged branches AFTER merge confirmation

## Prohibitions

- Create PRs autonomously or after "approved"/"go"
- Ask "Ready for a PR?" or "Should I create a PR?"
- Merge PRs
- Submit PR without squashing to single commit
- Close issues before PR merge

## Cross-References

| Guideline | Content |
|-----------|---------|
| `113-git-pr-workflow.md` | Full PR workflow |
| `000-critical-rules.md` | Critical violation: PRs without instruction |
| `020-go-prohibitions.md` | GO does not authorize PR |
| `010-approval-gate.md` | PR timing requirements |
| `git-workflow` skill | Post-merge workflow including issue closure |