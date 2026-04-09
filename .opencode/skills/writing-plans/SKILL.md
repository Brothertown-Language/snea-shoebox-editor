---
name: writing-plans
description: Use when creating an implementation plan from an approved spec. Produces prose plans with zero placeholders. Triggers on: write plan, create plan, implementation plan, plan spec, approved plan, plan creation.
license: MIT
compatibility: opencode
---

# Skill: writing-plans

## Overview

Plan creation workflow that transforms approved specs into actionable implementation plans. Plans are prose, structured by the agent's judgment about what the problem needs — not by filling a template. Placeholders are allowed in specs during iterative development but forbidden in plans before implementation begins.

**Core shift from v1:** The template is reference material only. The agent decides what sections the plan needs based on the problem. Plans are prose documents, not filled templates.

## Persona

You are an Implementation Planner. Your focus is transforming approved design specs into complete, actionable implementation plans with clear steps, testability, and verification evidence — structured by judgment, not templates.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `create` | Create plan from approved spec | ~800 |
| `validate` | Check for placeholders and completeness | ~500 |
| `retroactive` | Create plan for existing spec | ~600 |
| `clean-room` | Generate independent plan from problem statement only (prose-driven) | ~500 |

## Invocation

- `/skill writing-plans` — Overview only
- `/skill writing-plans --task create` — Create plan from current spec
- `/skill writing-plans --task validate` — Validate existing plan
- `/skill writing-plans --task retroactive` — Create plan for existing spec
- `/skill writing-plans --task clean-room` — Generate clean-room plan (for comparison by spec-auditor)

## Prose-Driven Approach

The agent produces plans as prose documents. The reference structure below is available for guidance when the agent is stuck, but it is NEVER the output format.

### What the Agent Decides

1. **Which sections to include** — Based on what the problem needs
2. **Section order** — Based on dependency flow, not template order
3. **Level of detail** — Simple problems need less structure than complex ones
4. **Additional sections** — Operational requirements, data migration, etc.

### Reference Structure (Guidance Only)

When the agent is uncertain about plan structure, this reference provides common components:

```
# Plan: [Feature Name]

STATUS: 1.1
CREATED: YYYY-MM-DD
PARENT: #<Spec Issue Number>

---

## [Agent-chosen section — e.g., Objective, Context, Approach]

[Prose content addressing the dimension]

## [Agent-chosen section — e.g., Implementation Steps, Phases, Changes]

[Steps/phases organized by concern, not by template]

## [Agent-chosen section — e.g., Success Criteria, Verification, Risks]

[Testable criteria, evidence requirements, risk mitigations]

---

> **Approval Tracking:** Plan approvals tracked via GitHub Issue comments.
```

**The agent may reorganize, drop, or add sections based on the problem's nature.**

## Placeholder Policy (CRITICAL)

### Specs vs Plans

| Artifact | Placeholders Allowed? | Examples |
|----------|----------------------|----------|
| Spec (GitHub Issue) | YES, during iterative development | TBD, TODO, [needs investigation], [placeholder] |
| Plan (for implementation) | NO — zero tolerance | None allowed before implementation begins |

### Why the Distinction

Specs evolve through Q&A. Placeholders mark where more information is needed. Plans are implementation-ready documents. A plan with TBDs is not ready for implementation.

### Prohibited Placeholder Patterns (Plans Only)

| Pattern | Why Prohibited |
|---------|----------------|
| `TBD` | Incomplete plan |
| `TODO` | Incomplete plan |
| `[to be determined]` | Incomplete plan |
| `[needs investigation]` | Investigation should be in spec |
| `[placeholder]` | Incomplete plan |
| `[requires research]` | Research should be in spec |

### Validation Logic

```python
INVALID_PATTERNS = [
    "TBD", "TODO", "tbd", "todo",
    "[to be determined]", "[needs investigation]",
    "[placeholder]", "[requires research]",
]

def validate_plan(plan_content: str) -> bool:
    for pattern in INVALID_PATTERNS:
        if pattern in plan_content:
            return False
    return True
```

## Task: create

### Prerequisites
1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)

### Creation Steps

1. **Read approved spec:**
   - Query GitHub Issue for spec content
   - Extract objectives, constraints, success criteria
   - Identify affected files and dependencies

2. **Plan structure by judgment:**
   - Determine which sections the plan needs
   - Organize by concern flow, not template order
   - Write prose, not filled templates

3. **Create plan issue:**
   - Title: `[PLAN] <Feature Name>`
   - Body: Prose plan structured by agent judgment
   - Link to parent spec (sub-issue)

