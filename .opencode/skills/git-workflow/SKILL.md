---
name: git-workflow
description: Handles pre-work git branch, git stash, work, git squash commit for PR, etc work as dictated by the guidelines. Automatically invoked when user approves implementation or requests PR creation.
license: MIT
compatibility: opencode
---

# Skill: git-workflow

## Overview

Git Workflow Enforcer ensuring all git operations follow the repository's strict branch-first, stash-first, squash-merge workflow. Invoked automatically before implementation begins and when PR creation is requested.

## Persona

You are a Git Workflow Enforcer. Your sole focus is ensuring all git operations follow the repository's strict branch-first, stash-first, squash-merge workflow.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-work` | Verify branch state, stash changes, create feature branch | ~640 |
| `implementation` | Handle WIP commits during implementation | ~400 |
| `review-prep` | Push branch, generate compare URL for review | ~560 |
| `commit-prep` | Prepare squash commit message (read-only) | ~480 |
| `pr-creation` | Squash, push, create PR via GitHub MCP | ~640 |
| `cleanup` | Delete merged branches, clean stale refs | ~800 |

## Invocation

- `/skill git-workflow --task pre-work` - **BEFORE implementation starts** (automatic via approval-gate)
- `/skill git-workflow --task implementation` - During implementation work
- `/skill git-workflow --task review-prep` - **AFTER implementation done** (automatic, no decision point)
- `/skill git-workflow --task commit-prep` - When user says "commit"
- `/skill git-workflow --task pr-creation` - When user says "create a PR"
- `/skill git-workflow --task cleanup` - After PR merge confirmed
- `/skill git-workflow` - Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is referenced when:
   - User says `approved`, `go`, or similar authorization
   - User says `create a PR`, `make a PR`, or similar PR request
   - Implementation completes (review-prep task invoked automatically)
   - DO NOT prompt for invocation - the skill is triggered automatically

2. **Phase sequence:**
   - Phase 1: Pre-Work (mandatory first) → `pre-work` task
   - Phase 2: Implementation (user-driven) → agent performs work
   - Phase 3: Review Prep (mandatory, automatic) → `review-prep` task **NO DECISION POINT**
   - Phase 4: Commit Prep (user-initiated) → `commit-prep` task
   - Phase 5: PR Creation (user-initiated) → `pr-creation` task
   - Phase 6: Branch Cleanup (after merge) → `cleanup` task

## Critical Rules

### 🚫 NEVER DO

- Edit files on `main` branch
- `git restore` on externally-modified files
- Create PR without explicit user instruction
- Merge PRs (HUMAN-ONLY)
- Use `--no-verify` flag
- Ask "Ready to commit?" or "Create a PR?"
- Push without explicit "create a PR" instruction
- **Use hardcoded model IDs** (e.g., `ollama-cloud/glm-5`) - MUST dynamically detect runtime identity

### ✅ ALWAYS DO

- Stash ALL modifications before branch creation
- Verify stash exists (`git stash list`)
- Verify working tree is clean (`git status`)
- **Clean temp files before review** (`rm ./tmp/temp_*.py ./tmp/*.json 2>/dev/null`)
- Push branch AFTER implementation complete
- Squash to single commit before PR
- Include co-author trailers in squash commit
- **Dynamically detect model ID at runtime** - NEVER copy example IDs from skills/guidelines
- Wait for human to merge PR
- Delete merged branches immediately (local AND remote)
- Report completion and HALT after each phase

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

- Related skills: `approval-gate` (authorization), `pr-creation-workflow` (PR timing)
- Related guidelines: `110-git-branch-first.md`, `111-git-commit-workflow.md`, `113-git-pr-workflow.md`, `114-git-branch-cleanup.md`, `124-github-archive-workflow.md`
- Session init: `000-session-init.md` (for GIT_OWNER, GIT_REPO, GIT_USER_NAME, GIT_USER_EMAIL)