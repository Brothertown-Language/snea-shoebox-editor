---
name: spec-auditor
description: Audit orchestrator that determines which subtasks to run and reports all findings. The single entry point for spec quality auditing.
license: MIT
compatibility: opencode
---

# Skill: spec-auditor

## Overview

Single audit orchestrator entry point for spec quality. Determines which subtasks to run based on the issue's nature, runs the minimal baseline always, and reports all findings for agent decision-making. Findings are reported, NOT auto-applied.

**Core v2 shift:** Spec-auditor is now the orchestrator. Plan-fidelity-auditor and concern-separation-auditor are no longer invoked directly — their logic lives as subtasks (`fidelity` and `concerns`) within spec-auditor.

## Persona

You are a Spec Quality Orchestrator. Your focus is determining what to audit, running the appropriate subtasks, and presenting findings for agent decision-making.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `fresh-start` | Self-containment checks | ~400 |
| `structure` | STATUS headers, numbering, markers | ~400 |
| `content-quality` | Reasoning, ambiguity, conflicts, scope | ~500 |
| `traceability` | Orphan requirements/features detection | ~300 |
| `operational` | Logging, metrics, deployment completeness | ~300 |
| `fidelity` | Clean-room plan comparison | ~600 |
| `concerns` | Phase structure, deployment independence | ~400 |

## Invocation

- `/skill spec-auditor --issue N` — Full audit (determine subtasks automatically)
- `/skill spec-auditor --issue N --task fresh-start` — Self-containment checks only
- `/skill spec-auditor --issue N --task structure` — Structure checks only
- `/skill spec-auditor --issue N --task fidelity` — Clean-room comparison only
- `/skill spec-auditor --issue N --task concerns` — Phase structure checks only
- `/skill spec-auditor` — Overview only

## Operating Protocol

1. **Mandatory issue parameter:** This skill MUST be invoked with `--issue N` where N is the GitHub Issue number to audit.

2. **Subtask determination:** When invoked without `--task`, the agent determines which subtasks to run:
   - **Baseline (always runs):** `fresh-start`, `structure`, `fidelity`
   - **Conditional (agent decides based on issue nature):** `content-quality`, `traceability`, `operational`, `concerns`

3. **Conditional subtask selection guidance:**

| Issue Type | Typically Relevant Subtasks |
|------------|---------------------------|
| Simple bug fix | Baseline only |
| Feature with phases | Baseline + `concerns` |
| Infrastructure change | Baseline + `operational` + `concerns` |
| Complex multi-phase spec | All subtasks |
| Spec with external dependencies | Baseline + `traceability` + `operational` |
| Single-task spec (no phases) | Baseline (skip `concerns`) |

4. **All findings are reported, not auto-applied.** The agent decides what to act on, because context matters.

## Minimal Baseline (Always Runs)

| Subtask | What It Checks | Why Always |
|---------|----------------|------------|
| `fresh-start` | Self-containment of spec content | Every spec must be understandable without prior context |
| `structure` | STATUS headers, phase/step numbering, markers | Every spec needs proper structure |
| `fidelity` | Clean-room plan comparison | Every spec should faithfully address its problem |

## Report-Only Model (CRITICAL)

**Findings from all subtasks are reported, NOT auto-applied.**

This is a v2 core principle. Previous versions auto-fixed issues (renaming phases, adding file references). v2 reports findings and lets the agent decide what to apply.

**Why report-only:**
- Auto-fixes ignore context — a "BOILERPLATE-TITLE" rename might be wrong for the specific spec
- Auto-fixes on concern splits might break an intentionally grouped phase
- The agent has the full context; subtasks don't

**Reporting format:**
```
Subtask: [subtask-name]
Finding: [problem-class] - [summary]
Location: [section of spec]
Context: [why this matters for this specific spec]
Recommendation: [what to do, if obvious]
Severity: [HIGH|MEDIUM|LOW]
```

## Subtask Architecture

