---
name: receiving-code-review
description: Use when receiving code review feedback on a PR, or when addressing review comments. Triggers on: code review, PR feedback, review comment, address feedback, fix review, respond to review.
type: technique
license: MIT
compatibility: opencode
---

# Skill: receiving-code-review

## Overview

Workflow for responding to code review feedback on pull requests. Ensures all reviewer comments are addressed systematically, changes are minimal and targeted, and no scope creep occurs during review response. Adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `address` | Address all review comments | ~350 |
| `respond` | Reply to review comments | ~250 |

## Invocation

- `/skill receiving-code-review` — Overview only
- `/skill receiving-code-review --task address` — Address review feedback
- `/skill receiving-code-review --task respond` — Reply to comments

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when PR receives review comments, user says "address review" or "fix review feedback", or agent detects review comments on PR. NOT automatic — requires user instruction.
2. **Scoping discipline:** Address ONLY what the reviewer requested. No "while I'm here" changes. No refactoring beyond what was asked. No new features added during review.
3. **Exit conditions:** Review response is COMPLETE when all reviewer comments addressed, all replies posted, tests still pass, and branch pushed with changes.

## Anti-Patterns

### 🚫 Scope Creep During Review

```python
# ❌ WRONG: Refactoring while addressing review
# Reviewer asked: "Rename this variable"
# Agent also: Refactored the entire function, changed return type, added logging
```

### ✅ Targeted Review Response

```python
# ✅ CORRECT: Address only what was requested
# Reviewer asked: "Rename this variable"
# Agent: Renamed the variable, nothing else
```

## Integration with Existing Workflow

### Dispatch Order

```
PR review received → receiving-code-review (address) → push changes → (reviewer re-reviews)
```

### Git-Workflow Integration

- Address review comments on existing branch
- Push additional commits (do NOT squash review fixes)
- PR is updated automatically on push

## Cross-References

- Related skills: `requesting-code-review` (requesting review), `git-workflow` (branch management)
- Related guidelines: `050-scope-autonomy.md` (no scope creep), `060-tool-usage.md` (commands)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable