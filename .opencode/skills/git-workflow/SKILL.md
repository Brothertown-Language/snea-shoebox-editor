---
name: git-workflow
description: Handles pre-work git branch, git stash, work, git squash commit for PR, etc work as dictated by the guidelines. Automatically invoked when user approves implementation or requests PR creation.
license: MIT
compatibility: opencode
---

# Skill: git-workflow

Git Workflow Enforcer ensuring all git operations follow the repository's strict branch-first, stash-first, squash-merge workflow. Invoked automatically before implementation and when PR creation is requested.

## When to Use

- User says "approved" or "go" (pre-work phase - AUTO)
- Implementation completes (review-prep phase - AUTO)
- User says "create a PR" or "pr" (pr-creation phase)
- PR merge confirmed (cleanup phase - AUTO)

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-work` | Verify branch state, stash changes (with --include-untracked), create feature branch | ~700 |
| `implementation` | Handle grouped commits during implementation, WIP commits before HALT | ~500 |
| `review-prep` | Push branch, generate compare URL, post to issue AND chat | ~620 |
| `commit-prep` | Prepare squash commit message (read-only) | ~480 |
| `pr-creation` | Squash, push, create PR with changelog via subtask | ~900 |
| `cleanup` | Delete merged branches, clean stale refs | ~800 |

## Invocation

- `/skill git-workflow --task pre-work` - **BEFORE implementation starts** (automatic via approval-gate)
- `/skill git-workflow --task implementation` - During implementation work
- `/skill git-workflow --task review-prep` - **AFTER implementation done** (automatic, no decision point)
- `/skill git-workflow --task commit-prep` - When user says "commit"
- `/skill git-workflow --task pr-creation` - When user says "create a PR" or "pr"
- `/skill git-workflow --task cleanup` - After PR merge confirmed
- `/skill git-workflow` - Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is referenced when:

   - User says `approved`, `go`, or similar authorization
   - User says `create a PR`, `pr`, or similar PR request
   - Implementation completes (review-prep task invoked automatically)
   - DO NOT prompt for invocation - the skill is triggered automatically

1. **Phase sequence:**

   - Phase 1: Pre-Work (mandatory first) → `pre-work` task
   - Phase 2: Implementation (user-driven) → agent performs work
   - Phase 3: Review Prep (mandatory, automatic) → `review-prep` task **NO DECISION POINT**
   - Phase 4: Commit Prep (user-initiated) → `commit-prep` task
   - Phase 5: PR Creation (user-initiated) → `pr-creation` task
   - Phase 6: Branch Cleanup (after merge) → `cleanup` task

## Automatic Invocation Triggers

**This skill MUST be invoked automatically (no user prompt) at these enforcement points:**

| Trigger Point | Action | Verification |
|---------------|--------|--------------|
| **After implementation completes** | Load skill → `review-prep` task | Push branch, generate compare URL, HALT |
| **Before ANY git branch operation** | Load skill → `pre-work` task | Verify branch state, stash changes |
| **When user says "create a PR"** | Load skill → `pr-creation` task | Squash to single commit, push, create PR, HALT |
| **After PR merge confirmed** | Load skill → `cleanup` task | Verify merge via GitHub API, close issues, delete branches |

**Enforcement:** Do NOT proceed with git operations at these trigger points without first loading this skill and verifying workflow compliance.

### ⚠️ MANDATORY: review-prep Is Automatic (No Decision Point)

**After implementation completes, the agent MUST automatically invoke review-prep — there is NO choice.**

The sequence is FIXED:

1. Implementation task finishes all file changes
2. Implementation task commits AND pushes the branch
3. Implementation task reports completion
4. **review-prep is invoked AUTOMATICALLY** → generates compare URL → HALTs

**DO NOT:**
- Skip review-prep because "changes are trivial"
- Skip review-prep because "developer can review via git log"
- Skip review-prep and proceed directly to PR creation
- Ask developer "do you want to review?" — just do it

**The compare URL is MANDATORY visibility for developers before PR creation.**

## Critical Workflow Sequence

**🚫 CRITICAL: Skipping phases or HALT points is a CRITICAL GUIDELINE VIOLATION.**

### Mandatory Sequence (NO EXCEPTIONS)

```
Implementation complete
    ↓
review-prep invoked AUTOMATICALLY (Phase 3)
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
git log origin/main..HEAD --oneline

# Step 2: If MORE THAN ONE commit shown, SQUASH NOW
git reset --soft origin/main
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

1. **Close issue directly with verification comment:**

   ```markdown
   🤖 ✅ Completed by <AgentName> (<ModelID>)

   **Summary:**

   Verified all proposed changes were already implemented. No modifications needed.

   **Verification Results:**

   - [File:line references for existing content]
   - [Confirmation of each spec requirement]

   **Outcome:** Spec verified complete without additional changes.
   ```

1. **Use `state_reason: "completed"` when closing:**

   - Indicates successful completion (not cancellation)

1. **Report completion in chat and HALT:**

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
