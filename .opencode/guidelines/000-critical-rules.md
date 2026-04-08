# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated.

## Critical Violation: Skipping Git Pre-Check Before ANY Work

**⚠️ Working on files without checking git state is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Starting ANY work (implementation, verification, editing) WITHOUT checking git state first
- Assuming working tree is clean without `git status` verification
- Creating files while on `main` or `dev` branch
- Editing files while on `main` or `dev` branch
- Skipping stash when pending changes exist

### ✅ MANDATORY PRE-CHECK SEQUENCE

**BEFORE any file operation, ANY verification, ANY work:**

```bash
# Step 1: Check git state (MANDATORY)
git branch --show-current
git status

# Step 2: If ANY pending changes (modified, deleted, untracked)
git stash push -u -m "WIP: before <branch-name>"

# Step 3: Verify stash succeeded
git stash list  # MUST show stash entry
git status      # MUST show clean working tree

# Step 4: Create feature branch (if on main or dev)
git checkout dev && git pull origin dev
git checkout -b spec/<short-name>

# Step 5: NOW proceed with work
```

### Why This Matters

| Scenario | Consequence |
|----------|-------------|
| Edit files on `main` | Cannot create branch, changes stuck on `main` |
| Skip git status check | Untracked files lost when switching branches |
| Forget `-u` flag | Untracked files NOT stashed, lost forever |
| Skip stash verification | Modifictions silently lost |

### Data Loss Prevention

**The `-u` flag is MANDATORY when stashing.**

| Command | What It Stashes |
|---------|------------------|
| `git stash push -m "..."` | Modified files ONLY |
| `git stash push -u -m "..."` | Modified + untracked + deleted files |

**ALWAYS use `-u` flag. Untracked files are just as important as tracked files.**

### Verification Requirements

**After stashing, these MUST pass before creating branch:**

| Check | Command | Expected Result |
|-------|---------|------------------|
| Stash created | `git stash list \| grep "WIP:"` | Shows stash entry |
| Working tree clean | `git status --porcelain` | Empty output (no characters) |

**If EITHER check fails ⇒ STOP. Report failure. Let user resolve.**

______________________________________________________________________

## Agent-Specific Notes

### OpenCode Desktop (OPENCODE=1)

- MCP tools auto-probe on startup
- Use OpenCode-specific instructions from `opencode.json`
- Read `.opencode/guidelines/` for detailed guidance

### Amazon Q / CodeWhisperer

- Treat as unknown agent — use manual MCP probe

## Critical Violation: Implementing Without Documentation Verification

**⚠️ Implementing code without verifying against live documentation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Implementing API calls without verifying parameter names from official docs
- Using environment variables without confirming correct names from config files
- Guessing function signatures from memory or similar libraries
- Using outdated blog posts/tutorials instead of official documentation

### ✅ REQUIRED

- **ALWAYS verify API signatures before implementing**
- Check official documentation for current API usage
- Use `srclight_get_signature` or `pycharm_get_symbol_info` for function signatures
- Read source code and type hints when docs unavailable
- Confirm environment variable names from `.env.example` or config

### Why This Matters

- Assumption-based implementations lead to broken functionality
- API changes between library versions cause silent failures
- Incorrect parameter names waste debugging time
- Outdated patterns accumulate technical debt

______________________________________________________________________

## Critical Violation: Skipping review-prep After Implementation

**⚠️ Failing to invoke `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Marking implementation complete WITHOUT committing, pushing, and generating URL
- Skipping `review-prep` because "no changes were made"
- Skipping `review-prep` because "already pushed"
- Skipping `review-prep` for documentation/guideline changes
- Proceeding to next phase without URL in chat

### ✅ REQUIRED

After EVERY implementation:

1. Commit all changes with proper trailers
1. Push feature branch to remote
1. Invoke `review-prep` automatically
1. Generate GitHub compare URL
1. Report exec summary + URL in chat (URL LAST)
1. Post completion comment to issue (NO URL)
1. HALT and wait for "create a PR"

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| No commit | Changes lost, no tracking |
| No push | Remote has no branch, compare URL fails |
| No URL | Developer cannot review changes |
| No HALT | Premature PR creation or issue closure |
| Wrong format | Developer lacks context before URL |

**The `review-prep` task is invoked AUTOMATICALLY after implementation. There is NO decision point.**

**See `git-workflow` skill for complete review-prep workflow.**

______________________________________________________________________

## Critical Violation: Wrong Chat Output Format

**⚠️ Posting URL before executive summary in chat is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

```
Compare URL: https://github.com/owner/repo/compare/main...branch

**Summary:** Changes to skill files...
**Outcome:** Added enforcement rules
```

### ✅ REQUIRED

```
**Summary:**

Updated git-workflow skill to enforce automatic invocation...

**Outcome:** Developers will now see compare URL after every implementation.

Compare URL: https://github.com/owner/repo/compare/main...branch
```

### Why This Matters

- Developer needs context BEFORE clicking URL
- Executive summary explains business impact
- Outcome states what changed for stakeholders
- URL appears LAST as actionable link

**See `git-workflow` skill → "Chat Output Format (CRITICAL)" section.**

______________________________________________________________________

## Critical Violation: Wrong PR Body Format

**⚠️ Writing implementation details instead of executive summary in PR bodies is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

```
Add plan-fidelity-auditor skill as the first auditor in the mandatory audit chain. It generates independent clean-room plans from problem statements and compares them against existing spec plans to identify substantive gaps — missing phases, incorrect approaches, and scope misalignment — before structural and content auditors run.

Fixes #505
```

**Why this is wrong:** This describes *what the code does* (implementation details, skill internals, methodology) rather than *why the change matters* (stakeholder impact, quality improvement). A non-technical stakeholder cannot understand the value.

### ✅ REQUIRED

The PR body MUST use the same executive summary format as chat output and issue comments:

```
**Summary:**

Ensures specs are audited for plan fidelity before implementation, catching missing phases and scope misalignment early.

