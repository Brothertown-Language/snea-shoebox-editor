# Approval Gate

> **See `approval-gate` skill for complete procedural workflow including:**
> - Spec + authorization requirements
> - Sub-issue verification gate
> - Single-task exemption
> - Re-evaluation checklist
> - Bug report response
> - Authorization cleanup workflow
> - Closed-issue audit workflow

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

### Implementation Gates (MANDATORY)

**⚠️ All implementation MUST invoke pattern verification at these gates:**

| Gate | Invocation | Purpose |
|------|------------|---------|
| Before creating ANY file | `/skill implementation-quality --task file-locations` | Verify file location patterns |
| At implementation start | `/skill implementation-quality --task code-structure` | Verify code structure patterns (load once, reference continuously) |
| Before running commands | `/skill implementation-quality --task environment` | Verify environment patterns |
| Before handling data | `/skill implementation-quality --task data-integrity` | Verify data integrity patterns |

**Enforcement:** These invocations are MANDATORY. Do NOT proceed with implementation without first loading the appropriate task and verifying pattern compliance.

**Loop Prevention:** If tool invocation fails repeatedly without progress, HALT and report the loop. Check for infinite retry patterns in the calling code and add termination conditions.

### Sub-Issue Verification Gate (MANDATORY)

**⚠️ Before implementing ANY spec, the agent MUST verify sub-issue structure:**

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

## Risk-Aware Authorization (CRITICAL)

**⚠️ High-risk and large-blast-radius phases may require explicit phase-by-phase approval, even with unqualified authorization.**

### When Phase-by-Phase Authorization Is Required

| Phase Risk Level | Blast Radius | Authorization Rule |
|-----------------|--------------|---------------------|
| **LOW** | SMALL | Unqualified approval sufficient |
| **MEDIUM** | MEDIUM | Unqualified approval sufficient |
| **HIGH** | SMALL | Unqualified approval sufficient |
| **HIGH** | MEDIUM | **EXPLICIT phase approval recommended** |
| **ANY** | LARGE | **EXPLICIT phase approval required** |

### Risk Levels Defined

| Risk | Characteristics | Examples |
|------|-----------------|----------|
| **LOW** | Read-only, additive, localized, easily reversible | Adding a new query, adding a test file, documentation |
| **MEDIUM** | Modifies existing code, affects one module, moderate rollback complexity | Refactoring a service, adding API endpoint, modifying schema |
| **HIGH** | Breaking changes, affects multiple modules, hard to rollback, production-critical | Database migration, authentication rewrite, API versioning, deployment changes |

### Blast Radius Defined

| Blast Radius | Scope | Rollback Difficulty |
|--------------|-------|---------------------|
| **SMALL** | Single file/module, no dependencies | Easy (simple revert) |
| **MEDIUM** | Multiple files, internal dependencies | Moderate (may need data migration) |
| **LARGE** | Cross-module, external dependencies, production systems | Difficult (may need data rollback, coordination) |

### Authorization Commands for Risk-Aware Phases

**For HIGH/MEDIUM risk or ANY/large blast radius:**

| Command | Purpose |
|---------|---------|
| `approved: N` | Approve only Phase N (phase-by-phase authorization) |
| `approved: N.M` | Approve only Phase N Step M |
| `approved` | Approve ALL phases (only if developer understands cumulative risk) |

## Compound Command Recognition

**Approval tokens must be STANDALONE (separated by whitespace) to constitute valid authorization.**

| Message | Standalone? | Authorization? |
|---------|-------------|----------------|
| `"approved check pr"` | YES (space separation) | YES |
| `"#196 approved"` | YES (space separation) | YES |
| `"#196 approvedcheck pr"` | NO (compound text) | NO |
| `"check pr"` | N/A (verification) | NO |

### Revision Revokes Approval (MANDATORY)

**Any modification to a spec or task document MUST immediately revoke approval.**

When a spec is modified:
1. **Status transitions to pending**: `STATUS: X.Y` → `STATUS: X.Y (REVISED - NEEDS APPROVAL)`
2. **Label applied**: Add `needs-approval` label to the issue
3. **Agent MUST HALT**: Do NOT proceed with implementation
4. **Fresh authorization required**: New explicit approval needed before implementation

**This applies to:**
- Any modification to the spec body (requirements, steps, criteria)
- Any modification to task steps or acceptance criteria
- Typo fixes in spec content (use GitHub comments for clarifications instead)
- Minor clarifications that affect interpretation

**Exempt from approval revocation:**
- STATUS marker updates (`☐ → ☑`, `1.1 → 1.2`)
- Progress comments added to issue
- Bug report additions (separate from spec content changes)

## Questions Are Not Bypass Authorization (CRITICAL)

**⚠️ Answering questions is NOT authorization verification. Questions are NOT a shortcut around mandatory checks.**

### 🚫 FORBIDDEN (ZERO TOLERANCE)

| Forbidden Pattern | Why It's Wrong |
|-------------------|-----------------|
| Answering question without session init | Missing critical context |
| Answering question without checking conflicts | Duplicate/wasted work |
| Treating question as authorization shortcut | Questions are NOT approval |
| Skipping verification because "user asked" | User inquiry ≠ permission to bypass |

### ✅ REQUIRED SEQUENCE

**When user asks ANY question:**

1. **Run verification sequence** (session init, superseding check, codebase verify)
2. **Query sub-issues** if implementation involved
3. **THEN respond to the question**
4. **If question is about implementation**: Check authorization separately
5. **If question implies implementation**: HALT and wait for explicit `approved`/`go`

## Related Guidelines

| Guideline | Purpose |
|-----------|---------|
| `000-critical-rules.md` | Critical violations and auditor enforcement |
| `020-go-prohibitions.md` | GO command restrictions |
| `120-github-issue-first.md` | Issue-first strategy and sub-issues |
| `124-github-archive-workflow.md` | Issue closure timing |
| `github-sub-issues` skill | Sub-issue creation workflow |
| `pr-creation-workflow` skill | PR creation timing