---
name: git-conventions
description: Reference for Git best practices — Conventional Commits, branch naming, PR standards
license: MIT
compatibility: opencode
---

# Git Conventions

A comprehensive reference for Git best practices. Use this skill when you need to follow or enforce Git conventions.

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
- This skill EXEMPT from codebase verification (reference document)
- This skill EXEMPT from issue conflict check (reference document)

## Conventional Commits

Format:
```
type(scope): subject

[optional body]

[optional footer]
```

### Types

| Type | Emoji | Description | Example |
|------|-------|-------------|---------|
| `feat` | ✨ | New feature | `feat(auth): add password reset` |
| `fix` | 🐛 | Bug fix | `fix(cart): prevent negative quantity` |
| `docs` | 📝 | Documentation | `docs(readme): add installation steps` |
| `style` | 💄 | Formatting, no code change | `style: fix indentation` |
| `refactor` | ♻️ | Code change, no behavior change | `refactor(api): extract validation logic` |
| `perf` | ⚡ | Performance improvement | `perf(query): add index on user_id` |
| `test` | ✅ | Adding/updating tests | `test(auth): add login edge cases` |
| `build` | 📦 | Build system, dependencies | `build: upgrade webpack to v5` |
| `ci` | 👷 | CI configuration | `ci: add GitHub Actions workflow` |
| `chore` | 🔧 | Maintenance tasks | `chore: update .gitignore` |
| `revert` | ⏪ | Revert a commit | `revert: feat(auth): add password reset` |
| `security` | 🔒 | Security fix | `security(deps): patch vulnerable package` |

### Subject Rules

- Use imperative mood: "add" not "added" or "adds"
- Maximum 50 characters
- Lowercase (no capitalization)
- No period at the end

### Body Rules

- Explain the "why", not the "what"
- Wrap at 72 characters
- Separate from subject with blank line
- **Plain text only** — no markdown, no bullets, no headers
- Use blank lines to separate paragraphs if needed

### Footer Rules

- Reference issues: `Closes #123`, `Fixes #456`, `Refs #789`
- Breaking changes: `BREAKING CHANGE: description`

### Breaking Changes

Two ways to indicate:
```
feat(api)!: change response format

BREAKING CHANGE: The API now returns data in a nested structure.
```

Or just the footer:
```
feat(api): change response format

BREAKING CHANGE: The API now returns data in a nested structure.
```

## Branch Naming

Format: `type/short-description`

### Patterns

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/description` | `feat/user-authentication` |
| Bug fix | `fix/description` | `fix/login-redirect` |
| Hotfix | `hotfix/description` | `hotfix/payment-crash` |
| Release | `release/version` | `release/1.2.0` |
| Docs | `docs/description` | `docs/api-reference` |
| Refactor | `refactor/description` | `refactor/database-layer` |
| Test | `test/description` | `test/e2e-checkout` |

### Rules

- Lowercase only
- Use hyphens, not underscores
- Keep it short but descriptive
- Include ticket number if applicable: `feat/AUTH-123-password-reset`

## Pull Request Standards

### Title

Same format as commits:
```
✨ feat(auth): add password reset flow
🐛 fix(orders): prevent duplicate submission
```

### Description Structure

```markdown
## What
[Brief description — what this PR does]

## Why
[Context — why is this change needed]

## Changes
- [Key change 1]
- [Key change 2]

## How to Test
1. [Step 1]
2. [Step 2]
3. [Expected result]

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related
Closes #123
```

## Release Versioning (SemVer)

Format: `MAJOR.MINOR.PATCH`

| Increment | When | Example |
|-----------|------|---------|
| MAJOR | Breaking changes | `1.0.0` → `2.0.0` |
| MINOR | New features (backward compatible) | `1.0.0` → `1.1.0` |
| PATCH | Bug fixes (backward compatible) | `1.0.0` → `1.0.1` |

### Pre-release Tags

- Alpha: `1.0.0-alpha.1`
- Beta: `1.0.0-beta.1`
- Release candidate: `1.0.0-rc.1`

## Changelog Format (Keep a Changelog)

```markdown
## [1.2.0] - 2025-01-10

### Added
- New feature description

### Changed
- Change description

### Deprecated
- Deprecated feature

### Removed
- Removed feature

### Fixed
- Bug fix description

### Security
- Security fix description
```

### Mapping from Commits

| Commit Type | Changelog Section |
|-------------|-------------------|
| `feat` | Added |
| `fix` | Fixed |
| `perf` | Changed |
| `refactor` | Changed (if notable) |
| `security` | Security |
| `deprecate` | Deprecated |
| `remove` | Removed |