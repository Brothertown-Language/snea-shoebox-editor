---
name: git-workflow
description: Use when creating a branch, committing changes, pushing work, or creating a PR. Triggers on: branch, commit, push, PR, pull request, pre-work, review-prep, feature branch, dev branch, squash.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: git-workflow

## Overview

Git Workflow Enforcer ensuring all git operations follow the repository's three-branch workflow: feature → dev → main. AI commits are blocked on `main`/`master`/`dev` branches by local git hooks. All feature branches merge to `dev` (staging/integration), and releases merge from `dev` to `main` via human-triggered workflow. Squashing happens ONLY at PR creation time, not during implementation. Invoked automatically before implementation begins and when PR creation is requested.

## Three-Branch Architecture

**Branch Model:**
- **Feature branches** (`feature/*` or `spec/*`): Short-lived, one per issue/spec
- **Dev branch** (`dev`): Evergreen staging/integration branch (never deleted)
- **Main branch** (`main` or `master`): Production-ready code

**Merge Paths:**
1. **Feature → Dev**: PR required (squash to single commit, no CI tests required)
2. **Dev → Main**: Human-triggered release (no approval required, CI tests required)

**AI Restrictions:**
- AI cannot commit directly to `main`, `master`, or `dev`
- AI must branch from `dev` for new features (not `main`)
- AI must sync with `dev` before creating feature branch

## Persona

You are a Git Workflow Enforcer. Your sole focus is ensuring all git operations follow the repository's three-branch workflow: feature → dev → main. AI commits are blocked on protected branches. Squashing is ONLY for PR creation, not during feature branch development.

## Role in Orchestration Architecture

**⚠️ CRITICAL: Git-workflow is called by implementation-workflow orchestration layer.**

Git-workflow tasks handle **pure git operations only**. Implementation logic is handled by the implementation-workflow orchestrator and implementation subagent.

**Architecture:**
```
implementation-workflow (orchestration layer)
    ├─ calls git-workflow --task pre-work (git ops only)
    ├─ invokes implementation subagent (does actual work)
    └─ calls git-workflow --task review-prep (git ops only)
```

**What git-workflow DOES:**
- Git operations (stash, branch, commit, push)
- Git state checks (branch verification, working tree status)
- Git cleanup (delete merged branches)

**What git-workflow DOES NOT do:**
- Implementation decisions
- File editing
- Spec reading
- Authorization checks (handled by approval-gate + orchestration layer)

## Authorization Gate (Moved to Implementation-Workflow)

**Previous behavior (REMOVED):** Git-workflow pre-work checked authorization.

**New behavior:** Authorization is verified by `approval-gate` BEFORE implementation-workflow is invoked. Git-workflow tasks receive context from orchestration layer.

### Mandatory Checks (Now in Orchestration Layer)

| Task | Authorization Check Location |
|------|------------------------------|
| `pre-work` | `implementation-workflow` receives auth from `approval-gate` |
| `pr-creation` | `implementation-workflow` checks for explicit "create a PR" |
| `review-prep` | No authorization needed (implementation complete) |
| `cleanup` | No authorization needed (PR merged) |

### Authorization Verification Protocol

**For `pre-work` task:**
1. Get issue context from invocation
2. Query GitHub Issue for:
   - Labels: Check for `needs-approval` label
   - Comments: Check for explicit "approved", "go", or `"#N approved"` in comments
3. If `needs-approval` label present AND NO explicit authorization:
   - HALT with message: "Authorization required. Issue has needs-approval label and no explicit 'approved' or 'go' comment."
4. If explicit authorization found (even with label):
   - PROCEED (explicit auth overrides label)
5. If NO label AND NO explicit authorization:
   - HALT with message: "Authorization required. Please say 'approved' or 'go' to begin implementation."

**For `pr-creation` task:**
1. Check if user said "create a PR", "make a PR", or similar
2. If NOT explicit PR instruction:
   - HALT with message: "PR creation requires explicit instruction. Please say 'create a PR' to proceed."
