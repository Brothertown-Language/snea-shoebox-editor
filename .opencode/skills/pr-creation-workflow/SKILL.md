---
name: pr-creation-workflow
description: Handles PR creation timing requirements. Defines when PRs can be created, what authorizes PR creation, and the mandatory HALT after PR creation.
license: MIT
compatibility: opencode
---

# PR Creation Workflow Skill

## Role

You are a PR Creation Workflow enforcer. Your focus is ensuring PRs are created ONLY with explicit developer
instruction, HALTing after PR creation, and NEVER merging PRs.

## Core Principle

**PR creation is a DISTINCT phase requiring EXPLICIT instruction — it is NOT automatic after implementation.**

## Authorization Boundary (CRITICAL)

### What Authorizes Implementation (BUT NOT PR)

| Authorization   | Meaning                   | PR Authorized? |
|-----------------|---------------------------|----------------|
| `approved`      | Begin implementation      | ❌ NO           |
| `go`            | Proceed to next task      | ❌ NO           |
| `approved: 1`   | Implement Phase 1         | ❌ NO           |
| `approved: 2.3` | Implement Phase 2, Step 3 | ❌ NO           |
| `proceed`       | Continue with plan        | ❌ NO           |

**None of these authorize PR creation.** They authorize implementation only.

### What Authorizes PR Creation

| Authorization           | Valid? |
|-------------------------|--------|
| "create a PR"           | ✅ YES  |
| "make a PR"             | ✅ YES  |
| "push and create PR"    | ✅ YES  |
| "let's get a PR up"     | ✅ YES  |
| "create a pull request" | ✅ YES  |

**The developer MUST explicitly say one of these phrases (or unambiguous equivalent).**

## PR Creation Workflow

### After Implementation Completes

1. ✅ Report completion (concise summary)
2. ✅ HALT — do NOT ask about PRs
3. ✅ WAIT for explicit "create a PR" instruction
4. ❌ Do NOT ask "Ready for a PR?" or "Should I create a PR?"
5. ❌ Do NOT create PR automatically

### When Developer Says "create a PR"

#### ⚠️ MANDATORY: Pre-PR Creation Checklist

**Before creating ANY PR, you MUST verify ALL of the following:**

```markdown
## Pre-PR Creation Checklist (MANDATORY)

☐ **Squash Verification**
  - Run: `git log origin/main..HEAD --oneline`
  - Verify: EXACTLY ONE commit on branch
  - If multiple commits: Run `git reset --soft origin/main && git commit`
  - NEVER proceed with multiple commits

☐ **Branch State**
  - Run: `git status`
  - Verify: Working tree clean (no uncommitted changes)
  - If dirty: Commit or stash before proceeding

☐ **Push Verification**
  - Run: `git log origin/<branch>..HEAD --oneline`
  - Verify: No unpushed commits
  - If unpushed: Run `git push --force-with-lease origin <branch>`

☐ **Co-Author Trailers**
  - Verify: Commit message includes BOTH trailers:
    - AI Author: `Co-authored-by: <AI-Name> (<model-id>) <ai-email>`
    - Human Collaborator: `Co-authored-by: <Human-Name> <human-email>`

☐ **Issue References**
  - For single-task: Include `Fixes #<parent>` in PR body
  - For multi-task: Include `Fixes #<parent>` AND `Fixes #<child>` for EACH sub-issue
```

**🚫 CRITICAL VIOLATION: Creating PR with multiple commits is FORBIDDEN.**

| Violation | Consequence |
|-----------|-------------|
| Multiple commits in PR | PR REJECTED — squash required |
| Missing PR URL report | CRITICAL — communication failure |
| Premature merge attempt | CRITICAL — HUMAN-ONLY operation |

### Violation Warning

**Creating a PR with multiple commits is a CRITICAL GUIDELINE VIOLATION.**

If you accidentally create a PR with multiple commits:

1. **DO NOT ask user to fix it** — Fix it yourself immediately:
   ```bash
   git reset --soft origin/main
   git commit -m "<descriptive message>" \
       --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
       --trailer "Co-authored-by: <Human-Name> <human-email>"
   git push --force-with-lease origin <branch>
   ```

2. **Close the bad PR** and create a new one if necessary.

3. **Report the violation** in the GitHub issue comment.

**User intervention should NEVER be required to fix squash violations.**

1. **Collect sub-issues** (for multi-task specs):
   ```python
   # Fetch all sub-issues for the parent issue
   sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)
   
   # Build autoclose list: parent + all sub-issues
   autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
   ```

2. **Squash commits** (MANDATORY):
   ```bash
   git reset --soft origin/main
   git commit -m "<descriptive message>" \
       --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
       --trailer "Co-authored-by: <Human-Name> <human-email>"
   ```

3. **Force push**:
   ```bash
   git push --force-with-lease origin <branch>
   ```

4. **Create PR via GitHub MCP**:
   - Title: `[SPEC] <description>`
   - Body: Must include `Fixes #<issue-number>` for EACH issue to autoclose
     - Single-task spec: `Fixes #<parent>`
     - Multi-task spec: `Fixes #<parent>` AND `Fixes #<child1>` AND `Fixes #<child2>` (all sub-issues)
   - Head: `<branch-name>`
   - Base: `main`

