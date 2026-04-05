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

## Critical Violation: Auto-Issue Creation for Repeated Workflow Violations

**⚠️ Repeated bypass of mandatory workflows is a CRITICAL GUIDELINE VIOLATION that MUST be tracked.**

When the agent bypasses mandatory workflow steps (review-prep, PR creation, issue closure), an issue MUST be created to track the violation.

### What Triggers Auto-Issue Creation

| Violation | When to Create Issue |
|-----------|----------------------|
| Skipping review-prep | Agent HALTs without pushing branch, generating compare URL, or posting to issue/chat |
| Bypassing PR workflow skill | Agent manually runs git commands instead of invoking skill |
| PR creation without instruction | Agent creates PR without explicit "create a PR" from user |
| Closing issues before PR merge | Agent closes issues without verifying merge via GitHub API |

### Auto-Issue Workflow

**When violation detected:**

1. Create issue: `[SPEC-FIX] Review-prep workflow bypass` (or relevant violation type)
2. Document which implementation phase was affected
3. Add `needs-approval` label
4. Post comment explaining:
   - What violation occurred
   - Which files/workflow were affected
   - What correct workflow should have been followed

### Issue Template for Violations

```markdown
# [SPEC-FIX] <Violation Type>

**Violation:** <What occurred>

**Affected Files:**
- <File paths that were modified without proper workflow>

**Expected Workflow:**
1. <Step 1 of correct workflow>
2. <Step 2 of correct workflow>
...

**What Happened:**
<Description of how workflow was bypassed>

**Correction Required:**
- <What needs to be verified/fixed>

---
🤖 ❌ Violation detected by <AgentName> (<ModelID>)
```

### Why This Matters

- Violations indicate gaps in workflow understanding or enforcement
- Tracking violations helps identify patterns
- Creates accountability for workflow compliance
- Enables systematic improvement of guidelines

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
   - `DEV_NAME` (human name for commit trailers)
   - `DEV_EMAIL` (human email for commit trailers)
   - `GIT_OWNER` (repository owner for GitHub API calls)
   - `GIT_REPO` (repository name for GitHub API calls)
   - `GIT_HOOKS_PATH` (git hooks path)
   - `GIT_REMOTE_URL` (full remote URL)
3. Use `GIT_OWNER` and `GIT_REPO` for EVERY GitHub MCP call
4. NEVER assume or hardcode owner/repo values

### Why This Matters
- File paths vary across machines (`/home/<user>/` vs `/home/<other>/` )
- `$USER` returns local username, NOT GitHub owner
- `git config user.name` returns human name, NOT GitHub owner
- Cached values become stale across sessions
- Incorrect owner causes GitHub API failures

---

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.**

AI co-authorship applies to **original content authored by AI**, NOT copy-pasted content.

### ⚠️ MANDATORY: Dynamic Runtime Identity Detection

**Agents MUST use their ACTUAL runtime identity — NEVER copy placeholder values from examples.**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AI-Name>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
| `<model-id>` | Backing model ID at runtime | Copying "ollama-cloud/glm-5" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

**Example Values in Guidelines are ILLUSTRATIVE:**
- `OpenCode (ollama-cloud/glm-5)` → Example only
- `AI Assistant (model-id)` → Placeholder only
- **DETECT YOUR OWN IDENTITY** at runtime

**When Identity Unknown:**
- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

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

**Example:** `Co-authored with AI: MyAIAgent (provider/model-name)`

### Repository Creation

When creating a new repository, the README MUST include:

```markdown
## Co-Authored With AI

This repository was created with assistance from AI:

- **AI Agent**: <AI-Name>
- **Model**: <model-id>
- **Date**: YYYY-MM-DD
```

**Note:** The LICENSE file uses standard MIT license without modification. AI attribution goes in README, not LICENSE.

**See `.opencode/guidelines/080-code-standards.md` for complete attribution requirements.**

## Critical Violation: Unauthorized Question Asking

**⚠️ Asking questions during implementation is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN Question Patterns