3. If explicit PR instruction:
   - PROCEED with squash and PR creation

### What Counts as Authorization

| Authorization Type | Valid? | Notes |
|-------------------|--------|-------|
| `approved` | ✅ YES | Explicit authorization to proceed |
| `go` | ✅ YES | Explicit authorization to proceed |
| `#83 approved` | ✅ YES | Explicit authorization for issue #83 |
| `approved: 1.2` | ✅ YES | Phase-level authorization |
| `continue` | ❌ NO | Conditional - not explicit authorization |
| `if you have next steps` | ❌ NO | Conditional - not explicit authorization |
| `you can proceed` | ⚠️ AMBIGUOUS | Treat as authorization only if clear intent |
| No comment, no label | ❌ NO | No authorization detected |

### What Does NOT Count as Authorization

| Non-Authorization | Reason |
|-------------------|--------|
| `continue` | Ambiguous - could mean "continue analysis" |
| `proceed with next steps` | Ambiguous - could mean analysis |
| `if you have next steps, or ask for clarification` | CONDITIONAL - requires agent to have next steps OR ask |
| `should I do X?` | Question - seeking permission |
| `would you like me to X?` | Question - seeking permission |
| Analysis results presented | Analysis is NOT authorization |
| Spec created | Spec creation is NOT authorization |

### Conditional Phrases Are NOT Authorization

**⚠️ CRITICAL: Conditionals like "if" or "when" are NOT authorization.**

Example violation: User said "Continue if you have next steps, or ask for clarification."
- This is a CONDITIONAL with two branches
- Agent interpreted it as authorization and committed/pushed
- Correct interpretation: HALT and ask for clarification OR present next steps

**Correct handling of conditionals:**
- "If you have next steps, proceed" → Must present next steps first
- "When ready, continue" → Must report ready, wait for "continue"
- "After analysis, proceed" → Must report analysis, wait for "proceed"

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-work` | Verify branch state, stash changes, create feature branch | ~640 |
| `implementation` | Handle WIP commits during implementation | ~400 |
| `review-prep` | Push branch, generate compare URL for review | ~560 |
| `pr-creation` | Squash, push, create PR via GitHub MCP | ~640 |
| `cleanup` | Delete merged branches, clean stale refs | ~800 |

## Invocation

- `/skill git-workflow --task pre-work` - **BEFORE implementation starts** (automatic via approval-gate)
- `/skill git-workflow --task implementation` - During implementation work
- `/skill git-workflow --task review-prep` - **AFTER implementation done** (automatic, no decision point)
- `/skill git-workflow --task pr-creation` - When user says "create a PR"
- `/skill git-workflow --task cleanup` - After PR merge confirmed
- `/skill git-workflow` - Overview only

## Automatic Invocation (CRITICAL)

**⚠️ CRITICAL: This skill is ALWAYS invoked automatically. There is NO decision point.**

### When This Skill Is Invoked

| Trigger | Task | Timing |
|---------|------|--------|
| User says `approved` or `go` | `pre-work` | BEFORE any file modification |
| Implementation completes | `review-prep` | AFTER all work done, BEFORE HALT |
| User says `create a PR` | `pr-creation` | Only after explicit instruction |
| User confirms `PR merged` | `cleanup` | Only after merge confirmed |

### Automatic Sequence (NO ASKING)

```
Authorization received
    ↓
pre-work invoked AUTOMATICALLY (Phase 1)
    ↓
Implementation work done
    ↓
review-prep invoked AUTOMATICALLY (Phase 3) ← **MANDATORY, NO DECISION POINT**
    ↓
Push branch → Generate URL → HALT
    ↓
(Developer reviews)
    ↓
Developer says "create a PR" ← EXPLICIT instruction required
    ↓
pr-creation: Squash → Create PR → HALT
```

### 🚫 CRITICAL VIOLATION: Skipping Automatic Invocation

**Skipping `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