5. **Report PR URL and HALT** — Wait for human to merge

### Sub-Issue Collection (CRITICAL)

**When creating a PR for a multi-task spec with sub-issues:**

1. **Fetch sub-issues** using `github_issue_read method="get_sub_issues"`
2. **Include ALL sub-issues** in the PR body:
   ```
   Fixes #446
   Fixes #451
   Fixes #452
   ```
3. **GitHub autocloses ALL issues** when PR merges

**Single-task exemption:** If no sub-issues exist, include only the parent issue.

**Example Multi-Task PR Body:**
```markdown
## Summary
Update PR workflow skills to include sub-issue autoclose.

Fixes #446
Fixes #451
```

## Developer Must Test Before PR

**Implementation completion does NOT mean "ready for PR".**

### The Developer Needs To:

1. Run human tests that agent cannot run
2. Verify implementation works in their environment
3. Request adjustments if something isn't right
4. Explicitly tell agent to create a PR AFTER verification passes

### Why Testing Matters

- Agent cannot run all tests (e.g., production data tests)
- Agent cannot verify integration in developer's environment
- Developer may find issues during testing
- PR is a single instruction, not a phase transition

## After PR Creation

### Mandatory HALT

- Agent MUST report PR URL
- Agent MUST HALT — wait for human to merge
- Agent MUST NOT prompt for merge
- Agent MUST NOT merge (PROHIBITED)

### Issue Closure Timing

**Issues are closed ONLY AFTER the PR is merged — NEVER before.**

**🚫 FORBIDDEN:**
- Closing issues when PR is created but not merged
- Closing parent issues while child issues remain open

**✅ REQUIRED SEQUENCE:**
1. Create PR → Report URL → HALT
2. Wait for human to merge
3. ONLY after merge confirmation → Close issues

**Why:** PRs may be rejected. Premature closure loses visibility.

## PR Merging (PROHIBITED)

### 🚫 NEVER DO

- Call `github_merge_pull_request` (or any merge operation)
- Merge PRs without human approval
- Assume "go" authorizes merging
- Click "Merge" button or equivalent

### ✅ REQUIRED

- Create PRs only
- Report PR URL
- Wait for human to merge
- Delete branches AFTER merge confirmation

## Violation Responses

### If Asked "Should I Create a PR?"

**STOP.** This is a question, not authorization.

**Response:** Report completion concisely, then HALT. Do NOT create PR.

### If Told to Create PR Without Explicit Phrase

**STOP.** Verify the instruction.

If unclear, ask: "Would you like me to create a PR?"

Wait for explicit "yes, create a PR" before proceeding.

## Prohibitions Summary

### 🚫 NEVER DO

- Create PRs autonomously
- Create PRs after "approved" or "go"
- Ask "Ready for a PR?" or "Should I create a PR?"
- Merge PRs (HUMAN-ONLY)
- Submit PR without squashing to single commit

### ✅ ALWAYS DO

- Wait for explicit "create a PR" instruction
- Squash to single commit before PR
- Report PR URL
- HALT after PR creation
- Wait for human to merge

## Integration With Guidelines

| Guideline                | Content                                           |
|--------------------------|---------------------------------------------------|
| `113-git-pr-workflow.md` | Full PR workflow (timing rules consolidated here) |
| `000-critical-rules.md`  | Critical violation: PRs without instruction       |
| `020-go-prohibitions.md` | GO does not authorize PR                          |
| `010-approval-gate.md`   | PR timing requirements                            |
| `git-workflow` skill  | Post-merge workflow including issue closure       |

## Example Workflows

### Implementation Complete — No PR authorized

```
User: "approved: 1" for Phase 1

Agent:
→ Implements Phase 1
→ Reports: "Phase 1 complete. Files: [list]"
→ HALTS (no prompt, no PR)
```

### Developer Requests PR

```
User: "create a PR"

Agent:
→ Squashes commits to single commit
→ Adds co-author trailers
→ Pushes to remote
→ Creates PR via GitHub MCP
→ Reports: "PR created: https://github.com/owner/repo/pull/123"
→ HALTS (waits for merge)
```

### Wrong Pattern — PR Not Authorized

```
User: "approved" for spec

Agent:
→ Implements all tasks
→ WRONG: Creates PR automatically
→ WRONG: Reports PR URL

CORRECT:
→ Implements all tasks
→ Reports completion
→ HALTS (waits for "create a PR")
```

## Quick Reference Card

| Situation                    | Action                             |
|------------------------------|------------------------------------|
| Developer says "approved"    | Implement → Report → HALT          |
| Developer says "go"          | Next task → Report → HALT          |
| Developer says "create a PR" | Squash → Push → Create PR → HALT   |
| Developer says "merge it"    | ❌ FORBIDDEN — humans merge         |
| After PR created             | Report URL → HALT → Wait for merge |
| PR merged                    | Delete branches → Report complete  |