The agent must NEVER ask questions like:
- "What would you prefer I focus on first?"
- "Should I continue?"
- "Ready for PR?"
- "What should I do next?"
- "How would you like me to proceed?"
- "Ready when you are"

**These questions violate the silent HALT protocol:**
- `000-critical-rules.md`: HALT protocol requires SILENT halt, not questions
- `010-approval-gate.md`: No authorization prompts after task completion
- `050-scope-autonomy.md`: Questions are NOT authorization
- `125-github-issue-comments.md`: No "awaiting authorization" or dialog prompts

### ✅ REQUIRED Behavior

| Situation | Action |
|-----------|--------|
| Task complete but more work remains | Continue implementation autonomously |
| Task complete and no more work | HALT silently, provide executive summary in chat |
| Blocked by genuine ambiguity | Post comment to issue asking for clarification, then HALT |
| Error encountered | Post error details to issue, then HALT |
| Waiting for authorization | HALT silently, wait for explicit "approved" or "go" |

### Edge Cases

| Edge Case | Action |
|-----------|--------|
| Genuine ambiguity about requirements | Post comment to issue explaining ambiguity, ask for clarification, then HALT |
| Blocked by external factor | Post comment explaining blocker, then HALT |
| Error encountered | Post error details to issue, then HALT |
| Multiple tasks remaining | Continue with next task (if authorized for all phases) |

**Why This Matters:**
- Questions break the non-interactive, autonomous execution model
- Questions create friction and require user intervention
- Questions signal confusion about task completion
- Questions during implementation are NEVER appropriate

---

## Critical Violation: GitHub Progress Comments Are NOISE — CHAT ONLY

**⚠️ Posting progress comments to GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

GitHub Issue comments are for **historical record (closure summaries)**, NOT for implementation progress.

**The PR itself is the notification. The compare URL in chat is the progress update.**

### ✅ REQUIRED Behavior

| Event | GitHub Comment? | Chat Update? |
|-------|-----------------|--------------|
| Implementation done | ❌ NO | ✅ YES - executive summary |
| Review-prep done | ❌ NO | ✅ YES - compare URL |
| PR created | ❌ NO | ✅ YES - PR URL |
| Issue closed AFTER MERGE | ✅ YES - closure summary | ✅ YES - completion notice |

### 🚫 FORBIDDEN

| Forbidden Action | Why |
|-----------------|-----|
| Posting progress after implementation | NOISE - compare URL in chat is sufficient |
| Posting progress after review-prep | NOISE - developer can view GitHub diff |
| Posting "PR created" to GitHub | NOISE - PR itself is the notification |
| Posting status blocks | NOISE - executive summary in chat is sufficient |

### ✅ Chat Output Format

```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

https://github.com/<owner>/<repo>/compare/dev...<branch>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### When GitHub Comments ARE Required

| Event | Why |
|-------|-----|
| Issue closure after merge | Historical record for future maintainers |
| Spec revision | Document what changed and why |
| Answering user question | User cannot see internal reasoning |
| Blocking issue | Explain blocker and await clarification |

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

## Critical Violation: URLs in GitHub Issue Comments

**⚠️ Putting URLs in GitHub Issue comments is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

**NEVER put URLs in GitHub Issue comments.**

GitHub Issue comments are for **future maintainers** who need context-based summaries explaining WHAT changed and WHY — NOT for developers who need clickable links to compare diffs.

| Location | Audience | Purpose | URL? |
|----------|-----------|---------|------|
| GitHub Issue comment | Future maintainers | Historical context (WHAT/WHY) | 🚫 NO |
| Chat output | Immediate developer | Actionable navigation (clickable diff) | ✅ YES |

### ✅ REQUIRED

When URLs are needed (e.g., code compare links, PR links, issue links):

1. **GitHub Issue comments**: Context-based summary **WITHOUT URL**
2. **Chat output**: Same executive summary **WITH URL**

### Why This Matters

- **GitHub Issues are historical records**: Future maintainers read comments for context, not navigation
- **URLs become outdated**: Branches get deleted, repos move, links break
- **Context is what persists**: "The rate limiting was added to prevent API quota exhaustion" survives; `https://github.com/.../compare/dev...branch` does not
- **Chat is for immediate action**: Developers in the current session need clickable links to navigate

