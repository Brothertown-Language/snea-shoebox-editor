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

**Detect branch type first:**

```bash
# Check if this is a work branch (assembly by assemble-work)
ls .opencode/tmp/work-*.md 2>/dev/null

# Read scope fields from work state file if present
# authorization_scope, halt_at, pr_strategy

# Check commit count between dev and HEAD
git log origin/dev..HEAD --oneline
```

**Scope check:** If `pr_strategy == none` or `halt_at < pr_created`, HALT — PR creation is not authorized by the current scope. The scope boundary is a hard wall.

**Single-issue branch (no work state file):**

```bash
# If MORE THAN ONE commit shown, SQUASH NOW:
git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AgentName> (<ModelId>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
git push --force-with-lease origin <branch>
```

Single-issue PRs must have EXACTLY ONE commit. No exceptions.

**Work branch (work state file exists):**

Work branches have one commit per implementation item (N commits). This is correct — do NOT re-squash. The `assemble-work` task already squash-merged each feature branch into the work branch with proper individual commit messages.

```bash
# Verify work branch has expected commits (one per implementation item)
# Do NOT squash — N commits is correct for work branches
```

Work PRs correctly have N commits where N = number of implementation items.

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
- AI Author: `Co-authored-by: <AgentName> (<ModelId>) <ai-email>`
- Human Collaborator: `Co-authored-by: <Human-Name> <human-email>`

**6. Issue References**

- Single-task: Include `Fixes #<parent>` in PR body
- Multi-task: Include `Fixes #<parent>` AND `Fixes #<child>` for EACH sub-issue

**7. Dispatch Chain Completion (MANDATORY — Zero Tolerance)**

Before creating a PR, verify that ALL post-implementation dispatch chain steps were completed. These steps are listed in `approval-gate/SKILL.md` §Dispatch Order and are MANDATORY before PR creation.

| Step | Evidence to Verify | On Missing |
| -- | -- | -- |
| `verification-before-completion` | Success criteria verification results exist in chat output | HALT and invoke `verification-before-completion` before proceeding |
| `finishing-a-development-branch --task checklist` | All checklist items verified via tool-call artifacts (see checklist.md Live Verification table) | HALT and invoke `--task checklist` before proceeding |
| `git-workflow --task review-prep` | Compare URL generated and reported in chat with mandatory format (summary → outcome → URL → byline) | HALT and invoke `--task review-prep` before proceeding |

**If ANY dispatch chain step is missing evidence, the agent MUST invoke the missing step before proceeding with PR creation.** This is a belt-and-suspenders check: even if a step was skipped earlier, this gate catches the omission before the PR is created.

Skipping this verification is a CRITICAL GUIDELINE VIOLATION per `approval-gate/SKILL.md` §Enforcement checkpoint rules.

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
        --trailer "Co-authored-by: <AgentName> (<ModelId>) <ai-email>" \
        --trailer "Co-authored-by: <Human-Name> <human-email>"
    git push --force-with-lease origin <branch>
    ```
2. **Close the bad PR** and create a new one if necessary
3. **Report the violation** in the GitHub issue comment

User intervention should NEVER be required to fix squash violations.