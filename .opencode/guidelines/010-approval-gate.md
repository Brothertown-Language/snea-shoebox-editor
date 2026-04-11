# Approval Gate

> **See `approval-gate` skill for complete procedural workflow including:**
> - Spec + authorization requirements
> - Sub-issue verification gate
> - Single-task exemption
> - Re-evaluation checklist
> - Bug report response

## Tier 0: Zero Tolerance Rules

**These rules are inviolable. Violation is a protocol breach.**

### Mandatory Requirements

| Requirement | Rule |
|-------------|------|
| **Spec before code** | NO code/guideline changes WITHOUT approved spec |
| **Authorization required** | NO implementation WITHOUT explicit `"approved"` or `"go"` |
| **Explicit auth overrides label** | When user says `approved`/`go`, proceed REGARDLESS of `needs-approval` label |
| **Branch first** | Create feature branch BEFORE any file modification |
| **Human-only merge** | Agents MUST NEVER merge PRs |
| **MCP tools** | Use appropriate tools per five-tier hierarchy (see `mcp-tool-usage` skill) |
| **Silent halt** | HALT after completion, after PR creation — no prompts |
| **PR timing** | PRs require explicit `"create a PR"` instruction |
| **Issue closure** | Close issues ONLY after PR merge confirmed |

### Explicit Authorization Priority (Critical)

**⚠️ When user provides explicit authorization (`approved`, `go`, `#123 approved`), proceed with implementation even if the `needs-approval` label is present.**

The `needs-approval` label is a **tracking tool**, not a permanent gate. Its purpose is:
- Indicate "awaiting approval" visually
- Remind reviewers that approval hasn't been given yet
- Block agents from proceeding **until** explicit authorization is received

**The label does NOT override explicit user authorization.**

| Scenario | Action |
|----------|--------|
| User says `approved` AND label present | ✅ **PROCEED** - explicit auth wins |
| User says `#123 approved` AND label present | ✅ **PROCEED** - explicit auth wins |
| User says `go` AND label present | ✅ **PROCEED** - explicit auth wins |
| NO user authorization AND label present | ⛔ **HALT** - wait for authorization |
| Label removed by user | ✅ **Proceed if authorized** - no issue |

### Authorization Scope

- **Issue-bound**: Authorization applies ONLY to the specific issue where it was given
- **Session-bound**: New session = new authorization required (no carryover from previous sessions)
- **Single-use**: Authorization for current phase/task only within that issue
- **External input invalidates**: Bug reports require re-authorization
- **Revision ≠ implementation**: Spec updates don't authorize code changes

**🚫 CRITICAL: Old authorizations do NOT apply:**
- "Approved #332" in previous session → NOT VALID for new session
- Previous session authorization → NOT VALID for new issue/spec
- Authorization is ZERO-BASED — every task needs NEW authorization

### Multi-Task Spec Authorization (CRITICAL)

**When parent issue has sub-issues:** authorization cascades to ALL sub-issues.

**See `approval-gate` skill → "Multi-Task Spec Authorization" for the complete authorization cascade workflow and enforcement matrix.**

Key rules:
- 🚫 DO NOT halt after each phase of multi-task spec
- 🚫 DO NOT ask for re-authorization between phases
- 🚫 DO NOT treat sub-issues as separate authorization units
- ✅ Complete ALL phases, then report ONCE and HALT ONCE

**Exception:** User explicitly names a phase (e.g., "approved: 1.2" or "Phase 2 only") → complete that phase ONLY, then HALT.

### Revision Revokes Approval (MANDATORY)

**Any modification to a spec or task document MUST immediately revoke approval.**

**See `approval-gate` skill for revision status transition rules, mandatory actions, and exemption categories.**

Key rule: Revision = `STATUS: X.Y (REVISED - NEEDS APPROVAL)` + `needs-approval` label + chat output + Issue comment + HALT.

Exempt from approval revocation:
- STATUS marker updates (`☐ → ☑`, `1.1 → 1.2`)
- Progress comments added to issue
- Bug report additions (separate from spec content changes)

### Label Handling

**The `needs-approval` label is informational when explicit authorization is present.**

**See `approval-gate` skill for the complete label handling enforcement matrix.**

Key rule: Explicit authorization (`approved`/`go`) OVERRIDES the `needs-approval` label.

### Bug Report Response

**See `approval-gate` skill for the complete bug report response protocol.**

Key rule: Bug reports requiring code changes → add `needs-approval` label → HALT → wait for explicit authorization.

### Bug Discovery Protocol (CRITICAL)

**⚠️ Finding a bug during analysis or any other activity does NOT authorize fixing it.**

**See `000-critical-rules.md` → "Bug Discovery Does NOT Authorize Bug Fixing" for the complete authorization matrix, self-correction protocol, and enforcement details.**

Key rules:
- 🚫 NEVER edit source code after discovering a bug without an approved spec
- 🚫 NEVER create a branch for a bug fix without authorization
- ✅ ALWAYS create a bug report issue (permitted without authorization)
- ✅ ALWAYS perform read-only analysis (permitted without authorization)
- ✅ ALWAYS HALT and wait for explicit authorization before any code changes
- ✅ If you catch yourself editing code without a spec, immediately `git checkout` and HALT

**Bug discovery is a reporting action, NOT an implementation authorization.**

## Skill Enforcement (CRITICAL)

**⚠️ CRITICAL: Skills MUST enforce authorization — guidelines alone are insufficient.**

**See `approval-gate` skill for the complete enforcement specification including:**
- Which skills MUST check authorization
- What each skill MUST check (pre-work, pr-creation)
- Enforcement matrix (explicit auth, label + no auth, conditionals)
- Conditional phrases that are NOT authorization

## What This Guideline Does NOT Cover

**The skill handles procedural workflow:**

- Spec + approval requirements details
- Re-evaluation checklist
- Pre-implementation verification steps
- Single-task exemption logic
- Authorization scope rules
- Workflow decision tree

**See the skill for complete implementation details.**

## Related Guidelines

| Guideline | Purpose |
|-----------|---------|
| `000-critical-rules.md` | Critical violations and auditor enforcement |
| `020-go-prohibitions.md` | GO command restrictions |
| `120-github-issue-first.md` | Issue-first strategy and sub-issues |
| `124-github-archive-workflow.md` | Issue closure timing |
| `github-sub-issues` skill | Sub-issue creation workflow |
| `pr-creation-workflow` skill | PR creation timing |