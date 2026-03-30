# CRITICAL RULES — Zero Tolerance Violations

**See AGENTS.md for the authoritative list of critical rules.**
**See `.opencode/guidelines/` for detailed rules.**

This file provides critical rules that must never be violated.

## Agent-Specific Notes

### OpenCode Desktop (OPENCODE=1)
- MCP tools auto-probe on startup
- Use OpenCode-specific instructions from `opencode.json`
- Read `.opencode/guidelines/` for detailed guidance

### Junie (MARKER_JUNIE_TERMINAL=true)
- Requires manual MCP probe
- Needs `ai_bin/start` for initialization

### Amazon Q / CodeWhisperer
- Treat as unknown agent — use manual MCP probe

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.

## Critical Violation: Missing Progress Comments

**⚠️ Failing to post progress comments to the associated issue is a CRITICAL GUIDELINE VIOLATION.**

Every implementation task MUST be documented with progress comments on the GitHub issue:
- Post comment IMMEDIATELY after completing each task
- Post comment when creating PR
- Never proceed to next task without commenting first

### AI Authorship Attribution

**AI bylines are MANDATORY for AI-GENERATED content.**

**Content copied from ANY source does NOT get AI attribution** — the original source holds the copyright.

| Scenario | Byline Required? |
|----------|-------------------|
| AI writes original content | ✅ YES |
| AI copies Stack Overflow | ❌ NO (cite original) |
| AI quotes documentation | ❌ NO (cite original) |
| AI paraphrases external content | ✅ Partial (cite + AI byline) |

**See `088-ai-authorship.md` for complete rules.**

### Required Format: Executive Summary

**ALL bylines MUST include "on behalf of <HumanName>".**

**Dynamic Components:**
- `<AgentIcon>`: Agent iconography (🤖 for OpenCode, 🟣 for Claude, 💙 for Copilot)
- `<AgentBrand>`: Agent brand identifier (e.g., `OpenCode/glm-5`, `Claude/sonnet-4`)
- `<HumanName>`: From `git config user.name` (fallback to `$USER`)

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity and human name at runtime.**

**Intermediate task (multi-task spec):**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✅ Task Complete: <task-name>
```

**Final task or single-task spec:**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

All tasks complete from this specification.

🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✅ Task Complete: <task-name>
```

### Required Byline Format Table (MANDATORY)

**ALL comments AND issue body signatures MUST include "on behalf of <HumanName>".**

**Structure: Attribution italicized; status plain.**

| Type | Required Format |
|------|-----------------|
| Progress (task completion) | `<content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✅ Task Complete: <task-name>` |
| Body update | `<content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* 📝 Updated: <reason>` |
| Spec alteration | `<content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* 📝 Spec altered: <summary>` |
| Closure | `<content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* ❌ Closed - <reason>` |
| General response | `<content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* 🤖` |
| Issue body signature | `<issue content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✨ Created` |
| PR body signature | `<pr content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✨ Created` |

**Structure Breakdown:**

```
<AgentIcon> *AI: <AgentBrand> on behalf of <HumanName>* <ContextEmoji> <TypeText>
```

| Part | Content | Format |
|------|---------|--------|
| Agent icon | `🤖` | Plain (outside italics) |
| Attribution | `AI: OpenCode/glm-5 on behalf of Michael Conrad` | Italicized |
| Context emoji | `✅` | Plain (outside italics) |
| Type text | `Task Complete: schema` | Plain (outside italics) |

**⚠️ CRITICAL: Icon Placement (Most Common Mistake)**

The agent icon (🤖) must be **OUTSIDE the asterisks** — never inside them.

