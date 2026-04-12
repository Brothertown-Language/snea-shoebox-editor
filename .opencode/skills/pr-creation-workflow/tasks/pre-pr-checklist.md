# Task: pre-pr-checklist

## Purpose

Mandatory checks that must pass before creating ANY PR. No exceptions.

## Pre-PR Creation Checklist (ALL Platforms)

**Changelog generation is MANDATORY for ALL PRs — GitHub, GitBucket, or any other platform.**

```
☐ Changelog Generated
  - Run: /skill changelog-generator --since-last-release
  - Stage: git add CHANGELOG.md
  - Verify: git status --porcelain CHANGELOG.md shows "M CHANGELOG.md"
  - OR: [skip changelog] directive present in commit message or PR title
```

### Step-by-Step Verification

**1. Squash Verification**

```bash
# Check commit count between dev and HEAD
git log origin/dev..HEAD --oneline

# If MORE THAN ONE commit shown, SQUASH NOW:
git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
git push --force-with-lease origin <branch>
```

Every PR must have EXACTLY ONE commit. No exceptions.

**2. Changelog Generated**

```bash
/skill changelog-generator --since-last-release
git add CHANGELOG.md
git status --porcelain CHANGELOG.md  # Should show staged changes
```

NO platform exemptions — GitHub, GitBucket, all platforms require changelog.

**3. Branch State**

```bash
git status
# Working tree must be clean (no uncommitted changes)
# If dirty: commit or stash before proceeding
```

**4. Push Verification**

```bash
git log origin/<branch>..HEAD --oneline
# Should show NO unpushed commits
# If unpushed: git push --force-with-lease origin <branch>
```

**5. Co-Author Trailers**

Verify commit message includes BOTH trailers:
- AI Author: `Co-authored-by: <AI-Name> (<model-id>) <ai-email>`
- Human Collaborator: `Co-authored-by: <Human-Name> <human-email>`

**6. Issue References**

- Single-task: Include `Fixes #<parent>` in PR body
- Multi-task: Include `Fixes #<parent>` AND `Fixes #<child>` for EACH sub-issue

## CRITICAL Violations

| Violation | Consequence |
|-----------|-------------|
| Multiple commits in PR | PR REJECTED — squash required |
| Missing PR URL in chat | CRITICAL — communication failure |
| Premature merge attempt | CRITICAL — HUMAN-ONLY operation |

## Violation Recovery

If you accidentally create a PR with multiple commits:

1. **DO NOT ask user to fix it** — Fix it yourself:
    ```bash
    git reset --soft origin/main
    git commit -m "<descriptive message>" \
        --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
        --trailer "Co-authored-by: <Human-Name> <human-email>"
    git push --force-with-lease origin <branch>
    ```
2. **Close the bad PR** and create a new one if necessary
3. **Report the violation** in the GitHub issue comment

User intervention should NEVER be required to fix squash violations.