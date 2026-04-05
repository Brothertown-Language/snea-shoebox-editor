---
name: pr-creation-workflow
description: Handles PR creation timing requirements. Defines when PRs can be created, what authorizes PR creation, and the mandatory HALT after PR creation.
license: MIT
compatibility: opencode
---

# PR Creation Workflow

Defines when PRs can be created, what authorizes PR creation, and the mandatory HALT after PR creation.

## Core Principle

**PR creation is a DISTINCT phase requiring EXPLICIT instruction — it is NOT automatic after implementation.**

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at this workflow trigger:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| User says "create a PR" | `/skill git-workflow --task pr-creation` | Squash to single commit, push, create PR, HALT |

**Note:** PR creation timing is part of `git-workflow` skill. This skill (`pr-creation-workflow`) defines the RULES, not the invocation.

## Available Tasks

| Task | Description |
|------|-------------|
| `overview` | Complete PR creation workflow with authorization boundary |

## Authorization Boundary (CRITICAL)

### What Authorizes Implementation (BUT NOT PR)

| Authorization | Meaning | PR Authorized? |
|---------------|---------|----------------|
| `approved` | Begin implementation | ❌ NO |
| `go` | Proceed to next task | ❌ NO |
| `approved: 1` | Implement Phase 1 | ❌ NO |
| `approved: 2.3` | Implement Phase 2, Step 3 | ❌ NO |
| `proceed` | Continue with plan | ❌ NO |

### What Authorizes PR Creation

| Authorization | Valid? |
|--------------|--------|
| "create a PR" | ✅ YES |
| "pr" | ✅ YES |
| "make a PR" | ✅ YES |
| "push and create PR" | ✅ YES |
| "let's get a PR up" | ✅ YES |
| "create a pull request" | ✅ YES |

## After Implementation Completes

1. ✅ Report completion (concise summary)
1. ✅ HALT — do NOT ask about PRs
1. ✅ WAIT for explicit "create a PR" instruction
1. ❌ Do NOT ask "Ready for a PR?" or "Should I create a PR?"
1. ❌ Do NOT create PR automatically

## Pre-PR Creation Checklist (MANDATORY)

Before creating ANY PR:

☑ **Review Workflow Verification (MANDATORY)**
- Verify: Branch is pushed to remote (prerequisite for compare URL)
- Verify: Compare URL was posted to chat (NOT issue)
- Verify: Executive summary was posted to issue AND chat
- **If NOT completed:** HALT - review workflow was skipped (CRITICAL VIOLATION)

☑ **Squash Verification**
- Run: `git log origin/dev..HEAD --oneline`
- Verify: EXACTLY ONE commit on branch

☑ **Branch State**
- Run: `git status`
- Verify: Working tree clean

☑ **Push Verification**
- Run: `git log origin/<branch>..HEAD --oneline`
- Verify: No unpushed commits

☑ **Co-Author Trailers**
- Verify commit includes BOTH trailers:
  - AI: `Co-authored-by: <AI-Name> (<model-id>) <ai-email>`
  - Human: `Co-authored-by: <Human-Name> <human-email>`

☑ **Merged PR Check**
- Run: `gh pr list --head <branch> --state merged --json number`
- Verify: No merged PR exists on this branch
- If merged PR exists: Create new branch before PR creation

☑ **Changelog Skill Availability**
- Verify: changelog-generator skill is available for invocation

**⚠️ CRITICAL: Skipping review workflow verification is a ZERO TOLERANCE violation.**

## Sub-Issue Autoclose with Changelog

### Single-Task Spec PR Body

```markdown
## Summary

<Executive summary from changelog skill>

## Changes

<Changelog content from skill invocation>

Fixes #<parent>
```

### Multi-Task Spec PR Body

```markdown
## Summary

<Executive summary from changelog skill>

## Changes

<Changelog content from skill invocation>

Fixes #<parent>
Fixes #<child1>
Fixes #<child2>
```

## Edge Case Handling

### Merged PR on Branch

**Detection:**
```bash
gh pr list --head <branch> --state merged --json number,url,mergedAt
```

**If merged PR exists:**
1. Report: "Branch has merged PR. Creating new PR against current dev."
2. Fetch and checkout dev: `git fetch origin && git checkout dev && git pull origin dev`
3. Create new branch: `git checkout -b <new-branch-name>`
4. Cherry-pick or reapply changes
5. Continue with PR creation workflow

### No Changelog Entries

**If changelog skill returns empty:**

Use squash commit message as PR body:
```markdown
## Changes


Fixes #
```

## Quick Start

Use `/skill pr-creation-workflow --task overview` for complete workflow.