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

### Step 1: Push Feature Branch

```bash
git push -u origin <branch-name>
```

This pushes the branch to remote WITHOUT creating a PR.

### Step 2: Generate Compare URL

Using session values (GIT_OWNER, GIT_REPO):

```
https://github.com/${GIT_OWNER}/${GIT_REPO}/compare/main...<branch-name>
```

### Step 3: Report Completion

Format for issue and chat:

```markdown
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

**Ready for Review:**

https://github.com/NewsRx/newsrx-genai-python/compare/main...<branch-name>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Step 4: HALT

**DO NOT:**
- Squash commits (happens at PR creation)
- Create PR (requires explicit "create a PR" instruction)
- Push again (push happens once)

**WAIT for:**
- Developer reviews changes via GitHub diff viewer
- Developer says "create a PR" to proceed

## Context Required

- Guidelines: `113-git-pr-workflow.md` (review phase)
- Related skills: `pr-creation-workflow` (PR timing)
- Related tasks: `commit-prep` (squash), `pr-creation` (PR)

## Why This Task Exists

- Developers need visibility before PR creation
- GitHub diff viewer is superior to local review
- Prevents premature PR creation
- Clear separation between "done implementing" and "create PR"

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