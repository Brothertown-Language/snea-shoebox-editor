# Task: pr-creation

## Purpose

Create pull request after explicit user instruction. Use subtasks for context isolation.

**Key Improvement:** Main task is now ~200 lines (down from ~850).
Subtasks handle their own context, discarded after return.

## Workflow

1. **User-initiated only:** This task runs when user says "create a PR" or similar
2. **Squash to single commit:** ALL implementation commits combined into ONE clean commit
3. **HALT after PR creation:** Wait for human to merge

## ⚠️ CRITICAL: This Skill Must Be Invoked

**When user says "pr", "create a PR", "make a PR", or similar:**

1. **LOAD this task** via `/skill git-workflow --task pr-creation`
2. **DO NOT** manually decide "PR exists, update it"
3. **DO NOT** skip steps or execute outside the task
4. **FOLLOW** all steps in order

**Bypassing this skill is a CRITICAL GUIDELINE VIOLATION.**

## Preconditions

- User says "create a PR", "make a PR", "push and create PR", or similar
- Implementation is complete
- Developer has reviewed changes via compare URL

## Postconditions

- PR created via GitHub MCP
- PR URL reported to user
- Waiting for human merge

## Procedure

### Step 1: Check PR State (Subtask)

**Invoke subtask to determine if PR already exists:**

```
task tool with:
- subagent_type: "general"
- description: "Check PR state for current branch"
- prompt: "Use the check-pr-state subtask at .opencode/skills/git-workflow/tasks/check-pr-state.md to determine PR state. Return JSON with: branch, pr_state, pr_number, action."
```

**Subtask returns:**

```json
{
  "branch": "feature/xyz",
  "pr_state": "none|open|merged|closed",
  "pr_number": 123,
  "action": "create_new_pr|update_existing|create_new_branch"
}
```

**Decision tree based on action:**

| Action | What to Do |
|--------|-----------|
| `create_new_pr` | Continue with workflow |
| `update_existing` | Squash, push, update PR body via `github_update_pull_request`, HALT |
| `create_new_branch` | Report "Branch has merged PR - creating new branch", then create new branch from dev |

**✅ GATE: PR state determined. Proceed to Collect Sub-Issues.**

### Step 2: Collect Sub-Issues (Subtask)

**Invoke subtask to collect sub-issues for PR body:**

```
task tool with:
- subagent_type: "general"
- description: "Collect sub-issues for autoclose"
- prompt: "Use the collect-sub-issues subtask at .opencode/skills/git-workflow/tasks/collect-sub-issues.md. Parent issue is <PARENT_ISSUE>. Return JSON with: parent_issue, sub_issues, autoclose_list, is_single_task."
```

**Subtask returns:**

```json
{
  "parent_issue": 100,
  "sub_issues": [101, 102, 103],
  "autoclose_list": [100, 101, 102, 103],
  "is_single_task": false
}
```

**✅ GATE: Sub-issues collected. Proceed to Version Bump.**

### Step 3: Version Bump (Conditional)

**⚠️ CRITICAL: Only for PRs with code changes. Skip for docs/chore/refactor PRs.**

Run these checks BEFORE deciding on version bump:

```bash
CHANGED_FILES=$(git diff origin/dev...HEAD --name-only)
echo "$CHANGED_FILES" | grep -qE '\.(py|js|ts|rs|java|go|rb)$'
CODE_CHANGES=$?

if [ $CODE_CHANGES -eq 0 ]; then
    # Code changes - invoke version-bump subtask
    # See version-bump skill for invocation
else
    # Docs only - skip version bump
    echo "✅ Gate: No code changes - version bump skipped"
fi
```

**✅ GATE: Version bump processed (or skipped). Proceed to Generate Changelog.**

### Step 4: Generate Changelog (Subtask)

**Invoke changelog-generator as subtask:**

```
task tool with:
- subagent_type: "general"
- description: "Generate changelog for PR"
- prompt: "Use the changelog-generator skill. Load with /skill changelog-generator. Write changelog to CHANGELOG.md. Return JSON with: summary, changelog, success."
```

**Subtask returns:**

