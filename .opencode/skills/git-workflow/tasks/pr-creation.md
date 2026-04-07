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

### Step 0: Clear Implementation Todos (MANDATORY)

**Before PR creation workflow begins:**

```python
# Clear any stale implementation todos
todowrite(todos=[])
```

**Why:** Implementation todos are for tracking work progress. PR creation has explicit procedural steps in this task - no todo list needed. Clearing prevents confusion about stale "X of Y complete" status.

**CRITICAL:** This step runs BEFORE checking PR state, collecting sub-issues, or any other PR workflow steps.

______________________________________________________________________

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

**Update progress:**

```python
todowrite([
    {"content": "Step 0: Clear implementation todos", "status": "completed", "priority": "high"},
    {"content": "Step 1: Check PR state", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Collect sub-issues", "status": "in_progress", "priority": "high"},
    {"content": "Step 3: Version bump", "status": "pending", "priority": "medium"},
    {"content": "Step 4: Generate changelog", "status": "pending", "priority": "medium"},
    {"content": "Step 5: Stage changelog", "status": "pending", "priority": "medium"},
    {"content": "Step 6: Squash to single commit", "status": "pending", "priority": "high"},
    {"content": "Step 7: Push to remote", "status": "pending", "priority": "high"},
    {"content": "Step 8: Create PR", "status": "pending", "priority": "high"},
    {"content": "Step 9: Report URL and HALT", "status": "pending", "priority": "medium"},
])
```

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

**Update progress:**

```python
todowrite([
    {"content": "Step 0: Clear implementation todos", "status": "completed", "priority": "high"},
    {"content": "Step 1: Check PR state", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Collect sub-issues", "status": "completed", "priority": "high"},
    {"content": "Step 3: Version bump", "status": "completed", "priority": "medium"},
    {"content": "Step 4: Generate changelog", "status": "in_progress", "priority": "medium"},
    {"content": "Step 5: Stage changelog", "status": "pending", "priority": "medium"},
    {"content": "Step 6: Squash to single commit", "status": "pending", "priority": "high"},
    {"content": "Step 7: Push to remote", "status": "pending", "priority": "high"},
    {"content": "Step 8: Create PR", "status": "pending", "priority": "high"},
    {"content": "Step 9: Report URL and HALT", "status": "pending", "priority": "medium"},
])
```

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

**Update progress:**

```python
todowrite([
    {"content": "Step 0: Clear implementation todos", "status": "completed", "priority": "high"},
    {"content": "Step 1: Check PR state", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Collect sub-issues", "status": "completed", "priority": "high"},
    {"content": "Step 3: Version bump", "status": "completed", "priority": "medium"},
    {"content": "Step 4: Generate changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 5: Stage changelog", "status": "in_progress", "priority": "medium"},
    {"content": "Step 6: Squash to single commit", "status": "pending", "priority": "high"},
    {"content": "Step 7: Push to remote", "status": "pending", "priority": "high"},
    {"content": "Step 8: Create PR", "status": "pending", "priority": "high"},
    {"content": "Step 9: Report URL and HALT", "status": "pending", "priority": "medium"},
])
```

### Step 5: Stage Changelog

```bash
git add CHANGELOG.md
git status  # Verify CHANGELOG.md is staged
```

**✅ GATE: CHANGELOG.md staged. Proceed to Squash.**

**Update progress:**

```python
todowrite([
    {"content": "Step 0: Clear implementation todos", "status": "completed", "priority": "high"},
    {"content": "Step 1: Check PR state", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Collect sub-issues", "status": "completed", "priority": "high"},
    {"content": "Step 3: Version bump", "status": "completed", "priority": "medium"},
    {"content": "Step 4: Generate changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 5: Stage changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 6: Squash to single commit", "status": "in_progress", "priority": "high"},
    {"content": "Step 7: Push to remote", "status": "pending", "priority": "high"},
    {"content": "Step 8: Create PR", "status": "pending", "priority": "high"},
    {"content": "Step 9: Report URL and HALT", "status": "pending", "priority": "medium"},
])
```

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

**Update progress:**

```python
todowrite([
    {"content": "Step 0: Clear implementation todos", "status": "completed", "priority": "high"},
    {"content": "Step 1: Check PR state", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Collect sub-issues", "status": "completed", "priority": "high"},
    {"content": "Step 3: Version bump", "status": "completed", "priority": "medium"},
    {"content": "Step 4: Generate changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 5: Stage changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 6: Squash to single commit", "status": "completed", "priority": "high"},
    {"content": "Step 7: Push to remote", "status": "in_progress", "priority": "high"},
    {"content": "Step 8: Create PR", "status": "pending", "priority": "high"},
    {"content": "Step 9: Report URL and HALT", "status": "pending", "priority": "medium"},
])
```

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

**Update progress:**

