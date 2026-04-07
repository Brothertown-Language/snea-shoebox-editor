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

---

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
2. Store ALL output values for session duration
3. Use `GIT_OWNER` and `GIT_REPO` for EVERY GitHub MCP call
4. NEVER assume or hardcode owner/repo values

---

## Critical Violation: Missing AI Co-Authored Attribution

**⚠️ Failing to include AI co-authored attribution is a CRITICAL GUIDELINE VIOLATION.**

Attribution for AI-authored content. See `080-code-standards.md` for complete requirements.

**What Requires Attribution:**
- Python files (module docstring)
- README files (footer section)
- New repositories (README section required)
- Original docs (footer)

**What Does NOT Require Attribution:**
- Standard licenses (MIT, Apache, GPL)
- Copy-pasted content (original source holds copyright)
- Auto-generated files (lock files, `__pycache__`)
- Framework boilerplate
- Minor edits

**Format:** `Co-authored with AI: <AI-Name> (<model-id>)`

---

## Critical Violation: Unauthorized Question Asking

**⚠️ Asking questions during implementation is a CRITICAL GUIDELINE VIOLATION.**

The agent must NEVER ask questions like:
- "What should I do next?"
- "Should I continue?"
- "Ready for PR?"
- "How would you like me to proceed?"

**✅ Required Behavior:**
- Task complete but more work remains → Continue autonomously
- Task complete and no more work → HALT silently, executive summary in chat
- Blocked by genuine ambiguity → Post comment to issue asking for clarification, then HALT
- Waiting for authorization → HALT silently

---

## Critical Violation: GitHub Progress Comments Are NOISE — CHAT ONLY

> **See `github-comments` skill for complete protocol.**

GitHub Issue comments are for **substantive content** — NOT for state tracking or progress notifications.

**State tracking uses LABELS. Progress notifications go to CHAT.**

### 🚫 FORBIDDEN in GitHub Comments
- State tracking (STATUS updates, progress blocks)
- Progress notifications (implementation, review-prep, PR creation)
- Routine updates (file changes, test results)

### ✅ ALWAYS Acceptable in GitHub Comments
- Answering questions asked via GitHub comments
- Executive summary when issue closes (historical record)

### ✅ Chat Output (with URL)
- Implementation complete → Executive summary + compare URL
- Review-prep complete → Executive summary + compare URL
- PR created → PR URL

---

## Critical Violation: Ignoring Issue Comments

**⚠️ Failing to respond to user comments on GitHub Issues is a CRITICAL GUIDELINE VIOLATION.**

**MANDATORY RESPONSE PROTOCOL:**
1. Read issue comments via `github_issue_read method=get_comments`
2. Respond PUBLICLY via `github_add_issue_comment`
3. Include analysis, findings, and next steps
4. Ask for authorization if needed

> **See `github-comments` skill → "Responding to User Comments (MANDATORY)" section.**

---

## Critical Violation: URLs in GitHub Issue Comments

**⚠️ Putting URLs in GitHub Issue comments is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN

**NEVER put URLs in GitHub Issue comments.**

| Location | Audience | Purpose | URL? |
|----------|-----------|---------|------|
| GitHub Issue comment | Future maintainers | Historical context (WHAT/WHY) | 🚫 NO |
| Chat output | Immediate developer | Actionable navigation (clickable diff) | ✅ YES |

### ✅ REQUIRED

1. **GitHub Issue comments**: Context-based summary **WITHOUT URL**
2. **Chat output**: Same executive summary **WITH URL**

> **See `github-comments` skill for complete requirements.**

---

## Critical Violation: Sub-issue Structure Bypass — Multi-task Specs

**⚠️ Implementing a multi-task spec without sub-issues is a CRITICAL GUIDELINE VIOLATION.**

1. **First**: Call `github_issue_read method=get_sub_issues` on the parent issue
2. **When empty**: AUTO-CREATE sub-issues at PHASE level (see `github-sub-issues` skill)
3. **Then**: Verify the task being implemented is linked as a sub-issue

**🚫 FORBIDDEN:**
- Implementing a phase that exists only as text in parent body
- Proceeding when `get_sub_issues` returns empty for multi-task specs
- Assuming markdown checkboxes = task tracking
- Creating step-level sub-issues instead of phase-level

**✅ REQUIRED:**
- Sub-issues at PHASE level, not step level
- Each phase as separate GitHub Issue linked via `github_sub_issue_write method=add`
- Single-task specs are exempt

> **See `github-sub-issues` skill for complete workflow.**

---

## Critical Violation: Bypassing Mandatory Verification Gates

**⚠️ Skipping verification gates to answer questions immediately is a CRITICAL GUIDELINE VIOLATION.**