### Examples

**❌ WRONG (URL in GitHub Issue):**

```markdown
Phase 1 complete: Added rate limiting to PubMed client.

https://github.com/owner/repo/compare/dev...feature-branch
```

**✅ CORRECT (Context in GitHub Issue, URL in Chat):**

**GitHub Issue Comment:**
```markdown
**Context-Based Summary:**

Added rate limiting middleware to the PubMed client to prevent API quota exhaustion. The implementation uses a sliding window algorithm that tracks requests per minute and queues excess calls. This ensures we stay within PubMed's 3 requests/second limit without losing data.

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

**Chat Output (same message with URL):**
```markdown
**Summary:**

Added rate limiting middleware to PubMed client to prevent API quota exhaustion.

**Outcome:** PubMed API calls now respect rate limits, preventing quota exhaustion errors.

https://github.com/owner/repo/compare/dev...feature-branch

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

### Non-Substantive Updates (NO Comment Needed)

**NO comment is required for non-substantive updates:**

- Adding origin links or cross-references to issue body
- STATUS field updates (`STATUS: 1.1` → `STATUS: 1.2`)
- Label changes
- Typo fixes in issue body

**These are housekeeping, not substantive changes.**

### Cross-Reference Links in Issue Body

Origin links and cross-references belong in the **issue body**, NOT in comments:

```markdown
> **Origin:** Issue #123
> **Investigation Result:** api-agent cannot be used
```

These are reference metadata for future readers, not actionable navigation.

**See `github-comments` skill for complete requirements.**

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

---

## Critical Violation: Bypassing Mandatory Verification Gates

**⚠️ Skipping verification gates to answer questions immediately is a CRITICAL GUIDELINE VIOLATION.**

### Mandatory Gates Before ANY Response

**Before responding to ANY user input (question, task, request), the agent MUST:**

| Gate | Check | Action |
|------|-------|--------|
| **Session Init** | Has session init run? | Run `ai_bin/session_init.py` FIRST |
| **Codebase State** | Is codebase current? | Verify with `srclight_codebase_map` or `srclight_index_status` |
| **Spec Conflicts** | Are there superseding issues? | Query all `[SPEC]` issues, check for conflicts |

### 🚫 FORBIDDEN

| Action | Why It's Wrong |
|--------|----------------|
| Answering questions without session init | Missing GIT_OWNER, DEV_NAME, MCP availability |
| Creating specs without checking conflicts | Duplicate/superseded specs waste work |
| Implementing without verification | Stale specs, changed codebase |
| Using question-answering as bypass | Questions are NOT authorization to skip checks |

### ✅ REQUIRED

**Before responding to questions:**
1. Run session init if not already done
2. Check for superseding/conflicting issues
3. Verify codebase state matches spec assumptions
4. HALT if verification reveals conflicts

**Before creating specs:**
1. Query all open `[SPEC]` issues for conflicts
2. Check if related PRs have been merged
3. Verify referenced code still exists

**Before implementing:**
1. Verify sub-issues exist for multi-task specs
2. Confirm authorization (`approved` or `go`)
3. Check that spec is not superseded

### Why This Matters

- Agent skipping session init → wrong GIT_OWNER, broken GitHub MCP calls
- Agent creating duplicate specs → wasted work, confusion
- Agent implementing stale specs → code that doesn't match requirements
- Agent answering questions without checks → incorrect responses based on outdated assumptions

### Integration Points

- `000-session-init.md` — Session init is MANDATORY first step
- `130-authority-source.md` — Check for superseding issues before implementation
- `010-approval-gate.md` — Verify sub-issues before implementing

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

## Critical Violation: Incorrect HALT After Phase Completion — Unqualified Approval

**⚠️ Halting after completing a phase when unqualified approval was given is a CRITICAL GUIDELINE VIOLATION.**

### The Problem