**Outcome:** Developers will catch spec quality issues before code changes begin.

Fixes #505
```

### Format Requirements

| Section | Purpose | Content |
|---------|---------|---------|
| `**Summary:**` | Why this matters | 1-2 sentences describing stakeholder value and business impact |
| `**Outcome:**` | What changed | What stakeholders will experience differently |
| `Fixes #N` | Autoclose | Issue numbers for automatic closure on merge |

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| Implementation details in PR body | Non-technical stakeholders cannot understand value |
| No stakeholder context | reviewers must parse code to understand purpose |
| Inconsistent format | Different expectations for chat vs PR vs comments |

**See `git-workflow` skill → `pr-creation` task → "PR Body Requirements" section.**

______________________________________________________________________

## Critical Violation: Uncommitted/Unpushed Changes After Implementation

**⚠️ Marking implementation complete WITHOUT committing and pushing is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Marking task complete when `git status` shows uncommitted changes
- Skipping `git commit` because "changes are small"
- Skipping `git push` because "branch exists"
- Proceeding to review-prep without push verification

### ✅ REQUIRED

**Before marking any task complete:**

```bash
git status              # Verify changes are staged
git add -A              # Stage all changes
git commit -m "message" --trailer "Co-authored-by: ..." --trailer "Co-authored-by: ..."
git push -u origin <branch>  # Push to remote
git branch -vv          # Verify upstream is set
```

### Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Changes staged | `git status --porcelain` | Empty (all committed) |
| Branch pushed | `git branch -vv` | Shows `[origin/branch]` |
| Commits exist | `git log origin/main..HEAD --oneline` | Shows commits |

**If ANY check fails → STOP. Fix and retry.**

**See `git-workflow` skill → "Enforcement Checklist" sections.**

______________________________________________________________________

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.

## Critical Violation: Fabricating URLs — ZERO TOLERANCE

**⚠️ Generating URLs from memory, guesswork, or hardcoded patterns is a CRITICAL GUIDELINE VIOLATION.**

All URLs must be constructed exclusively from values provided by the session-init plugin output. No exceptions.

### 🚫 FORBIDDEN

- Hard-coding domain names, hostnames, or URL paths in any output
- Using "known correct" URLs from previous sessions, specs, or documentation as source
- Guessing URL patterns from git remote URLs or other indirect sources
- Caching URL base values across sessions
- Including example URLs in guidelines/skills that might be copied as fact
- **Constructing URLs from the git remote hostname** (e.g., `tomcat-0002.newsrx.com` ≠ `gitbucket.newsrx.com`)

### ✅ REQUIRED

1. Values are automatically injected by the session-init plugin (`.opencode/scripts/session_init.py`)
1. Extract `GITBUCKET_HTML_URL` (preferred) or `GITBUCKET_URL` (legacy) from session init output
1. Construct ALL URLs using that base URL + `GIT_OWNER` + `GIT_REPO`
1. If session init does not provide a required URL component → HALT and report

### URL Construction Rules

| URL Type | Construction |
|----------|-------------|
| Issue/PR | `{GITBUCKET_HTML_URL}{GIT_OWNER}/{GIT_REPO}/issues/{number}` |
| Compare | `{GITBUCKET_HTML_URL}{GIT_OWNER}/{GIT_REPO}/compare/{base}...{head}` |
| Pull request | `{GITBUCKET_HTML_URL}{GIT_OWNER}/{GIT_REPO}/pull/{number}` |

Where `{GITBUCKET_HTML_URL}` is from session init output only.

### Specific Anti-Pattern: SSH Hostname ≠ Web URL

**The git remote SSH hostname is NEVER the same as the web UI hostname.**

```
GIT_REMOTE_URL=ssh://git@tomcat-0002.newsrx.com:29418/org/repo.git
GITBUCKET_HTML_URL=https://gitbucket.newsrx.com/gitbucket/
```

| Wrong (fabricated from remote) | Right (from GITBUCKET_HTML_URL) |
|-------------------------------|-------------------------------|
| `https://tomcat-0002.newsrx.com/gitbucket/...` | `https://gitbucket.newsrx.com/gitbucket/...` |

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| Hardcoded domain | Wrong server, broken links, eroded trust |
| Cached from prior session | Stale after infrastructure changes |
| Guessed from remote URL | Fragile, often incorrect |
| Example URL copied as fact | Propagates errors across specs/docs |

### Session Init Unavailable

If session init has not been run or does not provide URL components:

1. **REFUSE** to generate any URL
1. Report: "Cannot generate URLs — session init not run or missing URL components"
1. HALT and wait for user to run session init

______________________________________________________________________

## Critical Violation: Inferring GitHub Owner from File Paths/Usernames

**⚠️ Inferring GitHub owner from file paths or usernames is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Inferring `owner=XXXX` from file path `/home/XXXX/git/...`
- Inferring owner from `$USER` environment variable
- Inferring owner from git username (`git config user.name`)
- Using cached/stale owner values from previous sessions
- Making ANY GitHub MCP call without session init values being available

### ✅ REQUIRED SEQUENCE

1. Values are automatically injected by the session-init plugin (`.opencode/scripts/session_init.py`)
1. Store ALL output values for session duration:
   - `DEV_NAME` (human name for commit trailers)
   - `DEV_EMAIL` (human email for commit trailers)
   - `GIT_OWNER` (repository owner for GitHub API calls)
   - `GIT_REPO` (repository name for GitHub API calls)
   - `GIT_HOOKS_PATH` (git hooks path)
   - `GIT_REMOTE_URL` (full remote URL)
1. Use `GIT_OWNER` and `GIT_REPO` for EVERY GitHub MCP call
1. NEVER assume or hardcode owner/repo values

### Why This Matters

- File paths vary across machines (`/home/<user>/` vs `/home/<other>/` )
- `$USER` returns local username, NOT GitHub owner
- `git config user.name` returns human name, NOT GitHub owner
- Cached values become stale across sessions
- Incorrect owner causes GitHub API failures