| Wrong Behavior | Correct Behavior |
|----------------|------------------|
| Implementation done → HALT | Implementation done → `review-prep` → HALT |
| Skip push and URL generation | ALWAYS push, ALWAYS generate URL, ALWAYS HALT |
| "Done implementing" ends work | `review-prep` is part of implementation workflow |

### What "Automatic" Means

- **No asking**: Do not say "Run review-prep?" or "Push branch?"
- **No prompting**: Do not say "Ready to push?" or "Generate URL?"
- **No opt-out**: Developer cannot skip this phase
- **Mandatory sequence**: Implementation → commit → push → review-prep → HALT

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
   - Phase 4: PR Creation (user-initiated) → `pr-creation` task
   - Phase 5: Branch Cleanup (after merge) → `cleanup` task

## Chat Output Format (CRITICAL)

**⚠️ CRITICAL: Chat output MUST have executive summary BEFORE the URL.**

### Correct Format

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

Compare URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>
```

(`BASE_URL` = `GITBUCKET_HTML_URL` for GitBucket, `https://github.com/` for GitHub. Never hardcode.)

### 🚫 WRONG Format (CRITICAL VIOLATION)

```
Compare URL: ${BASE_URL}${GIT_OWNER}/${GIT_REPO}/compare/dev...<branch-name>

**Summary:**
...
```

**Why:** Developer needs context BEFORE clicking URL. Summary explains WHAT changed and WHY it matters.

### Format Rules

| Element | Requirement |
|---------|-------------|
| Executive summary | MUST appear first |
| Outcome line | MUST appear after summary |
| URL | MUST appear LAST |
| URL in chat ONLY | NEVER post URL to GitHub Issues |

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
| After review-prep | Report exec summary + URL in chat, completion comment to issue (NO URL) | "create a PR" instruction |
| After pr-creation | Report exec summary + PR URL in chat | "PR merged" confirmation |
| After PR merged | Close issues | Next explicit instruction |

### 🚫 CRITICAL VIOLATIONS

| Violation | Consequence |
|-----------|-------------|
| Skip review-prep | No developer visibility, premature PR |
| Skip HALT after push | Issues closed without PR |
| Close issues without PR merge | Lost tracking, audit trail broken |
| Skip GitHub API verification | Closing issues on unmerged PRs |
| **Close issues directly for doc/guideline changes** | **CRITICAL - docs require full PR workflow** |

## Common Violations (LEARN FROM THESE)

**This exact failure pattern triggered this spec:**

### Violation 1: Skipping review-prep After Implementation

**What Happened:** Agent completed skill creation, marked task complete, but did not invoke `review-prep`.

**Wrong Sequence:**
```
Implementation done
    ↓
Mark task complete
    ↓
HALT (no push, no URL, no review-prep)
```

**Correct Sequence:**
```
Implementation done
    ↓
git add -A && git commit (commit changes)
    ↓
git push -u origin <branch> (push branch)
    ↓
review-prep invoked AUTOMATICALLY
    ↓
Generate compare URL
    ↓
Report exec summary + URL in chat
    ↓
Post completion comment to issue (NO URL)
    ↓
HALT
```

**Why This Failed:**
- No commit made → No changes tracked
- No push → No remote branch
- No URL → Developer cannot review
- No visibility into what changed

### Violation 2: Wrong Chat Output Format

**What Happened:** Agent reported URL first, then summary.

**Wrong Sequence:**
```
Compare URL: ${BASE_URL}owner/repo/compare/dev...branch

**Summary:** Changes to skill files...
**Outcome:** Added enforcement rules
```

**Correct Sequence:**
```
**Summary:** Updated git-workflow skill to enforce automatic...

**Outcome:** Developers will now see compare URL after every implementation.

Compare URL: ${BASE_URL}owner/repo/compare/dev...branch
```

**Why This Matters:**
- Developer needs context before clicking URL
- Summary explains business impact
- Outcome states what changed for stakeholders
- URL appears LAST as actionable link

### Violation 3: Uncommitted/Unpushed Changes After Implementation

**What Happened:** Agent marked complete but `git status` showed uncommitted changes.