When a developer says `approved` or `go` **without a phase qualifier**, this authorizes ALL phases of the spec. The agent must continue through all phases without stopping.

Some agents incorrectly HALT after completing Phase 1 and mark remaining phases as `needs-approval`. This violates the principle of trust in approval tokens and creates unnecessary friction.

### 🚫 FORBIDDEN

| Forbidden Pattern | Why It's Wrong |
|-------------------|-----------------|
| HALT after Phase 1 when `approved` given | Unqualified approval = ALL phases authorized |
| Mark remaining phases as `needs-approval` | Approval was already granted |
| Ask for re-approval after each phase | Friction that violates developer mental model |
| Assume phase-by-phase approval required | Only required for HIGH/MEDIUM+LARGE blast radius |

### ✅ REQUIRED Behavior

**With unqualified approval (`approved` or `go`):**
1. Proceed through Phase 1
2. Continue to Phase 2 (no HALT)
3. Continue through ALL remaining phases
4. HALT only after completing ENTIRE spec
5. DO NOT mark remaining phases as `needs-approval`

**With qualified approval (`approved: 1` or `approved: 2.3`):**
1. Proceed through the authorized phase/step ONLY
2. HALT after completing that phase/step
3. Wait for next authorization before continuing

### Exception: Risk-Aware Phases

**For HIGH/MEDIUM risk + LARGE blast radius phases, recommend phase-by-phase approval:**

| Phase Risk | Blast Radius | Recommendation |
|------------|-------------|----------------|
| HIGH + LARGE | Large | Explicit phase approval required |
| HIGH + MEDIUM | Medium | Explicit phase approval recommended |
| Any other combination | Any | Unqualified approval sufficient |

**If developer provides unqualified approval for risky phases:**
- PROCEED (developer accepted cumulative risk)
- Document risk acknowledgment in implementation comment

### Why This Matters

- Developer mental model: "approved means go ahead"
- Repeated authorization requests create friction
- Trust in approval tokens is undermined by unnecessary HALTs
- Unqualified approval is a complete authorization, not partial

### Integration Points

- `010-approval-gate.md` → "Authorization Scope for Multi-Phase Specs"
- `020-go-prohibitions.md` → "Multi-Phase Authorization Scope"
- This section adds critical violation enforcement

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

**CRITICAL: If you run ONE auditor, you MUST run ALL THREE in order.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, deployment independence, risk isolation, blast radius, phase names |
| **2nd** | `spec-auditor` | Fresh-start context, completeness, content quality, LLM implementability |
| **3rd** | `dev-architect --task review-spec` | Architectural correctness, compliance, interdependencies, ordering |

### Sub-Issue Auditing (MANDATORY)

**ALL auditors MUST discover and audit sub-issues when present.**

**Sub-Issue Discovery Workflow:**
```
For parent issue N:
1. Query sub-issues: github_issue_read(method="get_sub_issues", issue_number=N)
2. If empty → audit parent only (current behavior)
3. If sub-issues exist → audit parent first, then each sub-issue in sequence
4. Report all findings aggregated
```

**Sub-Issue-Specific Checks:**
- Parent-sub-issue consistency (`INCONSISTENT-HIERARCHY`)
- Sub-issue overlap (`OVERLAPPING-SUB-ISSUES`)
- Missing sub-issue (`INCOMPLETE-DECOMPOSITION`)
- Stale sub-issue (`STALE-SUB-ISSUE`)
- Orphaned sub-issue (`ORPHANED-SUB-ISSUE`)
- Draft-live mismatch (`DRAFT-LIVE-MISMATCH`)

**Per-Sub-Issue Draft Generation (CRITICAL):**
Each sub-issue requires independent draft generation BEFORE viewing live sub-issue content to prevent context pollution.

| Step | Action | Purpose |
|------|--------|---------|
| 1 | Create parent draft | Independent draft for parent |
| 2 | View parent spec | Load live parent |
| 3 | Compare parent draft vs live | Identify parent gaps |
| 4 | Fix parent issues | Apply auto-fixes |
| 5 | For each sub-issue: create draft | Independent draft for sub-issue |
| 6 | For each sub-issue: view live | Load live sub-issue |
| 7 | For each sub-issue: compare | Identify sub-issue gaps |
| 8 | For each sub-issue: fix | Apply auto-fixes |
| 9 | Aggregate all findings | Single audit log |

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

