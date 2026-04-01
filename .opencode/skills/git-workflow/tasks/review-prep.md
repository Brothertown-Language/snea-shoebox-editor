# Task: review-prep

## Purpose

Push feature branch to remote and generate GitHub compare URL for developer review. This provides the developer with visibility into changes BEFORE deciding to create a PR.

## ⚠️ MANDATORY INVOCATION

**This task is ALWAYS invoked automatically after implementation completes. There is NO decision point.**

The sequence is:
1. Implementation complete → **review-prep invoked automatically**
2. Branch pushed, compare URL generated → HALT
3. Wait for developer to say "create a PR"

**DO NOT skip this task after implementation. DO NOT ask the developer if they want review. Just push the branch.**

### ⚠️ CRITICAL: NO EXCEPTIONS

**Review prep is MANDATORY regardless of:**
- Whether file changes were made
- Whether "no changes needed" was determined
- Whether branch is already up-to-date
- Whether implementation made zero modifications

**The review prep workflow provides developer visibility - it must NEVER be skipped.**

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

- All implementation work complete
- Feature branch exists (not main)
- No explicit "create a PR" instruction yet
- Temp files cleaned up (see Step 0)

## Exit Criteria

- Feature branch pushed to remote
- GitHub compare URL generated
- Developer can review changes via GitHub diff viewer

## Procedure

### Step 0: Temp File Cleanup (MANDATORY)

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

### Step 1: Push Feature Branch (ALWAYS EXECUTE)

```bash
git push -u origin <branch-name>
```

**This pushes the branch to remote WITHOUT creating a PR.**

**CRITICAL:** This step is ALWAYS executed, even if:
- Git reports "Everything up-to-date"
- No file changes were made during implementation
- Branch already exists on remote

The push establishes remote tracking and ensures the compare URL will work correctly.

### Step 2: Generate Compare URL

Using session values (GIT_OWNER, GIT_REPO):

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/main...<branch-name>
```

### Step 3: Report Completion (BOTH Issue AND Chat)

**⚠️ CRITICAL: Completion comment MUST be posted to BOTH the GitHub issue AND chat.**

Post to GitHub issue:
```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

**Ready for Review:**

https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/main...<branch-name>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

Post to chat (same content):
- Same executive summary + compare URL
- Ensures visibility in BOTH GitHub history AND current session

### Step 4: HALT (MANDATORY - NO EXCEPTIONS)

**🚫 CRITICAL VIOLATION: Proceeding past this point without explicit "create a PR" is a CRITICAL GUIDELINE VIOLATION.**

**DO NOT:**
- Squash commits (happens at PR creation)
- Create PR (requires explicit "create a PR" instruction)
- Push again (push happens once)
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

### ⚠️ CRITICAL: PR Request Before Review-Prep

**If user requests "create a PR" but review-prep was NOT completed:**

1. **Detect skipped review-prep:**
   - Branch not pushed to remote, OR
   - No compare URL was provided, OR
   - No completion comment posted

2. **Inform user:** "Review step must be completed first"

3. **Complete review-prep now:**
   - Commit any uncommitted changes
   - Push feature branch: `git push -u origin <branch-name>`
   - Generate GitHub compare URL
   - Post completion comment

4. **HALT:** Wait for developer to review via diff URL

5. **After developer reviews:** User says "create a PR" again → proceed with PR creation workflow

**Why:** Developer must have visibility BEFORE PR creation decision.

## Context Required

- Guidelines: `113-git-pr-workflow.md` (review phase)
- Related skills: `pr-creation-workflow` (PR timing)
- Related tasks: `commit-prep` (squash), `pr-creation` (PR)

## Why This Task Exists

- Developers need visibility before PR creation
- GitHub diff viewer is superior to local review
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"

## Correct vs Incorrect Workflow

### ✅ CORRECT Workflow

```
Implementation complete
    ↓
review-prep invoked AUTOMATICALLY
    ↓
Push branch to remote
    ↓
Generate compare URL
    ↓
Post compare URL to issue + chat
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
Push branch to remote
    ↓
Close issues IMMEDIATELY (SKIPPED HALT)
    ↓
NO compare URL posted
NO PR created
NO merge verification
```

**This incorrect workflow VIOLATES critical rules and causes:**
- Issues closed without PR tracking
- No developer visibility via compare URL
- No review before closure
- Lost audit trail

## Example

```markdown
**Summary:**

Updated git-workflow skill to push feature branches after implementation and provide GitHub compare URL for developer review.

**Outcome:** Developers can now review changes via GitHub diff viewer before deciding to create a PR.

**Ready for Review:**

https://github.com/NewsRx/newsrx-genai-python/compare/main...spec/my-feature

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```