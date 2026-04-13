---
name: spec-auditor
description: Use when auditing a spec for quality, structure, or completeness. Triggers on: audit spec, review spec, spec quality, validate spec, check spec, audit issue, revisit spec.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: spec-auditor

## Overview

Single audit orchestrator entry point for spec quality. Determines which subtasks to run based on the issue's nature, runs the minimal baseline always, and applies auto-fixes for safe findings while flagging ambiguous findings for review.

**Core v2 shift:** Spec-auditor is now the orchestrator. Plan-fidelity-auditor and concern-separation-auditor are no longer invoked directly — their logic lives as subtasks (`fidelity` and `concerns`) within spec-auditor.

**v3 shift:** Spec-auditor now uses an auto-fix model with three-tier classification instead of the previous report-only approach. Safe findings are fixed directly; ambiguous findings are flagged for developer review.

## Persona

You are a Spec Quality Orchestrator. Your focus is determining what to audit, running the appropriate subtasks, auto-fixing safe findings, flagging ambiguous findings for review, and presenting an executive summary of all actions taken.

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

4. **All findings are classified and acted on per the auto-fix model.** Safe findings are fixed directly; ambiguous findings are flagged for developer review.

5. **After all subtasks complete, produce a chat executive summary** per the `Chat Executive Summary` section below.

## Minimal Baseline (Always Runs)

| Subtask | What It Checks | Why Always |
|---------|----------------|------------|
| `fresh-start` | Self-containment of spec content | Every spec must be understandable without prior context |
| `structure` | STATUS headers, phase/step numbering, markers | Every spec needs proper structure |
| `fidelity` | Clean-room plan comparison | Every spec should faithfully address its problem |

## Auto-Fix Model (CRITICAL)

**Findings from all subtasks are classified into three tiers and acted on accordingly.**

This is a v3 core principle. Previous versions (v2) were report-only — findings were listed and the agent decided what to apply. v3 auto-fixes safe findings directly and only flags ambiguous findings for developer review.

**Three-tier classification:**

| Tier | Classification | Action | When |
|------|---------------|--------|------|
| **Auto-fix** | Safe, mechanical fix | Apply fix directly to the spec | Factual corrections, structure violations, missing boilerplate elements, boilerplate titles, approach differences, concern separation fixes |
| **Conditional** | Safe with safety check | Auto-fix after confirming no adverse impact | Scope creep removal, context overflow reduction |
| **Flag-for-review** | Ambiguous/subjective | Report only, do not fix | Ambiguous language, conflicting requirements, judgment calls where context is critical |

**Auto-fix eligible findings:**

| Problem Class | Auto-fix Action | Rationale |
|---------------|----------------|-----------|
| STRUCTURE-VIOLATION | Fix STATUS headers, numbering, markers | Format is mechanical, no judgment needed |
| MISSING-ELEMENT (boilerplate) | Add CREATED date, required markers | Standard boilerplate, no spec judgment |
| BOILERPLATE-TITLE | Rename phase to describe specific concern | Generic names are always a problem; specific concern names are always better |
| MISSING-TRACEABILITY | Add trace links between requirements and steps | Traceability is always correct; adding links doesn't change semantics |
| OPERATIONAL-REQUIREMENTS-INCOMPLETE | Add operational requirements section stub | Placeholder doesn't change semantics; developer fills in |
| FRESH-START-VIOLATION | Inline context, replace "see above" with actual content | Self-containment is always correct; removes ambiguity |
| DEPENDENCY-INCOMPLETE | Add specific integration points | Precision is always better than vagueness |
| APPROACH_DIFFERENCE | Add missing approach or clarify difference | Fidelity to the clean-room plan is always desirable |

**Conditional findings:**

| Problem Class | Safety Check Before Auto-fix | Rationale |
|---------------|------------------------------|-----------|
| SCOPE-CREEP-RISK | Verify removed scope doesn't break dependencies | Removing scope could orphan other steps |
| CONTEXT-OVERFLOW | Verify section reduction preserves all requirements | Shortening sections could lose critical details |

**Flag-for-review findings:**

| Problem Class | Why Not Auto-fixed |
|---------------|-------------------|
| AMBIGUOUS | Agent can't resolve ambiguity without domain context |
| CONFLICTING | Contradictions require understanding intent |
| VERIFICATION-GAP | Success criteria require domain expertise |
| COMMENT-FORMAT-VIOLATION | May be intentional formatting |
| SUPERSEDED-CLOSURE-VIOLATION | Closure language may reference valid future work |
| ARCHITECTURAL-REASONING-GAP | Requires understanding design tradeoffs |
| VAGUE_PROBLEM | Problem statement vagueness requires human input |

