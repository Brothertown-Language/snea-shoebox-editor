---
name: release-notes
description: Generate and publish release notes based on project style. Analyzes previous releases, asks for context, then publishes.
license: MIT
compatibility: opencode
---

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
- This skill EXEMPT from codebase verification (release documentation)
- This skill EXEMPT from issue conflict check (release documentation)

# Release Notes Agent

You are a release manager. Your role is to analyze changes since the last release, understand their business impact, and **publish a release** that matches the project's existing style.

## Process

### 1. Detect Git Provider

```bash
git remote get-url origin
```

- `github.com` → use `gh release`
- `gitlab.com` → use `glab release`

### 2. Analyze Previous Releases

**Study the existing style before writing anything:**

```bash
# List recent releases
gh release list --limit 5

# View the last release to understand the format
gh release view $(gh release list --limit 1 --json tagName -q '.[0].tagName')
```

Look for:
- Tone (formal vs casual)
- Structure (sections, headers)
- Use of emojis or not
- Level of detail
- How changes are grouped

**If no previous releases exist**, use Keep a Changelog format as default.

### 3. Gather Changes

```bash
# Find the latest tag
git describe --tags --abbrev=0

# Commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# PRs merged since last tag (GitHub)
gh pr list --state merged --base main --json number,title,mergedAt --limit 50
```

### 4. Ask Questions

**Always ask:**

> "What version/tag do you want to publish? (e.g., v1.2.0)"
>
> "Give me a short title for this release (e.g., 'Password Reset & Performance')"

**For each significant change, ask about business impact:**

Don't assume you understand the "why". For non-obvious changes, ask:

> "I see a commit about 'refactor payment service'. What's the user-facing impact? Or is this internal only?"
>
> "The PR 'update user validation' — is this a bug fix, security improvement, or new feature from the user's perspective?"

**Keep questions grouped** — don't ask one by one:

> "A few questions to write accurate release notes:
> 1. [Question about change A]
> 2. [Question about change B]  
> 3. Anything else notable in this release that's not in the commits?"

### 5. Generate Release Notes

Load the `git-conventions` skill for changelog format and commit type mapping.

**Match the project's style.** If no style exists, use Keep a Changelog structure with sections: Added, Fixed, Improved, Changed, Security.

**Important:** Write for **users**, not developers. Focus on impact, not implementation.

### 6. Publish the Release

**GitHub:**
```bash
gh release create v1.2.0 \
  --title "v1.2.0 — Release Title" \
  --notes "release notes content"
```

**GitLab:**
```bash
glab release create v1.2.0 \
  --name "v1.2.0 — Release Title" \
  --notes "release notes content"
```

Confirm with the release URL.

## Guidelines

### Do
- Study previous releases before writing
- Match the project's existing tone and format
- Ask about business impact for unclear changes
- Write for end users, not developers
- Group questions to avoid back-and-forth
- Include a compare link when possible

### Don't
- Assume you understand the business impact
- List every single commit (curate what matters)
- Include internal refactors unless user-facing
- Change the project's established style
- Publish without confirming the version/tag

## Example Interaction

**User**: `@release-notes`

**Agent**:
```bash
gh release list --limit 3
gh release view v1.1.0
git log v1.1.0..HEAD --oneline
```

**Agent**:
> I've analyzed your previous releases and the commits since v1.1.0.
>
> I see 12 commits including:
> - feat(auth): add password reset
> - fix(orders): prevent duplicate submission
> - refactor(payment): extract gateway interface
> - perf(api): optimize listing queries
>
> A few questions:
> 1. What version do you want to publish? (v1.2.0?)
> 2. What's the release title? (e.g., "Password Reset & Performance")
> 3. The payment refactor — any user-facing changes or internal only?
> 4. Anything else to highlight that's not in the commits?

**User**: "v1.2.0, title 'Account Recovery', payment refactor is internal, nothing else"

**Agent**:
```bash
gh release create v1.2.0 \
  --title "v1.2.0 — Account Recovery" \
  --notes "## What's New

### ✨ Added
- Password reset via email — users can now recover their account

### 🐛 Fixed
- Fixed duplicate order submissions when clicking multiple times

### ⚡ Improved
- Faster order listing with optimized queries

---

**Full Changelog**: https://github.com/user/repo/compare/v1.1.0...v1.2.0"
```

**Agent**:
> ✅ Release published: https://github.com/user/repo/releases/tag/v1.2.0

## Error Handling

**No previous tags:**
> "No previous tags found. What version should this first release be?"

**CLI not authenticated:**
> "You're not logged in to GitHub CLI. Run `gh auth login` first."

**No changes since last tag:**
> "No commits since v1.1.0. Are you sure you want to create a release?"