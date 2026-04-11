# Task: review-prep

## Purpose

Generate GitHub compare URL for developer review AFTER the implementation task has already pushed the branch. This provides the developer with visibility into changes BEFORE deciding to create a PR.

## ⚠️ MANDATORY INVOCATION

**This task is ALWAYS invoked automatically after implementation completes. There is NO decision point.**

The sequence is:
1. Implementation complete → commit → push → **review-prep invoked automatically**
2. Compare URL generated → HALT
3. Wait for developer to say "create a PR"

**DO NOT skip this task after implementation. DO NOT ask the developer if they want review. Just generate the compare URL.**

## ⚠️ CRITICAL: This Task Is NOT Optional

**Every feature branch push MUST be followed by review-prep. No exceptions.**

**Why this is mandatory:**
- Developer needs visibility into changes before deciding to create PR
- Compare URL allows review via GitHub's superior diff viewer
- Prevents premature PR creation
- Ensures clear separation between "done implementing" and "create PR"

**When to invoke:**
- After ANY commit+push to a feature branch
- After ANY file modifications are committed and pushed
- Even if branch is "just tracking existing work"
- Even if "no changes needed" was determined
- Even if changes are documentation-only

### ⚠️ CRITICAL: Branch Must Be Pushed Before This Task

**The `implementation` task is responsible for pushing the branch.**

**Correct sequence:**
```
Implementation task:
  1. Make changes
  2. git status (verify)
  3. git add -A (stage)
  4. git commit (commit)
  5. git push -u origin <branch> (push)
  6. Report completion
  7. Invoke review-prep

Review-prep task:
  1. Verify branch is pushed
  2. Generate compare URL
  3. Post completion comment
  4. HALT
```

**If this task is invoked and branch is NOT pushed:**
1. Inform user: "Implementation task must push before review-prep"
2. Push the branch: `git push -u origin <branch-name>`
3. Continue to generate compare URL

### ⚠️ CRITICAL: NO EXCEPTIONS

**Review prep is MANDATORY regardless of:**
- Whether file changes were made
- Whether "no changes needed" was determined
- Whether branch is already up-to-date
- Whether implementation made zero modifications

**The review prep workflow provides developer visibility - it must NEVER be skipped.**

**⚠️ "No File Changes" Edge Case Clarification:**

The "Already Implemented" edge case in SKILL.md applies ONLY when **ZERO files were modified**.

| Scenario | Workflow |
|----------|----------|
| Zero files modified (all changes already present) | Skip PR workflow, close with verification |
| ANY file modified (including docs/guidelines) | FULL PR workflow REQUIRED |
| Guideline/documentation changes | FULL PR workflow REQUIRED |

**Guideline and documentation changes are NOT exempt from PR workflow.**

If ANY file was created, modified, or deleted (including `.md` files in `.opencode/`):
1. **Follow full PR workflow** - commit → push → review-prep → PR creation → merge → cleanup
2. **Do NOT skip review-prep** - developer visibility is mandatory
3. **Do NOT close issues directly** - requires PR merge verification

**"No File Changes" Edge Case:**
When implementation determines "no file changes needed":
1. **STILL push branch** - git will report "up-to-date", which is acceptable
2. **STILL generate compare URL** - developer can see branch state
3. **STILL post completion comment** - clear signal that work is done
4. **NEVER skip review prep** - visibility is mandatory

**Why this matters:** Developer needs visibility into what was checked, even if no changes were made.

### ⚠️ CRITICAL: Model ID Detection

**When posting completion comment (Step 3):**
- **MUST dynamically detect model ID** - NEVER use hardcoded `ollama-cloud/glm-5`
- **MUST detect actual runtime identity** from environment/MCP tools
- **If model ID unknown:** STOP and ask user - DO NOT use example from documentation

## Operating Protocol

1. **After implementation:** This task runs AFTER all implementation is complete - NO EXCEPTIONS
2. **MANDATORY step:** Branch MUST be pushed to remote for developer review - NO ASKING
3. **HALT after push:** Wait for developer to review and authorize PR creation

## Entry Criteria

- All implementation work complete AND pushed to remote
- Feature branch pushed (done by implementation task)
- No explicit "create a PR" instruction yet
- Temp files cleaned up (see Step 1)

## Exit Criteria

- Compare URL generated and reported in CHAT ONLY
- Developer can review changes via GitHub diff viewer

## Procedure

### Step 1: Temp File Cleanup (MANDATORY)