## Critical Violation: Auditor Comment Practices — Two-Channel Rule

**⚠️ Posting complete audit reports to GitHub Issues when no revision was made is a CRITICAL GUIDELINE VIOLATION.**

### The Problem

Auditors have been posting complete audit findings as GitHub Issue comments even when no revision was made. This creates noise that:
- Buries revision history
- Makes it hard for future developers to find what actually changed
- Violates the distinction between chat (developer coordination) and GitHub Issues (revision history)

### 🚫 FORBIDDEN

| Channel | When NOT to Post | Why |
|---------|------------------|-----|
| GitHub Issues | Complete audit report when no revision made | Creates noise, buries history |
| Chat | Silence when audit finds no issues | Developer doesn't know audit ran |
| GitHub Issues | Checklist-style pass/fail without revision | No context for future developers |

### ✅ REQUIRED (Two-Channel Rule)

| Channel | When to Post | Content |
|---------|--------------|---------|
| **Chat** | ALWAYS (success OR fixes) | Executive summary: pass/fail status, fixes applied |
| **GitHub Issues** | ONLY on revision | WHY revision needed, WHAT changed - for future developer context |

### Chat Executive Summary Format

```
**Audit Complete:** [audit type] [passed/failed]

**Issues Found:** N
**Issues Fixed:** M (if any)
**Status:** [No concerns detected | N issues fixed]

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### GitHub Issue Revision Comment Format

```
Fixed [issue description]

**Why:** [reason for revision]
**What:** [what changed]

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### Examples

**Audit passed (no issues):**
- Chat: Post executive summary with "passed" status
- GitHub Issues: NO COMMENT (no revision made)

**Audit found issues and fixed them:**
- Chat: Post executive summary with issues found and fixes applied
- GitHub Issues: Post revision comment explaining WHY and WHAT changed

**Audit found catastrophic issue (HALT):**
- Chat: Post summary explaining blocker
- GitHub Issues: NO COMMENT (issue is blocking, not fixed)

### Why This Matters

- Developers need confirmation audits ran (even when pass)
- Future developers read GitHub Issues to understand WHAT changed and WHY
- Audit reports are noise without revision context
- Two channels serve different purposes: chat for coordination, issues for history

---

## Critical Violation: Bypassing Skills At Workflow Points

**⚠️ Bypassing MANDATORY skill invocations is a CRITICAL GUIDELINE VIOLATION.**

Skills are MANDATORY enforcement points - not optional helpers.

### 🚫 FORBIDDEN - NO BYPASS

| Workflow Point | Required Skill Invocation | What Agent MUST NOT Do |
|----------------|--------------------------|------------------------|
| Before branch creation | `/skill git-workflow --task pre-work` | Manually run `git checkout -b` |
| After implementation | `/skill git-workflow --task review-prep` | Stop after reading files, skip workflow |
| After "create a PR" | `/skill git-workflow --task pr-creation` | Manually squash/push/create PR |
| After "PR merged" | `/skill git-workflow --task cleanup` | Manually close issues/delete branches |

### ✅ REQUIRED WORKFLOW

**Before ANY git operation:**

1. **STOP** - Do NOT run git commands manually
2. **INVOKE** the appropriate skill task
3. **LET THE SKILL** handle all git operations
4. **FOLLOW** what the skill does/outputs

**Example - Creating a Branch:**

```
❌ WRONG: git checkout -b spec/my-feature
✅ RIGHT: /skill git-workflow --task pre-work
           (skill handles: stash → verify clean → create branch)
```

**Example - After Implementation:**

```
❌ WRONG: Just stop after reading files
✅ RIGHT: /skill git-workflow --task review-prep
           (skill handles: commit → push → compare URL → HALT)
```