______________________________________________________________________

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.**

AI co-authorship applies to **original content authored by AI**, NOT copy-pasted content.

### What Requires Attribution

- **Python files**: Module docstring with `Co-authored with AI: AI-Name (model-id)`
- **README files**: Footer section with `## Co-Authored With AI`
- **New repositories**: README MUST include AI co-authored section
- **Original docs**: Footer with `*Co-authored with AI: AI-Name (model-id)*`

### What Does NOT Require Attribution

- **Standard licenses** (MIT, Apache, GPL) - established legal templates
- **Copy-pasted code/docs** - original source holds copyright, NOT AI co-authorship
- **Auto-generated files** (lock files, `__pycache__`)
- **Framework boilerplate** (default configs, project structures)
- **Minor edits** (typo fixes, formatting)

### Attribution Format

```
Co-authored with AI: <AI-Name> (<model-id>)
```

**Example:** `Co-authored with AI: OpenCode (ollama-cloud/glm-5)`

### Repository Creation

When creating a new repository, the README MUST include:

```markdown
## Co-Authored With AI

This repository was created with assistance from AI:

- **AI Agent**: OpenCode
- **Model**: ollama-cloud/glm-5
- **Date**: YYYY-MM-DD
```

**Note:** The LICENSE file uses standard MIT license without modification. AI attribution goes in README, not LICENSE.

**See `.opencode/guidelines/080-code-standards.md` for complete attribution requirements.**

## Critical Violation: Missing Progress Comments

**⚠️ Failing to post progress comments to the associated issue is a CRITICAL GUIDELINE VIOLATION.**

Every implementation task MUST be documented with progress comments on the GitHub issue:

- Post comment IMMEDIATELY after completing each task
- Post comment when creating PR
- Never proceed to next task without commenting first

### Required Format: Executive Summary

**Intermediate task (multi-task spec):**

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**Final task or single-task spec:**

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**⚠️ CRITICAL: Emoji must be PLAIN TEXT (not inside italic/bold formatting).**

**Status Emoji Guide:**
| Status | Emoji | Byline Format |
|--------|-------|---------------|
| Task Complete | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| In Progress | ↻ | `🤖 ↻ Working by <AgentName> (<ModelID>)` |
| Created | ✨ | `🤖 ✨ Created by <AgentName> (<ModelID>)[: Issue #N]` |
| Updated | 📝 | `🤖 📝 Updated by <AgentName> (<ModelID>)[: description]` |
| Completed | ✅ | `🤖 ✅ Completed by <AgentName> (<ModelID>)` |
| Rejected | ❌ | `🤖 ❌ Rejected by <AgentName> (<ModelID>): <reason>` |

**When to include context in byline:**

- **Progress comments**: No context (content already describes the work)
- **Issue creation**: Optional — add issue number if useful
- **Rejection/Superseded**: Always include reason or replacement reference

### 🚫 FORBIDDEN in Progress Comments

- **File lists** — Redundant (visible in git commits)
- **"Next" field** — Dialog prompt (violates `AGENTS.md` § 125)
- **Punch-list format** — Use executive summary paragraphs
- **"Awaiting authorization"** — Use HALT protocol, not comments
- **Technical changelog** — Focus on impact, not file-by-file changes

### ⚠️ Chat Output Rule (CRITICAL)

**Progress executive summaries go to BOTH GitHub comments AND chat.**

| Location | Content |
|----------|---------|
| **GitHub Issue Comment** | Full executive summary (summary, outcome) |
| **Chat Output** | Same executive summary (summary, outcome) |

**Why:** Both GitHub history AND chat transcript should show progress. GitHub preserves long-term history; chat maintains session context.

**✅ DO:** Post executive summary to GitHub, then provide SAME summary in chat
**🚫 NEVER:** Skip either location
**🚫 NEVER:** Put full summary in chat but skip GitHub comment

**See `github-comments` skill for complete requirements.**

______________________________________________________________________

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

Users communicating via GitHub Issues:

- Cannot see your internal analysis
- Are not mind readers
- Expect responses where they asked the question

**MANDATORY RESPONSE PROTOCOL:**

1. Read issue comments via `github_issue_read method=get_comments`
1. Respond PUBLICLY via `github_add_issue_comment`
1. Include analysis, findings, and next steps in your response
1. Ask for authorization if needed

**See `github-comments` skill → "Responding to User Comments (MANDATORY)" section for complete requirements.**

______________________________________________________________________

## Critical Violation: Sub-issue Structure Bypass — Multi-task Specs

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

When implementing a multi-task spec (one with multiple phases/tasks):

1. **First**: Call `github_issue_read method=get_sub_issues` on the parent issue
1. **When empty**: AUTO-CREATE sub-issues at PHASE level (see `github-sub-issues` skill)
1. **Then**: Verify the task being implemented is linked as a sub-issue

**🚫 FORBIDDEN:**

- Implementing a phase that exists only as text in the parent issue body
- Proceeding when `get_sub_issues` returns empty array for multi-task specs
- Assuming markdown checkboxes = task tracking
- Creating step-level sub-issues instead of phase-level

**✅ REQUIRED:**

- Sub-issues at PHASE level, not step level
- Each phase as separate GitHub Issue linked via `github_sub_issue_write method=add`
- Single-task specs are exempt from sub-issue requirement

**See `github-sub-issues` skill for complete workflow including:**

- Single-task vs multi-task exemption
- Auto-create workflow
- Database ID requirement
- Phase-level structure

______________________________________________________________________

## Critical Violation: Stopping After Single Phase in Multi-Task Spec

**⚠️ Halting after completing a single phase of a multi-task spec is a CRITICAL GUIDELINE VIOLATION.**

When a parent issue has sub-issues, authorization cascades to ALL sub-issues. The agent must complete ALL phases before HALTing.

### 🚫 FORBIDDEN

- Completing Phase 2, then HALTing expecting re-authorization for Phase 3
- Treating sub-issues as separate authorization units
- Asking for "approved" between phases of multi-task spec
- Reporting completion after each phase instead of after ALL phases