**Before pushing, clean up temporary files.**

```bash
# Remove temporary scripts (safe for task artifacts)
rm ./tmp/temp_*.py ./tmp/test_*.py 2>/dev/null

# Remove temporary data files (safe for task artifacts)
rm ./tmp/*.json ./tmp/*.csv ./tmp/*.html 2>/dev/null

# Verify cleanup
ls ./tmp/
```

**Preserve:**
- `./tmp/*.db` (SQLite databases)
- `./tmp/*.log` (log files)
- `./tmp/.*` (hidden files like `.output.txt`)

### Step 1.5: Rebase on Current Dev (MANDATORY)

Before pushing for review, sync the feature branch with the current state of `dev`:

```bash
git fetch origin
git rebase origin/dev
```

**Why this matters:**
- Other agents may have merged work into `dev` since branch creation
- The compare URL must reflect an accurate diff against current `dev`
- Merge conflicts surfacing at review time are better than at PR creation time
- The developer reviews the actual changes that will be in the PR

**If conflicts occur during rebase, invoke `/skill conflict-resolution` to classify and resolve them:**

1. **Invoke conflict-resolution skill** — classify each conflict into tier (trivial, textual, intent)
2. **Resolve Tier 1 and Tier 2 conflicts** — auto-resolve, notify via chat
3. **HALT for Tier 3 (intent) conflicts** — flag for developer review, create GitHub Issue for complex conflicts
4. **After all conflicts resolved** — verify rebased result satisfies original spec (see Step 4 in conflict-resolution skill)

**🚫 NEVER resolve ALL conflicts with `git checkout --theirs` or `git checkout --ours` without classification. This is a CRITICAL VIOLATION.**

**See `conflict-resolution` skill for the complete procedural workflow.**

**This step is MANDATORY even if no other agents are known to be working.** Dev may have been updated by human merges, other agents, or CI.

**For worktree-based branches:** The rebase runs inside the worktree directory. The `origin/dev` reference is shared across all worktrees, so `git fetch origin` and `git rebase origin/dev` work correctly from any worktree.

### Step 2: Verify Branch Is Pushed

**Before generating compare URL, verify branch is on remote.**

```bash
git branch -vv
```

**If branch is NOT pushed to remote:**

```bash
# Push branch
git push -u origin <branch-name>
```

**This ensures compare URL will work correctly.**

### Step 3: Generate Compare URL

**⚠️ CRITICAL: URLs must be constructed from session init values ONLY. Never hardcode domains.**

Using session values (GIT_OWNER, GIT_REPO, GIT_PLATFORM, GITBUCKET_HTML_URL):

**For GitBucket (GIT_PLATFORM=gitbucket):**

```
${GITBUCKET_HTML_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

Where `GITBUCKET_HTML_URL` comes from session init (read from `.env`).

**For GitHub (GIT_PLATFORM=github):**

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

**If GITBUCKET_HTML_URL is empty (not in .env):**
1. REFUSE to generate any URL
2. Report: "Cannot generate URL — GITBUCKET_HTML_URL not configured in .env"
3. HALT — do not guess or fabricate a URL

### Step 4: Report Completion (BOTH Issue AND Chat)

**⚠️ CRITICAL: URLs go in CHAT ONLY - NEVER to GitHub Issues.**

Post completion comment to GitHub issue (NO URL):
```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

Post to chat (exec summary + URL):
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