### Why Skills Are Mandatory

Skills enforce:
- Correct git workflow sequence
- Stash before branch creation
- Squash before PR
- GitHub API verification before issue closure
- Consistent executive summary format
- Co-author trailers in commits

**Manual operations bypass these enforcements → CRITICAL VIOLATION.**

---

## Critical Violation: Skipping Review-Prep After Implementation

**⚠️ Failing to invoke review-prep after implementation completes is a CRITICAL GUIDELINE VIOLATION.**

After implementation completes, the agent MUST automatically:
1. **Invoke `/skill git-workflow --task review-prep`** (MANDATORY - NO EXCEPTIONS)
2. The skill handles: commit → push → generate compare URL → post to issue AND chat → HALT
3. **NO silent HALT without completing the workflow**

**🚫 FORBIDDEN:**
- Completing implementation and just HALTing silently
- Skipping review-prep because "changes are trivial"
- Skipping review-prep because "developer can use git log"
- Skipping review-prep and asking "do you want to review?"
- Proceeding directly to PR creation without compare URL
- Reporting completion without providing compare URL
- **Stopping after reading files/loading skills without implementing**

**✅ REQUIRED SEQUENCE:**
1. Implementation completes all file changes
2. **AUTOMATIC:** Agent invokes `/skill git-workflow --task review-prep`
3. Skill handles: commit → push → generate compare URL → post to issue/chat → HALT
4. Agent reports completion with executive summary

**Why This Matters:**
- Developers need visibility into ALL changes before PR creation
- GitHub diff viewer provides superior review experience
- Prevents accidental PRs without developer review
- Establishes clear boundary between "implementation done" and "PR requested"
- Compare URL is the canonical way for developers to review branch changes
- **Silent HALT without workflow completion loses all progress tracking**

**Executive Summary REQUIREMENT:**

When posting completion after review-prep, the agent MUST include an executive summary:

| Location | Content |
|----------|---------|
| **GitHub Issue Comment** | Full executive summary (summary, outcome) |
| **Chat Output** | Same executive summary (summary, outcome) |

**Executive Summary Format:**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**🚫 FORBIDDEN in Completion Comments:**
- File lists (redundant with git diff)
- "Next" field (dialog prompt)
- Punch-list format
- Technical changelog (focus on impact)

**See `113-git-pr-workflow.md` → "Review Phase" and `git-workflow` skill → `review-prep` task.**

---

## Critical Violation: Skipping Review-Prep After Implementation

**⚠️ Failing to invoke review-prep after implementation completes is a CRITICAL GUIDELINE VIOLATION.**

After implementation completes, the agent MUST automatically:
1. **Invoke `/skill git-workflow --task review-prep`** (MANDATORY - NO EXCEPTIONS)
2. The skill handles: commit → push → generate compare URL → post to issue AND chat → HALT
3. **NO silent HALT without completing the workflow**

**🚫 FORBIDDEN:**
- Completing implementation and just HALTing silently
- Skipping review-prep because "changes are trivial"
- Skipping review-prep because "developer can use git log"
- Skipping review-prep and asking "do you want to review?"
- Proceeding directly to PR creation without compare URL
- Reporting completion without providing compare URL
- **Stopping after reading files/loading skills without implementing**

**✅ REQUIRED SEQUENCE:**
1. Implementation completes all file changes
2. **AUTOMATIC:** Agent invokes `/skill git-workflow --task review-prep`
3. Skill handles: commit → push → generate compare URL → post to issue/chat → HALT
4. Agent reports completion with executive summary

**Why This Matters:**
- Developers need visibility into ALL changes before PR creation
- GitHub diff viewer provides superior review experience
- Prevents accidental PRs without developer review
- Establishes clear boundary between "implementation done" and "PR requested"
- Compare URL is the canonical way for developers to review branch changes
- **Silent HALT without workflow completion loses all progress tracking**

**Executive Summary REQUIREMENT:**

When posting completion after review-prep, the agent MUST include an executive summary:

