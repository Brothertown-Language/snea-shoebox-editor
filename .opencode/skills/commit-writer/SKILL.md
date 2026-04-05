---
name: commit-writer
description: Generate commit messages following Git best practices (Conventional Commits)
license: MIT
compatibility: opencode
---

# Commit Message Writer

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Preparing commit message | `/skill commit-writer` | Generate Conventional Commits message |
| After git add, before commit | `/skill commit-writer` | Analyze staged changes |

## This Skill's Tasks

| Task | Description | Words |
|------|-------------|-------|
| `overview` | Generate commit message from staged changes | ~150 |

## Process

1. Run `git status` to check for staged changes
2. Run `git diff --staged` to analyze what has changed
3. Generate a commit message following Conventional Commits format

## Commit Format

```
type(scope): subject

[optional body]

[optional footer]
```

- **Type**: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- **Scope**: module or area affected (optional)
- **Subject**: imperative mood, max 50 chars, lowercase, no period
- **Body**: explain "why" not "what", wrap at 72 chars, **plain text only (no markdown)**
- **Footer**: issue refs (`Closes #123`), breaking changes

## Examples

Simple:
```
feat(auth): add password reset endpoint
```

With body (plain text, no markdown):
```
fix(api): prevent null pointer on empty response

The API was crashing when the external service returned an empty
response. Added null check and default empty array fallback.

Fixes #234
```

## Output

Provide ONLY the commit message, ready to be used with `git commit`. No explanations, no markdown code blocks.

If multiple logical changes are staged, suggest splitting into separate commits and provide each message.