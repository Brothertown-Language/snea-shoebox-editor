---
name: plan-fidelity-auditor
description: Use when auditing a plan for fidelity against a spec. Triggers on: plan fidelity, plan audit, spec vs plan, discrepancy, clean-room plan.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: plan-fidelity-auditor

## Overview

Plan Fidelity Auditor generates a clean-room plan from the spec's problem statement using prose-driven exploration, then compares it against the existing plan to identify discrepancies. All findings are reported, NOT auto-applied. Invoked via spec-auditor orchestrator as the `fidelity` subtask.

**Core v2 shifts:**
- Report-only: Findings reported to agent, no auto-fixes
- Prose-driven clean-room: Uses prose exploration, not template structure
- Invoked via orchestrator: Not called directly
- Recommends brainstorming: When significant gaps emerge, recommends deeper exploration

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `audit` | Full audit workflow (default) | ~600 |
| `compare` | Compare clean-room plan against existing plan | ~500 |
| `report` | Report findings (renamed from auto-fix) | ~300 |

## Invocation

**This skill is NOT invoked directly.** It is called by the spec-auditor orchestrator via `/skill spec-auditor --issue N --task fidelity`.

If invoked directly (deprecated, but still works):
- `/skill plan-fidelity-auditor --issue N` — Audit (report-only mode)

## Report-Only Model (CRITICAL)

**All findings are reported, NOT auto-applied.**

Previous versions auto-fixed simple discrepancies. v2 reports all findings and lets the agent decide:

- A missing file reference might not need adding (context determines relevance)
- A different approach might be intentional (not a bug to fix)
- A missing phase might need brainstorming (not just flagging)

**Why report-only:**
- Auto-fixes ignore context
- A BOILERPLATE-TITLE rename might be wrong for the specific spec
- A concern split might break an intentionally grouped phase
- The agent has the full context; the auditor doesn't

**Report format:**
```
Finding: [MISSING_PHASE|EXTRA_PHASE|MISSING_STEP|EXTRA_STEP|APPROACH_DIFFERENCE|MISSING_EDGE_CASE|MISSING_FILE_REF|ORDERING_DIFFERENCE|SCOPE_EXPANSION|VAGUE_PROBLEM] - [summary]
Location: [phase/step]
Context: [why this matters for implementation fidelity]
Recommendation: [add missing step OR investigate approach OR trigger brainstorming]
Severity: [HIGH|MEDIUM|LOW]
```

## Clean-Room Plan Generation

### Process

1. **Extract problem statement** from the spec issue (Objective, Problem Statement, Context, Constraints, Success Criteria only)
2. **Write extracted content** to `./tmp/clean-room-input-N.md`
3. **Invoke writing-plans subtask** with prose-driven approach (no template)
4. **Compare** against existing plan using the `compare` task
5. **Report** all findings

### Clean-Room Input Isolation

The clean-room plan MUST be generated from:
- **ONLY** the problem statement, context, constraints, and success criteria
- **NOT** the existing phases, steps, or implementation details
- **NOT** any other issues, comments, or external context

### Prose-Driven Clean-Room (v2 Change)

The clean-room plan is generated using prose-driven exploration rather than template structure. This means:
- Agent decides what sections to include based on the problem
- No template structure imposed
- More likely to surface issues that template-driven generation misses

### When Significant Gaps Are Found

When the comparison reveals fundamental misunderstandings or large gaps:
- **Recommend brainstorming** rather than just flagging
- This is a v2 improvement: instead of just flagging, actively recommend deeper exploration

## Comparison Levels

| Level | What's Compared | Example |
|-------|----------------|---------|
| Phase-level | Missing phases, extra phases, phase ordering | Clean-room has "Database Schema" phase not in original |
| Step-level | Missing steps, extra steps, step ordering | Clean-room has "Add index" step not in original |
| Content-level | Different approaches, missing edge cases | Clean-room covers pagination edge case not in original |

## Semantic Matching

Before reporting differences, attempt semantic matching:
- "User Schema" vs "Database Tables" → matching (same concept, different naming)
- "Authentication Setup" vs "OAuth2 Integration" → matching if OAuth2 is the auth method
- "API Endpoints" vs "REST API" → matching (same concept)

Only substantive differences after semantic matching are reported.

## Key Differences from v1

| v1 (Auto-Fix) | v2 (Report-Only) |
|----------------|-------------------|
| Auto-fixes simple discrepancies | Reports all findings |
| `auto-fix` task | `report` task (renamed) |
| Template-driven clean-room | Prose-driven clean-room |
| Invoked directly | Invoked via spec-auditor orchestrator |
| Flag-only for substantive changes | Recommends brainstorming for significant gaps |
| Mandatory audit chain entry | Subtask within orchestrator |

## Cross-References

- Orchestrated by: `spec-auditor` (via `fidelity` subtask)
- Related tasks: `compare` (comparison logic), `report` (finding reporting)
- Related skills: `writing-plans` (clean-room generation), `brainstorming` (recommended for gaps)

Co-authored with AI: <AI-Name> (<model-id>)