---
name: requesting-code-review
description: Use when preparing a PR for code review, or when reviewer context and documentation are needed. Triggers on: request review, code review, review request, ready for review, review preparation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: requesting-code-review

## Overview

Workflow for preparing and requesting code reviews. Ensures PR descriptions have proper context, reviewers can understand changes quickly, and review requests are targeted and informative. Adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `prepare` | Prepare PR for review | ~400 |
| `request` | Submit review request | ~250 |

## Invocation

- `/skill requesting-code-review` — Overview only
- `/skill requesting-code-review --task prepare` — Prepare PR for review
- `/skill requesting-code-review --task request` — Submit review request

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when user says "request review" or "ready for review", or PR is created and ready for review. NOT automatic — requires user instruction.
2. **Review preparation:** PR must have clear description, all checks passing, well-documented changes, and identified reviewers before requesting review.
3. **Exit conditions:** Review request is COMPLETE when PR description is comprehensive, review request submitted, and agent HALTs to wait for review.
4. **Scoping:** Address ONLY what reviewers request. No "while I'm here" changes during review response.

## Anti-Patterns

### 🚫 Poor Review Request

"Please review this PR" — no context on what changed, why, or how to test.

### ✅ Good Review Request

Includes type, scope, complexity, key changes, testing commands, and specific questions for reviewers.

## Integration with Existing Workflow

### Dispatch Order

```
finishing-a-development-branch → PR created by user → requesting-code-review (prepare) → (reviewer reviews)
```

### PR Creation Timing

- This skill is invoked AFTER PR creation
- PR creation requires explicit "create a PR" instruction
- This skill does NOT create PRs — only prepares them for review

## Cross-References

- Related skills: `receiving-code-review` (responding to review), `git-workflow` (PR creation), `pr-creation-workflow` (PR timing)
- Related guidelines: `080-code-standards.md` (AI attribution), `060-tool-usage.md` (commands)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable