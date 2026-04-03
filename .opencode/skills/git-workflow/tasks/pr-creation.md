# Task: pr-creation

## Purpose

Create pull request after explicit user instruction. Squash commits to single commit, push branch, create PR via GitHub MCP.

## Operating Protocol

1. **User-initiated only:** This task runs when user says "create a PR" or similar
1. **Squash to single commit:** ALL implementation commits combined into ONE clean commit
1. **HALT after PR creation:** Wait for human to merge

## Entry Criteria

- User says "create a PR", "make a PR", "push and create PR", or similar
- Implementation is complete
- Developer has reviewed changes via compare URL

## Exit Criteria

- PR created via GitHub MCP
- PR URL reported to user
- Waiting for human merge

## Procedure

### Step 0: Check PR State

**Before creating PR, check if branch already has a merged PR:**

```bash
# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Check for existing PRs on this branch
gh pr list --head "$CURRENT_BRANCH" --state merged --json number,url,mergedAt
```

**If merged PR exists:**
1. Get current main state: `git fetch origin && git checkout main && git pull origin main`
2. Create new branch: `git checkout -b <new-branch-name>`
3. Cherry-pick or reapply changes
4. Continue with PR creation

**Report to user:**
```
⚠️ Branch <name> has a merged PR. Creating new PR against current main.
```

### Step 1: Collect Sub-Issues (Multi-Task Specs)

**For specs with sub-issues:**

```python
# Fetch all sub-issues for the parent issue
sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)

# Build autoclose list: parent + all sub-issues
autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
```

**For single-task specs:**

No sub-issues needed. Include only parent issue.

### Step 2: Generate Changelog via Subtask

**⚠️ CRITICAL: Use task tool to prevent context pollution.**

The changelog-generator skill loads ~400 lines into context. To avoid polluting the git-workflow execution context, invoke it as a subtask using the `task` tool.

**Invoke as subtask:**

```
task tool with:
- subagent_type: "general"
- description: "Generate changelog for PR"
- prompt: "Use the changelog-generator skill to generate changelog entries from commits since branching from origin/main. Write the changelog to CHANGELOG.md (prepend to [Unreleased] section if exists, or create file if missing). Return a JSON object with: 1) 'summary' - executive summary (1-2 sentences), 2) 'changelog' - full markdown changelog content, 3) 'success' - boolean indicating if changelog was written. The skill is at .opencode/skills/changelog-generator/SKILL.md. Load it with /skill changelog-generator first."
```

**Subtask execution:**
1. Loads changelog-generator skill in isolated context (~400 lines)
2. Runs `git log origin/main..HEAD --oneline` to get commits
3. Generates user-facing changelog from technical commits
4. Writes to CHANGELOG.md using file tools
5. Returns results to main agent
6. Context is discarded after return (no pollution)

**Subtask returns:**

```json
{
  "summary": "Implemented feature X with improvements to Y and Z.",
  "changelog": "## Changes\n\n### Features\n- Added X\n\n### Fixes\n- Fixed Y\n\n...",
  "success": true
}
```

**If subtask fails or returns empty:**

Use fallback format for PR body:

```markdown
## Summary

<Brief description of changes from spec>

## Changes

- List key changes based on spec content
- Group by: Features, Improvements, Fixes
```

### Step 3: Stage CHANGELOG.md

**After subtask completes:**

The subtask has already written CHANGELOG.md. Now stage it:

```bash
git add CHANGELOG.md
git status  # Verify CHANGELOG.md is staged
```

**If CHANGELOG.md doesn't exist after subtask:**

The subtask should have created it. If missing, create minimal fallback:

```bash
# Fallback: Create basic changelog if subtask failed
cat > CHANGELOG.md << 'EOF'
# Changelog

## [Unreleased]

### Changes
- See PR for details

EOF
git add CHANGELOG.md
```

### Step 4: Squash to Single Commit

**MANDATORY:** All PRs must have exactly ONE commit, including CHANGELOG.md changes.

```bash
# Stage all changes including CHANGELOG.md
git add -A

# Squash to single commit
git reset --soft origin/main
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

### Step 5: Push to Remote

```bash
git push --force-with-lease origin <branch>
```

### Step 6: Create PR via GitHub MCP

**Use the summary and changelog from subtask for PR body.**

```python
github_create_pull_request(
    owner=<GIT_OWNER>,
    repo=<GIT_REPO>,
    title="[SPEC] <description>",
    body=f"""## Summary

{subtask_result['summary']}

## Changes

{subtask_result['changelog']}

Fixes #<parent>
Fixes #<child1>
Fixes #<child2>
...
""",
    head=<branch-name>,
    base="main"
)
```

**PR Body from Fallback (if subtask failed):**

```python
body=f"""## Summary

<Brief description from spec>

## Changes

- List key changes from spec content
- Group: Features, Improvements, Fixes

Fixes #<parent>
"""
```

**PR Body Requirements:**

- Executive summary section (from subtask or fallback)
- Changes section with user-facing descriptions (from subtask or fallback)
- `Fixes #<issue-number>` for autoclose
- Include ALL sub-issues for multi-task specs

### Step 7: Report PR URL and HALT

**⚠️ CRITICAL: PR URL Reporting is MANDATORY**

**You MUST report the PR URL in chat:**

1. **Chat Output:**
   ```
   **Summary:**
   
   <1-2 sentences describing stakeholder value>
   
   **Outcome:** <What changed for stakeholders>
   
   ---
   🤖 ✅ Completed by <AgentName> (<ModelID>)
   
   **PR Created:** https://github.com/<owner>/<repo>/pull/<number>
   ```

**Format Requirements:**

- Executive summary + byline footer come FIRST
- PR URL comes AFTER byline
- Same format in both GitHub comment and chat

### ⚠️ CRITICAL: Model ID Detection

**When posting completion comment:**

- **MUST dynamically detect model ID** - NEVER use hardcoded values from examples
- **MUST detect actual runtime identity** from environment/MCP tools
- **If model ID unknown:** STOP and ask user - DO NOT use example model IDs

### What If PR Creation Fails?

| Failure Reason | Response |
|----------------|----------|
| Merged PR exists on branch | Report: "Branch has merged PR. Creating new branch and PR." → Create new branch |
| No commits between branches | Report: "Branch has no commits to main. Changes may already be merged. Verify and HALT." |
| Branch conflicts | Report: "Branch conflicts with main. Rebase and push, then create PR." |
| GitHub API error | Report error details and HALT |

### Post-PR Creation Checklist

- \[ \] PR URL reported in chat
- \[ \] Brief implementation summary included
- \[ \] HALT — waiting for human merge

**🚫 NEVER:** Skip reporting PR URL, merge PR, or proceed without developer confirmation.

## Context Required

- Guidelines: `113-git-pr-workflow.md`
- Related skills: `pr-creation-workflow` (PR timing)
- Related tasks: `review-prep` (push before), `cleanup` (after merge)

## Co-Author Trailers (MANDATORY)

See `commit-prep` task for trailer format.

Every squash commit MUST include:

1. AI Author trailer
1. Human Collaborator trailer

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
1. HALT — wait for human merge
1. Do NOT merge (human-only operation)
