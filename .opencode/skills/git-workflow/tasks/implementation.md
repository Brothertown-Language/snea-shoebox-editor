# Task: implementation

## Purpose

Handle work-in-progress commits during implementation. Multiple commits during implementation are acceptable for checkpointing.

## Todo Tracking for Multi-Phase Specs

**When implementing a multi-phase spec authorized with unqualified approval (`approved` or `go`):**

Use `todowrite` at the START of implementation to track phase progress:

```python
todowrite([
    {"content": "Phase 1: [description]", "status": "in_progress", "priority": "high"},
    {"content": "Phase 2: [description]", "status": "pending", "priority": "high"},
    # ... remaining phases
])
```

**Update todo after each phase completion:**

```python
# After Phase 1 completes
todowrite([
    {"content": "Phase 1: [description]", "status": "completed", "priority": "high"},
    {"content": "Phase 2: [description]", "status": "in_progress", "priority": "high"},
    # ... remaining phases
])
```

**Continue through ALL phases without HALT between phases.**

See `020-go-prohibitions.md` Section 6 for unqualified approval scope.

### Todo Clearing at Workflow Transitions

**Clear todos at these transition points:**

| Transition Point | Action |
|------------------|--------|
| Implementation → PR creation | Clear implementation todos (no todo needed for PR steps) |
| After PR creation | Clear PR workflow todos (waiting for human merge) |
| After cleanup | Clear all todos (workflow complete) |

**Why:** Each workflow phase has explicit steps in skills. Todo lists track implementation progress, not procedural steps.

**When to Clear:**

- **Before PR creation workflow:** `todowrite(todos=[])`
- **After cleanup workflow:** `todowrite(todos=[])`
- **After authorization (if interrupted):** `todowrite(todos=[])`

## Workflow

1. **User-driven work:** The agent performs approved implementation tasks
1. **Checkpoint commits allowed:** Commits during implementation serve to stage changes and prevent accidental loss
1. **Squashing is deferred:** Squashing to single commit happens during PR creation, not during implementation

## Preconditions

- Feature branch exists and is checked out
- Implementation authorized for this phase/task
- Working tree clean (or stashed)

## Postconditions

- All implementation work complete for authorized phase/task
- Changes committed (implementation commits acceptable)
- Ready for review and PR preparation

## Procedure

### Making Implementation Commits

Commits during implementation are checkpoint commits to prevent data loss. They do NOT need to be polished.

```bash
git add <files>
git commit -m "WIP: <descriptive message>"
```

**No co-author trailers required** during implementation commits - those are added during squash at PR time.

### ⚠️ CRITICAL: Commit Before Push

**The most common workflow failure is pushing without committing.**

**Correct sequence:**

```
1. Make file changes (edit tool, etc.)
2. git status (verify changes exist)
3. git add -A (stage changes)
4. git commit (commit changes)
5. git push (push committed branch)
```

**Incorrect sequence (CRITICAL VIOLATION):**

```
1. Make file changes
2. git push (WRONG - uncommitted changes)
   Result: Empty branch on remote
   Result: GitHub compare shows "nothing to compare"
```

**Verification before push:**

- `git status` MUST show "nothing to commit, working tree clean"
- Local branch MUST have at least one commit ahead of remote
- If `git status` shows uncommitted changes → COMMIT FIRST

## Multiple Commits Are Acceptable

| Commit Type | When | Message | Trailers |
|-------------|------|---------|----------|
| Implementation commit | During work | `WIP: description` | None |
| Squash commit | PR creation | Descriptive | Full co-author trailers |

## Important Rules

- **DO NOT squash until PR creation** - Multiple implementation commits are expected
- **DO NOT create PR without explicit instruction** - PR requires explicit "create a PR"
- **ALWAYS push after committing** - Push ensures GitHub compare works correctly

## Context Required

- Guidelines: `111-git-commit-workflow.md`
- Related skills: `approval-gate` (authorization scope)
- Related tasks: `commit-prep` (squash for PR), `pr-creation` (push and PR)

## When to Commit During Implementation

Commit when:

- Completing a discrete logical unit of work
- Reaching a checkpoint that might need rollback
- Before attempting something risky
- At natural break points in the work
- **Before ANY HALT** (awaiting approval, clarification, error, session end)

## WIP Commit Before HALT (MANDATORY)

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

### What Counts as HALT

| HALT Trigger | WIP Required? | Example |
|-------------|--------------|---------|
| Awaiting approval | ✅ YES | Mid-task, need clarifications approved |
| Awaiting clarification | ✅ YES | Question posted, waiting for answer |
| Mid-task pause | ✅ YES | Session ending, context exhausts |
| Error encountered | ✅ YES | Fixable error, need to save progress |
| Session ending | ✅ YES | Developer ending session |
| Task complete | ❌ NO | Use full commit with proper message |
| Phase complete | ❌ NO | Use full commit with proper message |

### WIP Commit Workflow

**Before ANY HALT (awaiting approval, clarification, error, session end):**

```bash
# Step 1: Check for uncommitted changes
git status

# Step 2: If changes exist, commit WIP
if git status shows changes:
    git add -A
    git commit -m "WIP: Phase N - <brief description>" \
        --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
        --trailer "Co-authored-by: <Human-Name> <human-email>"

# Step 3: Verify commit was created
git log -1 --oneline

# Step 4: Report WIP commit made
```

### WIP Commit Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Prefix** | Always starts with `WIP:` for easy identification |
| **Phase** | Includes phase number for context |
| **Description** | Brief description of what was being worked on |
| **Trailers** | Same co-author trailers as full commits |
| **Squashable** | Can be squashed or amended later with subsequent work |

### After WIP Commit

- **Continue work**: Next commit can amend or squash the WIP commit
- **Session resumes**: Rebase or continue from WIP commit
- **PR creation**: Squash WIP commits with final work before PR

## After Implementation Completes

### ⚠️ MANDATORY PUSH BEFORE HALT

**Implementation task MUST commit AND push before ANY HALT.**

**Pre-HALT Checklist:**

```bash
# Step 1: CHECK FOR UNCOMMITTED CHANGES
git status

# Step 2: COMMIT IF CHANGES EXIST
if git status shows changes:
    git add -A
    git commit -m "[Phase N] Implementation complete" \
        --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
        --trailer "Co-authored-by: <Human-Name> <human-email>"

# Step 3: CHECK FOR LOCAL COMMITS
git log origin/<branch>..HEAD --oneline

# Step 4: PUSH IF COMMITS EXIST
if output shows commits:
    git push -u origin <branch-name>

# Step 5: VERIFY PUSH
git branch -vv
# Must show: [origin/<branch>] tracking ref

# Step 6: REPORT COMPLETION
"Implementation complete. Branch pushed with X commits."
```

### Implementation Workflow Sequence

1. **Make file changes** (edit tool, etc.)
2. **Commit changes** (`git add -A && git commit`)
3. **Push to remote** (`git push -u origin <branch-name>`)
4. **Report completion** (executive summary to issue AND chat)
5. **HALT** — do NOT create PR
6. **WAIT** for explicit "create a PR" instruction

**CRITICAL: Skipping push is a ZERO TOLERANCE violation.**

**See:** `pr-creation-workflow` skill for complete PR workflow.