### ✅ CORRECT BEHAVIOR

**Multi-task authorization flow:**

```
User: "#34 approved" (parent issue with sub-issues)
    ↓
Agent verifies: parent has sub-issues? YES
    ↓
ALL sub-issues authorized (cascade)
    ↓
Complete Phase 2 (#39)
Continue to Phase 3 (#40)
Continue to Phase 4 (#41)
Continue to Phase 5 (#42)
Continue to Phase 6 (#43)
    ↓
ALL phases done
    ↓
Report once at end
    ↓
HALT once at end
```

**Exception: User explicitly restricts authorization**

```
User: "approved: Phase 2 only"
    ↓
Agent completes Phase 2 only
    ↓
HALT
```

### Enforcement Matrix

| Authorization | Scope | Behavior |
|---------------|-------|----------|
| `#34 approved` (parent with sub-issues) | ALL sub-issues | Complete ALL phases, HALT once at end |
| `#39 approved` (single sub-issue) | That sub-issue only | Complete that phase, HALT |
| `approved: 1.2` (specific phase) | That phase only | Complete that phase, HALT |

### Why This Matters

| Wrong Behavior | Impact |
|----------------|--------|
| HALT after Phase 2 | Wasted developer time re-authorizing |
| Per-phase authorization | Broken workflow expectations |
| Multiple HALTs | Loss of trust in AI reliability |

### Checklist for Multi-Task Specs

- \[ \] User authorized parent issue
- \[ \] Verify parent has sub-issues
- \[ \] Authorization cascades to ALL sub-issues
- \[ \] Complete Phase 2
- \[ \] Continue to Phase 3 (NO HALT)
- \[ \] Continue to Phase 4 (NO HALT)
- \[ \] Continue to Phase 5 (NO HALT)
- \[ \] Continue to Phase 6 (NO HALT)
- \[ \] ALL phases complete → Report → HALT

**STOP conditions (require dev intervention):**

- Exception raised during implementation
- Conflict detected requiring resolution
- Missing dependency blocking progress
- User explicitly says "stop" or "wait"

**See `010-approval-gate.md` → "Multi-Task Spec Authorization"**

## Critical Violation: Sub-issue Closure Timing — ZERO TOLERANCE

**⚠️ Closing sub-issues before PR merge is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- **Closing sub-issues after implementation but BEFORE PR merge**
- **Closing sub-issues when PR is created but not merged**
- **Manually closing sub-issues that have "Fixes #N" in PR description**
- **Closing sub-issues without verifying PR merge via GitHub API**

### ✅ CORRECT WORKFLOW

**The platform (GitBucket/GitHub) closes issues automatically via "Fixes #N" annotations.**

1. **Implement sub-issue** → Create PR with `Fixes #N` in description (NO manual sub-issue closure)
1. **PR created** → Report URL, HALT
1. **Human merges PR** → Platform automatically closes sub-issue
1. **User confirms "pr merged"** → Agent verifies merge via GitHub API
1. **Agent verifies sub-issues are closed** → API check (`state: "closed"`)
1. **If sub-issue still open (edge case)** → Agent closes it manually
1. **All sub-issues closed?** → Close parent issue

### Why This Matters

| Wrong Behavior | Correct Behavior |
|----------------|------------------|
| Agent closes sub-issue after implementation | Platform closes via "Fixes #N" |
| Sub-issue shows "completed" before PR merge | Sub-issue closes WHEN PR merges |
| Tracks completion without code review | Tracks completion AFTER code review |
| May hide problems if PR never merges | PR merge is the verification step |

### "Fixes #N" Annotation (MANDATORY)

**PR descriptions MUST include sub-issue numbers to enable automatic closure:**

```markdown
Fixes #86, #87, #88

[PR body...]
```

**This allows GitBucket/GitHub to automatically close sub-issues when the PR merges.**

### Final Verification Step (AFTER PR Merge)

After user confirms "pr merged":

```python
# Step 1: Verify PR merge via GitHub API
pr = github_pull_request_read(method="get", owner=..., repo=..., pullNumber=...)
if pr.get("merged_at") is None:
    halt("PR not merged yet")

# Step 2: Check all sub-issues are closed
children = github_issue_read(method="get_sub_issues", issue_number=parent)
open_children = [c for c in children if c["state"] == "open"]

if open_children:
    # Edge case: Platform failed to auto-close
    for child in open_children:
        github_issue_write(method="update", issue_number=child["number"], 
                          state="closed", state_reason="completed")

# Step 3: Close parent only after all children closed
if not open_children:
    github_issue_write(method="update", issue_number=parent,
                       state="closed", state_reason="completed")
```

### Edge Case Handling

| Scenario | Action |
|----------|--------|
| Platform fails to auto-close sub-issue | Agent closes manually after PR merge verification |
| PR closed without merge | Sub-issues remain open (correct behavior) |
| Draft PR | Sub-issues remain open until PR is merged (correct behavior) |
| Multiple sub-issues in one PR | Include all in "Fixes #N, #M, #P" annotation |

**See `124-github-archive-workflow.md` for complete closure timing workflow.**
**See `git-workflow` skill → "cleanup" task for post-merge verification.**

## Critical Violation: Scope Creep — NEVER Do Things Outside the Spec

**⚠️ Implementing changes not explicitly called for in the spec is a CRITICAL GUIDELINE VIOLATION.**

The spec defines EXACTLY what to implement. Nothing more. Nothing less.

**🚫 FORBIDDEN:**

- Adding "helper" functions not requested
- Improving "nearby" code while you're there
- Refactoring things adjacent to the change
- Adding tests for unrequested functionality
- Modifying related files "just to be safe"
- Fixing "similar issues" in the same area
- Any change not explicitly stated in the issue/PR description

**If you think something ELSE should be changed:**

1. STOP — do not implement it
1. Comment on the issue noting the additional concern
1. Wait for explicit approval before implementing anything outside the spec

**When in doubt: ASK, don't assume.**

