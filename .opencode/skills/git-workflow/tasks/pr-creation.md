# Task: pr-creation

## Purpose

Create pull request after explicit user instruction. Squash commits to single commit, push branch, create PR via GitHub MCP.

## Operating Protocol

1. **User-initiated only:** This task runs when user says "create a PR" or similar
2. **Squash to single commit:** ALL implementation commits combined into ONE clean commit
3. **HALT after PR creation:** Wait for human to merge

## Entry Criteria

- User says "create a PR", "make a PR", "push and create PR", or similar
- Implementation is complete
- Developer has reviewed changes via compare URL

## Exit Criteria

- PR created via GitHub MCP
- PR URL reported to user
- Waiting for human merge

## Procedure

### Step 1: Squash to Single Commit

**MANDATORY:** All PRs must have exactly ONE commit.

```bash
git reset --soft origin/main
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

### Step 2: Push to Remote

```bash
git push --force-with-lease origin <branch>
```

### Step 3: Collect Sub-Issues (Multi-Task Specs)

**For specs with sub-issues:**

```python
# Fetch all sub-issues for the parent issue
sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)

# Build autoclose list: parent + all sub-issues
autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
```

**For single-task specs:**

No sub-issues needed. Include only parent issue.

### Step 4: Create PR via GitHub MCP

```python
github_create_pull_request(
    owner=<GIT_OWNER>,
    repo=<GIT_REPO>,
    title="[SPEC] <description>",
    body="""<description>

Fixes #<parent>
Fixes #<child1>
Fixes #<child2>
...
""",
    head=<branch-name>,
    base="main"
)
```

**PR Body Requirements:**
- Must include `Fixes #<issue-number>` for autoclose
- Include ALL sub-issues for multi-task specs
- Brief description of changes

### Step 5: Report PR URL and HALT

### ⚠️ CRITICAL: PR URL Reporting is MANDATORY

**You MUST report the PR URL in chat:**

1. **Chat Output:**
   ```
   PR created: https://github.com/<owner>/<repo>/pull/<number>
   
   <Brief implementation summary>
   
   Wait for human to merge.
   ```

### What If PR Creation Fails?

| Failure Reason | Response |
|----------------|----------|
| No commits between branches | Report: "Branch has no commits to main. Changes may already be merged. Verify and HALT." |
| Branch conflicts | Report: "Branch conflicts with main. Rebase and push, then create PR." |
| GitHub API error | Report error details and HALT |

### Post-PR Creation Checklist

- [ ] PR URL reported in chat
- [ ] Brief implementation summary included
- [ ] HALT — waiting for human merge

**🚫 NEVER:** Skip reporting PR URL, merge PR, or proceed without developer confirmation.

## Context Required

- Guidelines: `113-git-pr-workflow.md`
- Related skills: `pr-creation-workflow` (PR timing)
- Related tasks: `review-prep` (push before), `cleanup` (after merge)

## Co-Author Trailers (MANDATORY)

See `commit-prep` task for trailer format.

Every squash commit MUST include:
1. AI Author trailer
2. Human Collaborator trailer

## Sub-Issue Autoclose

| Spec Type | PR Body Format |
|-----------|---------------|
| Single-task | `Fixes #<parent>` |
| Multi-task | `Fixes #<parent>` AND `Fixes #<child>` for each sub-issue |

**Example Multi-Task PR Body:**

```markdown
Implemented sub-task architecture for skills.

Fixes #469
Fixes #470
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Multiple commits in PR | Run `git reset --soft origin/main` and re-commit |
| PR body missing Fixes | Verify sub-issues, add all to body |
| Branch conflicts | Rebase on main: `git rebase origin/main` |

## After PR Creation

1. Report PR URL
2. HALT — wait for human merge
3. Do NOT merge (human-only operation)