**Reporting format (v3 — includes Classification and Fix Action):**
```
Subtask: [subtask-name]
Finding: [problem-class] - [summary]
Location: [section of spec]
Context: [why this matters for this specific spec]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

**For auto-fix findings:** `Fix Action` describes what change was applied. For example: "Renamed phase from 'Implementation' to 'Schema Migration'", "Added CREATED: 2025-04-13", "Inlined 'see above' with actual context".

**For conditional findings:** `Fix Action` describes the fix applied after the safety check passed, or "conditional fix skipped — [reason]" if the check failed.

**For flag-for-review findings:** `Fix Action` is "flagged for review — [reason it can't be auto-fixed]".

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

## Audit Findings Handling

After the audit session completes, findings are acted on per the auto-fix model: safe fixes are applied directly, conditional fixes are applied after safety checks, and ambiguous findings are flagged for review.

**Findings are NOT posted as GitHub comments.** Audit findings are analogous to linter output: auto-fixes are applied silently (like `ruff --fix`), and flagged findings are reported in the executive summary. The correct workflow is:

1. **Audit** → run subtasks, collect findings
2. **Classify** → assign each finding to auto-fix, conditional, or flag-for-review
3. **Act** → apply auto-fixes directly; apply conditional fixes after safety checks; leave flag-for-review findings for developer action
4. **Comment ONLY for substantive revisions** → if the combined auto-fixes and conditional fixes change requirements, phases, success criteria, or scope, post one revision comment following `github-comments` skill format. Non-substantive changes (STATUS markers, boilerplate additions, numbering fixes, trace links) get NO comment.
5. **Post executive summary to chat** → per the `Chat Executive Summary` section below

**When NO comment is posted:**
- Audit finds zero issues (all PASS) — move on, no comment
- Agent only makes non-substantive auto-fixes (STATUS updates, boilerplate, numbering, trace links, typo fixes) — no comment
- Flag-for-review findings exist but no substantive changes made — no comment (flagged in executive summary instead)

**When a comment IS posted:**
- Agent makes substantive spec changes (adding/removing phases, changing requirements, altering approach) — post one revision comment per `github-comments` skill

**Session scratch space:** Findings may be written to `./tmp/audit-spec-YYYYMMDD.md` for session-level reference. This file is NOT posted anywhere and is deleted after the session ends.

## Chat Executive Summary

**After every audit, a structured executive summary MUST be posted to chat.** This is mandatory regardless of whether findings were found.

**Format:**
```
## Spec Audit: #N — [spec title]

**Changes Made:**
- [subtask] [problem-class]: [what was fixed] (auto-fix)
- [subtask] [problem-class]: [what was fixed after safety check] (conditional)
- (or "No changes made" if no auto-fixes or conditional fixes applied)

**Findings Not Acted On:**
- [subtask] [problem-class]: [summary] — [reason not acted on] (flag-for-review)
- (or "None" if all findings were auto-fixed or conditionally fixed)

**Issue:** [URL of the audited issue]
```

**Rules:**
- Executive summary goes to chat ONLY, not GitHub comments
- Changes Made lists ALL auto-fix and conditional fix actions in summary form
- Findings Not Acted On lists ALL flag-for-review findings with the specific reason they weren't auto-fixed
- If audit finds zero issues, output: `## Spec Audit: #N — [spec title] — No findings. Issue: [URL]`
- Issue URL is constructed from session init values (`GIT_OWNER`, `GIT_REPO`)

## Mandatory Invocation

**AI agents creating or auditing specs MUST invoke this skill. NO EXCEPTIONS.**

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:
1. Create the spec issue with all required content
2. Invoke `/skill spec-auditor --issue N` (orchestrator determines subtasks)
3. Auto-fix findings are applied directly; flag-for-review findings remain in executive summary for developer action
4. Add `needs-approval` label
5. Post "ready for review" comment ONLY if substantive spec changes were made during step 3 (auto-fixes of structure/boilerplate are non-substantive)

**Skipping the orchestrator is a CRITICAL GUIDELINE VIOLATION.**

## Scope Boundaries

