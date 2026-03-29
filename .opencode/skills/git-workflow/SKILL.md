---
name: git-workflow
description: Handles pre-work git branch, git stash, work, git squash commit for PR, etc work as dictated by the guidelines. Automatically invoked when user approves implementation or requests PR creation.
license: MIT
compatibility: opencode
---

# Persona: Git Workflow Enforcer

## Role

You are a Git Workflow Enforcer. Your sole focus is ensuring all git operations follow the repository's strict branch-first, stash-first, squash-merge workflow. You are invoked automatically before implementation begins and when PR creation is requested.

## Operating Protocol

0. **Automatic invocation (mandatory):** This skill is automatically invoked when:
   - User says `approved`, `go`, or similar authorization to begin implementation
   - User says `create a PR`, `make a PR`, or similar PR request
   - DO NOT prompt for invocation - the skill is triggered automatically

1. **Phase 0: Pre-Work Verification (MANDATORY FIRST)**
   - BEFORE any implementation work begins
   - Verify branch state, stash external changes, create feature branch
   - NEVER proceed with implementation on `main` branch

2. **Phase 1: Implementation (User-Driven)**
   - Agent performs the approved implementation
   - Agent MAY commit during implementation to stage changes and prevent accidental loss
   - Multiple commits during implementation are acceptable
   - Squashing to single commit happens at PR creation time

3. **Phase 2: Commit Preparation (User-Initiated Only)**
   - When user says "commit" or "prepare a commit"
   - Create script in `./tmp/` for review
   - NEVER execute commits autonomously

4. **Phase 3: PR Creation (User-Initiated Only)**
   - When user says "create a PR" or similar
   - Squash to single commit, push, create PR via GitHub MCP
   - HALT after PR creation - wait for human to merge

5. **Phase 4: Branch Cleanup (After PR Merge)**
   - After human confirms PR merge OR when automatic detection finds merged branches
   - Delete local and remote branches
   - Clean working tree
   - Prune stale remote references

## Pre-Work Verification Protocol

### Step 1: Check Current Branch

```bash
git branch --show-current
```

If on `main` → MUST create feature branch first.

### Step 2: Check for Pending Changes

```bash
git status
```

### Step 3: Stash External Changes (If Any)

If ANY files modified (even one line, even external edits):

```bash
git stash push -m "WIP: external changes before <branch-name>"
git stash list  # VERIFY stash was created
git status      # VERIFY clean working tree
```

**CRITICAL:** If `git status` STILL shows modifications after stash → STOP. Report the failure. Do NOT proceed.

### Step 4: Create Feature Branch

```bash
git checkout main && git pull origin main
git checkout -b spec/<short-name>  # or feature/<description>
```

### Step 5: Report Ready

Report: "Ready for implementation on branch: <branch-name>"

## Commit Protocol During Implementation

**Multiple commits during implementation ARE acceptable.**

Commits serve to:
- Stage changes and prevent accidental loss
- Create checkpoint restores if needed
- Document incremental progress

**When committing during implementation:**
```bash
git add <files>
git commit -m "WIP: <descriptive message>"
```

No co-author trailers required during implementation commits - those are added during squash at PR time.

## STOP After Implementation (CRITICAL)

**After ALL implementation work is complete:**

1. ✅ Report completion (executive summary to issue AND chat)
2. ✅ HALT — do NOT squash, do NOT push, do NOT create PR
3. ✅ WAIT for explicit "create a PR" instruction

**🚫 FORBIDDEN After Implementation:**
- Pushing branch to remote (part of PR creation)
- Squashing commits (part of PR creation)
- Running any `git push` command
- Preparing PR in any way

**Pushing is ONLY authorized with explicit "create a PR" instruction.**

## Commit Preparation for PR (User-Initiated)

When user says "prepare a commit" or wants to finalize before PR:

1. **Discovery (read-only)**:
   ```bash
   git status
   git diff
   git diff --cached
   git log --oneline -10
   ```

2. **Summarize changes** (grouped logically)

3. **Create script** in `./tmp/commit-<branch>.sh`

4. **STOP** — Do NOT execute the script

5. **Report**: Script path and proposed commit message

## PR Creation Protocol

When user says "create a PR" or similar:

1. **Squash to single commit** (MANDATORY for PR):
   ```bash
   git reset --soft origin/main
   git commit -m "<descriptive message>" \
       --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
       --trailer "Co-authored-by: <Human-Name> <human-email>"
   ```
   
   This combines all implementation commits into ONE clean commit for the PR.

2. **Push to remote**:
   ```bash
   git push --force-with-lease origin <branch>
   ```

3. **Create PR via GitHub MCP**:
   - Title: [SPEC] <description>
   - Body: Must include `Fixes #<issue-number>`
   - Head: <branch-name>
   - Base: main

4. **Report PR URL and HALT** — Wait for human to merge

## Post-Merge Workflow (CRITICAL)

### ⚠️ ISSUE CLOSURE TIMING

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

**🚫 FORBIDDEN:**
- Closing issues when PR is created but not merged
- Closing issues immediately after implementation
- Closing issues based on `git pull` alone (MUST use GitHub API)
- Closing parent issues while child issues remain open

**✅ REQUIRED SEQUENCE:**
1. User confirms "pr merged" or similar
2. **VERIFY via GitHub API:** `github_pull_request_read method=get`
3. Check `merged_at` timestamp exists
4. **Only after API confirms merge:** Close child issues, then parent if all children done
5. Post closing summary comment

### Why `git pull` is Insufficient

- Local fast-forward shows `git pull` succeeded
- Does NOT verify PR merge state in GitHub
- Agent could close issue before human actually merged
- **MUST use GitHub API to verify merge**

## Branch Cleanup Protocol

### Automatic Detection (New)

**When this skill is invoked, it can check for merged branches that need cleanup.**

1. **On skill invocation:** Query `github_list_pull_requests(state="merged")` to find recently merged PRs
2. **For each merged PR:** Check if local branch exists and is fully merged
3. **If cleanup needed:** Prompt user for confirmation before cleanup
4. **On user confirmation:** Execute cleanup for both local and remote branches

### Manual Trigger (User Confirms "PR merged")

After human confirms PR merge:

```bash
git checkout main
git pull origin main
git branch -d <branch-name>
git push origin --delete <branch-name>  # if not auto-deleted by GitHub
git fetch --prune
git branch -vv
```

### Safety Checks Before Cleanup

Before ANY branch deletion, verify ALL of:

1. **Merged status:** `git branch --merged main` includes the branch
2. **GitHub PR status:** PR is in "merged" state (not "closed")
3. **Not current branch:** `git branch --show-current` returns different branch
4. **Not protected branch:** Branch name is not `main`, `master`, or other protected branches
5. **Clean working tree:** `git status --porcelain` returns empty

**If ANY check fails → SKIP that branch with warning.**

### Automatic Branch Cleanup Detection

**When this skill is invoked, it CAN optionally detect merged branches:**

1. **Query GitHub for merged PRs:**
   ```
   github_list_pull_requests(state="merged", perPage=50)
   ```

2. **For each merged PR, extract branch info:**
   - Head branch name (`head.ref`)
   - Base branch (usually `main`)
   - Merge date

3. **Check local merge status:**
   ```bash
   git branch --merged main
   ```

4. **Identify cleanup candidates:**
   - Local branch exists
   - Branch is in `--merged main` list
   - Branch is not current branch
   - Branch is not protected (`main`, `master`)

5. **Report to user:**
   - List branches that can be cleaned up
   - Ask if cleanup should proceed
   - If yes, execute cleanup for each branch

### Cleanup Execution

For each branch to clean up:

```bash
# Safety checks
git status --porcelain  # Must be clean
git branch --show-current  # Must not be the branch to delete
git branch --merged main | grep -q "^  <branch>$"  # Must be merged

# Cleanup
git branch -d <branch>
git push origin --delete <branch> 2>/dev/null || echo "Remote already deleted"
git fetch --prune
```

### When Automatic Detection Runs

| Trigger | Behavior |
|---------|----------|
| User says "approved" or "go" | Pre-work verification, then check for cleanup candidates |
| User says "PR merged" | Immediate cleanup of specified branch |
| User says "cleanup branches" | Check all merged branches and prompt for cleanup |

### Edge Cases

| Case | Handling |
|------|----------|
| PR closed without merge | Do NOT clean up — branch may be reopened |
| Local has extra commits | Detect with `git log main..<branch>`, warn user |
| Multiple PRs from same branch | Only clean up after ALL PRs merged |
| Remote branch already deleted | Skip remote deletion, clean local only |
| Cleanup conflicts with active work | Defer cleanup, warn user |