| Location | Content |
|----------|---------|
| **GitHub Issue Comment** | Full executive summary (summary, outcome) |
| **Chat Output** | Same executive summary (summary, outcome) |

**Executive Summary Format:**
```
**Summary:**

<1-2 sentences describing the impact and stakeholder value.>

**Outcome:** <What changed for stakeholders>

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

**🚫 FORBIDDEN in Completion Comments:**
- File lists (redundant with git diff)
- "Next" field (dialog prompt)
- Punch-list format
- Technical changelog (focus on impact)

**See `113-git-pr-workflow.md` → "Review Phase" and `git-workflow` skill → `review-prep` task.**

---

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.**

PRs require the developer to say one of these EXACT phrases:
- "create a PR"
- "pr"
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

## Critical Violation: Bypassing git-workflow Skill for Cleanup (CRITICAL)

**⚠️ Running manual git commands instead of invoking the mandatory cleanup skill is a CRITICAL GUIDELINE VIOLATION.**

The issue is NOT "manual handling" — the issue is **bypassing the mandatory skill invocation** by running git commands directly.

### 🚫 FORBIDDEN - Bypassing Skill Invocation

These actions bypass the mandatory skill and are CRITICAL VIOLATIONS:

| Forbidden Action | Why It's Wrong |
|-----------------|----------------|
| `git branch -d <branch>` after "pr merged" | Bypasses cleanup skill workflow |
| `git push origin --delete <branch>` after "pr merged" | Bypasses cleanup skill workflow |
| `git pull` to verify merge state | Bypasses GitHub API verification in cleanup |
| Manually closing issues after seeing "merged" | Bypasses issue structure verification in cleanup |
| Running ANY git commands for cleanup | Cleanup task MUST handle all operations |

### ✅ REQUIRED - Skill Invocation

When user says "pr merged", "merged", or similar:

1. **INVOKE `/skill git-workflow --task cleanup`** — this is MANDATORY, not optional
2. The cleanup skill handles:
   - GitHub API verification (`github_pull_request_read method=get`)
   - Issue closure with proper parent/child verification
   - Branch deletion (local AND remote)
   - Stash cleanup (if applicable)
   - Hotfix dev-merge ticket creation (if applicable)

**The trigger phrase alone authorizes skill invocation — no additional confirmation needed.**

**Trigger Phrases for Mandatory Skill Invocation:**
| User Says | Skill Task |
|-----------|-----------|
| "pr merged" | `/skill git-workflow --task cleanup` |
| "merged" | `/skill git-workflow --task cleanup` |
| "PR is merged" | `/skill git-workflow --task cleanup` |
| "merge confirmed" | `/skill git-workflow --task cleanup` |

**See `git-workflow` skill → `cleanup` task for complete post-merge workflow.**

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
**See `git-workflow` skill "Task Dependencies" section for post-merge workflow including issue closure.**

---

## Critical Violation: Parent/Child Issue Closure

**⚠️ Closing a parent issue while child issues remain open, or assuming parent status reflects sub-issue completion, is a CRITICAL GUIDELINE VIOLATION.**

When working with parent/child issue hierarchies (specs with sub-issues):

**🚫 FORBIDDEN:**
- Closing a parent `[SPEC]` issue when ANY child `[Task]` issues are still open
- Closing a parent after PR merge if other child tasks are incomplete
- Assuming "the PR covers everything" when sub-issues exist
- **Assuming parent status reflects sub-issue status — ALWAYS query sub-issues**
- **Closing ANY issue without first calling `github_issue_read(method="get_sub_issues")`**

**⚠️ CRITICAL: Step 1 is MANDATORY before closing ANY issue - parent or child. No exceptions.**

### MANDATORY Pre-Close Checklist (NO EXCEPTIONS)

Before closing ANY issue (parent OR child), the agent MUST complete this checklist in order:

| Step | Action | MUST Result |
|------|--------|-------------|
| **1** | Query sub-issues: `github_issue_read(method="get_sub_issues", issue_number=N)` | `[]` empty or verified all closed |
| **2** | Verify PR merge state: `github_pull_request_read(method="get", pullNumber=PR)` | `merged_at` field exists |
| **3** | Close child issues | Only children addressed by merged PR |
| **4** | Re-query parent sub-issues | Verify all children now closed |
| **5** | Close parent | Only if ALL children closed |

**If ANY step fails → DO NOT CLOSE the issue.**

### Example: Parent Closure Workflow

```python
# Step 1: ALWAYS query sub-issues FIRST (MANDATORY)
children = github_issue_read(method="get_sub_issues", issue_number=parent_issue)

