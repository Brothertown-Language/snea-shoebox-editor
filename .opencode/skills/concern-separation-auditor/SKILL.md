---
name: concern-separation-auditor
description: Use when auditing a spec for phase structure quality or concern separation. Triggers on: concern separation, phase structure, spec audit, mixed concerns.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: concern-separation-auditor

## Overview

Concern Separation Auditor analyzes spec phase structures to identify deployment independence, risk profile, and blast radius issues. Reports findings to the agent for decision-making — does NOT auto-fix.

**Core v2 shift:** Report-only. Findings are presented to the agent, who decides whether to apply them given the context. No longer invoked directly — called by spec-auditor orchestrator when relevant.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `audit-phases` | Analyze phase structure for concern quality | ~400 |
| `check-independence` | Validate deployment independence between phases | ~300 |
| `concern-coverage` | Verify sub-issue bodies reflect Plan concern boundaries | ~350 |

## Invocation

**This skill is NOT invoked directly.** It is called by the spec-auditor orchestrator via `/skill spec-auditor --issue N --task concerns`.

If invoked directly (deprecated, but still works):
- `/skill concern-separation-auditor --issue N` — Audit (report-only mode)

## Report-Only Model

**All findings are reported, NOT auto-applied.**

Previous versions auto-fixed BOILERPLATE-TITLE and phase splits. v2 reports findings and lets the agent decide:

- A BOILERPLATE-TITLE rename might be wrong for the specific spec
- A concern split might break an intentionally grouped phase
- The agent has full context; this subtask doesn't

**Report format:**
```
Finding: [BOILERPLATE-TITLE|CONCERN_MIXING|DEPENDENCY_REVERSAL|HIGH_RISK_GROUPING] - [summary]
Location: [phase/step]
Context: [why this matters for this spec]
Recommendation: [suggested change, if obvious]
Severity: [HIGH|MEDIUM|LOW]
```

## Concern-Based Analysis (NOT Rigid Template)

This skill analyzes ACTUAL concerns, not static templates.

**What this is NOT:**
- NOT a rigid DB→Repo→BL→UI template
- NOT a mandatory ordering
- NOT applying patterns blindly

**What this IS:**
- Analyzes deployment independence for each step
- Analyzes risk profile (HIGH/MEDIUM/LOW)
- Analyzes blast radius
- Groups steps by ACTUAL concern boundaries

**Different project structures:**

| Project Type | Typical Concerns | Notes |
|--------------|------------------|-------|
| Stateless service | Config → API → Tests | No DB, no UI |
| CLI tool | Args → Core → Output | Deployment is reinstall |
| Frontend-only | Components → State → Tests | No backend |
| Infrastructure | Setup | Crosses all layers, ONE concern |
| Monolith | Schema → API → UI | May not have repository layer |

## Key Differences from v1

| v1 (Auto-Fix) | v2 (Report-Only) |
|----------------|-------------------|
| Auto-fixes BOILERPLATE-TITLE | Reports BOILERPLATE-TITLE finding |
| Auto-splits phases | Reports concern mixing recommendation |
| Invoked directly via `/skill concern-separation-auditor` | Invoked via spec-auditor `--task concerns` |
| Standalone skill | Subtask within orchestrator |
| `--interactive` mode for human review | Always report-only |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `spec-auditor` in Cross-References (orchestrated by) | File exists at `.opencode/skills/spec-auditor/SKILL.md` | MISSING-TRACEABILITY if missing |
| `writing-plans` in Cross-References section | File exists at `.opencode/skills/writing-plans/SKILL.md` | MISSING-TRACEABILITY if missing |
| `programming-principles` in Cross-References section | File exists at `.opencode/skills/programming-principles/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `audit-phases` | File exists at `.opencode/skills/concern-separation-auditor/tasks/audit-phases.md` | MISSING-TRACEABILITY if missing |
| Task table entry `check-independence` | File exists at `.opencode/skills/concern-separation-auditor/tasks/check-independence.md` | MISSING-TRACEABILITY if missing |
| Task table entry `concern-coverage` | File exists at `.opencode/skills/concern-separation-auditor/tasks/concern-coverage.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` orchestration behavior | Matches actual SKILL.md: `concerns` subtask delegates to this skill | CONFLICTING if mismatched |
| `writing-plans` clean-room behavior | Matches actual SKILL.md: `clean-room` task for fidelity generation | CONFLICTING if mismatched |
| `programming-principles` principle definitions | Matches actual SKILL.md: SoC and Blast Radius principles defined there | CONFLICTING if mismatched |

**Verification Procedure:**

Before invoking any cross-referenced skill:
1. `ls .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: file exists or MISSING-TRACEABILITY
2. `grep -c "<task-name>" .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: task referenced or MISSING-TRACEABILITY
3. Compare described behavior with actual content → EVIDENCE: match or CONFLICTING

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced skill file missing | MISSING-TRACEABILITY | flag-for-review | Cannot verify cross-reference |
| Referenced task file missing | MISSING-TRACEABILITY | flag-for-review | Task may have been renamed |
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |
| Invocation mismatch | CONFLICTING | flag-for-review | Skill may have been updated |

## Cross-References

- Orchestrated by: `spec-auditor` (via `concerns` subtask)
- Related skills: `spec-auditor` (orchestrator), `writing-plans` (clean-room for fidelity), `programming-principles` (principle definitions for SoC and Blast Radius — this subtask checks structural separation, that skill defines the underlying principles)
- Related guidelines: `000-critical-rules.md` (auditor enforcement), `142-planning-archive-workflow.md`

Co-authored with AI: <AI-Name> (<model-id>)

## Symbolic Engine Integration

**Optional pre-step:** Before auditing, invoke the symbolic analysis engine for formal evidence:

```bash
./.opencode/tools/symbolic flow
```

- `sym-flow`: Builds a networkx DiGraph from rule triggers/requires and detects activation graph anomalies. Cross-concern triggers (edges linking rules in different concern areas) indicate potential concern mixing.

Results are used as **evidence** (not verdict) — they supplement prose-only analysis with formal activation graph showing cross-concern dependencies.

**Graceful degradation:** If the engine is unavailable or produces no results, fall back to prose-only analysis. Do NOT block the audit if the engine fails.