Compare URL: ${GITBUCKET_HTML_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

(GitBucket example — for GitHub use `https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>`)

**Why This Matters:**
- Chat gets exec summary + URL (developer needs visibility)
- Issues get exec summary only (NO URL - keeps history clean)
- Developer can click URL from chat to review changes
- BOTH locations have matching summaries for context

### Step 5: HALT (MANDATORY - NO EXCEPTIONS)

**🚫 CRITICAL VIOLATION: Proceeding past this point without explicit "create a PR" is a CRITICAL GUIDELINE VIOLATION.**

**DO NOT:**
- Squash commits (happens at PR creation)
- Create PR (requires explicit "create a PR" instruction)
- Push again (already pushed in implementation)
- Close issues (requires PR merge verification)
- Proceed to any next step (HALT means STOP)

**WAIT for EXPLICIT instruction:**
- Developer reviews changes via GitHub diff viewer
- Developer says "create a PR" to proceed
- NO assumptions, NO auto-progression

**What HALT means:**
- Report completion (issue + chat)
- STOP all further action
- Wait for developer's next explicit instruction
- If developer says "approved" or "go" again → STILL WAIT for "create a PR"

### ⚠️ CRITICAL: Implementation Must Push Before Review-Prep

**If review-prep is invoked but branch is NOT pushed:**

1. **Detect missed push:** `git branch -vv` shows no upstream
2. **Inform user:** "Implementation task must commit and push. Fixing now."
3. **Fix and continue:** `git push -u origin <branch-name>`
4. **Continue:** Generate compare URL, post completion comment

**Why:** Commit without push = empty compare URL. Push is mandatory after commit.

## Context Required

- Related skills: `pr-creation-workflow` (PR timing)
- Related tasks: `pr-creation` (PR)

## Why This Task Exists

- Developers need visibility before PR creation
- GitHub diff viewer is superior to local review
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"

## Enforcement Checklist

**Before invoking review-prep, verify:**

- ✅ Implementation work is complete
- ✅ All file changes are committed (`git status` shows clean)
- ✅ Branch is pushed to remote (`git branch -vv` shows upstream)
- ✅ Temp files are cleaned (no `./tmp/temp_*.py` or `./tmp/*.json`)
- ✅ Compare URL generated correctly (using session init base URL + `compare/dev...branch`)
- ✅ Chat output format correct (summary BEFORE URL)
- ✅ Issue comment posted (NO URL in issue comment)

**These checks are MANDATORY. If ANY check fails → STOP and report.**

## When review-prep MUST Run

**This task runs AFTER EVERY implementation. No exceptions.**

| Scenario | Run review-prep? |
|----------|------------------|
| Code file modified | YES |
| Documentation modified | YES |
| Guidelines modified | YES |
| Config file modified | YES |
| Zero files modified | YES (still push, still generate URL) |
| Branch already pushed | YES (verify push, generate URL) |
| "No changes needed" determined | YES (still push, still generate URL for visibility) |

**🚫 CRITICAL: Skipping this task is a CRITICAL GUIDELINE VIOLATION.**

## Verification Steps

**After review-prep completes, verify:**

| Check | Command | Expected |
|-------|---------|----------|
| Branch pushed | `git branch -vv` | Shows `[origin/branch]` |
| Compare URL works | Open URL in browser | Shows diff |
| Chat has summary | Check chat output | Exec summary + URL |
| Issue has comment | Check GitHub issue | Completion comment (NO URL) |

## Correct vs Incorrect Workflow

### ✅ CORRECT Workflow

```
Implementation task:
    ↓
Make file changes
    ↓
git status (verify changes)
    ↓
git add -A (stage)
    ↓
git commit (commit)
    ↓
git push -u origin <branch> (push)
    ↓
Report completion
    ↓
review-prep invoked AUTOMATICALLY
    ↓
Verify branch is pushed
    ↓
Generate compare URL
    ↓
Report URL in CHAT ONLY (NEVER to GitHub Issues)
    ↓
Post completion comment to issue (NO URL)
    ↓
HALT - Wait for "create a PR"
    ↓
Developer reviews via GitHub diff
    ↓
Developer says "create a PR"
    ↓
pr-creation workflow begins
```

### 🚫 INCORRECT Workflow (CRITICAL VIOLATION)

```
Implementation complete
    ↓
[SKIPPED: commit]
[SKIPPED: push]
    ↓
Push branch to remote
    ↓
Close issues IMMEDIATELY (SKIPPED HALT)
    ↓
NO compare URL reported in chat
NO PR created
NO merge verification

**This incorrect workflow VIOLATES critical rules and causes:**
- Issues closed without PR tracking
- No developer visibility via compare URL in chat
- No review before closure
- Lost audit trail

### 🚫 CRITICAL VIOLATION: Commit Without Push

```
Implementation complete
    ↓
git commit (commit made)
    ↓
[SKIPPED: git push]
    ↓
review-prep invoked
    ↓
Generate compare URL
    ↓
Result: "nothing to compare"
Result: Developer CANNOT review changes
Result: Workflow STALLS
```

**Why this fails:**
- Compare URL requires pushed commits
- Unpushed commits are local only
- Remote branch has NO commits
- Compare URL shows empty diff

## Example

```markdown
**Summary:**

Updated git-workflow skill to push feature branches after implementation and provide GitHub compare URL for developer review.

**Outcome:** Developers can now review changes via GitHub diff viewer before deciding to create a PR.

**Ready for Review:**

${GITBUCKET_HTML_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```