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

☑ **Squash Verification**
- Run: `git log origin/main..HEAD --oneline`
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

## Quick Start

Use `/skill pr-creation-workflow --task overview` for complete workflow.