**Detection:**
```bash
git status --porcelain
# Shows modified/untracked files
```

**Resolution:**
```bash
git add -A
git commit -m "message" --trailer "Co-authored-by: ..." --trailer "Co-authored-by: ..."
git push -u origin <branch>
```

**Why This Matters:**
- Uncommitted changes = lost work
- Unpushed commits = no remote visibility
- Review URL requires pushed commits

### Violation 4: No Enforcement Checklist

**What Happened:** Agent skipped steps because there was no checklist to verify.

**Fix:** Added enforcement checklist to `review-prep` task:
- ✅ Branch pushed?
- ✅ Commits squashed?
- ✅ Temp files cleaned?
- ✅ Compare URL generated?
- ✅ Exec summary + URL in chat?
- ✅ Completion comment to issue (NO URL)?

### Violation 5: Created PR Without "Create a PR" Instruction (CRITICAL)

**What Happened (2026-04-02):**
1. User said "fix the skill and guideline" (implementation instruction)
2. Agent made changes, committed, pushed
3. Agent created PR directly WITHOUT:
   - Generating compare URL for review
   - HALTing for review
   - Waiting for "create a PR" instruction
4. Only compare URL was provided AFTER user complained

**Wrong Sequence:**
```
User: "fix the skill and guideline"
    ↓
Implementation done
    ↓
Created PR immediately (SKIPPED review-prep, SKIPPED HALT)
    ↓
Reported PR URL
    ↓
User: "and yet you still are not using the skills correctly"
```

**Correct Sequence:**
```
User: "fix the skill and guideline"
    ↓
Implementation done
    ↓
git commit && git push
    ↓
review-prep invoked AUTOMATICALLY
    ↓
Generate compare URL
    ↓
Report exec summary + URL in chat
    ↓
Post completion comment to issue (NO URL)
    ↓
HALT - Wait for developer review
    ↓
(Developer reviews via GitHub diff)
    ↓
Developer says "create a PR"
    ↓
pr-creation: Squash → Create PR → HALT
```

**Why This Failed:**
- Agent treated implementation complete as PR authorization
- Skipped automatic review-prep phase
- No HALT for developer review
- No waiting for explicit "create a PR"

**Fix:** Added explicit enforcement in pr-creation.md Step 0 and strengthened review-prep.md warnings.

### Violation 6: Executed Skill Without Following Its Steps

**What Happened (2026-04-02):**
1. User said "pr merged" (cleanup confirmation)
2. Agent invoked git-workflow skill
3. Agent loaded skill content but did NOT execute cleanup task
4. Agent just reported completion and HALTed without proper workflow

**Wrong Sequence:**
```
User: "pr merged"
    ↓
Agent invokes /skill git-workflow
    ↓
Agent loads skill content
    ↓
Agent HALTs without executing cleanup task
    ↓
User: "actually perform the appropriate skill"
```

**Correct Sequence:**
```
User: "pr merged"
    ↓
Agent invokes /skill git-workflow
    ↓
Agent EXECUTES cleanup task:
    1. Verify PR merge via GitHub API
    2. Switch to main
    3. Delete merged branch
    4. Clean up stale refs
    5. Post succinct confirmation
    ↓
HALT
```

**Why This Failed:**
- Agent treated skill invocation as reading documentation
- Did not follow procedural steps
- Skill is executable workflow, not just reference material

**Fix:** Agent must EXECUTE the loaded skill, not just read it.

### Violation 7: PR Status Report Missing Mandatory Info Format (CRITICAL)

**What Happened (2026-04-03):**
1. Agent created PR successfully
2. Agent reported PR completion without providing exec summary and outcome
3. When asked "why didn't you provide this info", agent admitted it was a skill/guideline violation
4. Agent had to be prompted to provide the mandatory format

**Wrong Output:**
```
PR #15 is ready for you to merge (I cannot merge PRs - human-only operation).

Once you've merged it, let me know and I'll start work on Tasks 6-13...
```

