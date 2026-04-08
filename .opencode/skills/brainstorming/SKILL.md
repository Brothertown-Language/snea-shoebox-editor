---
name: brainstorming
description: Mandatory pre-spec brainstorming workflow with agent-driven exploration instead of rigid templates. Dimensions are chosen by judgment, not mandated.
license: MIT
compatibility: opencode
---

# Skill: brainstorming

## Overview

Mandatory pre-spec exploration workflow. The agent explores dimensions relevant to the problem — choosing what to investigate based on judgment, not a fixed checklist. Output is prose, not a filled template.

**Core shift from v1:** Dimensions are starting points for thinking, not sections to fill. The agent decides which dimensions matter and which to drop or add.

## Persona

You are a Requirements Explorer. Your focus is ensuring thorough exploration before any spec is created — but exploration driven by the problem's nature, not by a mandatory checklist.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `explore` | Full exploration workflow (default) | ~800 |

## Invocation

- `/skill brainstorming` — Start exploration workflow
- `/skill brainstorming --task explore` — Same as above

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked by dispatch-table.yaml when:
   - User says `spec` or `plan` or similar planning terms
   - User provides a feature description for planning
   - DO NOT proceed to spec creation until exploration completes

2. **Exit conditions:** Exploration is COMPLETE when:
   - All relevant dimensions explored (agent decides which)
   - User confirms requirements are complete
   - HALT and wait for explicit approval to proceed to spec creation

## Baseline Dimensions (Reference, Not Required)

These are starting points the agent can use when stuck. They are NOT mandatory sections.

| Dimension | When Relevant | When to Drop |
|-----------|--------------|--------------|
| Problem Understanding | Always | Never — this is always needed |
| User Requirements | When there are end users | Bug fixes with no user-facing change |
| Alternatives Analysis | When multiple approaches exist | Bug fixes with one obvious fix |
| Success Criteria | When outcomes are measurable | Exploratory research |
| Impact Assessment | When change affects other systems | Isolated changes with no blast radius |
| Operational Requirements | Non-trivial systems | Simple scripts or one-off changes |
| Interface Investigation | When APIs/UIs are involved | Internal-only refactors |
| Regulatory/Compliance | When domain has regulations | Internal tooling |
| Data Migration | When schema changes | New features with no existing data |

**Agent judgment governs all dimension selection.** A bug fix may only need Problem Understanding and Success Criteria. An infrastructure change may need Operational Requirements plus Impact Assessment.

## Operational Requirements Dimension

For non-trivial systems, the agent should consider:

- Logging: What events to log, at what level, with what context
- Metrics: What to measure, alert thresholds
- Alerts: Failure notifications, escalation paths
- Deployment constraints: Blue/green, canary, rollback strategy
- Data migration: Schema changes, backfills, zero-downtime requirements

These are discovered through Q&A with the user, not assumed.

## Exploration Output

The agent produces a **prose exploration summary** — not a filled template. The summary documents:

1. **What was explored** — Which dimensions were investigated and why
2. **What was discovered** — Key findings per dimension
3. **What was dropped** — Which baseline dimensions were skipped and why
4. **What was added** — Any non-baseline dimensions the agent identified
5. **Open questions** — Unresolved items requiring user input

The reference template below provides structural hints for agents who are stuck, but it is NEVER the output format.

### Reference Template (For Structure Hints Only)

When exploration is complete, the agent may use this structure as guidance for what a good summary covers — but the agent should reorganize, drop, or add sections based on what the problem demands:

```
## Exploration Summary: [Feature Name]

### Dimensions Explored
[List of dimensions explored and why each was relevant]

### Dimensions Skipped
[List of baseline dimensions skipped and why]

### Key Findings

[Prose summary organized by relevant dimensions, not by template order]

### Alternatives Considered
[Only if alternatives analysis was relevant]

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Option 1 | ... | ... | Chosen/Rejected |
| Option 2 | ... | ... | Chosen/Rejected |

### Success Criteria
[Testable outcomes — only what's measurable]

### Open Questions
[Unresolved items requiring user input before spec creation]

### Ready for Spec Creation?
- [ ] All relevant dimensions explored
- [ ] User confirmed requirements complete (or explicitly deferred)
```

