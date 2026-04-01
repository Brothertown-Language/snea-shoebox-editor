# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated.

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

---

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.

## Critical Violation: Inferring GitHub Owner from File Paths/Usernames

**⚠️ Inferring GitHub owner from file paths or usernames is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN
- Inferring `owner=XXXX` from file path `/home/XXXX/git/...`
- Inferring owner from `$USER` environment variable
- Inferring owner from git username (`git config user.name`)
- Using cached/stale owner values from previous sessions
- Making ANY GitHub MCP call without first running `ai_bin/session_init.py`

### ✅ REQUIRED SEQUENCE
1. Run session init: `uv run python ai_bin/session_init.py`
2. Store ALL output values for session duration:
   - `GIT_USER_NAME` (human name for commit trailers)
   - `GIT_USER_EMAIL` (human email for commit trailers)
   - `GIT_OWNER` (repository owner for GitHub API calls)
   - `GIT_REPO` (repository name for GitHub API calls)
   - `GIT_HOOKS_PATH` (git hooks path)
   - `GIT_REMOTE_URL` (full remote URL)
3. Use `GIT_OWNER` and `GIT_REPO` for EVERY GitHub MCP call
4. NEVER assume or hardcode owner/repo values

### Why This Matters
- File paths vary across machines (`/home/michael/` vs `/home/user/`)
- `$USER` returns local username, NOT GitHub owner
- `git config user.name` returns human name, NOT GitHub owner
- Cached values become stale across sessions
- Incorrect owner causes GitHub API failures

---

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

---

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

Users communicating via GitHub Issues:
- Cannot see your internal analysis
- Are not mind readers
- Expect responses where they asked the question

**MANDATORY RESPONSE PROTOCOL:**
1. Read issue comments via `github_issue_read method=get_comments`
2. Respond PUBLICLY via `github_add_issue_comment`
3. Include analysis, findings, and next steps in your response
4. Ask for authorization if needed

**See `github-comments` skill → "Responding to User Comments (MANDATORY)" section for complete requirements.**

---

## Critical Violation: Sub-issue Structure Bypass — Multi-task Specs

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

When implementing a multi-task spec (one with multiple phases/tasks):

1. **First**: Call `github_issue_read method=get_sub_issues` on the parent issue
2. **When empty**: AUTO-CREATE sub-issues at PHASE level (see `github-sub-issues` skill)
3. **Then**: Verify the task being implemented is linked as a sub-issue

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
2. Comment on the issue noting the additional concern
3. Wait for explicit approval before implementing anything outside the spec

**When in doubt: ASK, don't assume.**

---

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

---

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
2. Report the conflict to the issue
3. Do NOT proceed with the superseded spec
4. Wait for user direction

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
2. Report the revision via comment on the issue
3. HALT — wait for user approval before proceeding
4. Never implement a stale spec without revision

### Where to Check

This check is REQUIRED in these workflows:

| Workflow | Guideline |
|----------|-----------|
| Before implementing any spec | `010-approval-gate.md` |
| When listing available specs | `140-planning-spec-creation.md` |
| Before revising a spec | `130-authority-source.md` |

---

## Auditor Skills Enforcement

**⚠️ MANDATORY AUDIT CHAIN: ALL auditor skills must run in order. NO SKIPPING.**

### When to Run Auditor Skills

**Trigger words that require ALL skills in order:**
- "audit this spec"
- "review this issue"
- "revisit this task"
- "check this [SPEC]"
- "validate the spec"
- "audit the issue"
- Any request involving spec quality or structure

**CRITICAL: If you run ONE auditor, you MUST run BOTH auditors in order.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, deployment independence, risk isolation, blast radius, phase names |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality, LLM implementability |

### Guideline Auditor (`guideline-auditor`)

Invoked with: `/skill guideline-auditor`

**Purpose:** Audit `.opencode/guidelines/` for gaps, conflicts, and LLM compliance.

**When to invoke:**
- Before approving guideline changes
- Periodic maintenance to check for guideline drift
- Post-implementation verification for guideline changes

**Output:** Creates audit log in `./tmp/audit-YYYYMMDD.md`

### Spec Auditor (`spec-auditor`)

Invoked with: `/skill spec-auditor --issue N`

**Purpose:** Audit GitHub Issue `[SPEC]` specs against master spec standards.

**When to invoke:**
- After running `concern-separation-auditor --issue N`
- When "audit/review/revisit" keywords used
- Before approving spec implementation
- During spec review for quality
- Periodic audit to check for spec drift

**Output:** Posts findings to GitHub Issue, creates audit log in `./tmp/audit-spec-YYYYMMDD.md`

### Concern Separation Auditor (`concern-separation-auditor`)

Invoked with: `/skill concern-separation-auditor --issue N`

**Purpose:** Audit spec phase structure for concern separation, deployment independence, and risk isolation.

**When to invoke:**
- FIRST before spec-auditor (mandatory order)
- When "audit/review/revisit" keywords used
- When creating new specs
- Before approving spec implementation

**Output:** Posts findings to GitHub Issue

### Enforcement Flow

| Trigger | Action |
|---------|--------|
| Spec created | REQUIRED: Run BOTH auditors in order (concern-separation FIRST, then spec-auditor) |
| "Audit/review/revisit this spec" | REQUIRED: Run BOTH auditors in order |
| Before implementation approval | REQUIRED: Verify both auditors passed |
| Guideline change proposed | Optional: `/skill guideline-auditor` |
| Post-implementation | Optional: Re-run auditors to verify no new issues |

---

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

---

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues BEFORE the PR is merged is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**
- Closing issues immediately after implementation
- Closing issues when PR is created but not merged
- Closing parent issues while child issues remain open
- Closing issues without explicit "merge confirmed" from human
- Closing issues based on `git pull` fast-forward alone (MUST use GitHub API)

**✅ REQUIRED SEQUENCE:**
1. Complete implementation → Create PR → Report PR URL → **HALT**
2. Wait for human to review and merge PR
3. User confirms "pr merged" → **Call `github_pull_request_read method=get` to verify**
4. Verify `merged_at` timestamp or `state: "closed"` with merge
5. ONLY after API confirms merge → Close issues
6. Post closing summary comment

**Why `git pull` is insufficient:**
- Local fast-forward shows `git pull` succeeded
- Does NOT verify the PR merge state in GitHub
- Agent could close issue before human actually merged

**See `124-github-archive-workflow.md` for complete issue closure timing.**
**See `git-workflow` skill → "Phase 4" section for post-merge workflow including issue closure.**

---

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
2. **ALSO close the parent issue** (all children are now complete)
3. Add summary comment to the parent explaining all work is complete

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

---

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

---

## Critical: Engineering Mindset Required

**⚠️ All work must be approached with proper engineering discipline.**

See `.opencode/guidelines/085-engineering-approach.md` for complete requirements.

### Core Engineering Principles

1. **Understand Before Solving** — Read all relevant code before proposing changes
2. **Design Before Implementing** — Document approach and obtain approval before coding
3. **Verify Before Declaring Complete** — Run tests, check edge cases, validate success criteria
4. **Communicate Changes** — Post comments when changes occur (NOT when creating issues)

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

---

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.