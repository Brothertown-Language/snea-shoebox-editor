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
| **Review-prep after implementation** | Push branch, generate compare URL, post summary, HALT — MANDATORY after implementation |
| **Human-only merge** | Agents MUST NEVER merge PRs |
| **MCP tools** | Use PyCharm/GitHub MCP for file operations when available |
| **Silent halt** | HALT after completion, after PR creation — no prompts |
| **PR timing** | PRs require explicit `"create a PR"` instruction |
| **Issue closure** | Close issues ONLY after PR merge confirmed |

### Implementation Gates (MANDATORY)

**⚠️ All implementation MUST invoke pattern verification at these gates:**

| Gate | Invocation | Purpose |
|------|------------|---------|
| Before creating ANY file | `/skill implementation-quality --task file-locations` | Verify file location patterns |
| At implementation start | `/skill implementation-quality --task code-structure` | Verify code structure patterns (load once, reference continuously) |
| Before running commands | `/skill implementation-quality --task environment` | Verify environment patterns |
| Before handling data | `/skill implementation-quality --task data-integrity` | Verify data integrity patterns |

**Enforcement:** These invocations are MANDATORY. Do NOT proceed with implementation without first loading the appropriate task and verifying pattern compliance.

**Loop Prevention:** If tool invocation fails repeatedly without progress, see `150-task-loop-prevention.md` for detection heuristics and exit strategies.

### Sub-Issue Verification Gate (MANDATORY)

**⚠️ Before implementing ANY spec, the agent MUST verify sub-issue structure:**

```python
# MANDATORY: Before implementing spec N
sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)

if sub_issues:
    # Multi-task spec - sub-issues exist
    # Proceed with implementation (sub-issues track phases)
    pass
else:
    # Check if single-task or missing sub-issues
    if has_multiple_phases(spec_body):
        # Multi-task spec without sub-issues - AUTO-CREATE THEM
        # See github-sub-issues skill for workflow
        create_sub_issues_for_phases(issue_number=N)
    else:
        # Single-task spec - no sub-issues needed
        proceed_with_implementation()
```

**Single-Task Exemption:**
- Specs with exactly ONE implementation task do NOT require sub-issues
- All multi-task specs MUST have sub-issues before implementation

**Why This Matters:**
- Sub-issues provide phase-level tracking for multi-task specs
- Each phase must be trackable as its own GitHub Issue
- Parent-child hierarchy enables proper closure workflow
- Prevents "orphaned" phases without issue tracking

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

### Authorization Scope for Multi-Phase Specs (CRITICAL)

**⚠️ Unqualified approval authorizes ALL phases of a spec.**

When a developer says `approved` or `go` **without a phase qualifier**, the agent is authorized to implement ALL phases of the spec in sequence. The agent will proceed from Phase 1 through all phases without stopping for re-approval between phases.

| Command | Scope | Behavior |
|---------|-------|----------|
| `approved` | ALL phases | Proceed through all phases without stopping |
| `go` | ALL phases | Proceed through all phases without stopping |
| `approved: 1` | Phase 1 only | HALT after Phase 1, wait for next authorization |
| `approved: 2.3` | Phase 2 Step 3 only | HALT after completing Step 3, wait for next authorization |

**Rationale:**
- Unqualified approval matches developer mental model of "approved means go ahead"
- Phase-by-phase approval is intentional scoping (opt-in via qualifiers)
- Prevents unnecessary back-and-forth on multi-phase implementations

**Developer Workflow:**

- **Approve entire spec:** Use `approved` or `go` without qualifiers
- **Approve one phase:** Use `approved: N` where N is the phase number
- **Approve specific step:** Use `approved: N.M` where N is phase and M is step

**Agent Behavior:**

**With unqualified approval (`approved` or `go`):**
1. Proceed through Phase 1
2. Continue to Phase 2 (no HALT)
3. Continue through all remaining phases
4. HALT only after completing the entire spec