## Enforcement Mechanism

**Skills MUST enforce brainstorming — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before spec creation:**
   - Has exploration been invoked?
   - Is exploration output present?
   - Has problem understanding been explored?

2. **Enforcement matrix:**
   - Exploration NOT invoked → INVOKE brainstorming
   - Exploration invoked but incomplete (missing problem understanding) → COMPLETE exploration
   - Exploration complete → PROCEED to spec creation

3. **What does NOT bypass exploration:**
   - "skip brainstorming" → NOT allowed
   - "I already know what I want" → Still require brief exploration (problem understanding at minimum)
   - User impatience → Document partial exploration, ask to proceed

### Enforcement Messages

**Missing exploration:**
```
Exploration required before spec creation.

This ensures thorough requirements investigation before planning.

To invoke: Say '/skill brainstorming' or describe your feature to start exploration.
```

**Incomplete exploration:**
```
Exploration incomplete. Problem understanding must be explored at minimum.

Please complete exploration before proceeding to spec creation.
```

## Integration with Existing Workflow

### Dispatch Order
```
brainstorming (mandatory) → spec creation → approval-gate → git-workflow
```

### Approval Gate Integration
- Exploration is a PRE-REQUISITE to spec creation
- Approval gate checks for spec existence AFTER exploration
- Exploration does NOT require approval (exploration phase)

## Investigation Completion Criteria

**Before creating a spec, investigation MUST be complete.** This is a hard gate, not optional.

### Completion Requirements

| Requirement | Evidence |
|-------------|----------|
| Problem understood | Clearly stated problem, context, stakeholders |
| Codebase explored | Existing patterns, reusable components identified |
| Hypotheses tested | Test scripts run, results documented |
| Alternatives considered | At least 2 approaches documented with tradeoffs |
| Risks identified | Risk assessment with mitigation strategies |
| Success criteria defined | Testable, measurable completion criteria |

### Permissible Investigation Activities

| Activity | Allowed? | Notes |
|----------|----------|-------|
| Read production code | YES | Read-only exploration |
| Read production data | YES | Read-only analysis |
| Create test scripts in `./tmp/` | YES | Isolated from production |
| Run test scripts in `./tmp/` | YES | No production impact |
| Create isolated test fixtures | YES | Dedicated test databases/schemas |
| Run static analysis | YES | Code verification |
| Modify production code | NO | Requires approved spec |
| Modify production data | NO | Requires approved spec |
| Run code against production DB | NO | Requires explicit user authorization |

### CRITICAL VIOLATION: Spec Without Investigation

Creating a spec without completed investigation is a CRITICAL GUIDELINE VIOLATION:
- PROHIBITED: Creating specs from vague requirements without exploration
- PROHIBITED: Skipping codebase analysis before planning
- PROHIBITED: Finalizing specs before investigating edge cases
- PROHIBITED: Proceeding without success criteria defined
- PROHIBITED: Running test code against production systems

**See `142-planning-archive-workflow.md` → "Investigation Completion Criteria" and `000-critical-rules.md` → "Spec Without Investigation" for the zero-tolerance rules.**

## Cross-References

- Related skills: `approval-gate` (authorization), `writing-plans` (plan creation)
- Related guidelines: `140-planning-spec-creation.md` (spec workflow), `045-open-questions.md` (Q&A protocol)

## Key Differences from v1

| v1 (Template-Driven) | v2 (Agent-Driven) |
|----------------------|-------------------|
| Five mandatory dimensions | Baseline dimensions as reference |
| Must fill all five sections | Agent chooses relevant dimensions |
| Template output format | Prose exploration summary |
| Operational requirements not mentioned | Operational requirements as a dimension |
| No dimension additions | Agent can add dimensions |
| Fixed section order | Agent organizes by relevance |

Co-authored with AI: OpenCode (ollama-cloud/glm-5)