______________________________________________________________________

## Critical Violation: Spec Without Investigation

**⚠️ Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION.**

Investigation MUST be completed BEFORE finalizing a spec for review.

**🚫 FORBIDDEN:**

- Creating specs from vague requirements without exploration
- Skipping codebase analysis before planning
- Finalizing specs before investigating edge cases
- Proceeding without success criteria defined
- Running test code against production systems during investigation

**✅ REQUIRED:**

- Investigate codebase for existing patterns and reusable components
- Create test scripts in `./tmp/` to validate hypotheses (isolated from production)
- Document alternatives considered with tradeoffs
- Identify risks and mitigation strategies
- Define testable, measurable success criteria

**✅ ALLOWED During Investigation:**

- Read production code (exploration)
- Read production data (analysis)
- Create and run test scripts in `./tmp/` (isolated fixtures)
- Create isolated test fixtures (dedicated test DB/schemas)
- Run static analysis (lint, typecheck)
- Document findings for the spec

**Investigation Completion Criteria:**

Before creating a spec, the agent MUST verify:

| Requirement | Evidence |
|-------------|----------|
| Problem understood | Clearly stated problem, context, stakeholders |
| Codebase explored | Existing patterns, reusable components identified |
| Hypotheses tested | Test scripts run, results documented |
| Alternatives considered | At least 2 approaches documented with tradeoffs |
| Risks identified | Risk assessment with mitigation strategies |
| Success criteria defined | Testable, measurable completion criteria |

See `142-planning-archive-workflow.md` → "Investigation Completion Criteria" for complete requirements.

______________________________________________________________________

## Critical Violation: Implementing Stale or Superseded Specs

**⚠️ Implementing a stale or superseded spec without revision is a CRITICAL GUIDELINE VIOLATION.**

Before implementing OR revising any spec, the agent MUST check for:

### Superseding Issues

**When to check:** Before any implementation or revision of a spec.

**What to check:**

- Query all open `[SPEC]`, `[SPEC-FIX]`, and `[SPEC-ENHANCEMENT]` issues
- Identify conflicting/overlapping objectives
- Look for later issues that may render the active spec obsolete

**If superseding issue exists:**

1. SILENTLY HALT
1. Report the conflict to the issue
1. Do NOT proceed with the superseded spec
1. Wait for user direction

### Staleness from Implemented Specs

**When to check:** Before any implementation or revision of a spec.

**What to check:**

- Check for merged PRs that implemented related functionality
- Check if referenced code locations have been modified since spec creation
- Check if referenced dependencies/libraries have changed
- Check if the problem statement still applies (may have been fixed by another implementation)

**If staleness detected:**

**🚫 FORBIDDEN:**

- Implementing a stale spec as-is
- Assuming "the spec is still valid" without verification
- Skipping revision to "save time"

**✅ REQUIRED:**

1. REVISE the spec to reflect current reality:
   - Update problem statement if context changed
   - Update affected files/lines if code locations changed
   - Update success criteria if requirements shifted
   - Update dependencies if integration points changed
1. Report the revision via comment on the issue
1. HALT — wait for user approval before proceeding
1. Never implement a stale spec without revision

### Where to Check

This check is REQUIRED in these workflows:

| Workflow | Guideline |
|----------|-----------|
| Before implementing any spec | `010-approval-gate.md` |
| When listing available specs | `140-planning-spec-creation.md` |
| Before revising a spec | `130-authority-source.md` |

______________________________________________________________________

## Auditor Skills Enforcement

**⚠️ MANDATORY AUDIT: Run spec-auditor orchestrator when auditing specs. NO SKIPPING.**

### When to Run Auditor Skills

**Trigger words that require the auditor:**

- "audit this spec"
- "review this issue"
- "revisit this task"
- "check this \[SPEC\]"
- "validate the spec"
- "audit the issue"
- Any request involving spec quality or structure

### Orchestration Model (CURRENT)

**spec-auditor is the orchestrator.** It decides which subtasks to run based on scope:

```
spec-auditor --issue N
    ├── Baseline (always run):
    │   ├── fresh-start      — Self-contained context, fresh-start requirements
    │   ├── structure        — Phase structure, concern separation, naming quality
    │   ├── content-quality  — Completeness, clarity, LLM implementability
    │   └── traceability     — Cross-references, anchors, no stale line numbers
    └── Conditional (based on scope):
        ├── operational      — Operational requirements, success criteria
        ├── fidelity         — Plan fidelity, clean-room comparison (replaces old plan-fidelity-auditor)
        └── concerns         — Concern separation, deployment independence (replaces old concern-separation-auditor)
```

**Why orchestration over fixed chains:**
- Not every spec needs fidelity or concern audits
- Spec-auditor determines scope and selects relevant subtasks
- Eliminates rigid "run ALL three in order" requirement
- Agent judgment replaces rote checklist execution

### Guideline Auditor (`guideline-auditor`)

Invoked with: `/skill guideline-auditor`

**Purpose:** Audit `.opencode/guidelines/` for gaps, conflicts, and LLM compliance.

**When to invoke:**

- Before approving guideline changes
- Periodic maintenance to check for guideline drift
- Post-implementation verification for guideline changes

**Output:** Creates audit log in `./tmp/audit-YYYYMMDD.md`

### Spec Auditor (`spec-auditor`) — Orchestrator

Invoked with: `/skill spec-auditor --issue N`

**Purpose:** Orchestrate spec quality audit by selecting and running relevant subtasks.

**When to invoke:**

- When "audit/review/revisit" keywords used
- After spec creation
- Before approving spec implementation
- Periodic audit to check for spec drift

**Subtask invocation:**

```
/skill spec-auditor --task fresh-start     # Fresh-start context audit
/skill spec-auditor --task structure       # Phase structure audit
/skill spec-auditor --task content-quality # Content completeness audit
/skill spec-auditor --task traceability    # Cross-reference audit
/skill spec-auditor --task operational     # Operational requirements audit
/skill spec-auditor --task fidelity        # Plan fidelity audit (replaces old plan-fidelity-auditor)
/skill spec-auditor --task concerns        # Concern separation audit (replaces old concern-separation-auditor)
```