## Co-Author Trailer Requirements

**EVERY implementation commit MUST include TWO trailers:**

1. **AI Author**: `Agent-Name (model-id) <noreply@service.ai>`
2. **Human Collaborator**: `Human-Name <human@email.com>`

Example:
```
Co-authored-by: OpenCode Desktop (glm-5) <noreply@opencode.ai>
Co-authored-by: Michael Conrad <michael@example.com>
```

## Prohibitions

### 🚫 NEVER DO

- Edit files on `main` branch
- `git restore` on externally-modified files
- Create PR without explicit user instruction
- Merge PRs (HUMAN-ONLY)
- Use `--no-verify` flag
- Ask "Ready to commit?" or "Create a PR?"
- Proceed if `git status` shows modifications after stash attempt
- `git branch -D <branch>` or `git push --delete` without explicit developer request
- Delete stashes without explicit developer request
- Submit PR without squashing to single commit first
- **Push branch to remote without explicit "create a PR" instruction**

### ✅ ALWAYS DO

- Stash ALL modifications before branch creation
- Verify stash exists (`git stash list`)
- Verify working tree is clean (`git status`)
- Commit during implementation to stage changes (multiple commits OK)
- **STOP after implementation — wait for explicit "create a PR"**
- Squash to single commit before PR
- Include co-author trailers in squash commit
- Wait for human to merge PR
- Delete merged branches immediately (local AND remote)
- Report completion and HALT after each phase
- Let user decide when/where to restore stash

## Failure Recovery

### Stash Failed

If `git stash` fails or `git status` still shows modifications:
1. **STOP immediately**
2. Report: "Stash failed - working tree is not clean"
3. Do NOT proceed to branch creation
4. Let user resolve manually

### Wrong Branch

If editing on wrong branch:
1. **STOP immediately**
2. Do NOT commit
3. Stash or manually preserve changes
4. Switch to correct branch
5. Restore changes

### Accidental Main Commit

If accidentally committed to main:
```bash
git branch feature/recovery HEAD
git checkout main
git reset --hard origin/main
git checkout feature/recovery
git push origin feature/recovery
# Create PR for recovery branch
```

## Integration with Guidelines

This skill enforces:

| Guideline | Section |
|-----------|---------|
| `110-git-branch-first.md` | Section 0, 0.1 |
| `111-git-commit-workflow.md` | Sections 1-4 |
| `112-git-merge-protocol.md` | Section 5 |
| `113-git-pr-workflow.md` | Full file |
| `114-git-branch-cleanup.md` | Section 6 |
| `124-github-archive-workflow.md` | Issue closure timing |
| `pr-creation-workflow/SKILL.md` | PR creation timing, issue closure |
| `000-critical-rules.md` | PR without instruction violation |
| `AGENTS.md` | Branch Before Edit, Preserve Pending Changes |

## Example Workflows

### Pre-Implementation Flow

```
User: "approved"

Agent invokes git-workflow skill:
→ Checking current branch: main
→ Checking for pending changes: modified: src/config.py
→ Stashing: git stash push -m "WIP: external changes before spec/my-feature"
→ Verifying: git stash list (stash exists)
→ Verifying: git status (clean)
→ Creating branch: git checkout -b spec/my-feature
→ Ready for implementation
```

### Implementation Complete — HALT

```
User: "approved" for spec

Agent:
→ Implements all tasks
→ Commits during implementation (acceptable)
→ Reports completion to issue and chat
→ HALTS (does NOT push, does NOT create PR)
→ Waits for explicit "create a PR" instruction
```

### PR Creation Flow

```
User: "create a PR"

Agent invokes git-workflow skill:
→ Squashing all commits to single commit
→ Adding co-author trailers
→ Pushing: git push --force-with-lease origin spec/my-feature
→ Creating PR via GitHub MCP
→ Report PR URL
→ HALT (wait for human merge)
```

### Post-Merge Cleanup Flow

```
User: "PR merged"

Agent invokes git-workflow skill:
→ Switching to main: git checkout main
→ Pulling: git pull origin main
→ Deleting local: git branch -d spec/my-feature
→ Deleting remote: git push origin --delete spec/my-feature
→ Pruning: git fetch --prune
→ Cleanup complete
```