### Mandatory Gates Before ANY Response

| Gate | Check | Action |
|------|-------|--------|
| **Session Init** | Has session init run? | Run `ai_bin/session_init.py` FIRST |
| **Codebase State** | Is codebase current? | Verify with `srclight_codebase_map` |
| **Spec Conflicts** | Are there superseding issues? | Query all `[SPEC]` issues |

### ✅ REQUIRED

**Before responding to questions:**
1. Run session init if not already done
2. Check for superseding/conflicting issues
3. Verify codebase state matches spec assumptions
4. HALT if verification reveals conflicts

---

## Critical Violation: Scope Creep — NEVER Do Things Outside the Spec

**⚠️ Implementing changes not explicitly called for in the spec is a CRITICAL GUIDELINE VIOLATION.**

The spec defines EXACTLY what to implement. Nothing more. Nothing less.

**🚫 FORBIDDEN:**
- Adding "helper" functions not requested
- Improving "nearby" code while you're there
- Refactoring things adjacent to the change
- Adding tests for unrequested functionality
- Any change not explicitly stated in spec

**If you think something ELSE should be changed:**
1. STOP — do not implement it
2. Comment on the issue noting the additional concern
3. Wait for explicit approval

---

## Critical Violation: Incorrect HALT After Phase Completion — Unqualified Approval

**⚠️ Halting after completing a phase when unqualified approval was given is a CRITICAL GUIDELINE VIOLATION.**

When a developer says `approved` or `go` **without a phase qualifier**, this authorizes ALL phases. The agent must continue through all phases without stopping.

### 🚫 FORBIDDEN

| Forbidden Pattern | Why It's Wrong |
|-------------------|-----------------|
| HALT after Phase 1 when `approved` given | Unqualified approval = ALL phases authorized |
| Mark remaining phases as `needs-approval` | Approval was already granted |
| Ask for re-approval after each phase | Friction that violates developer mental model |

### ✅ REQUIRED Behavior

**With unqualified approval (`approved` or `go`):**
1. Proceed through Phase 1
2. Continue to Phase 2 (no HALT between phases)
3. Continue through ALL remaining phases
4. HALT only after completing ENTIRE spec

**With qualified approval (`approved: 1` or `approved: 2.3`):**
1. Proceed through the authorized phase/step ONLY
2. HALT after completing that phase/step
3. Wait for next authorization

> **See `010-approval-gate.md` → "Authorization Scope for Multi-Phase Specs"**

---

## Critical Violation: Spec Without Investigation

**⚠️ Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION.**

Investigation MUST be completed BEFORE finalizing a spec for review.

**Investigation Completion Criteria:**
- Problem understood with context
- Codebase explored for existing patterns
- Hypotheses tested with isolated test scripts
- Alternatives considered with tradeoffs
- Risks identified with mitigation strategies
- Success criteria defined (testable, measurable)

---

## Critical Violation: Implementing Stale or Superseded Specs

**⚠️ Implementing a stale or superseded spec without revision is a CRITICAL GUIDELINE VIOLATION.**

Before implementing OR revising any spec, check for:
- Superseding issues (conflicting objectives)
- Staleness from implemented specs (code changed, requirements shifted)

**If superseding issue exists:**
1. SILENTLY HALT
2. Report the conflict to the issue
3. Do NOT proceed

**If staleness detected:**
1. REVISE the spec to reflect current reality
2. Report the revision via comment
3. HALT — wait for approval

---

## Auditor Skills Enforcement

**⚠️ MANDATORY AUDIT CHAIN: ALL auditor skills must run in order. NO SKIPPING.**

### Complete Audit Chain

| Order | Skill | Purpose |
|-------|-------|---------|
| **1st** | `concern-separation-auditor` | Phase structure, deployment independence |
| **2nd** | `spec-auditor` | Fresh-start context, completeness |
| **3rd** | `dev-architect --task review-spec` | Architectural correctness |

**CRITICAL: If you run ONE auditor, you MUST run ALL THREE in order.**

> **See individual skill files for complete requirements.**

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

1. **STOP** - Do NOT run git commands manually
2. **INVOKE** the appropriate skill task
3. **LET THE SKILL** handle all operations
4. **FOLLOW** what the skill does/outputs

> **See `git-workflow` skill for complete workflow.**

---

## Critical Violation: Skipping Review-Prep After Implementation

**⚠️ Failing to invoke review-prep after implementation completes is a CRITICAL GUIDELINE VIOLATION.**

After implementation completes, the agent MUST automatically:
1. **Invoke `/skill git-workflow --task review-prep`** (MANDATORY - NO EXCEPTIONS)
2. Skill handles: commit → push → compare URL → post to chat → HALT
3. **NO silent HALT without completing the workflow**

