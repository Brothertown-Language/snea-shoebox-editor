______________________________________________________________________

## name: git-workflow description: Git Workflow Enforcer ensuring all git operations follow the repository's strict branch-first, stash-first, squash-merge workflow. Invoked automatically before implementation and when PR creation is requested. license: MIT compatibility: opencode

# Skill: git-workflow

Git Workflow Enforcer ensuring all git operations follow the repository's strict branch-first, stash-first, squash-merge workflow.

## ⚠️ CRITICAL: THIS SKILL IS MANDATORY - NO BYPASS {#critical-skill}

**Bypassing this skill is a CRITICAL GUIDELINE VIOLATION.**

At workflow trigger points, the agent MUST invoke this skill - NOT run git commands manually.

**🚫 NEVER BYPASS:**

- Run `git checkout -b` manually → MUST invoke `pre-work` task
- Stop after reading files → MUST invoke `review-prep` task
- Squash/push/create PR manually → MUST invoke `pr-creation` task
- Close issues after "merged" → MUST invoke `cleanup` task

**Manual operations at these points = CRITICAL VIOLATION.**

______________________________________________________________________

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| After approval ("approved" or "go") | `/skill git-workflow --task pre-work` | Stash changes, create feature branch |
| After implementation completes | `/skill git-workflow --task review-prep` | Push branch, generate compare URL, HALT |
| User says "create a PR" | `/skill git-workflow --task pr-creation` | Squash to single commit, push, create PR, HALT |
| User says "PR merged" | `/skill git-workflow --task cleanup` | Close issues, delete branches |

## Tasks

| Task | Purpose | Words | Subtasks |
|------|---------|-------|----------|
| `pre-work` | Verify branch state, stash changes, create feature branch | ~130 | `verify-stash-branch` |
| `implementation` | Handle grouped commits during implementation, WIP commits before HALT | ~500 | — |
| `review-prep` | Push branch, generate compare URL, post to issue AND chat | ~250 | — |
| `commit-prep` | Prepare squash commit message (read-only) | ~480 | — |
| `pr-creation` | Squash, push, create PR with changelog | ~220 | `check-pr-state`, `collect-sub-issues` |
| `cleanup` | Delete merged branches, verify issue structure, hotfix dev-merge ticket | ~240 | `verify-sub-issues` |

### Subtask Architecture

**Context efficiency through isolation:**

Complex workflow steps are isolated in focused subtasks (~70-190 lines) to:

1. Keep main task files concise (~130-220 lines)
2. Isolate complex logic (PR state verification, issue structure verification)
3. Reduce context window usage at any given time
4. Enable reusable verification components

**Subtask invocation pattern:**

```
/task subagent_type="general" description="Subtask name" prompt="Use the git-workflow skill <subtask-name> subtask to <purpose>."
```

**Available subtasks:**

| Subtask | Purpose | Invoke From |
|---------|---------|-------------|
| `check-pr-state` | Check if branch has existing PR (open/merged/closed) | `pr-creation` |
| `collect-sub-issues` | Collect sub-issues for multi-task spec PR body | `pr-creation` |
| `verify-stash-branch` | Verify clean working tree and preserve external changes | `pre-work` |
| `verify-sub-issues` | Verify parent/child issue structure before closing parent | `cleanup` |

**Return format:**

Subtasks return structured JSON to calling task:

```json
{
  "success": true,
  "field1": "value1",
  "field2": "value2"
}
```

**Error handling:**

Subtasks return structured error information:

```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional context"
}
```

**Todo tracking (optional):**

Subtasks may use `todowrite` tool for progress tracking, but this is internal to the subtask context and does not pollute the main task context.

## Invocation

- `/skill git-workflow --task pre-work` - **BEFORE implementation starts** (automatic via approval-gate)
- `/skill git-workflow --task implementation` - During implementation work
- `/skill git-workflow --task review-prep` - **AFTER implementation done** (automatic, no decision point)
- `/skill git-workflow --task commit-prep` - When user says "commit"
- `/skill git-workflow --task pr-creation` - When user says "create a PR" or "pr"
- `/skill git-workflow --task cleanup` - **When user says "pr merged" or "merged"** (automatic)
- `/skill git-workflow` - Overview only

## This Skill's Tasks

**`pre-work`**: Use after authorization. Verifies branch state, stashes external changes (with --include-untracted), creates feature branch from dev.

**`implementation`**: Use during work. Handles grouped commits, WIP commits before HALT, executive summaries after completion.

**`review-prep`**: Use after implementation completes (automatic). Pushes branch, generates GitHub compare URL, posts to issue AND chat, HALTs for developer review.

**`commit-prep`**: Use when user says "commit". Prepares squash commit message by reading commit history (read-only, no commits).

**`pr-creation`**: Use when user says "create a PR" or "pr". Squashes to single commit, pushes, creates PR with changelog, HALTs.

**`cleanup`**: Use when user says "pr merged" or "merged" (automatic). Verifies merge via GitHub API, creates hotfix dev-merge ticket if applicable, closes issues, deletes local and remote branches.

