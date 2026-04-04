---
name: pr-creation-workflow
description: Handles PR creation timing requirements. Defines when PRs can be created, what authorizes PR creation, and the mandatory HALT after PR creation.
license: MIT
compatibility: opencode
---

# PR Creation Workflow

Defines when PRs can be created, what authorizes PR creation, and the mandatory HALT after PR creation.

## Operating Protocol

### ⚠️ VERIFICATION STEPS (MANDATORY FIRST)

**Before ANY skill operation, verify:**

1. **Session Init Check:**
   - Has `ai_bin/session_init.py` run?
   - Store: `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL`
   - If NOT run → STOP, run session init FIRST

2. **Codebase Verification:**
   - Is codebase state current?
   - Run: `srclight_codebase_map` or `srclight_index_status`
   - Verify: No stale assumptions from previous sessions

3. **Issue Conflict Check:**
   - Query open `[SPEC]` issues for conflicts
   - Check for superseding/invalidating issues
   - If conflict found → HALT, report conflict

**Exemption Conditions:**
- This skill EXEMPT from codebase verification (timing rules)
- This skill EXEMPT from issue conflict check (PR workflow rules)

## Core Principle

**PR creation is a DISTINCT phase requiring EXPLICIT instruction — it is NOT automatic after implementation.**

## ⚠️ CRITICAL: Authorization Gate Must Be Invoked First

**BEFORE any PR workflow, verify authorization was checked:**

1. **Authorization keywords** (`approved`, `go`) trigger `/skill approval-gate --task verify-authorization`
1. **approval-gate** verifies:
   - Spec exists and is authorized
   - Sub-issues structure (multi-task specs)
   - No superseding/conflicting issues
   - Authorization scope is correct
1. **git-workflow pre-work** runs AFTER approval-gate verification
1. **PR creation** happens after explicit "create a PR" instruction

**Bypassing approval-gate verification is a CRITICAL GUIDELINE VIOLATION.**

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