```python
todowrite([
    {"content": "Step 0: Clear implementation todos", "status": "completed", "priority": "high"},
    {"content": "Step 1: Check PR state", "status": "completed", "priority": "critical"},
    {"content": "Step 2: Collect sub-issues", "status": "completed", "priority": "high"},
    {"content": "Step 3: Version bump", "status": "completed", "priority": "medium"},
    {"content": "Step 4: Generate changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 5: Stage changelog", "status": "completed", "priority": "medium"},
    {"content": "Step 6: Squash to single commit", "status": "completed", "priority": "high"},
    {"content": "Step 7: Push to remote", "status": "completed", "priority": "high"},
    {"content": "Step 8: Create PR", "status": "in_progress", "priority": "high"},
    {"content": "Step 9: Report URL and HALT", "status": "pending", "priority": "medium"},
])
```

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

### Step 8.5: Verify Closing Keywords (MANDATORY)

**⚠️ CRITICAL: Every PR MUST include at least one closing keyword.**

A PR cannot be created if its body lacks a GitHub closing keyword. This ensures linked issues are automatically closed on merge.

**Closing Keywords:**

- `Fixes #N` — Closes issue when PR merges (most common)
- `Closes #N` — Alternative syntax
- `Resolves #N` — Alternative syntax

**Verification:**

```python
# Verify PR body includes closing keyword
pr_body = f"""## Summary

{subtask_result['summary']}

## Changes

{subtask_result['changelog']}

Fixes #{parent_issue}
"""

has_closing_keyword = any(
    keyword in pr_body
    for keyword in ['Fixes #', 'Closes #', 'Resolves #']
)

if not has_closing_keyword:
    # Add parent issue as Fixes reference
    pr_body += f"\n\nFixes #{parent_issue}"
```

**✅ GATE: Closing keyword present. Proceed to Clear TODO List.**

**✅ GATE: PR created. Proceed to Clear TODO List.**

### Step 9: Clear TODO List (MANDATORY - FIRST)

**⚠️ CRITICAL: This step MUST be done FIRST after PR creation, BEFORE any reporting.**

```python
todowrite(todos=[])
```

**Why:** PR creation workflow is complete. No todo tracking needed for the final report step. Clearing ensures clean state before HALT.

**✅ GATE: TODO list cleared. Proceed to Generate Summary.**

### Step 10: Generate Summary (SECOND)

**⚠️ CRITICAL: Generate the executive summary BEFORE displaying anything.**

Use the `changelog-generator` subtask result from Step 4 to build the summary:

```markdown
**Summary:**

<1-2 sentences describing stakeholder value>
```

**Summary content (use subtask results):**

- Extract stakeholder value from `subtask_result['summary']`
- Focus on WHAT changed and WHY it matters
- Keep to 1-2 sentences (concise)

**✅ GATE: Summary generated. Proceed to Display Output.**

### Step 11: Display Output in Chat (THIRD - FINAL OUTPUT)

**⚠️ CRITICAL: OUTPUT FORMAT ENFORCEMENT - ZERO TOLERANCE**

**The output MUST be EXACTLY the format below, displayed IN THIS ORDER, NOTHING ELSE.**

**🚫 FORBIDDEN (CRITICAL VIOLATION):**

- ANY output before Step 9 (Clear TODO) is complete
- ANY output before Step 10 (Generate Summary) is complete
- "✅ Pre-PR Checklist Completed" or verification checklists
- "PR state: open" or intermediate step outputs
- "Sub-issues collected" or workflow step details
- "Creating PR..." or progress messages
- ANY content NOT in exact format below

**✅ REQUIRED OUTPUT ORDER (MANDATORY SEQUENCE):**

After PR creation completes, display IN THIS EXACT ORDER:

```
1. Clear todowrite list (Step 9 - already done)
2. Generate summary (Step 10 - already done)
3. Display in chat:

**Summary:**

<1-2 sentences describing stakeholder value>

**Outcome:** <What changed for stakeholders>

https://github.com/<owner>/<repo>/pull/<number>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

4. HALT (Step 12)
```

**Format Requirements (CRITICAL - ENFORCED ORDER):**

| Order | Content | Notes |
|-------|---------|-------|
| 1 | **Summary:** | Executive summary describing stakeholder value |
| 2 | **Outcome:** | What changed for stakeholders |
| 3 | **PR URL** | The pull request URL (newline BEFORE byline) |
| 4 | **---** | Separator |
| 5 | **Byline** | AI agent attribution (LAST line) |

**🚫 Output order violations (CRITICAL):**

- URL BEFORE summary = WRONG
- Byline BEFORE URL = WRONG
- Summary AFTER URL = WRONG
- Additional content of ANY kind = WRONG
- ANY output before clearing TODO list = WRONG

**Why This Order:**

- Clear TODO list FIRST (prevents stale state confusion)
- Generate summary SECOND (ensures content is ready)
- Display output THIRD (all components ready, clean state)
- URL comes AFTER summary/outcome (provides navigation AFTER context)
- Byline comes LAST (attribution is final element)
- HALT after display (no further action)

**✅ REPORT COMPLETE. Proceed to HALT.**

### Step 12: HALT (MANDATORY - NO EXCEPTIONS)

**After displaying the chat output, HALT immediately.**

**DO NOT:**

- Ask the developer for next steps
- Suggest merging the PR
- Create additional files
- Make additional commits
- Proceed with any other workflow

**WAIT for:**

- Developer to review PR
- Developer to say "PR merged" (then invoke `cleanup` task)

**This is the END of the PR creation workflow. NO further action without explicit user instruction.**

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
