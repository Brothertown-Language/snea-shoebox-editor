# Task: create/plan-structure

## Purpose

Structure the implementation plan from approved spec: verification gate, combined/separate decision, file structure mapping, and TDD task definition with RED verification checkpoints.

## Entry Criteria

- Approved spec (verified by approval-gate)
- Spec stored as GitHub Issue
- Spec has explicit approval

## Exit Criteria

- Combined/separate decision made and documented
- Duplicate plan check completed
- File structure mapped with clear boundaries
- Item decomposition verified with dependency ordering
- TDD tasks defined with mandatory RED checkpoints

## Procedure

### Pre-Step: Verification Gate (MANDATORY FIRST)

Before reading approved spec: `/skill verification-enforcement --task verify`

Collects evidence artifacts for factual claims. Unverified claims marked with `⚠️ UNVERIFIED`.

### Step 1: Read Approved Spec

- Query GitHub Issue for spec content
- Extract objectives, constraints, success criteria
- Identify affected files and dependencies

### Step 1.5: Combined vs Separate Plan Decision Gate

**Evaluate:** `single_task_determination` passed from post-creation (single-task/multi-task)

| Condition | Outcome |
| -- | -- |
| Multi-task spec (mixed concerns or independence) | **Always separate** — create [PLAN] issue with sub-issues |
| Single-task spec AND spec body can absorb plan content | **Candidate for combined** — agent evaluates readability |
| Single-task AND combining makes document hard to read | **Separate** — create [PLAN] issue |

**Decision output (MANDATORY):**
```
Plan structure decision: combined/separate
Reason: <justification referencing evaluation criteria>
```

**If COMBINED:**
- Append `## Implementation Plan` section to spec issue body
- Retain `[SPEC]` title prefix (not changed to `[PLAN]`)
- Proceed to Step 2 — plan content appended to spec body

**If SEPARATE:**
- Proceed to Step 2 — plan content stored in separate [PLAN] issue

### Step 1.6: Duplicate Plan Check

Search for existing plans referencing the same spec:
```python
plans = github_search_issues(query="label:plan", owner=<owner>, repo=<repo>, state="open")
```

For each plan found with `Spec: #<spec_number>`, present choice:
- Proceed with new plan (reference existing: `Supersedes #N` or `Parallel track to #N`)
- HALT and review existing plan

### Step 2: Map File Structure

- List all files to create or modify
- Define each file's responsibility
- Ensure decomposition has clear boundaries

### Step 3: Item Decomposition (per `091-incremental-build.md`)

**Verify before writing:**
| Requirement | Verification |
| -- | -- |
| Item enumeration | Every unit listed with name, scope, deliverable |
| Dependency ordering | Items ordered so dependencies satisfied |
| Acceptance criteria per item | Each has testable criteria |
| Concern boundary annotations | Cross-architectural items flagged |

**Failure:** Plan will fail `approval-gate --task verify-authorization` Step 4.5

### Step 3.5: Preserve Semantic Intent from Spec

When referencing spec success criteria:
- **TDD step guidance:** Explain WHY the test checks for a specific exact value, not just what it checks
- **RED verification checkpoint (MANDATORY):** Each TDD step MUST include explicit Step 2 checkpoint

Example task structure:
```
Task N: [Component Name]
  Step 1: Write the failing test
  Step 2: Run test, verify RED ← CHECKPOINT: must produce tool-call evidence of failure
  Step 3: Write minimal implementation
  Step 4: Run test, verify GREEN
  Step 5: Commit
```

**Behavioral RED/GREEN for rule-changing items:**
When changing guidelines or skills, use behavioral TDD:
1. **Behavioral RED:** Write test sending agent prompt, verify agent does NOT follow new rule yet
2. **Behavioral GREEN:** Make change, re-run test — now agent follows rule

### Step 4: Plan Phase Structure

Organize by concern flow:
- Determine phases needed
- Write prose for phase descriptions
- Prose-driven, not template-driven

### Step 5: Define Tasks Within Each Phase

- Each step is one action (2-5 minutes)
- Exact code, exact commands, exact file paths
- **Step 2 checkpoint is MANDATORY** — plans without it fail validation

## Context Required

- Related tasks: `create/create-and-validate`
- Related skills: `verification-enforcement` (Step 0), `approval-gate` (Step 4.5)