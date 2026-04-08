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
| **MCP tools** | Use PyCharm/GitHub MCP for file operations when available |
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

| Authorization | Scope | Behavior |
|---------------|-------|----------|
| `#34 approved` (parent with sub-issues) | ALL sub-issues authorized | Complete ALL phases in sequence, HALT once at end |
| `#39 approved` (single sub-issue) | That sub-issue only | Complete that phase, HALT after completion |
| `approved: 1.2` (specific phase) | That phase only | Complete that phase, HALT after completion |

**⚠️ PROHIBITED (Common Misinterpretation):**
- 🚫 DO NOT halt after each phase of multi-task spec
- 🚫 DO NOT ask for re-authorization between phases
- 🚫 DO NOT treat sub-issues as separate authorization units

**✅ REQUIRED Behavior:**
1. User authorizes parent issue
2. Verify: parent has sub-issues? → ALL sub-issues authorized (cascade)
3. Complete Phase 2 (or resume from current phase)
4. Continue to Phase 3, Phase 4, Phase 5, Phase 6
5. Report ONCE at the end
6. HALT ONCE after ALL phases complete

**Exception: User explicitly names a phase**
- If user says "Phase 2 only" or "approved: 1.2" → complete that phase ONLY, then HALT
- The explicit phase restriction OVERRIDES the cascade

**Rationale:**
- Sub-issues exist for **tracking visibility**, not authorization gates
- GitHub sub-issue view shows progress across all phases
- Developer already approved the entire spec—redundant per-phase HALTs waste time
- Sub-issue database IDs link phases to parent for GitHub's hierarchy view

### Revision Revokes Approval (MANDATORY)

**Any modification to a spec or task document MUST immediately revoke approval.**

When a spec is modified:
1. **Status transitions to pending**: `STATUS: X.Y` → `STATUS: X.Y (REVISED - NEEDS APPROVAL)`
2. **Label applied**: Add `needs-approval` label to the issue
3. **Agent MUST HALT**: Do NOT proceed with implementation
4. **Fresh authorization required**: New explicit approval needed before implementation

**Note**: When using `revise` command, the agent MAY post comments explaining changes but MUST NOT proceed with implementation. `revise` commands allow only documentation updates, never code changes.

**This applies to:**
- Any modification to the spec body (requirements, steps, criteria)
- Any modification to task steps or acceptance criteria
- Typo fixes in spec content (use GitHub comments for clarifications instead)
- Minor clarifications that affect interpretation

**Exempt from approval revocation:**
- STATUS marker updates (`☐ → ☑`, `1.1 → 1.2`)
- Progress comments added to issue
- Bug report additions (separate from spec content changes)

### Label Handling

**The `needs-approval` label is informational when explicit authorization is present.**

| Situation | Action |
|-----------|--------|
| User authorizes AND label present | Proceed with implementation. Label is informational, not blocking. |
| User authorizes AND no label | Proceed with implementation. |
| No authorization AND label present | HALT and wait for explicit authorization. |
| No authorization AND no label | Check for other blockers; proceed if clear. |

**Workflow:**
1. **Explicit authorization received** → Proceed (label status is informational)
2. **No explicit authorization** → Check for `needs-approval` label
3. **Label present without authorization** → HALT and wait for user to authorize

### Bug Report Response

When bug report requires code changes:

1. Add `needs-approval` label
2. Post additional spec comment
3. HALT immediately
4. Wait for explicit `go` or `approved`

## Skill Enforcement (CRITICAL)

**⚠️ CRITICAL: Skills MUST enforce authorization — guidelines alone are insufficient.**

### Why Skills Must Enforce

- **Guidelines document** what agents should do
- **Skills contain code** that actually executes
- Agents have proven to bypass documented guidelines
- Enforcement in code prevents bypass

**This is not theoretical. This actually happened:**
- User said "Continue IF you have next steps"
- Agent interpreted this as authorization
- Agent committed, pushed, created PR
- Both implementation and PR timing authorizations were bypassed

### Which Skills MUST Enforce

| Skill | Authorization Check Required |
|-------|------------------------------|
| `git-workflow` `--task pre-work` | ✅ YES - Check explicit "approved"/"go" before branch creation |
| `git-workflow` `--task pr-creation` | ✅ YES - Check explicit "create a PR" before PR creation |
| `git-workflow` `--task review-prep` | ❌ NO - Automatic after implementation |
| `git-workflow` `--task cleanup` | ❌ NO - Automatic after PR merge confirmed |
| All other skills | ❌ NO - Not git operation related |

### Enforcement Matrix

| Scenario | Action |
|----------|--------|
| Explicit "approved"/"go" | PROCEED - explicit auth wins |
| Label + no auth | HALT - wait for authorization |
| No label + no auth | HALT - wait for authorization |
| Conditional phrase | HALT - not explicit authorization |
| Implementation complete | HALT - wait for "create a PR" |

### What Skills MUST Check

**For `pre-work` task:**
1. Get issue context from invocation
2. Query GitHub Issue for labels (`needs-approval`)
3. Query GitHub Issue for comments (look for "approved", "go", #"N approved")
4. Check for conditionals ("if", "when", "continue if")
5. Apply enforcement matrix

**For `pr-creation` task:**
1. Check conversation for "create a PR" instruction
2. Distinguish implementation auth ("approved") from PR auth ("create a PR")
3. Apply enforcement matrix

### Conditional Phrases Are NOT Authorization

| Phrase | Why NOT Authorization |
|--------|----------------------|
| "continue if you have next steps" | CONDITIONAL - agent must have next steps OR ask |
| "proceed when ready" | CONDITIONAL - agent must report ready |
| "if you have a plan, continue" | CONDITIONAL - agent must present plan |
| "should I do X?" | QUESTION - seeking permission |
| Implementation complete | NOT an instruction |

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