**Output:** Posts findings to GitHub Issue, creates audit log in `./tmp/audit-spec-YYYYMMDD.md`

### Legacy Auditors (Subtasks, Not Separate Chain Entries)

**plan-fidelity-auditor** and **concern-separation-auditor** still exist as standalone skills but are invoked as subtasks by spec-auditor, not as separate chain entries:

- `/skill plan-fidelity-auditor` — Runs fidelity subtask internally (report-only, no auto-fix)
- `/skill concern-separation-auditor` — Runs concerns subtask internally (report-only, no auto-fix)

**These can also be invoked directly for standalone audits when only fidelity or concern checks are needed.**

### Enforcement Flow

| Trigger | Action |
|---------|--------|
| Spec created | REQUIRED: Invoke `spec-auditor --issue N` (orchestrator selects subtasks) |
| "Audit/review/revisit this spec" | REQUIRED: Invoke `spec-auditor --issue N` |
| Before implementation approval | REQUIRED: Verify spec-auditor found no critical issues |
| Guideline change proposed | Optional: `/skill guideline-auditor` |
| Post-implementation | Optional: Re-run spec-auditor to verify no new issues |

______________________________________________________________________

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.**

PRs require the developer to say one of these EXACT phrases:

- "create a PR"
- "make a PR"
- "push and create PR"
- "let's get a PR up"

**🚫 FORBIDDEN:**

- Creating a PR after "approved" or "go" — these authorize implementation ONLY
- Creating a PR after completing implementation — completion does NOT authorize PR creation
- Asking "Ready for a PR?" or "Should I create a PR?" — just STOP and report completion
- **Pushing branch to remote without "create a PR" instruction** — pushing is part of PR creation, NOT implementation

**✅ REQUIRED:**

- After completing implementation: report completion concisely, then STOP
- Wait for EXPLICIT "create a PR" instruction
- Only then: squash, push, create PR, report URL, STOP

**See `pr-creation-workflow` skill for the full PR timing workflow including:**

- Authorization boundary (what authorizes implementation vs PR)
- Developer must test before PR
- HALT after PR creation

______________________________________________________________________

## Critical Violation: Analysis → Implementation Without Authorization

**⚠️ Finding a bug during analysis does NOT authorize fixing it.**

### 🚫 FORBIDDEN

- Implementing fixes discovered during analysis tasks
- Creating branches/specs/PRs after finding bugs in analysis mode
- Treating analysis requests as implementation authorization
- "Vibe coding" — seeing a bug and immediately implementing a fix without spec

### ✅ REQUIRED SEQUENCE

| Request Type | Authorized Actions |
|-------------|---------------------|
| "check logs" | Read logs, report findings, HALT |
| "analyze error" | Analyze, report root cause, HALT |
| "why is this failing" | Investigate, report findings, HALT |
| "check X" | Analyze X, report findings, HALT |
| "fix this" | Create spec issue, get approval, implement |

1. User requests analysis → Perform analysis ONLY
1. Report findings (bugs, errors, issues) as factual observations
1. HALT and wait for explicit authorization
1. If user wants fix → Create spec issue, get approval, then implement

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| Implement during analysis | No spec to track changes |
| No spec issue | No approval workflow |
| Direct to implementation | Bypasses review process |
| Vibe coding | Untracked, undocumented changes |

**Discovery Protocol:**

1. Bug discovered during analysis → Record as factual observation
1. Create GitHub Issue for the discovery (if not exists)
1. Report existence in chat
1. HALT
1. Wait for explicit "fix this" or "create spec"
1. If authorized → Create spec, get approval, implement

______________________________________________________________________

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.**

PRs require the developer to say one of these EXACT phrases:

- "create a PR"
- "make a PR"
- "push and create PR"
- "let's get a PR up"

**🚫 FORBIDDEN:**

- Creating a PR after "approved" or "go" — these authorize implementation ONLY
- Creating a PR after completing implementation — completion does NOT authorize PR creation
- Asking "Ready for a PR?" or "Should I create a PR?" — just STOP and report completion
- **Pushing branch to remote without "create a PR" instruction** — pushing is part of PR creation, NOT implementation

**✅ REQUIRED:**

- After completing implementation: report completion concisely, then STOP
- Wait for EXPLICIT "create a PR" instruction
- Only then: squash, push, create PR, report URL, STOP

**The PR Timing Boundary:**

| Authorization | What It Authorizes |
|---------------|---------------------|
| "approved" / "go" | Implementation ONLY |
| Completion of implementation | Report + STOP |
| "create a PR" | PR creation workflow |
| Branch push | Part of PR creation, NOT implementation |

**Correct Sequence:**

1. "approved" → Implement → Report completion → STOP
1. Wait for "create a PR" → Push branch → Report URL in chat → STOP
1. Wait for "create a PR" → Squash → Create PR → Report URL in chat → STOP
1. Wait for human to merge → Close issues

**See `pr-creation-workflow` skill for the full PR timing workflow including:**

- Authorization boundary (what authorizes implementation vs PR)
- Developer must test before PR
- HALT after PR creation

______________________________________________________________________

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues BEFORE the PR is merged is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**

- Closing issues immediately after implementation
- Closing issues when PR is created but not merged
- Closing parent issues while child issues remain open
- Closing issues without explicit "merge confirmed" from human
- Closing issues based on `git pull` fast-forward alone (MUST use GitHub API)

**✅ REQUIRED SEQUENCE:**

1. Complete implementation → Create PR → Report URL in chat → **HALT**
1. Wait for human to review and merge PR
1. User confirms "pr merged" → **Call `github_pull_request_read method=get` to verify**
1. Verify `merged_at` timestamp or `state: "closed"` with merge
1. ONLY after API confirms merge → Close issues
1. Post closing summary comment

**Why `git pull` is insufficient:**