## Workflow Context

**Phase Sequence:**

1. `pre-work` → Create branch, verify clean state
2. `implementation` → Agent performs work, grouped commits
3. `review-prep` (automatic) → Push, generate compare URL, HALT
4. `commit-prep` (optional) → Prepare commit message
5. `pr-creation` (user-initiated) → Squash, push, create PR, HALT
6. `cleanup` (after merge) → Close issues, delete branches

- `/skill git-workflow --task review-prep` - **AFTER implementation done** (automatic, no decision point)
- `/skill git-workflow --task commit-prep` - When user says "commit"
- `/skill git-workflow --task pr-creation` - When user says "create a PR" or "pr"
- `/skill git-workflow --task cleanup` - **When user says "pr merged" or "merged"** (automatic)
- `/skill git-workflow` - Overview only

## Workflow Triggers

**Invoke this skill at these triggers:**

- User says `approved`, `go`, or similar authorization
- User says `create a PR`, `pr`, or similar PR request
- Implementation completes (invoke review-prep task)
- DO NOT prompt for invocation - invoke at these triggers

1. **Phase sequence:**

   - Phase 1: Pre-Work (mandatory first) → `pre-work` task
   - Phase 2: Implementation (user-driven) → agent performs work
   - Phase 3: Review Prep (mandatory, automatic) → `review-prep` task **NO DECISION POINT**
   - Phase 4: Commit Prep (user-initiated) → `commit-prep` task
   - Phase 5: PR Creation (user-initiated) → `pr-creation` task
   - Phase 6: Branch Cleanup (after merge) → `cleanup` task

## Enforcement Points

**Invoke this skill at these triggers (no user prompt needed):**

| Trigger Point | Action | Verification |
|---------------|--------|--------------|
| **Before ANY git branch operation** | Load skill → `pre-work` task | Verify branch state, stash changes |
| **After implementation completes** | Load skill → `review-prep` task | Push branch, generate compare URL, HALT |
| **When user says "create a PR"** | Load skill → `pr-creation` task | Squash to single commit, push, create PR, HALT |
| **When user says "pr merged" or "merged"** | Load skill → `cleanup` task | Verify merge via GitHub API, close issues, delete branches |

**Enforcement:** Do NOT proceed with git operations at these trigger points without first loading this skill and verifying workflow compliance.

### ⚠️ CRITICAL: POST-IMPLEMENTATION WORKFLOW IS MANDATORY

**After implementation completes, the agent MUST invoke `/skill git-workflow --task review-prep`.**

This is NOT optional. This is NOT a decision point. This is MANDATORY.

**Violation = CRITICAL GUIDELINE VIOLATION:**

- Silent HALT after implementation = SKIPPED WORKFLOW
- No compare URL posted = SKIPPED WORKFLOW
- No GitHub comment posted = SKIPPED WORKFLOW
- Agent just "finished reading files" = SKIPPED WORKFLOW

**NO EXCEPTIONS:**

- Not "trivial changes"
- Not "developer can use git log"
- Not "I already reviewed"
- **ALWAYS INVOKE THE SKILL**

### ⚠️ MANDATORY: review-prep Invoked After Implementation (No Decision Point)

**After implementation completes, the agent MUST invoke review-prep — there is NO choice.**

The sequence is FIXED:

1. Implementation task finishes all file changes
2. Implementation task commits AND pushes the branch
3. Implementation task reports completion
4. **review-prep is invoked** → generates compare URL → HALTs

**DO NOT:**

- Skip review-prep because "changes are trivial"
- Skip review-prep because "developer can review via git log"
- Skip review-prep and proceed directly to PR creation
- Ask developer "do you want to review?" — just do it

**The compare URL is MANDATORY visibility for developers before PR creation.**

### ⚠️ MANDATORY: cleanup Invoked After "PR merged" (No Decision Point)

**When user says "pr merged", "merged", or similar confirmation, the agent MUST invoke cleanup — there is NO choice.**

The sequence is FIXED:

1. User confirms PR merge with "pr merged", "merged", or similar
2. **cleanup is invoked** → verifies merge via GitHub API
3. cleanup closes issues, deletes branches, creates hotfix tickets if needed
4. cleanup reports completion

**DO NOT:**

- Run manual `git` commands for cleanup (branch deletion, issue closure)
- Ask developer "should I delete the branch?" — just do it
- Skip GitHub API verification (use `github_pull_request_read(method="get")`)
- Close issues before verifying PR merge via API
- Delete branches before closing issues
- Leave merged branches undeleted after merge

**The cleanup task is the ONLY authorized method for post-merge operations.**

## Critical Workflow Sequence

**🚫 CRITICAL: Skipping phases or HALT points is a CRITICAL GUIDELINE VIOLATION.**

### Mandatory Sequence (NO EXCEPTIONS)

