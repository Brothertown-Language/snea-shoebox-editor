---
name: requesting-code-review
description: Use when preparing a PR for code review, or when reviewer context and documentation are needed. Triggers on: request review, code review, review request, ready for review, review preparation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: requesting-code-review

## Overview

Workflow for preparing and requesting code reviews. This skill ensures PR descriptions have proper context, reviewers can understand changes quickly, and review requests are targeted and informative. It is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow.

**Source Attribution:** This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are a Review Requester. Your focus is ensuring reviewers have everything they need for efficient review.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `prepare` | Prepare PR for review | ~600 |
| `request` | Submit review request | ~400 |

## Invocation

- `/skill requesting-code-review` - Overview only
- `/skill requesting-code-review --task prepare` - Prepare PR for review
- `/skill requesting-code-review --task request` - Submit review request

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when:
   - User says "request review" or "ready for review"
   - PR is created and ready for review
   - Agent detects need for review
   - NOT automatic — requires user instruction

2. **Review preparation:**
   - PR must have clear description
   - Changes must be well-documented
   - Reviewers identified if necessary
   - All checks passing

3. **Exit conditions:** Review request is COMPLETE when:
   - PR description is comprehensive
   - Review request submitted
   - HALT and wait for review

## Prepare Review Workflow

### Step 1: Verify PR Description

PR description must include:

```markdown
## Summary

[1-3 sentence summary of changes]

## Changes

- [Change 1]
- [Change 2]
- [Change N]

## Testing

- [How changes were tested]
- [Test commands run]

## Related Issues

Fixes #N, #M, #P
```

### Step 2: Verify PR Readiness

- [ ] All checks pass (lint, test, typecheck)
- [ ] No TODO/FIXME comments remaining
- [ ] No debug prints or temporary code
- [ ] Branch is up to date with base
- [ ] Squash is appropriate (or not needed)

### Step 3: Identify Reviewers

- Check CODEOWNERS if available
- Consider who is familiar with the changed code
- Consider expertise needed for the change type
- Minimize review scope — targeted reviews

### Step 4: Prepare Context

For each reviewer, ensure:

- PR title clearly describes the change
- Description explains WHY (not just what)
- Related issues are linked
- Complex changes have code comments
- Breaking changes are highlighted

## Review Request Workflow

### Submit Review Request

1. **Post review request comment on PR:**

```markdown
## Review Request

**Type:** Feature / Bug Fix / Refactor / Documentation
**Scope:** [Brief description of affected area]
**Complexity:** Low / Medium / High

**Key Changes:**
- [Change 1]
- [Change 2]

**Testing:**
- [Test commands]

**Questions for Reviewer:**
- [Any specific questions]

---
🤖 📝 Review requested by OpenCode (ollama-cloud/glm-5)
```

2. **Update PR labels if available:**
   - Add `review-requested` label
   - Remove `work-in-progress` label if present

3. **Notify reviewer:**
   - The PR creator or user should notify the reviewer
   - Agent should NOT tag reviewers directly

## PR Description Template

```markdown
## Summary

[What this PR accomplishes and why it's needed]

## Changes

### [Component/Module Name]
- **[Change type]:** [Description of change]

## Testing

```bash
# Commands run to verify
uv run pytest test/test_module.py -v
uv run ruff check --fix src/
uv run pyright src/
```

## Related Issues

Fixes #[issue-number]

---
Co-authored with AI: OpenCode (ollama-cloud/glm-5)
```

## Anti-Patterns

### 🚫 Poor Review Request

```markdown
# ❌ WRONG: Vague review request
"Please review this PR"
# No context on what changed or why
# No testing information
# No related issues
```

### ✅ Good Review Request

```markdown
# ✅ CORRECT: Comprehensive review request
## Summary
Added OAuth2 token refresh to prevent unexpected logouts after 7 days.

## Changes
- Added `refresh_expired_token()` method to `OAuthClient`
- Added fallback authentication flow using stored credentials
- Added tests for token expiry scenarios

## Testing
- `uv run pytest test/test_oauth.py::test_token_refresh -v`
- `uv run ruff check --fix src/`
```

## Integration with Existing Workflow

### Dispatch Order

```
finishing-a-development-branch → PR created by user → requesting-code-review (prepare) → (reviewer reviews)
```

### GitBucket Platform Adaptations

- Use GitBucket PR API for review requests
- Use GitBucket labels for review status
- Post review context comments on PR

### PR Creation Timing

- This skill is invoked AFTER PR creation
- PR creation requires explicit "create a PR" instruction
- This skill does NOT create PRs — only prepares them for review

## Cross-References

- Related skills: `receiving-code-review` (responding to review), `git-workflow` (PR creation), `pr-creation-workflow` (PR timing)
- Related guidelines: `080-code-standards.md` (AI attribution), `060-tool-usage.md` (commands)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow ensures review requests are comprehensive and targeted.

**Key adaptations for OpenCode:**
- Integration with existing git-workflow skill for branch management
- GitBucket platform support via MCP tools
- Dispatch table integration for contextual invocation
- PR description template with AI attribution