- Local fast-forward shows `git pull` succeeded
- Does NOT verify the PR merge state in GitHub
- Agent could close issue before human actually merged

**See `124-github-archive-workflow.md` for complete issue closure timing.**
**See `git-workflow` skill → "Phase 4" section for post-merge workflow including issue closure.**

______________________________________________________________________

## Critical Violation: Skipping PR for Documentation/Guideline Changes

**⚠️ Documentation and guideline changes are NOT exempt from the PR workflow.**

**🚫 FORBIDDEN:**

- Treating documentation changes as "minor" and closing issues directly
- Skipping review-prep for `.md` file changes
- Closing issues without PR when guidelines, docs, or configs were modified
- Assuming "no code changes" allows skipping PR workflow

**✅ REQUIRED:**

- **ALL file modifications** (code, docs, guidelines, configs) require full PR workflow
- Branch-first rule applies to ALL file types
- review-prep is MANDATORY before any issue closure
- PR merge verification is required before closing ANY issue

**File Types That Require Full PR Workflow:**

| File Type | PR Required? | Reason |
|-----------|--------------|--------|
| Code (`.py`, `.java`, etc.) | ✅ YES | Code changes |
| Guidelines (`.opencode/`) | ✅ YES | Changes to rules |
| Documentation (`docs/`, `*.md`) | ✅ YES | Changes to docs |
| Config (`*.toml`, `*.yaml`) | ✅ YES | Config changes |
| **NO files modified** | ❌ NO | Already implemented |

**The only exception is when ZERO files were modified** — all proposed changes were already present in the codebase. In that case, close with a verification comment without PR workflow.

**See `git-workflow` skill → "Edge Case: Already Implemented" for the complete workflow.**

______________________________________________________________________

## Critical Violation: Parent/Child Issue Closure

**⚠️ Closing a parent issue while child issues remain open is a CRITICAL GUIDELINE VIOLATION.**

When working with parent/child issue hierarchies (specs with sub-issues):

**🚫 FORBIDDEN:**

- Closing a parent `[SPEC]` issue when ANY child `[Task]` issues are still open
- Closing a parent after PR merge if other child tasks are incomplete
- Assuming "the PR covers everything" when sub-issues exist

**✅ REQUIRED:**

- Only close the child issue that corresponds to the merged PR
- Parent issue remains open until ALL child issues are closed
- After closing a child: check if other children remain open
- If all children are closed, then (and only then) close the parent

### Correct Workflow

| Step | Action | Issues Affected |
|------|--------|-----------------|
| PR merged for child task | Close corresponding child issue | Child issue only |
| Check remaining children | Verify all children closed | No action yet |
| All children closed? | Close parent with summary | Parent issue |

### Example

```
SPEC #100 (parent)
├── Task #101: Phase 1 - Database schema
├── Task #102: Phase 2 - API endpoints
└── Task #103: Phase 3 - UI components

PR merges for Phase 1 → Close #101 ONLY
#100 remains open (children #102, #103 pending)

Later, PR merges for Phase 2 → Close #102 ONLY
#100 remains open (child #103 pending)

Later, PR merges for Phase 3 → Close #103 AND #100 (all children done)
```

### Exception: All Children Completed

**When ALL child issues are completed by a single PR merge:**

1. Close the child issue corresponding to the PR
1. **ALSO close the parent issue** (all children are now complete)
1. Add summary comment to the parent explaining all work is complete

**Example:** If PR #150 fixes both #102 and #103 (the last remaining children), close BOTH child issues AND the parent #100 after merge.

### Why This Matters

- Parent issues track overall progress across all phases
- Premature parent closure loses visibility into remaining work
- Stakeholders need to see open issues for incomplete work
- GitHub sub-issue view shows which children remain

### Sub-Issue Double-Check (MANDATORY)

**After closing child issues addressed by PR, ALWAYS verify remaining sub-issues before closing parent.**

**The Problem:**

- Single PR may address multiple sub-issues
- Agent may close sub-issues prematurely (before PR merge)
- Agent may forget to close sub-issues after PR merge
- Parent gets closed while children remain open

**See `git-workflow` skill → "Sub-Issue Double-Check" section and `124-github-archive-workflow.md` → "Sub-Issue Double-Check" section for complete workflow.**

______________________________________________________________________

## Critical Violation: Deleting Branches/Stashes Improperly

**⚠️ Improper branch deletion is a CRITICAL GUIDELINE VIOLATION.**

**MERGED branches must be deleted IMMEDIATELY after merge confirmation.**

**🚫 FORBIDDEN:**

- `git branch -D <branch>` on unmerged branches without explicit request
- `git stash drop` without explicit request
- Preserving merged branches "just in case"
- Asking "should I delete this merged branch?" — just delete it
- Deleting `main` or other protected branches

**✅ REQUIRED:**

- **MERGED branches**: Delete IMMEDIATELY after merge confirmation — no asking, no waiting
- **UNMERGED branches with work**: Preserve until explicitly asked to delete
- **Stashes**: Preserve until explicitly asked to delete
- After PR creation: report URL, wait for merge confirmation, then DELETE the branch

### Quick Reference

| Branch Status | Action |
|---------------|--------|
| Merged PR | **DELETE IMMEDIATELY** — no confirmation needed |
| Unmerged with commits | **PRESERVE** — wait for explicit delete request |
| Stashes | **PRESERVE** — wait for explicit delete request |
| `main` branch | **NEVER DELETE** |

______________________________________________________________________

## Critical: Engineering Mindset Required

**⚠️ All work must be approached with proper engineering discipline.**

See `.opencode/guidelines/085-engineering-approach.md` for complete requirements.

### Core Engineering Principles

1. **Understand Before Solving** — Read all relevant code before proposing changes
1. **Design Before Implementing** — Document approach and obtain approval before coding
1. **Verify Before Declaring Complete** — Run tests, check edge cases, validate success criteria
1. **Communicate Changes** — Post comments when changes occur (NOT when creating issues)