**With qualified approval (`approved: 1` or `approved: 2.3`):**
1. Proceed through the authorized phase/step ONLY
2. HALT after completing that phase/step
3. Wait for next authorization before continuing

## Compound Command Recognition

**Approval tokens must be STANDALONE (separated by whitespace) to constitute valid authorization.**

| Message | Standalone? | Authorization? |
|---------|-------------|----------------|
| `"approved check pr"` | YES (space separation) | YES |
| `"#196 approved"` | YES (space separation) | YES |
| `"#196 approvedcheck pr"` | NO (compound text) | NO |
| `"check pr"` | N/A (verification) | NO |

See `approval-gate` skill → `verify-authorization` task for complete pattern matching algorithm.

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

## Closed-Issue Audit (CRITICAL)

**When a closed issue is targeted for implementation via `#N approved`, the agent MUST audit before proceeding.**

### Why This Matters

Issuing `#N approved` for a closed issue assumes closure was correct. Without audit:

- Incorrectly-closed parents with open children propagate violations
- Agent implements on top of already-broken workflow state
- Missing work goes undetected

### Pre-Authorization Audit (MANDATORY)

**When `#N approved` targets a closed issue:**

1. **Query sub-issues immediately**: `github_issue_read(method="get_sub_issues", issue_number=N)`
2. **Detect violations**: Open sub-issues on closed parent = violation
3. **If NO sub-issues or ALL sub-issues closed**: Proceed to implementation
4. **If ANY sub-issue open**: Execute closed-issue remediation workflow (see `124-github-archive-workflow.md`)

### Direct Inspection Requirement (CRITICAL)

**NEVER rely on comments, changelogs, or memory.**

The agent MUST inspect the project directly:

| Evidence Type | Inspection Method | What It Proves |
|---------------|-------------------|----------------|
| **Code changes** | Read actual files mentioned in spec | Implementation exists or doesn't |
| **PR merge state** | `github_pull_request_read(method="get")` | PR was merged or wasn't |
| **Branch state** | `git log`, `git branch` | Commits exist in history |
| **Database state** | Query actual database/tables | Schema/data changes applied |
| **Config state** | Read actual config files | Configuration changed |

**FORBIDDEN Evidence Sources:**
- Issue comments (indirect, unverified)
- Memory from previous sessions
- Changelogs/README notes
- Issue body claims (only spec requirements are factual)
- Project conventions/assumptions

### Remediation Decision Tree

**Based on direct inspection results:**

| Inspection Result | Correct Action |
|------------------|----------------|
| Code exists in codebase as specified | Close sub-issue: `completed` |
| PR exists and `merged_at` is set | Close sub-issue: `completed` |
| No code, no PR, nothing implemented | **Reopen parent** (work not done) |
| Parent closed, no merged PR | **Reopen parent** (premature closure) |
| Superseding issue exists with completed work | Verify superseding issue complete, close: `not_planned` |

### Remediation Comments

**When agent remediates, it posts comments with direct inspection results:**

```
🤖 ✅ **Auto-Remediated: [Action]**

Parent issue #N was closed while this sub-issue remained open.

**Direct Inspection Results:**
- [Actual file/code checked and result]
- [Actual PR state from API call]
- [Actual evidence from project]

**Action:** [Close/Open] based on direct inspection

---
🤖 ✅ Completed by <AgentName> (<ModelID>)
```

### When to HALT During Audit

**HALT only when direct inspection is impossible:**
- Cannot access codebase (permission error)
- Cannot call GitHub API (network/auth failure)
- Spec is ambiguous about what deliverables to check

**HALT with actionable message explaining what couldn't be inspected.**

### Integration Points

| Workflow Stage | Guideline Reference |
|----------------|---------------------|
| Pre-authorization audit | This section |
| Post-merge cleanup | `124-github-archive-workflow.md` → "Parent Closure Pre-Check" |
| Skill enforcement | `approval-gate` skill → `verify-authorization` task |