| Incorrect (icon italicized) | Correct (icon plain) |
|----------------------------|---------------------|
| `*🤖 AI: OpenCode/glm-5 on behalf of Michael Conrad*` ❌ | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad*` ✓ |

**Why it matters:** Markdown italicizes everything between `*` characters. When the icon is inside asterisks:
- The icon may not render at all (some renderers fail to display emoji in italic context)
- The icon becomes italicized along with the text (where it does render)
- Inconsistent rendering across GitHub, IDEs, and markdown viewers

The icon must remain plain to ensure consistent rendering everywhere.

**Visual rendering:**
- ❌ Incorrect: `*🤖 AI: ...*` → *(icon may not render or is italicized)*
- ✓ Correct: `🤖 *AI: ...*` → 🤖 followed by italicized text

**Examples:**

| Type | Full Byline |
|------|-------------|
| Task complete | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* ✅ Task Complete: schema` |
| General response | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* 🤖` |
| Body update | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* 📝 Updated: added field` |
| Spec alteration | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* 📝 Spec altered: Phase 2` |
| Issue closure | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* ❌ Closed - Implemented` |
| Issue creation | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* ✨ Created` |
| PR creation | `🤖 *AI: OpenCode/glm-5 on behalf of Michael Conrad* ✨ Created` |

**Agent Icon Registry:**

| Agent | Icon | Brand |
|-------|------|-------|
| OpenCode | 🤖 | `OpenCode/<model>` |
| Claude | 🟣 | `Claude/<model>` |
| Copilot | 💙 | `Copilot/<model>` |
| Generic | 🤖 | `AI/<model>` |

**Context Emoji Reference:**

| Emoji | Type Text | Use Case |
|-------|-----------|----------|
| ✅ | `Task Complete: <task>` | Progress comments |
| 🤖 | *(none)* | General responses |
| 📝 | `Updated: <reason>` | Body updates |
| 📝 | `Spec altered: <summary>` | Spec alterations |
| ❌ | `Closed - <reason>` | Issue closures |
| 🔍 | `Analysis` | Investigation findings |
| ⚠️ | `Warning` | Cautions |
| ✨ | `Created` | Issue/PR creation |

**Dynamic Components:**
- `<AgentIcon>`: Agent iconography (🤖 for OpenCode)
- `<AgentBrand>`: Agent brand (e.g., `OpenCode/glm-5`)
- `<HumanName>`: From `git config user.name` (fallback to `$USER`)

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity and human name at runtime.**

**See `.opencode/skills/github-comments/SKILL.md` for complete requirements.**

- **File lists** — Redundant (visible in git commits)
- **"Next" field** — Dialog prompt (violates `125-github-issue-comments.md`)
- **Punch-list format** — Use executive summary paragraphs
- **"Awaiting authorization"** — Use HALT protocol, not comments
- **"Waiting for..."** — Use HALT protocol, not comments
- **"Ready for review"** — Use HALT protocol, not comments
- **"Ready for approval"** — Use HALT protocol, not comments
- **"Please confirm..."** — Use HALT protocol, not comments
- **"Let me know when..."** — Use HALT protocol, not comments
- **"Ready when you are"** — Use HALT protocol, not comments
- **Technical changelog** — Focus on impact, not file-by-file changes
- **Any procedural status** — "HALT", "Waiting", "Ready" — Use HALT protocol silently

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

**See `.opencode/skills/github-comments/SKILL.md` for complete requirements.**

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

**See `.opencode/skills/github-comments/SKILL.md` → "Responding to User Comments (MANDATORY)" for complete requirements.**

---

## Critical Violation: Sub-issue Structure Bypass — Multi-task Specs

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

When implementing a multi-task spec (one with multiple phases/tasks):

1. **First**: Call `github_issue_read method=get_sub_issues` on the parent issue
2. **When empty**: AUTO-CREATE sub-issues at PHASE level (see `.opencode/skills/github-sub-issues/SKILL.md`)
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

**See `.opencode/skills/github-sub-issues/SKILL.md` for complete workflow including:**
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

## Critical Violation: Using sed for File Operations

**⚠️ Using `sed`, `awk`, `tr`, or shell redirects for file operations is a CRITICAL GUIDELINE VIOLATION.**

These tools are too fragile and can corrupt files in unexpected ways:
- `sed` mangles line endings (CRLF vs LF)
- `sed` corrupts binary-like content
- `sed` fails silently on edge cases
- `sed` behaves differently across platforms (BSD vs GNU sed)
- Shell redirects (`> file`, `>> file`) corrupt notebook files (`.ipynb`)

**🚫 FORBIDDEN:**
- Use `sed` for file content operations
- Use `awk` or `tr` for file transformations
- Use shell redirect patterns (`> file`, `>> file`) for notebook files
- Use any shell text-processing tool on files

**✅ REQUIRED:**
- Use `edit` tool for targeted string replacements in text files
- Use `write` tool for complete file rewrites
- Use `the-notebook-mcp` tools (e.g., `the-notebook-mcp_notebook_read`, `the-notebook-mcp_notebook_edit_cell`) for `.ipynb` files
- Use PyCharm MCP tools (`pycharm_replace_text_in_file`, `pycharm_create_new_file`) when available

**See:** `060-tool-usage.md` for complete file operation guidelines.

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

**⚠️ Before approving implementation, verify spec/guideline quality with auditor skills.**

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
- Before approving spec implementation
- During spec review for quality
- Periodic audit to check for spec drift

**Output:** Posts findings to GitHub Issue, creates audit log in `./tmp/audit-spec-YYYYMMDD.md`

### Enforcement Flow

| Checkpoint | Action |
|------------|--------|
| Spec created | Optional: `/skill spec-auditor --issue N` |
| Before implementation approval | **REQUIRED**: Verify spec quality (manual or via auditor) |
| Guideline change proposed | Optional: `/skill guideline-auditor` |
| Post-implementation | Optional: Re-run auditor to verify no new issues |

**See:** `010-approval-gate.md` for spec-quality checkpoint integration

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

**See `.opencode/skills/pr-creation-workflow/SKILL.md` for the full PR timing workflow including:**
- Authorization boundary (what authorizes implementation vs PR)
- Developer must test before PR
- HALT after PR creation

---

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues BEFORE the PR is merged is a CRITICAL GUIDELINE VIOLATION.**

**Two closure paths exist — auto-close (GitHub) and manual closure (AI agent):**

### Path 1: GitHub Auto-Close (Acceptable)

If the PR body contains `fixes #N`, `closes #N`, or similar closing keyword:
- GitHub automatically closes the linked issue upon PR merge
- **No AI action required** — this is correct GitHub behavior
- The issue closes automatically when the PR merges