```json
{
  "summary": "Implemented feature X with improvements to Y.",
  "changelog": "## Changes\n\n### Features\n- Added X\n...",
  "success": true
}
```

**✅ GATE: Changelog generated. Proceed to Stage.**

### Step 5: Stage Changelog

```bash
git add CHANGELOG.md
git status  # Verify CHANGELOG.md is staged
```

**✅ GATE: CHANGELOG.md staged. Proceed to Squash.**

### Step 6: Squash to Single Commit

**Pre-squash verification (MANDATORY):**

```bash
git status
# MUST show all changes staged
```

**If not all staged:**

```bash
git add -A
git status  # Re-verify
```

**Execute squash:**

```bash
git reset --soft origin/dev && git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

**Post-squash verification:**

```bash
git log --oneline origin/dev..HEAD
# MUST show EXACTLY ONE commit
```

**✅ GATE: Single commit. Proceed to Push.**

### Step 7: Push to Remote

```bash
git push --force-with-lease origin <branch>
```

**Post-push verification:**

```bash
git log --oneline origin/dev..HEAD | head -1
# MUST show exactly one commit
```

**✅ GATE: Push succeeded. Proceed to Create PR.**

### Step 8: Create PR

**Determine base branch:**

```bash
CURRENT_BRANCH=$(git branch --show-current)

case "$CURRENT_BRANCH" in
    feature/*) BASE_BRANCH="dev" ;;
    release/*) BASE_BRANCH="main" ;;
    hotfix/*)  BASE_BRANCH="main" ;;
    *)        BASE_BRANCH="dev" ;;
esac
```

**Create PR:**

```python
github_create_pull_request(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    title="[SPEC] <description>",
    body=f"""## Summary

{subtask_result['summary']}

## Changes

{subtask_result['changelog']}

Fixes #<parent>
Fixes #<child1>
...
""",
    head=BRANCH_NAME,
    base=BASE_BRANCH
)
```

**CRITICAL:** Feature branches MUST target `dev`.

**✅ GATE: PR created. Proceed to Report URL.**

### Step 9: Report URL (Chat Only)

**Chat Output (MANDATORY):**

```markdown
**Summary:**

<1-2 sentences describing stakeholder value>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

**PR Created:** https://github.com/<owner>/<repo>/pull/<number>
```

**Format Requirements:**

| Location | Contains | Does NOT Contain |
|----------|----------|------------------|
| Chat | Summary, Outcome, byline, PR URL | — |
| GitHub Issue | Summary, Outcome, byline | PR URL (already visible via PR) |

**✅ REPORT COMPLETE. HALT after reporting.**

## Subtask Context Isolation

**Key benefit:** Subtasks load ~100-400 lines each, discarded after return.

| Subtask | Lines | Context Usage |
|---------|-------|---------------|
| `check-pr-state` | ~100 | Discarded after return |
| `collect-sub-issues` | ~80 | Discarded after return |
| `version-bump` | ~370 | Invoked conditionally |
| `changelog-generator` | ~400 | Discarded after return |

**Total context with subtasks:** ~200 lines (main) + ~100 (active subtask) = **~300 lines at any time**

**Previous context without subtasks:** ~850 lines loaded at once

**Result:** ~65% context reduction.

## Context Required

- Guidelines: `113-git-pr-workflow.md`
- Related skills: `pr-creation-workflow` (PR timing)
- Related tasks: `review-prep` (push before), `cleanup` (after merge)
- Session init: `GIT_OWNER`, `GIT_REPO`

## Co-Author Trailers (MANDATORY)

Every squash commit MUST include:

1. AI Author trailer: `Co-authored-by: <AI-Name> (<model-id>) <ai-email>`
2. Human Collaborator trailer: `Co-authored-by: <Human-Name> <human-email>`

**MUST dynamically detect model ID at runtime.** NEVER use hardcoded values from examples.

## Common Issues

| Issue | Resolution |
|-------|------------|
| Multiple commits | Run `git reset --soft origin/dev` and re-commit |
| PR body missing Fixes | Verify sub-issues, add all to body |
| Branch conflicts | Rebase on dev: `git rebase origin/dev` |

## After PR Creation

1. Report PR URL
2. HALT — wait for human merge
3. Do NOT merge (human-only operation)