## What This Guideline Does NOT Cover

**The skill handles procedural workflow:**

- Spec + approval requirements details
- Re-evaluation checklist
- Pre-implementation verification steps
- Single-task exemption logic
- Authorization scope rules
- Workflow decision tree

**See the skill for complete implementation details.**

## Questions Are Not Bypass Authorization (CRITICAL)

**⚠️ Answering questions is NOT authorization verification. Questions are NOT a shortcut around mandatory checks.**

### The Problem

Agents treat question-answering as a shortcut to bypass verification:

- User asks "Should I implement #123?" → Agent implements #123
- User asks "Would #456 fix the issue?" → Agent implements #456
- User says "approved check pr" → Agent treats "approved" as authorization AND skips verification

This is WRONG. Questions require verification FIRST, then response.

### 🚫 FORBIDDEN (ZERO TOLERANCE)

| Forbidden Pattern | Why It's Wrong |
|-------------------|-----------------|
| Answering question without session init | Missing critical context |
| Answering question without checking conflicts | Duplicate/wasted work |
| Treating question as authorization shortcut | Questions are NOT approval |
| Skipping verification because "user asked" | User inquiry ≠ permission to bypass |
| Responding to "#123 approved check pr" without checking | Compound text parsing is evasion |

### ✅ REQUIRED SEQUENCE

**When user asks ANY question:**

1. **Run verification sequence** (session init, superseding check, codebase verify)
2. **Query sub-issues** if implementation involved
3. **THEN respond to the question**
4. **If question is about implementation**: Check authorization separately
5. **If question implies implementation**: HALT and wait for explicit `approved`/`go`

### Question Types and Required Responses

| Question Type | Required Response |
|----------------|-------------------|
| "Should I implement #123?" | Verify #123 first, then answer if it's valid. Do NOT implement. |
| "Would #456 fix the issue?" | Analyze #456, then answer. Do NOT implement. |
| "#123 approved" | Parse as standalone token. Implement #123. |
| "#123 approved check pr" | Parse "approved" as standalone → implement. "check pr" is additional instruction. |
| "What's the status of #789?" | Verify #789's state, then answer. No implementation implied. |
| "Can you fix the bug?" | Create spec, add `needs-approval`, HALT. Answer "yes, spec created." |

### Authorization Token Parsing (CRITICAL)

**Approval tokens must be STANDALONE (separated by whitespace) to count.**

| Message | Token Parsing | Authorization? | Action |
|---------|---------------|----------------|--------|
| `approved check pr` | ["approved", "check", "pr"] | YES (approved standalone) | Implement, then check PR |
| `#196 approved` | ["approved"] | YES | Implement #196 |
| `#196 approvedcheck pr` | ["approvedcheck"] | NO (compound text) | Respond to question, do NOT implement |
| `check pr` | No approval token | NO | Check PR, do NOT implement |

**CRITICAL**: Do NOT parse compound text to extract approval. If "approved" is not surrounded by whitespace, it is NOT authorization.

### Why This Matters

- Questions can be answered without authorization
- Authorization enables implementation, not shortcuts
- Verification protects against stale/conflicting specs
- Proper parsing prevents compound-text bypass

### Integration with Verification-First Protocol

This section COMPLEMENTS the Verification-First Response Protocol in `085-engineering-approach.md`:

- **Verification-First**: Run checks before ANY response
- **Questions Are Not Bypass**: Authorization is separate from question-answering
- **Together**: Verify first, answer question, THEN check authorization if implementation implied

## Related Guidelines

| Guideline | Purpose |
|-----------|---------|
| `000-critical-rules.md` | Critical violations and auditor enforcement |
| `020-go-prohibitions.md` | GO command restrictions |
| `120-github-issue-first.md` | Issue-first strategy and sub-issues |
| `124-github-archive-workflow.md` | Issue closure timing |
| `github-sub-issues` skill | Sub-issue creation workflow |
| `pr-creation-workflow` skill | PR creation timing |