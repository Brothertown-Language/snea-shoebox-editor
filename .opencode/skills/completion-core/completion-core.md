# Completion Core — Shared Completion Operations

Reference this file from per-skill `tasks/completion.md` files for common completion operations.

## Common Completion Operations

### 1. Push Branch (Idempotent)

Check whether the branch has unpushed commits before pushing:

```bash
UNPUSHED=$(git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null)
if [ -n "$UNPUSHED" ]; then
    git push -u origin $(git branch --show-current)
else
    echo "Branch already up to date with remote. No push needed."
fi
```

If no remote tracking branch exists yet, `git push -u origin <branch>` creates it.

### 2. Generate URL

Two URL patterns depending on workflow type:

**Compare URL** (for git push workflows — implementation, git-workflow, finishing):

```bash
COMPARE_URL="${GITBUCKET_HTML_URL:-https://github.com/}${GIT_OWNER}/${GIT_REPO}/compare/dev...$(git branch --show-current)"
```

**Action URL** (for creation workflows — issue creation, approval gate):

- Issue URL: `${GITBUCKET_HTML_URL:-https://github.com/}${GIT_OWNER}/${GIT_REPO}/issues/<number>`
- PR URL: from `github_create_pull_request` response

### 3. Post Status Comment (Substantive Only)

Before posting, evaluate whether the comment is substantive per the `issue-operations` `comment` task Substantive Comment Gate:

```python
# ONLY post if the comment conveys stakeholder-meaningful information
if is_substantive:
    github_add_issue_comment(owner=<GitOwner>, repo=<GitRepo>, issue_number=N, body="...")
else:
    # Skip posting — progress goes to chat only
    pass
```

### 4. Report Executive Summary in Chat (Always Runs)

Chat output is idempotent by nature. Always produce:

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

<URL if applicable, ALWAYS LAST>
```

**URL is ALWAYS last** per `000-critical-rules.md`.

## Idempotency Summary

| Operation | Idempotency Mechanism | Applies To |
| -- | -- | -- |
| Push branch | Check `git log origin/..HEAD` before pushing | Git workflows only |
| Generate URL | Check if URL already generated; compare URL for pushes, action URL for creation workflows | All workflows |
| Post status comment | Substantiveness gate (per `issue-operations` skill `comment` task) | Workflows with issue context |
| Report executive summary + URL | Always run; idempotent by nature | All workflows |
