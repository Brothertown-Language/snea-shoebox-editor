# Task: pr-creation

## Purpose

Create pull request after explicit user instruction. Squash commits to single commit, push branch, create PR via GitHub MCP.

## Operating Protocol

1. **User-initiated only:** This task runs when user says "create a PR" or similar
1. **Squash to single commit:** ALL implementation commits combined into ONE clean commit
1. **HALT after PR creation:** Wait for human to merge

## ⚠️ CRITICAL: This Skill Must Be Invoked

**When user says "pr", "create a PR", "make a PR", or similar:**

1. **LOAD this task** via `/skill git-workflow --task pr-creation`
2. **DO NOT** manually decide "PR exists, update it"
3. **DO NOT** skip steps or execute outside the task
4. **FOLLOW** all steps in order

**Bypassing this skill is a CRITICAL GUIDELINE VIOLATION.**

## Entry Criteria

- User says "create a PR", "make a PR", "push and create PR", or similar
- Implementation is complete
- Developer has reviewed changes via compare URL

## Exit Criteria

- PR created via GitHub MCP
- PR URL reported to user
- Waiting for human merge

## Procedure

### ⚠️ MANDATORY EXECUTION ORDER - NO GATE SKIPPING {#mandatory-order}

**CRITICAL: Every step has a verification gate. Gates MUST pass before proceeding.**

```
Step 1: [Check PR State](#check-pr-state)
  └─ ✅ Gate: PR state determined (open/merged/closed/none)

Step 2: [Collect Sub-Issues](#collect-sub-issues)
  └─ ✅ Gate: Sub-issues collected or single-task confirmed

Step 3: [Version Bump](#version-bump)
  └─ ✅ Gate: `git diff` run AND (version-bump invoked OR skip recorded)

Step 4: [Generate Changelog](#generate-changelog)
  └─ ✅ Gate: Subtask returned `success: true` AND CHANGELOG.md created

Step 5: [Stage Changelog](#stage-changelog)
  └─ ✅ Gate: `git status` shows CHANGELOG.md staged

Step 6: [Squash Commit](#squash-commit)
  └─ ✅ Gate: `git log` shows EXACTLY ONE commit

Step 7: [Push Remote](#push-remote)
  └─ ✅ Gate: Force push succeeded

Step 8: [Create PR](#create-pr)
  └─ ✅ Gate: PR URL returned

Step 9: [Report URL](#report-url)
  └─ ✅ Gate: URL posted to chat (URL-LAST format)
```

**If ANY gate fails: STOP and fix before proceeding.**

### Check PR State {#check-pr-state}

**Before creating PR, check if branch already has a PR (open OR merged):**

```bash
# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)

# Check for ALL existing PRs on this branch (open, merged, closed)
gh pr list --head "$CURRENT_BRANCH" --state all --json number,url,state,mergedAt
```

#### Post-PR State Verification (MANDATORY)

**Gate Checklist:**
- [ ] Current branch name retrieved
- [ ] GitHub MCP queried for existing PRs
- [ ] PR state determined (open/merged/closed/none)
- [ ] Decision recorded: UPDATE | CREATE_NEW_BRANCH | CREATE_NEW_PR

**✅ GATE: PR state determined. Proceed to Collect Sub-Issues.**

**If open PR exists via GitHub MCP:**

```python
# Check via GitHub MCP
prs = github_list_pull_requests(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    head=CURRENT_BRANCH,
    state="all"
)

for pr in prs:
    if pr["state"] == "open":
        # Open PR exists - UPDATE it
        print(f"ℹ️ Branch {CURRENT_BRANCH} has open PR #{pr['number']}. Updating existing PR instead of creating new one.")
        # Squash, push, update PR body
        # HALT after update
        return
    elif pr["state"] == "closed" and pr.get("merged_at"):
        # Merged PR exists - CREATE NEW BRANCH
        print(f"⚠️ Branch {CURRENT_BRANCH} has merged PR #{pr['number']}. Creating new branch and PR.")
        # Create new branch, reapply changes
        # Continue with PR creation
```

**Decision tree:**

| PR State | Action |
|----------|--------|
| Open PR exists | **UPDATE existing PR** - squash, push, update PR body (do NOT create new PR) |
| Merged PR exists | **CREATE NEW BRANCH** - branch from current main, reapply changes, create new PR |
| Closed PR exists (not merged) | **CREATE NEW PR** - new PR against same branch |
| No PR exists | **CREATE NEW PR** - proceed with workflow |