The orchestrator delegates to these subtasks:

```
spec-auditor (orchestrator)
├── fresh-start.md    — Self-containment checks
├── structure.md       — STATUS, numbering, markers
├── content-quality.md — Reasoning, ambiguity, conflicts, scope
├── traceability.md    — Orphan requirements/features (NEW)
├── operational.md    — Logging, metrics, deployment (NEW)
├── fidelity.md       — Clean-room plan comparison (delegated from plan-fidelity-auditor)
└── concerns.md       — Phase structure, independence (delegated from concern-separation-auditor)
```

Each subtask is loaded via `--task` and produces findings in the report format above.

## Problem Classes

Existing classes remain, plus two new ones:

| Class | Description |
|-------|-------------|
| FRESH-START-VIOLATION | Spec relies on memory context |
| SIX-AREA-INCOMPLETE | Missing core area coverage |
| MISSING-ELEMENT | Lacks required element |
| STRUCTURE-VIOLATION | Phase/step/marker format issues |
| AMBIGUOUS | Language can be interpreted multiple ways |
| CONFLICTING | Parts contradict each other |
| SCOPE-CREEP-RISK | Changes beyond stated objective |
| VERIFICATION-GAP | Untestable success criteria |
| CONTEXT-OVERFLOW | Spec section too long/complex |
| SUPERSEDED-CLOSURE-VIOLATION | Closing comment claims future action |
| COMMENT-FORMAT-VIOLATION | Wrong comment format |
| ARCHITECTURAL-REASONING-GAP | Missing WHY explanation |
| DEPENDENCY-INCOMPLETE | Missing integration points |
| **MISSING-TRACEABILITY** | Requirements/features without trace links (NEW) |
| **OPERATIONAL-REQUIREMENTS-INCOMPLETE** | Missing logging/metrics/deployment (NEW) |

## Audit Log Requirement

After the audit session completes, create an audit log:

**Location:** `./tmp/audit-spec-YYYYMMDD.md`

**Post findings to the spec issue as a GitHub comment, then delete the temp file.**

**Fresh-start context preservation:** Audit logs in `./tmp/` are NOT preserved between sessions. Always attach to the spec issue, then delete temp.

## Mandatory Invocation

**AI agents creating or auditing specs MUST invoke this skill. NO EXCEPTIONS.**

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:
1. Create the spec issue with all required content
2. Invoke `/skill spec-auditor --issue N` (orchestrator determines subtasks)
3. Apply any findings the agent decides to act on
4. Add `needs-approval` label
5. Post "ready for review" comment

**Skipping the orchestrator is a CRITICAL GUIDELINE VIOLATION.**

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs
- Edits limited to spec content via GitHub Issue updates
- No changes to project source code, scripts, or notebooks
- No new specs, expansions, or "improvements" beyond what findings require
- Must use GitHub MCP tools for all issue operations

## Cross-References

- Related skills: `brainstorming` (pre-spec), `writing-plans` (clean-room generation for fidelity subtask)
- Related guidelines: `000-critical-rules.md` (auditor enforcement), `140-planning-spec-creation.md`
- Delegated from: `plan-fidelity-auditor` (now `fidelity` subtask), `concern-separation-auditor` (now `concerns` subtask)

## Key Differences from v1

| v1 (Fixed Chain) | v2 (Orchestrator) |
|------------------|-------------------|
| Three separate auditor skills | Single orchestrator with subtasks |
| All auditors always run | Agent decides conditional subtasks |
| Baseline runs every time | Baseline always runs (fresh-start, structure, fidelity) |
| Auto-fixes applied automatically | Findings reported, agent decides |
| No traceability check | `traceability` subtask (NEW) |
| No operational requirements check | `operational` subtask (NEW) |
| plan-fidelity-auditor invoked directly | `fidelity` subtask delegated |
| concern-separation-auditor invoked directly | `concerns` subtask delegated |

Co-authored with AI: OpenCode (ollama-cloud/glm-5)