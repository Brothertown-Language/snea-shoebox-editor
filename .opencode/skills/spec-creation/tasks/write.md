# Task: write

## Purpose

Assemble the final spec with acceptance criteria, ambiguity elimination, and deliverable structure. Includes self-review and user-review steps adapted from brainstorming Steps 7-9, extended with principles #4, #6, #10.

## Entry Criteria

- Requirements extraction completed (mandatory)
- Other prerequisite tasks completed or explicitly skipped via simplicity heuristic

## Exit Criteria

- GitHub Issue created with `[SPEC]` prefix and `needs-approval` label
- Self-review completed (placeholder scan, consistency, scope, ambiguity)
- Chat output is ONLY: `<exec summary>` + `<issue URL>` + `<byline>` (no full spec dump)
- User reviews spec ON THE ISSUE (not in chat)
- Ready for spec-auditor and approval-gate

## Procedure

### Step 1: Assemble Spec

Combine outputs from prerequisite tasks into a coherent spec. The spec should address the following content areas — the agent decides which sections to use and how to organize them:

- **Objectives and goals** — What this spec achieves
- **Constraints and scope** — What's in and out of scope
- **Success criteria** — Testable, binary pass/fail conditions
- **Risk and edge cases** — What could go wrong and boundary conditions
- **Implementation approach** — For the reader's understanding, not prescribing HOW (see Step 4.5)

Skip areas that don't apply to simple specs; add areas that do. The spec should be self-contained and clear, regardless of structure.

### Step 2: Eliminate Ambiguity (Principle #4)

Review every requirement statement:
- Replace vague terms with measurable, testable statements
- Replace "should" with "MUST", "SHALL", or "MAY"
- Replace "fast" with specific thresholds
- Replace "user-friendly" with specific UX criteria
- Every "etc." must become an explicit list

### Step 3: Define Acceptance Criteria (Principle #6)

For each feature/requirement:
- Binary pass/fail criteria (NOT subjective)
- Edge case coverage
- Negative test cases (what must NOT happen)
- Integration test expectations

### Step 4: Structure the Deliverable (Principle #10)

**Content coverage matters more than section structure.** The agent chooses the optimal structure for the spec's complexity:

- **Simple specs** (bug fixes, one-file changes): May use a minimal format — Problem, Context, Fix, Criteria, Edge Cases — all in flowing prose without section headers
- **Standard specs** (multi-file changes): May use typical sections — Objective, Problem, Context, Fix Approach, Success Criteria, Edge Cases
- **Complex specs** (cross-cutting, multi-phase): May use full structure — Objective, Problem, Context, Affected Files, Fix Approach, Success Criteria, Edge Cases, Dependencies, Risk, Decision Rationale, Phases

**Any format that covers the required content areas is acceptable.** The agent decides the structure that best serves the specific spec.

### Step 4.5: Spec/Plan Boundary Check

Review the assembled spec for plan-level content that belongs in the implementation plan, not the spec. Specs describe **WHAT** and **WHY**; plans describe **HOW**.

**Replacement rules:**

| Plan-Level Content (remove) | Spec-Level Replacement |
|------------------------------|------------------------|
| Function/class definitions with code | Function names + responsibilities table |
| SQL DDL statements (`CREATE TABLE...`) | Table names + constraints table |
| Implementation algorithms with step-by-step logic | Input/output contract (what goes in, what comes out) |
| File paths with "what to change" language | Affected files + anchors table (what exists, not what to write) |
| Architecture decisions without constraints | Architecture requirements table (what the system MUST satisfy) |

**Self-review question:** "Could two developers produce valid but different implementations from this spec?" If yes, the spec is at the right level. If no — if the spec only allows one implementation — it contains plan-level detail that should be removed.

### Step 5: Self-Review

After writing the spec, review with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

### Step 5.5: Evidence Artifact Verification (MANDATORY)

**🚫 CRITICAL: Each self-review checkpoint MUST produce a tool-call artifact demonstrating the verification was performed. Assertions without tool-call evidence are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Checkpoint | Verification Action | Tool Call | Problem Class |
|------------|-------------------|-----------|---------------|
| No placeholders remain | Verify spec body contains no "TBD", "TODO", "FIXME", or incomplete section markers | `github_issue_read(method=get, issue_number=N)` → search body for `/TBD\|TODO\|FIXME/` | STRUCTURE-VIOLATION |
| Internal consistency | Cross-reference requirement IDs between sections; verify no contradictions | `github_issue_read(method=get)` → parse section anchors vs referenced IDs | CONFLICTING |
| Scope check evidence | Verify scope is appropriate for single plan or flagged for decomposition | `github_issue_read(method=get)` → count affected files, check for phase markers | VERIFICATION-GAP |
| Ambiguity resolved | Verify no requirement can be interpreted two ways | `github_issue_read(method=get)` → scan for "should", "etc.", vague terms | STRUCTURE-VIOLATION |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Placeholders found in spec body | STRUCTURE-VIOLATION | auto-fix | Replace with concrete content |
| Contradictory requirements across sections | CONFLICTING | flag-for-review | Report, do not auto-resolve |
| Scope too large for single plan | VERIFICATION-GAP | conditional | Flag decomposition, then apply if confirmed |
| Vague/ambiguous terms present | STRUCTURE-VIOLATION | auto-fix | Replace with measurable terms |

**These verifications are MANDATORY after self-review. Skipping them is a CRITICAL GUIDELINE VIOLATION.**

### Step 6: Create GitHub Issue

Invoke `github-issue-creation` skill to persist the spec as a GitHub Issue:

1. Invoke `github-issue-creation --task pre-creation` to validate (check for conflicts, superseded issues, content coverage)
2. If validation fails → HALT and report. Fix issues and re-validate.
3. If validation passes → invoke `github-issue-creation --task single-task-check` to determine sub-issue needs
4. Invoke `github-issue-creation --task creation` to create the GitHub Issue
5. Record the issue number and URL

**Chat output is ONLY:**

```
<exec summary>

<issue URL>

🤖 <AgentName> (<ModelID>) created
```

**🚫 NEVER:**
- Dump full spec content to chat as the "review" step
- Claim spec is "written" without a GitHub Issue URL
- Ask the user to review the spec in chat

### Step 7: User Review on Issue

The user reviews the spec ON THE GITHUB ISSUE, not in chat.

- If user requests revisions via issue comments: update the issue body, then post update summary + URL + byline to chat
- If user approves the spec on the issue: proceed to Step 8
- Do NOT re-dump the spec to chat for any reason

### Step 8: Transition

After user approval of the spec on the GitHub Issue:
- Invoke `spec-auditor` for quality audit
- Then proceed to `approval-gate` for authorization
- Then `writing-plans` for implementation planning

## Context Required

- Preceded by: `requirements` (mandatory), `decompose`, `traceability`, `risk` (or explicitly skipped)
- Extends: brainstorming Steps 7-9 (adapted, not verbatim move)
- Calls: `github-issue-creation` (pre-creation → single-task-check → creation)
- Followed by: `spec-auditor`, then `approval-gate`