if children:
    # Parent with sub-issues - must verify all children closed
    open_children = [c for c in children if c.state == "open"]
    if open_children:
        # BLOCK: Cannot close parent with open children
        post_warning_comment(parent_issue, open_children)
        return  # DO NOT CLOSE
    
# Step 2: Verify PR merge
pr = github_pull_request_read(method="get", pullNumber=pr_number)
if not pr.get("merged_at"):
    return  # DO NOT CLOSE - PR not merged

# Steps 3-5: Proceed with closure only after all checks pass
close_issue_with_summary(parent_issue)
```

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
- **The MANDATORY sub-issue query prevents violations**

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

### WIP Commit Before HALT (MANDATORY)

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

When implementation halts (for ANY reason - awaiting approval, awaiting clarification, error, session end), uncommitted changes are at risk from:
- Session crashes
- Context window exhaustion
- Developer needs to switch branches
- Machine restarts

**✅ REQUIRED BEFORE ANY HALT:**

```bash
git status
# If changes exist:
git add -A
git commit -m "WIP: Phase N - <description>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

**🚫 FORBIDDEN:**
- HALTing without committing uncommitted changes
- Leaving working tree dirty before HALT
- "Waiting" without preserving work in progress

**✅ WIP Commit Characteristics:**
- Prefix: `WIP:` for easy identification
- Phase: Include phase number for context
- Description: Brief description of work in progress
- Trailers: Same co-author trailers as full commits
- Squashable: Can be amended later with subsequent work

**See `111-git-commit-workflow.md` → "WIP Commit Before HALT" section for complete workflow.**

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

## Critical Violation: Auto-Issue Creation for Repeated Workflow Violations

**⚠️ Repeated bypass of mandatory workflows is a CRITICAL GUIDELINE VIOLATION that MUST be tracked.**

When the agent bypasses mandatory workflow steps (review-prep, PR creation, issue closure), an issue MUST be created to track the violation.

### What Triggers Auto-Issue Creation

| Violation | When to Create Issue |
|-----------|----------------------|
| Skipping review-prep | Agent HALTs without pushing branch, generating compare URL, or posting to issue/chat |
| Bypassing PR workflow skill | Agent manually runs git commands instead of invoking skill |
| PR creation without instruction | Agent creates PR without explicit "create a PR" from user |
| Closing issues before PR merge | Agent closes issues without verifying merge via GitHub API |

### Auto-Issue Workflow

**When violation detected:**

1. Create issue: `[SPEC-FIX] Review-prep workflow bypass` (or relevant violation type)
2. Document which implementation phase was affected
3. Add `needs-approval` label
4. Post comment explaining:
   - What violation occurred
   - Which files/workflow were affected
   - What correct workflow should have been followed

### Issue Template for Violations

```markdown
# [SPEC-FIX] <Violation Type>

**Violation:** <What occurred>

**Affected Files:**
- <File paths that were modified without proper workflow>

**Expected Workflow:**
1. <Step 1 of correct workflow>
2. <Step 2 of correct workflow>
...

**What Happened:**
<Description of how workflow was bypassed>

**Correction Required:**
- <What needs to be verified/fixed>

---
🤖 ❌ Violation detected by <AgentName> (<ModelID>)
```

### Why This Matters

- Violations indicate gaps in workflow understanding or enforcement
- Tracking violations helps identify patterns
- Creates accountability for workflow compliance
- Enables systematic improvement of guidelines

---

**Search guidelines:** Use `srclight_search_symbols` or `pycharm_search_in_files_by_text` to find relevant guidelines.