### Path 2: Manual Closure (AI Agent)

If the PR body does NOT contain a closing keyword:
- Issue remains open after PR merge
- AI agent MUST receive explicit `"pr merged"` instruction
- AI MUST verify merge via GitHub API before closing
- AI posts closing summary comment after closure

**🚫 FORBIDDEN:**
- Closing issues immediately after implementation
- Closing issues when PR is created but not merged
- Closing parent issues while child issues remain open
- Closing issues without explicit "pr merged" instruction (for manual closure path)
- Closing issues based on `git pull` alone (MUST use GitHub API)

**✅ REQUIRED SEQUENCE (Manual Closure Path):**
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
**See `git-workflow/SKILL.md` Phase 4 for post-merge workflow including issue closure.**

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

## Critical Violation: Inferring Owner from File Paths or Usernames

**⚠️ Using file paths or usernames to infer GitHub owner is a CRITICAL GUIDELINE VIOLATION.**

The session init script is the SINGLE SOURCE OF TRUTH for owner/repo values.

**🚫 FORBIDDEN:**
- Inferring `owner=muksihs` from file path `/home/muksihs/git/...`
- Inferring owner from `$USER` environment variable
- Inferring owner from git username (`git config user.name`)
- Using cached/stale owner values from previous sessions
- Making ANY GitHub MCP call without first running session init

**✅ REQUIRED:**
1. Run `uv run python ai_bin/session_init.py` FIRST (before any other operations)
2. Store ALL output values for session duration
3. Use `GIT_OWNER` and `GIT_REPO` for EVERY GitHub MCP call
4. Never proceed with GitHub operations if session init fails

**Why this is critical:**
- Incorrect owner causes GitHub API 404 errors
- Wastes tokens on failed API calls
- Breaks workflow for issue/PR operations
- Demonstrates failure to follow documented procedure

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

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.