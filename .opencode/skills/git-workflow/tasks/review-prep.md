# Task: review-prep

## Purpose

Generate GitHub compare URL for developer review AFTER the implementation task has already pushed the branch. This provides the developer with visibility into changes BEFORE deciding to create a PR.

## Workflow Triggers

**Invoke this task at these workflow points:**
- After implementation completes (mandatory - no decision point)

The sequence is:

1. Implementation complete → commit → push → **invoke review-prep**
2. Compare URL generated → HALT
3. Wait for developer to say "create a PR"

**DO NOT skip this task after implementation. DO NOT ask the developer if they want review. Just generate the compare URL.**

### ⚠️ CRITICAL: Implementation MUST Push Branch

**The implementation task is responsible for committing AND pushing the branch BEFORE invoking review-prep.**

**Correct sequence:**

```
Implementation task:
  1. Make changes
  2. git status (verify)
  3. git add -A (stage)
  4. git commit (commit)
  5. git push -u origin <branch> (push) ← MANDATORY
  6. Report completion
  7. Invoke review-prep

Review-prep task:
  1. Verify branch is pushed
  2. Clear TODO list
  3. Generate compare URL
  4. Post completion comment (chat only)
  5. HALT
```

**If this task is invoked and branch is NOT pushed:**

1. **STOP and report the violation:** "Implementation task failed to push branch - fixing now"
2. **Push the branch:** `git push -u origin <branch-name>`
3. **Continue to generate compare URL**
4. **Document the gap in the completion comment**

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

**When posting completion comment (Step 5):**

- **MUST dynamically detect model ID** - NEVER use hardcoded `ollama-cloud/glm-5`
- **MUST detect actual runtime identity** from environment/MCP tools
- **If model ID unknown:** STOP and ask user - DO NOT use example from documentation

## Workflow

1. **After implementation:** This task runs AFTER all implementation is complete - NO EXCEPTIONS
2. **MANDATORY step:** Branch MUST be pushed to remote for developer review - NO ASKING
3. **HALT after push:** Wait for developer to review and authorize PR creation

## Preconditions

- All implementation work complete AND pushed to remote
- Feature branch pushed (done by implementation task)
- No explicit "create a PR" instruction yet
- Temp files cleaned up (see Step 0)

## Postconditions

- Compare URL generated and posted
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

### Step 1: Verify Branch Is Pushed

**MANDATORY ENFORCEMENT CHECK: Branch MUST be on remote before generating compare URL.**

```bash
git branch -vv
```

**Expected output:**

```
* spec/my-branch  abc123 [origin/spec/my-branch] Commit message
```

**If branch shows `[origin/<branch>]` with upstream tracking → ✅ Branch is pushed**

**If branch shows NO upstream or "gone" → 🚫 BRANCH NOT PUSHED - VIOLATION DETECTED**

**VIOLATION REMEDIATION (MANDATORY):**

If review-prep is invoked but branch is NOT pushed:

1. **STOP** - Detection: Workflow violation
2. **FIX IMMEDIATELY:**
   ```bash
   # Check for uncommitted changes
   git status
   git add -A
   git commit -m "Implementation complete" \
       --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
       --trailer "Co-authored-by: <Human-Name> <human-email>"

   # Push branch
   git push -u origin <branch-name>
   ```
3. **REPORT VIOLATION:** "Workflow violation detected: implementation task failed to push. Remediated now."
4. **CONTINUE:** Generate compare URL
5. **DOCUMENT IN COMPLETION COMMENT:** Note the workflow gap was fixed

**This violation indicates implementation task did NOT follow Pre-HALT Verification Checklist.**

### Step 2: Clear TODO List (MANDATORY)

**Before generating compare URL, clear any active todos to ensure clean workflow state.**

```bash
# Clear todo list to prevent stale state from affecting subsequent phases
todowrite todos=[]
```

**Why this matters:**
- Prevents stale todos from previous phases
- Ensures clean state before developer review
- Removes distraction from completed work

### Step 3: Generate Compare URL

Using session values (GIT_OWNER, GIT_REPO):

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

### Step 4: Pre-Post Verification (MANDATORY GATE)

**⚠️ CRITICAL: You MUST verify format BEFORE generating the completion comment.**

**Verification Checklist (ALL items MUST pass):**

```
✓ Will executive summary be <1-2 sentences?
✓ Will outcome field show stakeholder value?
✓ Will byline come AFTER `---` separator?
✓ Will byline be LAST line before URL?
✓ Will URL be FINAL line (after byline)?
✓ No URL before summary?
✓ No URL between summary and byline?
```

**Format Template (use this exact structure):**

```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

**If ANY check fails:** STOP. Fix the format BEFORE continuing to Step 3.

**Why this gate exists:**
- Prevents URL-before-summary violations
- Prevents byline-before-separator violations
- Catches format errors before they're posted
- Forces procedural verification, not informational

### Step 5: Report Completion (Chat ONLY)

**⚠️ CRITICAL: Progress goes to CHAT ONLY - NOT GitHub Issues.**

**Chat Output Format:**

```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

**Why chat only:**
- GitHub Issues are historical records - no need for compare URLs
- Chat provides immediate visibility for developer review
- URLs clutter issue history unnecessarily

**Post summary + URL to chat.**
**DO NOT post to GitHub issue.**

### Step 6: HALT (MANDATORY - NO EXCEPTIONS)

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
[SKIPPED: commit]
[SKIPPED: push]
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

---
🤖 ✅ Completed by <AgentName> (<ModelID>)

https://github.com/<owner>/<repo>/compare/dev...<branch-name>
```
