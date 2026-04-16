# Task: request

## Purpose

Submit a review request after the PR has been prepared with proper context and description.

## Operating Protocol

1. Invoked by: `/skill requesting-code-review --task request`
2. When to use: After `--task prepare` is complete and PR is ready
3. Exit criteria: Review request submitted, HALT and wait for review

## Review Request Workflow

### Step 1: Submit Review Request Comment

Post a review request comment on the PR:

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
🤖 <AgentName> (<ModelID>) ➕ created
```

### Step 2: Update PR Labels

- Add `review-requested` label if available
- Remove `work-in-progress` label if present

### Step 3: Notify Reviewer

- The PR creator or user should notify the reviewer
- Agent should NOT tag reviewers directly

## Important Notes

- This skill is invoked AFTER PR creation
- PR creation requires explicit "create a PR" instruction
- This skill does NOT create PRs — only prepares them for review
- After submitting review request, HALT and wait for review feedback

## Context Required

- Related skills: `requesting-code-review` (parent skill)
- Related tasks: `prepare`