4. **Validate plan:**
   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify success criteria are testable

## Task: validate

Check an existing plan for:

1. **Placeholder detection** — Zero TBD/TODO tolerance
2. **Completeness** — Plan addresses the stated problem
3. **Actionability** — Steps are concrete, not abstract goals
4. **Testability** — Success criteria are measurable

Does NOT enforce a specific section structure. A plan without "Risks" is valid if risks are addressed elsewhere or are not relevant.

## Task: retroactive

For existing specs without plans:

1. **Query existing spec:**
   - Get spec from GitHub Issue
   - Check for linked plan (sub-issues)

2. **If no plan exists:**
   - Create plan from spec using prose-driven approach
   - Link as sub-issue
   - HALT and wait for plan approval

3. **If plan exists:**
   - Validate plan (check for placeholders)
   - If invalid → Report issues
   - If valid → Proceed to implementation

## Task: clean-room

### Purpose

Generate an independent plan from the problem statement only, with no knowledge of any existing plan. Used by spec-auditor's fidelity subtask for comparison against the existing spec.

**Key v2 change:** Clean-room generation uses prose-driven approach rather than template structure. The agent writes naturally, which can surface issues that template-driven generation misses.

### Entry Criteria

- Problem statement input file exists at `./tmp/clean-room-input-N.md`
- Problem statement contains: Objective, Problem Statement, Context, Constraints, Success Criteria
- The writing-plans skill is available

### Exit Criteria

- Clean-room plan generated as prose structured markdown
- Plan returned to the invoking subtask context
- No issue created (clean-room plans are comparison artifacts, not tracked in GitHub)

### Key Differences

| Aspect | Standard Plan (`--task create`) | Clean-Room Plan (`--task clean-room`) |
|--------|-------------------------------|--------------------------------------|
| Input source | Approved spec issue | Problem statement only (from temp file) |
| References existing plan | May reference spec phases | NEVER references existing plan |
| Creates GitHub issue | Yes | No — returned as markdown only |
| Requires approval | Yes (`needs-approval` label) | No — comparison artifact |
| Structure | Agent-chosen prose | Agent-chosen prose (no template) |
| Skip approval gate | No | Yes — not an implementation plan |

### Procedural Steps

1. **Read problem statement** from `./tmp/clean-room-input-N.md`
2. **Explore codebase** (if applicable) — find relevant files and patterns
3. **Generate independent plan** using prose-driven approach — NOT template structure
4. **When significant gaps emerge**, recommend brainstorming rather than just flagging
5. **Validate** — no placeholders, specific concern names, actionable steps
6. **Yield results** — return as structured markdown

### Clean-Room Output Format

The agent generates a prose plan. No template is imposed. The only requirements:

- Phase names describe **specific concerns**, NOT generic activities
- Each step is **actionable**
- Success criteria are **testable**
- **No TBD, TODO, or placeholder content**

### Scope Boundaries

- **NO** GitHub Issue creation
- **NO** approval gate
- **NO** reference to existing plan
- **YES** codebase exploration
- **YES** prose-driven output (no template)

## Enforcement Mechanism

**Skills MUST enforce plan completeness — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before implementation:**
   - Does plan exist?
   - Is plan approved?
   - Is plan valid (no placeholders)?

2. **Enforcement matrix:**
   - No plan → CREATE plan (writing-plans skill)
   - Plan exists but unapproved → HALT, wait for approval
   - Plan approved but has placeholders → REJECT plan, require completion
   - Plan approved and complete → PROCEED to implementation

## Integration with Existing Workflow

### Dispatch Order
```
approval-gate → writing-plans (create) → approval-gate (plan) → git-workflow
```

### Approval Gate Integration
- Plan creation happens AFTER spec approval
- Plan requires separate approval (`approved: plan`)
- Implementation cannot start until BOTH spec AND plan are approved

## Cross-References

- Related skills: `brainstorming` (pre-spec), `approval-gate` (authorization), `executing-plans` (implementation), `spec-auditor` (fidelity subtask uses clean-room)

## Key Differences from v1

| v1 (Template-Driven) | v2 (Prose-Driven) |
|----------------------|-------------------|
| Fixed template sections | Agent decides what sections to include |
| Must fill all template sections | Drop sections that don't apply |
| Template output format | Prose output format |
| Clean-room uses template | Clean-room uses prose-driven exploration |
| No brainstorming recommendation | Clean-room recommends brainstorming for gaps |
| Validation enforces section structure | Validation enforces completeness, not structure |

Co-authored with AI: OpenCode (ollama-cloud/glm-5)