**🚫 FORBIDDEN:**
- Completing implementation and just HALTing silently
- Skipping review-prep because "changes are trivial"
- Proceeding directly to PR creation without compare URL

**✅ REQUIRED:**
1. Implementation completes
2. **AUTOMATIC:** Invoke `/skill git-workflow --task review-prep`
3. Skill handles: commit → push → compare URL → HALT
4. Report completion with executive summary

> **See `git-workflow` skill → `review-prep` task.**

---

## Critical Violation: Creating PRs Without Explicit Instruction

**⚠️ Creating a PR without EXPLICIT developer instruction is a CRITICAL GUIDELINE VIOLATION.**

PRs require EXPLICIT phrases: "create a PR", "pr", "make a PR", "push and create PR"

**🚫 FORBIDDEN:**
- Creating PR after "approved" or "go" — authorizes implementation ONLY
- Creating PR after completing implementation
- Asking "Ready for a PR?"

**✅ REQUIRED:**
- After completing implementation: report, then STOP and wait
- Only create PR after EXPLICIT "create a PR"
- Then: squash, push, create PR, report URL, STOP

> **See `pr-creation-workflow` skill for complete workflow.**

---

## Critical Violation: Closing Issues Before PR Merge

**⚠️ Closing issues before PR merge is a CRITICAL GUIDELINE VIOLATION.**

**🚫 FORBIDDEN:**
- Closing issues immediately after implementation
- Closing issues when PR is created but not merged
- Closing parent issues while child issues remain open
- Closing issues without GitHub API verification

**✅ REQUIRED SEQUENCE:**
1. Complete implementation → Create PR → Report URL → HALT
2. Wait for human to merge PR
3. User confirms "pr merged" → Call `github_pull_request_read method=get` to verify
4. Verify `merged_at` timestamp exists
5. Only after API confirms merge → Close issues

> **See `124-github-archive-workflow.md` and `git-workflow` skill → `cleanup` task.**

---

## Critical Violation: Parent/Child Issue Closure

**⚠️ Closing a parent issue while child issues remain open is a CRITICAL GUIDELINE VIOLATION.**

### MANDATORY Pre-Close Checklist (NO EXCEPTIONS)

| Step | Action | MUST Result |
|------|--------|-------------|
| **1** | Query sub-issues: `github_issue_read(method="get_sub_issues", issue_number=N)` | `[]` empty or all closed |
| **2** | Verify PR merge state: `github_pull_request_read(method="get", pullNumber=PR)` | `merged_at` field exists |
| **3** | Close child issues | Only children addressed by merged PR |
| **4** | Re-query parent sub-issues | Verify all children closed |
| **5** | Close parent | Only if ALL children closed |

**If ANY step fails → DO NOT CLOSE the issue.**

---

## Critical Violation: Deleting Branches Improperly

**⚠️ Improper branch deletion is a CRITICAL GUIDELINE VIOLATION.**

### 🚫 FORBIDDEN
- `git branch -D <branch>` on unmerged branches without explicit request
- `git stash drop` without explicit request
- Preserving merged branches "just in case"
- Asking "should I delete this merged branch?"

### ✅ REQUIRED
- **MERGED branches**: Delete IMMEDIATELY after merge confirmation
- **UNMERGED branches with work**: Preserve until explicitly asked to delete
- **Stashes**: Preserve until explicitly asked to delete

| Branch Status | Action |
|---------------|--------|
| Merged PR | **DELETE IMMEDIATELY** |
| Unmerged with commits | **PRESERVE** |
| Stashes | **PRESERVE** |
| `main` branch | **NEVER DELETE** |

---

## Critical: Engineering Mindset Required

**⚠️ All work must be approached with proper engineering discipline.**

> **See `085-engineering-approach.md` for complete requirements.**

### Core Engineering Principles

1. **Understand Before Solving** — Read code before proposing changes
2. **Design Before Implementing** — Document approach and get approval
3. **Verify Before Declaring Complete** — Run tests, check edge cases
4. **Communicate Changes** — Post comments when changes occur

### WIP Commit Before HALT (MANDATORY)

**CRITICAL: Work-in-progress commits MUST be made before ANY HALT to prevent data loss.**

**✅ REQUIRED BEFORE ANY HALT:**
```bash
git status
# If changes exist:
git add -A
git commit -m "WIP: Phase N - <description>" \
    --trailer "Co-authored-by: <AI-Name> (<model-id>) <ai-email>" \
    --trailer "Co-authored-by: <Human-Name> <human-email>"
```

> **See `111-git-commit-workflow.md` → "WIP Commit Before HALT" section.**