**Correct Output:**
```
---

## Summary

<1-2 sentences describing the impact and stakeholder value.>

## Outcome

<What changed for stakeholders>

**PR URL:** https://gitbucket.example.com/owner/repo/pull/15
```

**Why This Matters:**
- Developer needs context about what changed
- Summary explains business impact
- Outcome states what stakeholders get
- URL is actionable link at the END
- Format is documented in `git-workflow` skill and AGENTS.md

**Fix:**
1. After PR creation, ALWAYS report exec summary + outcome FIRST
2. Then provide PR URL LAST
3. Never report just the URL without context
4. Format is documented - follow it exactly

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

- **Stash ALL modifications before branch creation** — Use `git stash push -u` to include untracked files
- **Verify stash exists** (`git stash list`)
- **Verify working tree is clean** (`git status --porcelain` must return empty)
- **These checks are MANDATORY before ANY branch operation**
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

**🚫 CRITICAL: This edge case applies ONLY when ZERO file modifications were made.**

| Scenario | Workflow |
|----------|----------|
| Zero files modified (all changes already present) | Skip PR workflow, close with verification |
| ANY file modified (including docs/guidelines) | FULL PR workflow REQUIRED |
| Guideline/documentation changes | FULL PR workflow REQUIRED |

**When ZERO files modified:**

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

**When ANY file modified (including guidelines/docs):**

- MUST follow full PR workflow: commit → push → review-prep → PR creation → merge → cleanup
- Guidelines and documentation are NOT exempt from PR workflow
- Branch-first rule applies to ALL file types (code, docs, guidelines, configs)

## Task Dependencies

```
pre-work → implementation → review-prep → pr-creation → cleanup
                                             ↓
                                      (user says "create a PR")
                                                    ↓
                                              (user confirms "PR merged")
```

**Dependency Notes:**
- `cleanup` waits for human merge confirmation
- `review-prep` is mandatory after implementation

## Cross-References

- Related skills: `approval-gate` (authorization), `pr-creation-workflow` (PR timing), `changelog-generator` (changelog generation)
- Related guidelines: `110-git-branch-first.md`, `111-git-commit-workflow.md`, `113-git-pr-workflow.md`, `114-git-branch-cleanup.md`, `124-github-archive-workflow.md`
- Session init: `.opencode/plugins/session-enforcement.ts` (for GIT_OWNER, GIT_REPO, DEV_NAME, DEV_EMAIL)

## Changelog Generation (Sub-Task Integration)

**The changelog-generator skill MUST run as a sub-task during PR creation.**

### Why Sub-Task Execution Is Critical

The skill runs in an isolated context for **context isolation**:

| What Happens in Sub-Task | What Returns to Main Context |
|--------------------------|------------------------------|
| Git commit analysis | Only: "CHANGELOG.md updated" |
| Commit categorization logic | NOT: intermediate reasoning |
| Technical → User-friendly translation | NOT: commit details |
| Categorization reasoning | NOT: list of changes analyzed |
| Output formatting | NOT: generated changelog text |
| Noise filtering decisions | NOT: filtering logic |
| Thinking tokens | Minimal result token only |

### Sub-Task Invocation

```
/skill changelog-generator --since-last-release
```

When invoked:
1. Sub-task loads its own context (skill + task specification)
2. Sub-task analyzes commits, categorizes, generates changelog
3. Sub-task writes CHANGELOG.md to filesystem
4. Sub-task returns minimal result: "CHANGELOG.md updated with N entries"
5. Main context stages CHANGELOG.md and proceeds with squash

### Skip Directive

Use `[skip changelog]` in commit message or PR title to skip changelog generation:
- Last commit message (if squashing multiple commits)
- PR title

### Integration Point

The changelog sub-task is invoked in `pr-creation.md` Step 1, **before** the squash step:

1. Check for `[skip changelog]` directive
2. Invoke `/skill changelog-generator --since-last-release`
3. Stage result: `git add CHANGELOG.md`
4. Continue with squash (includes changelog changes)