**If open PR exists:**

Proceed through [Generate Changelog](#generate-changelog) → [Stage Changelog](#stage-changelog) → [Squash](#squash-commit) → [Push](#push-remote) → [Create PR](#create-pr) → [Report URL](#report-url):

1. Generate changelog via subtask ([Generate Changelog](#generate-changelog)) - **MANDATORY**
2. Stage CHANGELOG.md ([Stage Changelog](#stage-changelog)) - **MANDATORY**
3. Squash commits ([Squash](#squash-commit))
4. Push to same branch (force-with-lease, [Push](#push-remote))
5. Update PR body ([Create PR](#create-pr), use `github_update_pull_request` instead of `github_create_pull_request`)
6. Report PR URL and HALT ([Report URL](#report-url))
7. **DO NOT create a new PR**

**If merged PR exists:**

1. Get current dev state: `git fetch origin && git checkout dev && git pull origin dev`
2. Create new branch: `git checkout -b <new-branch-name>`
3. Cherry-pick or reapply changes
4. Continue with PR creation workflow

**Report to user:**
```
⚠️ Branch <name> has a merged PR. Creating new PR against current dev.
```

or

```
ℹ️ Branch <name> has open PR #<number>. Updating existing PR instead of creating new one.
```

### Collect Sub-Issues {#collect-sub-issues}

**For specs with sub-issues:**

```python
# Fetch all sub-issues for the parent issue
sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)

# Build autoclose list: parent + all sub-issues
autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
```

**For single-task specs:**

No sub-issues needed. Include only parent issue.

#### Post-Sub-Issues Verification (MANDATORY)

**Gate Checklist:**
- [ ] Queried sub-issues via `github_issue_read(method="get_sub_issues")`
- [ ] Result is either: empty array (single-task) OR list of sub-issues (multi-task)
- [ ] If multi-task: autoclose list includes parent + ALL sub-issues
- [ ] If single-task: autoclose list includes only parent

**✅ GATE: Sub-issues collected or single-task confirmed. Proceed to Version Bump.**

### Version Bump {#version-bump}

**⚠️ CRITICAL: Only for PRs with code changes. Skip for docs/chore/refactor PRs.**

#### Pre-Version-Bump Checklist (MANDATORY)

Run these checks BEFORE deciding on version bump:

```bash
# Step 1: Get list of changed files
git diff origin/dev...HEAD --name-only

# Step 2: Check if any code files changed
CHANGED_FILES=$(git diff origin/dev...HEAD --name-only)
echo "$CHANGED_FILES" | grep -qE '\.(py|js|ts|rs|java|go|rb)$'
CODE_CHANGES=$?

if [ $CODE_CHANGES -eq 0 ]; then
    echo "✅ Gate: Code changes detected - version bump required"
    # Continue to invoke version-bump subtask
else
    echo "✅ Gate: No code changes - version bump skipped (docs/chore/refactor)"
    # Skip version bump, proceed to changelog
fi
```

**Gate Checklist:**
- [ ] Ran `git diff origin/dev...HEAD --name-only`
- [ ] Checked file extensions for code files
- [ ] If code changes: Invoked version-bump subtask
- [ ] If docs only: Recorded "skip" and proceeded

**Skip version bump for:**
- Documentation-only changes (*.md files)
- CI/CD configuration (*.yml, *.yaml)
- Build configuration (Dockerfile, docker-compose.yml)
- Test files without production code changes
- Refactoring PRs without public API changes

**If code changes detected, invoke version-bump as subtask:**

```
task tool with:
- subagent_type: "general"
- description: "Version bump for PR"
- prompt: "Use the version-bump skill to analyze changes and update version files. Steps: 1) Load skill with /skill version-bump, 2) Invoke analyze task to determine bump type, 3) Invoke bump task to update version files, 4) Return JSON with: bump_type, old_version, new_version, files_updated, success. The skill is at .opencode/skills/version-bump/SKILL.md."
```

**Subtask execution:**
1. Loads version-bump skill in isolated context (~370 lines)
2. Runs analyze.md to determine bump type (major/minor/patch/skip)
3. Runs bump.md to update all version files atomically
4. Returns results to main agent
5. Context is discarded after return (no pollution)

**Subtask returns:**

```json
{
  "bump_type": "minor",
  "old_version": "1.2.3",
  "new_version": "1.3.0",
  "files_updated": ["pyproject.toml"],
  "success": true
}
```

**If subtask fails or returns skip:**

```json
{
  "bump_type": "skip",
  "reason": "No code changes detected",
  "success": true
}
```

No version bump needed. Continue to changelog generation.

**Stage version file changes:**

```bash
# Stage version file updates (if any)
if [ -n "$(git status --porcelain | grep -E '(pyproject.toml|setup.py|package.json|Cargo.toml|VERSION)')" ]; then
    git add pyproject.toml setup.py package.json Cargo.toml VERSION 2>/dev/null
fi
```

**Note:** Version bump changes are included in the [Squash](#squash-commit) step. They are NOT a separate commit.

#### Post-Version-Bump Verification (MANDATORY)

**After version-bump subtask completes, verify BEFORE proceeding to Generate Changelog:**

```bash
# Gate: Verify version bump was processed
# Subtask must return: { "bump_type": "...", "success": true }

# Gate: If code changes detected, version file must exist
if [ -n "$(git diff origin/dev...HEAD --name-only | grep -E '\.(py|js|ts|rs|java|go|rb)$')" ]; then
    # Code changes - version bump required
    # Verify version file was updated (or subtask recorded skip)
    git status --porcelain | grep -qE '(pyproject.toml|package.json|Cargo.toml|VERSION)' && echo "✅ Gate: Version file updated"
fi
```

**Gate Checklist:**
- [ ] Pre-Version-Bump checklist completed
- [ ] version-bump subtask invoked (if code changes) OR skip recorded (if docs only)
- [ ] Subtask returned `success: true`
- [ ] Version file staged (if version bump applied)

**✅ GATE: Version bump processed. Proceed to Generate Changelog.**

### Generate Changelog {#generate-changelog}

**⚠️ CRITICAL: Use task tool to prevent context pollution.**

The changelog-generator skill loads ~400 lines into context. To avoid polluting the git-workflow execution context, invoke it as a subtask using the `task` tool.

**Invoke as subtask:**

```
task tool with:
- subagent_type: "general"
- description: "Generate changelog for PR"
- prompt: "Use the changelog-generator skill to generate changelog entries from commits since branching from origin/dev. Write the changelog to CHANGELOG.md (prepend to [Unreleased] section if exists, or create file if missing). Return a JSON object with: 1) 'summary' - executive summary (1-2 sentences), 2) 'changelog' - full markdown changelog content, 3) 'success' - boolean indicating if changelog was written. The skill is at .opencode/skills/changelog-generator/SKILL.md. Load it with /skill changelog-generator first."
```

**Subtask execution:**
1. Loads changelog-generator skill in isolated context (~400 lines)
2. Runs `git log origin/dev..HEAD --oneline` to get commits
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

#### Post-Changelog Verification (MANDATORY)

**After subtask returns, verify BEFORE proceeding to Stage Changelog:**

```bash
# Gate 1: Check subtask result
# Subtask must return: { "summary": "...", "changelog": "...", "success": true }

# Gate 2: Verify CHANGELOG.md exists
ls -la .opencode/CHANGELOG.md && echo "✅ Gate: CHANGELOG.md created"

# Gate 3: Verify file has content
test -s .opencode/CHANGELOG.md && echo "✅ Gate: CHANGELOG.md not empty"
```

**Gate Checklist:**
- [ ] Subtask returned `success: true`
- [ ] CHANGELOG.md file exists
- [ ] CHANGELOG.md has content (> 0 bytes)

**If ANY gate fails: STOP and fix before proceeding to Stage Changelog.**

### Stage Changelog {#stage-changelog}

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

**✅ STAGE CHANGELOG COMPLETE:** CHANGELOG.md staged

#### Post-Stage Verification (MANDATORY)

**After staging CHANGELOG.md, verify BEFORE proceeding to Squash:**

```bash
# Gate: Verify CHANGELOG.md is staged
git status --porcelain | grep -q "M.*CHANGELOG.md" && echo "✅ Gate: CHANGELOG.md staged"
```

**Gate Checklist:**
- [ ] `git status` shows `modified: CHANGELOG.md` (staged)

**If gate fails:**
```bash
git add CHANGELOG.md
git status  # Re-verify
```

### Squash Commit {#squash-commit}

**⚠️ CRITICAL: This step MUST run AFTER [Stage Changelog](#stage-changelog).**

The squash commit combines ALL changes into ONE clean commit:
- All implementation changes
- Version bump (if applied in [Version Bump](#version-bump))
- CHANGELOG.md updates (from [Generate Changelog](#generate-changelog), staged in [Stage Changelog](#stage-changelog))

**Execution Order:**
1. [Generate Changelog](#generate-changelog) → writes CHANGELOG.md
2. [Stage Changelog](#stage-changelog) → adds to git index
3. [Squash Commit](#squash-commit) → combines all staged changes
4. [Push](#push-remote) → sends single commit to remote
5. [Create PR](#create-pr) → creates PR with single commit
6. [Report URL](#report-url) → HALT

**MANDATORY:** All PRs must have exactly ONE commit, including version bump and CHANGELOG.md changes.

#### Pre-Squash Verification (MANDATORY)

**Before running squash, VERIFY all changes are staged:**

```bash
# Check staged changes
git status

# MUST show:
#   Changes to be committed:
#     .opencode/CHANGELOG.md
#     .opencode/guidelines/...
#     (all modified files)
```

**If `git status` shows unstaged changes:**

```bash
# Stage ALL changes NOW - this is the last chance
git add -A
git status  # Verify again before proceeding
```

**Only proceed when `git status` shows ALL changes staged.**

#### Execute Squash (Atomic Block)

**Run as ONE atomic command - DO NOT split across lines:**

```bash
git add -A && git reset --soft origin/dev && git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

**Note:** The squash commit includes:
- All implementation changes
- Version bump (if applied in [Version Bump](#version-bump))
- CHANGELOG.md updates

These are NOT separate commits - all combined into ONE clean commit.

#### Post-Squash Verification (MANDATORY)

**Verify squash succeeded:**

```bash
git status
# MUST show: "nothing to commit, working tree clean"

git log --oneline origin/dev..HEAD
# MUST show: EXACTLY ONE commit
```

**If working tree is NOT clean:**
```bash
# Changes were created after subtask but before squash
# Stage and amend
git add -A
git commit --amend --no-edit
git status  # Verify clean
```

**If MORE THAN ONE commit shown:**
```bash
# Re-run squash
git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
git log --oneline origin/dev..HEAD  # Verify single commit
```

**✅ SQUASH COMPLETE:** Single commit created, working tree clean

### Push Remote {#push-remote}

```bash
git push --force-with-lease origin <branch>
```

### Create PR {#create-pr}

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

### Report URL {#report-url}

**⚠️ CRITICAL: PR URL Reporting is MANDATORY (Chat Only)**

**Chat Output (REQUIRED):**
```markdown
**Summary:**

<1-2 sentences describing stakeholder value>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

**PR Created:** https://github.com/<owner>/<repo>/pull/<number>
```

**⚠️ CRITICAL: URL-LAST FORMAT (MANDATORY)**

**PR URL MUST be the FINAL line in chat - AFTER the byline.**

**✅ CORRECT:**
```markdown
**Summary:**

<1-2 sentences describing stakeholder value>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

**PR Created:** https://github.com/<owner>/<repo>/pull/<number>
```

**❌ WRONG:**
```markdown
**PR Created:** https://github.com/<owner>/<repo>/pull/<number>

**Summary:**
<content>
```

**Format Requirements:**

| Location | Contains | Does NOT Contain |
|----------|----------|------------------|
| Chat | Summary, Outcome, byline, PR URL | — |
| GitHub Issue | Summary, Outcome, byline | PR URL (already visible via PR) |
| GitHub PR | Automatically linked | No comment needed |

**Why URL-Last:**
- URLs are long and may wrap across lines
- Placing URLs last allows developers to scan summary first
- Easy visual anchor: "look for the PR link at the end"
- Consistent pattern across all AI-generated summaries

**Report PR URL in chat only (not in GitHub issues or PR comments).**

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

### Pre-Post Verification (MANDATORY)

**Before reporting PR URL, VERIFY:**

```
✓ Executive summary present (<1-2 sentences)
✓ Outcome field present (stakeholder value)
✓ Byline present (agent name + model ID)
✓ PR URL is FINAL line (after byline)
✓ No URL before summary
✓ No URL between summary and byline
✓ NO unstaged changes in working tree
✓ EXACTLY ONE commit in branch
```

**If any check fails:** Fix the comment format BEFORE reporting.

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
| Multiple commits in PR | Run `git reset --soft origin/dev` and re-commit |
| PR body missing Fixes | Verify sub-issues, add all to body |
| Branch conflicts | Rebase on dev: `git rebase origin/dev` |

## After PR Creation

1. Report PR URL
1. HALT — wait for human merge
1. Do NOT merge (human-only operation)