### Requirements Analysis Mandatory

Every specification MUST include:

- Problem definition with context and stakeholders
- Constraints, assumptions, and success criteria
- Edge cases identified
- Dependencies and integrations affected
- Risk assessment

### No Feature Creep

- Implement ONLY what is in the approved spec
- No additions, enhancements, or "improvements" beyond scope
- No refactoring unless explicitly requested
- File separate issues for unrelated fixes discovered during work

### No Unapproved Work

- Never start implementation without explicit authorization
- "Should I do X?" is a question, not authorization
- Wait for clear "approved" or "go" before starting
- If unclear, ask — do not assume

## Critical Violation: Implementing Without Documentation Verification

**⚠️ Implementing code without verifying against live documentation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Implementing API calls without verifying parameter names from official docs
- Using environment variables without confirming correct names from config files
- Guessing function signatures from memory or similar libraries
- Using outdated blog posts/tutorials instead of official documentation

### ✅ REQUIRED

- **ALWAYS verify API signatures before implementing**
- Check official documentation for current API usage
- Use `srclight_get_signature` or `pycharm_get_symbol_info` for function signatures
- Read source code and type hints when docs unavailable
- Confirm environment variable names from `.env.example` or config

### Why This Matters

- Assumption-based implementations lead to broken functionality
- API changes between library versions cause silent failures
- Incorrect parameter names waste debugging time
- Outdated patterns accumulate technical debt

______________________________________________________________________

## Critical Violation: Skipping review-prep After Implementation

**⚠️ Failing to invoke `review-prep` after implementation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Marking implementation complete WITHOUT committing, pushing, and generating URL
- Skipping `review-prep` because "no changes were made"
- Skipping `review-prep` because "already pushed"
- Skipping `review-prep` for documentation/guideline changes
- Proceeding to next phase without URL in chat

### ✅ REQUIRED

After EVERY implementation:

1. Commit all changes with proper trailers
1. Push feature branch to remote
1. Invoke `review-prep` automatically
1. Generate GitHub compare URL
1. Report exec summary + URL in chat (URL LAST)
1. Post completion comment to issue (NO URL)
1. HALT and wait for "create a PR"

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| No commit | Changes lost, no tracking |
| No push | Remote has no branch, compare URL fails |
| No URL | Developer cannot review changes |
| No HALT | Premature PR creation or issue closure |
| Wrong format | Developer lacks context before URL |

**The `review-prep` task is invoked AUTOMATICALLY after implementation. There is NO decision point.**

**See `git-workflow` skill for complete review-prep workflow.**

______________________________________________________________________

## Critical Violation: Wrong Chat Output Format

**⚠️ Posting URL before executive summary in chat is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

```
Compare URL: https://github.com/owner/repo/compare/main...branch

**Summary:** Changes to skill files...
**Outcome:** Added enforcement rules
```

### ✅ REQUIRED

```
**Summary:**

Updated git-workflow skill to enforce automatic invocation...

**Outcome:** Developers will now see compare URL after every implementation.

Compare URL: https://github.com/owner/repo/compare/main...branch
```

### Why This Matters

- Developer needs context BEFORE clicking URL
- Executive summary explains business impact
- Outcome states what changed for stakeholders
- URL appears LAST as actionable link

**See `git-workflow` skill → "Chat Output Format (CRITICAL)" section.**

______________________________________________________________________

## Critical Violation: Wrong PR Body Format

**⚠️ Writing implementation details instead of executive summary in PR bodies is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

```
Add plan-fidelity-auditor skill as the first auditor in the mandatory audit chain. It generates independent clean-room plans from problem statements and compares them against existing spec plans to identify substantive gaps — missing phases, incorrect approaches, and scope misalignment — before structural and content auditors run.

Fixes #505
```

**Why this is wrong:** This describes *what the code does* (implementation details, skill internals, methodology) rather than *why the change matters* (stakeholder impact, quality improvement). A non-technical stakeholder cannot understand the value.

### ✅ REQUIRED

The PR body MUST use the same executive summary format as chat output and issue comments:

```
**Summary:**

Ensures specs are audited for plan fidelity before implementation, catching missing phases and scope misalignment early.

**Outcome:** Developers will catch spec quality issues before code changes begin.

Fixes #505
```

### Format Requirements

| Section | Purpose | Content |
|---------|---------|---------|
| `**Summary:**` | Why this matters | 1-2 sentences describing stakeholder value and business impact |
| `**Outcome:**` | What changed | What stakeholders will experience differently |
| `Fixes #N` | Autoclose | Issue numbers for automatic closure on merge |

### Why This Matters

| Violation | Consequence |
|-----------|-------------|
| Implementation details in PR body | Non-technical stakeholders cannot understand value |
| No stakeholder context | reviewers must parse code to understand purpose |
| Inconsistent format | Different expectations for chat vs PR vs comments |

**See `git-workflow` skill → `pr-creation` task → "PR Body Requirements" section.**

______________________________________________________________________

## Critical Violation: Uncommitted/Unpushed Changes After Implementation

**⚠️ Marking implementation complete WITHOUT committing and pushing is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

- Marking task complete when `git status` shows uncommitted changes
- Skipping `git commit` because "changes are small"
- Skipping `git push` because "branch exists"
- Proceeding to review-prep without push verification

### ✅ REQUIRED

**Before marking any task complete:**

```bash
git status              # Verify changes are staged
git add -A              # Stage all changes
git commit -m "message" --trailer "Co-authored-by: ..." --trailer "Co-authored-by: ..."
git push -u origin <branch>  # Push to remote
git branch -vv          # Verify upstream is set
```

### Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Changes staged | `git status --porcelain` | Empty (all committed) |
| Branch pushed | `git branch -vv` | Shows `[origin/branch]` |
| Commits exist | `git log origin/main..HEAD --oneline` | Shows commits |

**If ANY check fails → STOP. Fix and retry.**

**See `git-workflow` skill → "Enforcement Checklist" sections.**

______________________________________________________________________

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.