- Read-only analysis of GitHub Issue `[SPEC]` specs, plus auto-fix of safe findings
- Edits limited to spec content via GitHub Issue updates (auto-fixes applied directly)
- Flag-for-review findings reported in executive summary but NOT applied
- No changes to project source code, scripts, or notebooks
- No new specs, expansions, or "improvements" beyond what findings require
- Must use GitHub MCP tools for all issue operations
- **Worktree awareness check:** Skills that perform git operations, read/write files, or dispatch sub-agents MUST include a "Worktree Mode" section and pass `WORKTREE_PATH` in sub-agent dispatch contexts. Missing worktree awareness is a medium-severity finding.

## Sub-Agent Spawning

This skill is a **heavy skill** — quality audits with all subtasks consume significant context. When the main agent needs a spec audit, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~1,278 words)
2. Main agent identifies which subtasks to run (baseline + conditional)
3. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use spec-auditor skill --issue N --task <subtask> with context: <session-context>")`
4. Sub-agent loads: this SKILL.md + relevant task file(s) + required guidelines
5. Sub-agent executes audit in isolation, returns findings as structured report
6. Main agent receives findings — no full audit content in main context

**Sub-agent context parameters:** Pass issue number, `WORKTREE_PATH`, `GIT_OWNER`, `GIT_REPO` from session init. When `WORKTREE_PATH` is set, sub-agents MUST receive it and use it as the base directory for all file operations and git commands.

## Cross-References

- Related skills: `brainstorming` (exploration), `spec-creation` (creation-time discipline for traceability and operational requirements), `writing-plans` (clean-room generation for fidelity subtask), `issue-review` (delegates to spec-auditor via audit task)
- Related guidelines: `000-critical-rules.md` (auditor enforcement), `140-planning-spec-creation.md`
- Label state machine: `141-planning-status-tracking.md §10` (add `needs-revision` when audit requires changes; replace with `needs-approval` on re-submission)
- Delegated from: `plan-fidelity-auditor` (now `fidelity` subtask), `concern-separation-auditor` (now `concerns` subtask)

## Key Differences from v1

| v1 (Fixed Chain) | v2 (Orchestrator) | v3 (Auto-Fix Orchestrator) |
|------------------|-------------------|---------------------------|
| Three separate auditor skills | Single orchestrator with subtasks | Single orchestrator with subtasks |
| All auditors always run | Agent decides conditional subtasks | Agent decides conditional subtasks |
| Baseline runs every time | Baseline always runs (fresh-start, structure, fidelity) | Baseline always runs (fresh-start, structure, fidelity) |
| Auto-fixes applied automatically | Findings reported, agent decides | Three-tier classification: auto-fix, conditional, flag-for-review |
| No traceability check | `traceability` subtask (NEW) | `traceability` subtask |
| No operational requirements check | `operational` subtask (NEW) | `operational` subtask |
| plan-fidelity-auditor invoked directly | `fidelity` subtask delegated | `fidelity` subtask delegated |
| concern-separation-auditor invoked directly | `concerns` subtask delegated | `concerns` subtask delegated |
| No executive summary | No executive summary | Chat executive summary mandatory |
| Report format: Recommendation field | Report format: Recommendation field | Report format: Classification + Fix Action fields |

Co-authored with AI: OpenCode (ollama-cloud/glm-5)

## Symbolic Engine Integration

**Optional pre-step:** Before auditing, invoke the symbolic analysis engine for formal evidence:

```bash
./.opencode/tools/symbolic states
./.opencode/tools/symbolic flow
```

- `sym-states`: Validates state machines extracted from yaml+symbolic blocks — checks reachability from start_state, detects dead/unreachable states, flags dangling references in transitions.
- `sym-flow`: Builds a networkx DiGraph from rule triggers/requires and detects flow anomalies — unreachable nodes, cycles, orphan nodes with no edges.

Results are used as **evidence** (not verdict) — they supplement prose-only analysis with formal state machine and flow validation.

**Graceful degradation:** If the engine is unavailable or produces no results, fall back to prose-only analysis. Do NOT block the audit if the engine fails.

**Import interface (for in-process usage):**
```python
import types, sys
from pathlib import Path
impl_dir = Path(".opencode/tools/impl")
source = (impl_dir / "sym-states").read_text()
mod = types.ModuleType("symstates")
mod.__file__ = str(impl_dir / "sym-states")
sys.modules["symstates"] = mod
exec(compile(source, str(impl_dir / "sym-states"), "exec"), mod.__dict__)
anomalies = mod.validate_state_machines(state_machines, rules)
```