```
Implementation complete
    ↓
review-prep invoked (Phase 3)
    ↓
Push branch → Generate compare URL → HALT
    ↓
(DEVELOPER REVIEWS VIA GITHUB DIFF)
    ↓
Developer says "create a PR"
    ↓
pr-creation: Squash → Push → Create PR → HALT
    ↓
(DEVELOPER MERGES PR)
    ↓
Developer confirms "PR merged"
    ↓
cleanup: Verify merge via GitHub API → Close issues
```

### What HALT Means

**HALT = Stop all further action and wait for explicit instruction.**

| HALT Point | What Agent Does | What Agent WAITS For |
|------------|----------------|----------------------|
| After review-prep | Post compare URL + completion comment | "create a PR" instruction |
| After pr-creation | Post PR URL | "PR merged" confirmation |
| After PR merged | Close issues | Next explicit instruction |

### 🚫 CRITICAL VIOLATIONS

| Violation | Consequence |
|-----------|-------------|
| Skip review-prep | No developer visibility, premature PR |
| Skip HALT after push | Issues closed without PR |
| Close issues without PR merge | Lost tracking, audit trail broken |
| Skip GitHub API verification | Closing issues on unmerged PRs |

## Critical Rules

### 🚫 NEVER DO

- Edit files on `main` branch
- `git restore` on externally-modified files
- Create PR without explicit user instruction
- Create PR without squashing to SINGLE COMMIT first
- Create PR without closing keyword (`Fixes #N`, `Closes #N`, or `Resolves #N`)
- Merge PRs (HUMAN-ONLY)
- Use `--no-verify` flag
- Ask "Ready to commit?" or "Create a PR?"
- Close issues without PR merge verification
- **Use hardcoded model IDs** (e.g., `ollama-cloud/glm-5`) - MUST dynamically detect runtime identity

### ✅ ALWAYS DO

- Stash ALL modifications before branch creation
- Verify stash exists (`git stash list`)
- Verify working tree is clean (`git status`)
- **SQUASH TO SINGLE COMMIT BEFORE ANY PR** — See `pr-creation-workflow` skill for pre-PR checklist
- **INCLUDE CLOSING KEYWORD IN PR BODY** — Every PR MUST have `Fixes #N`, `Closes #N`, or `Resolves #N`
- **Commit ALL changes before pushing** (`git add -A && git commit`)
- **Push after committing** - ensures GitHub compare works correctly
- **Clean temp files before review** (`rm ./tmp/temp_*.py ./tmp/*.json 2>/dev/null`)
- Include co-author trailers in squash commit
- **Dynamically detect model ID at runtime** - NEVER copy example IDs from skills/guidelines
- Wait for human to merge PR
- Delete merged branches immediately (local AND remote)
- Report completion and HALT after each phase

### ⚠️ SQUASH IS MANDATORY — NO EXCEPTIONS

**Every PR must have EXACTLY ONE commit. No exceptions.**

**Before creating ANY PR:**

```bash
# Step 1: Verify commit count
git log origin/dev..HEAD --oneline

# Step 2: If MORE THAN ONE commit shown, SQUASH NOW
git reset --soft origin/dev
git commit -m "<descriptive message>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"

# Step 3: Force push the single commit
git push --force-with-lease origin <branch>
```

**See `pr-creation-workflow` skill for the complete pre-PR checklist.**

### ⚠️ Edge Case: Already Implemented (No Changes)

**When spec investigation reveals all changes are already present:**

1. **Skip branch creation entirely:**

   - Do NOT create feature branch
   - Do NOT push anything
   - Do NOT create PR

2. **Close issue directly with verification comment:**

   ```markdown
   🤖 ✅ Completed by <AgentName> (<ModelID>)

   **Summary:**

   Verified all proposed changes were already implemented. No modifications needed.

   **Verification Results:**

   - [File:line references for existing content]
   - [Confirmation of each spec requirement]

   **Outcome:** Spec verified complete without additional changes.
   ```

3. **Use `state_reason: "completed"` when closing:**

   - Indicates successful completion (not cancellation)

4. **Report completion in chat and HALT:**

   - No further workflow steps needed

## Task Dependencies

```
pre-work → implementation → review-prep → [commit-prep] → pr-creation → cleanup
                                          ↓
                                    (user says "commit")
                                                    ↓
                                              (user says "create a PR")
                                                    ↓
                                              (user confirms "PR merged")
```

**Dependency Notes:**

- `commit-prep` is optional (user may skip by saying "create a PR" directly)
- `cleanup` waits for human merge confirmation
- `review-prep` is mandatory after implementation

## Cross-References

- Related skills: `approval-gate` (authorization scope, WIP commits before HALT), `pr-creation-workflow` (PR timing)
- Related guidelines: `110-git-branch-first.md`, `111-git-commit-workflow.md` (WIP commit before HALT), `113-git-pr-workflow.md`, `114-git-branch-cleanup.md`, `124-github-archive-workflow.md`
- Session init: `000-session-init.md` (for GIT_OWNER, GIT_REPO, DEV_NAME, DEV_EMAIL)
