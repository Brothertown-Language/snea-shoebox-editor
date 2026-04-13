# Task: prepare

## Purpose

Prepare a PR for code review by ensuring description, checks, and reviewer context are complete before requesting review.

## Operating Protocol

1. Invoked by: `/skill requesting-code-review --task prepare`
2. When to use: When PR is created and ready for review preparation
3. Exit criteria: PR description verified, all checks passing, reviewers identified

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

## PR Description Template

```markdown
## Summary

[What this PR accomplishes and why it's needed]

## Changes

### [Component/Module Name]
- **[Change type]:** [Description of change]

## Testing

```bash
uv run pytest test/test_module.py -v
uv run ruff check --fix src/
uv run pyright src/
```

## Related Issues

Fixes #[issue-number]

---
Co-authored with AI: <AI-Name> (<model-id>)
```

## Anti-Patterns

### 🚫 Poor PR Description

"Please review this PR" with no context on what changed or why.

### ✅ Good PR Description

Includes summary, changes, testing commands, and related issues. Explains WHY, not just what.

## Context Required

- Related skills: `requesting-code-review` (parent skill)
- Related tasks: `request`