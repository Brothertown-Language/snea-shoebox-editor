---
name: spec-auditor
description: Use when auditing a spec for quality, structure, or completeness. Triggers on: audit spec, review spec, spec quality, validate spec, check spec, audit issue, revisit spec, audit plan, audit runbook, audit SOP, audit checklist, audit document, content-aware audit.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: spec-auditor

## Overview

Content-aware audit orchestrator that accepts any document type. Determines document type automatically (or via manual override), selects appropriate subtasks, runs the minimal baseline always, and applies auto-fixes for safe findings while flagging ambiguous findings for review.

**Core v2 shift:** Spec-auditor is now the orchestrator. Plan-fidelity-auditor and concern-separation-auditor are no longer invoked directly — their logic lives as subtasks (`fidelity` and `concerns`) within spec-auditor.

**v3 shift:** Spec-auditor now uses an auto-fix model with three-tier classification instead of the previous report-only approach. Safe findings are fixed directly; ambiguous findings are flagged for developer review.

**v4 shift:** Spec-auditor now supports content-aware auditing. Input can come from issues, files, or URLs. Document type is autodetected and subtask selection is tailored per type. Three new operational subtasks (`operational-flow`, `determinism`, `error-recovery`) support process flows, runbooks, and SOPs.

## Persona

You are a Content-Aware Audit Orchestrator. Your focus is determining document type, selecting appropriate subtasks, auto-fixing safe findings, flagging ambiguous findings for review, and presenting an executive summary of all actions taken.

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
| `operational-flow` | Process flow / runbook operational checks | ~400 |
| `determinism` | Deterministic behavior and state dependency checks | ~300 |
| `error-recovery` | Runbook error recovery and rollback checks | ~350 |

## Invocation

- `/skill spec-auditor --issue N` — Full audit of a GitHub Issue (determine subtasks automatically)
- `/skill spec-auditor --file path` — Full audit of a local file (determine subtasks automatically)
- `/skill spec-auditor --url URL` — Full audit of a URL (determine subtasks automatically)
- `/skill spec-auditor --issue N --task fresh-start` — Self-containment checks only
- `/skill spec-auditor --issue N --task structure` — Structure checks only
- `/skill spec-auditor --issue N --task fidelity` — Clean-room comparison only
- `/skill spec-auditor --issue N --task concerns` — Phase structure checks only
- `/skill spec-auditor --file path --type plan` — Audit with manual type override
- `/skill spec-auditor --url URL --type runbook` — Audit with manual type override
- `/skill spec-auditor` — Overview only

One of `--issue`, `--file`, or `--url` is mandatory (except for overview mode). Use `--type` to override autodetected document type. Use `--task` to run a single subtask.

## Operating Protocol

1. **Mandatory input parameter:** This skill MUST be invoked with one of `--issue N`, `--file path`, or `--url URL` (except overview mode). The content source determines how to read the document.

2. **Document type autodetection:** When invoked without `--type`, the agent detects the document type from content signals:

   **Signal table:**

   | Signal | Type Suggested | Weight |
   |--------|---------------|--------|
   | `STATUS:` header with phase.step format | Spec | 3 |
   | Phase/step numbering (`1.1`, `1.2`, `2.1`) | Spec | 2 |
   | Success criteria section | Spec | 2 |
   | `STATUS:` header without approval tracking | Plan | 2 |
   | Milestone/deliverable structure | Plan | 2 |
   | Sequential numbered steps (imperative mood) | Process Flow | 3 |
   | Step result feeds next step input | Process Flow | 2 |
   | "Runbook" or "SOP" in title or header | Runbook/SOP | 3 |
   | Prerequisites section | Runbook/SOP | 1 |
   | Error recovery / rollback sections | Runbook/SOP | 2 |
   | Checkbox list (`- [ ]`, `- [x]`) | Checklist | 3 |
   | Flat list of items without phases | Checklist | 2 |
   | Reference table, API documentation | Reference Doc | 3 |
   | No phases, no steps, no criteria | Reference Doc | 1 |

   **Scoring algorithm:**
   - Sum weights for each type from matching signals
   - Highest total score wins
   - Ties: prefer more specific type (Spec > Plan > Process Flow > Runbook/SOP > Checklist > Reference Doc)

   **Confidence levels:**

   | Confidence | Condition | Action |
   |------------|-----------|--------|
   | High | Single type score ≥ 5 AND ≥ 3 points above runner-up | Proceed with detected type |
   | Medium | Single type score ≥ 5 AND 1–2 points above runner-up | Proceed but note medium confidence in summary |
   | Low | Two or more types within 2 points, or top score 3–4 | Flag for user to confirm type before auditing |
   | None | Empty or unparseable content | Error out — cannot audit |

   **Manual override:** `--type <type>` bypasses autodetection. Valid types: `spec`, `plan`, `process-flow`, `runbook`, `checklist`, `reference-doc`.

3. **Subtask determination:** When invoked without `--task`, the agent determines which subtasks to run based on document type:

   | Document Type | Baseline Subtasks | Conditional Subtasks |
   |---------------|-------------------|---------------------|
   | Spec | `fresh-start`, `structure`, `fidelity` | `content-quality`, `traceability`, `operational`, `concerns` |
   | Plan | `fresh-start`, `structure` | `content-quality`, `concerns` |
   | Process Flow | `fresh-start`, `structure` (adapted) | `operational-flow`, `determinism` |
   | Runbook/SOP | `fresh-start`, `structure` (adapted) | `operational-flow`, `determinism`, `error-recovery` |
   | Checklist | `fresh-start`, `structure` (adapted) | — |
   | Reference Doc | `fresh-start` | — |

   **Conditional subtask selection guidance (Spec-type only):**

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

## Minimal Baseline (Varies by Document Type)

| Document Type | Baseline Subtasks | Why These |
|---------------|-------------------|-----------|
| Spec | `fresh-start`, `structure`, `fidelity` | Every spec must be self-contained, properly structured, and faithful to its problem |
| Plan | `fresh-start`, `structure` | Plans need self-containment and structure; `fidelity` applies only to specs |
| Process Flow | `fresh-start`, `structure` (adapted) | Flows need self-containment and adapted structure checks |
| Runbook/SOP | `fresh-start`, `structure` (adapted) | Runbooks need self-containment and adapted structure checks |
| Checklist | `fresh-start`, `structure` (adapted) | Checklists need self-containment and adapted structure checks |
| Reference Doc | `fresh-start` | Reference docs only need self-containment checks |

## Auto-Fix Model (CRITICAL)

**Findings from all subtasks are classified into three tiers and acted on accordingly.**

This is a v3 core principle. Previous versions (v2) were report-only — findings were listed and the agent decided what to apply. v3 auto-fixes safe findings directly and only flags ambiguous findings for developer review.

**Authorization path:** Auto-fix findings are exempt from the approval-gate's "no implementation without authorization" rule. See `010-approval-gate.md` → "Audit Auto-Fix Exemption" for the complete conditions. **Conditional findings are NOT exempt** — they require explicit authorization before application. **Flag-for-review findings are never applied** — they are reported in the executive summary only.

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
| OPERATIONAL-FLOW-GAP | Add placeholder for missing error recovery, I/O contract, or rollback step | Placeholder doesn't change semantics; developer fills in |
| DETERMINISM-VIOLATION | Add explicit environment assumptions and state dependency notes | Explicitness is always correct; removes ambiguity |
| ERROR-RECOVERY-GAP | Add prerequisites, scope, escalation, and version stub sections | Standard boilerplate for runbooks; developer fills in |

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
├── fresh-start.md         — Self-containment checks
├── structure.md            — STATUS, numbering, markers (adapted for non-spec types)
├── content-quality.md      — Reasoning, ambiguity, conflicts, scope
├── traceability.md         — Orphan requirements/features
├── operational.md           — Logging, metrics, deployment
├── fidelity.md             — Clean-room plan comparison (delegated from plan-fidelity-auditor)
├── concerns.md             — Phase structure, independence (delegated from concern-separation-auditor)
├── operational-flow.md     — Process flow / runbook operational checks (NEW)
├── determinism.md          — Deterministic behavior and state dependency checks (NEW)
└── error-recovery.md       — Runbook error recovery and rollback checks (NEW)
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
| **OPERATIONAL-FLOW-GAP** | Missing error recovery, I/O contracts, idempotency, or rollback in process flows |
| **DETERMINISM-VIOLATION** | Hidden non-determinism, unstated environment assumptions, undocumented state dependencies |
| **ERROR-RECOVERY-GAP** | Missing prerequisites, scope, escalation contacts, versioning, or validation gates in runbooks |

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
## Content Audit: [source identifier] — [document title]

**Document Type:** [Spec|Plan|Process Flow|Runbook/SOP|Checklist|Reference Doc] (confidence: [High|Medium|Low])
**Source:** [--issue N|--file path|--url URL]

**Changes Made:**
- [subtask] [problem-class]: [what was fixed] (auto-fix)
- [subtask] [problem-class]: [what was fixed after safety check] (conditional)
- (or "No changes made" if no auto-fixes or conditional fixes applied)

**Findings Not Acted On:**
- [subtask] [problem-class]: [summary] — [reason not acted on] (flag-for-review)
- (or "None" if all findings were auto-fixed or conditionally fixed)

**Issue:** [URL of the audited issue, if applicable]
```

**Rules:**
- Executive summary goes to chat ONLY, not GitHub comments
- Changes Made lists ALL auto-fix and conditional fix actions in summary form
- Findings Not Acted On lists ALL flag-for-review findings with the specific reason they weren't auto-fixed
- If audit finds zero issues, output: `## Content Audit: [source] — [title] — No findings. Type: [type] (confidence: [level]). Issue: [URL if applicable]`
- Issue URL is constructed from session init values (`GIT_OWNER`, `GIT_REPO`)

## Mandatory Invocation

**AI agents creating or auditing specs MUST invoke this skill. NO EXCEPTIONS.**

When creating a GitHub Issue `[SPEC]`, the AI agent MUST:
1. Create the spec issue with all required content
2. Invoke `/skill spec-auditor --issue N` (orchestrator determines type and subtasks)
3. Auto-fix findings are applied directly; flag-for-review findings remain in executive summary for developer action
4. Add `needs-approval` label
5. Post "ready for review" comment ONLY if substantive spec changes were made during step 3 (auto-fixes of structure/boilerplate are non-substantive)

When auditing a plan, runbook, process flow, checklist, or reference document, use `--file path` or `--url URL` as appropriate.

**Skipping the orchestrator is a CRITICAL GUIDELINE VIOLATION.**

## Scope Boundaries

- Read-only analysis of GitHub Issues, local files, or URLs, plus auto-fix of safe findings
- Edits limited to spec content via GitHub Issue updates (auto-fixes applied directly); file/URL sources are read-only
- Flag-for-review findings reported in executive summary but NOT applied
- No changes to project source code, scripts, or notebooks
- No new specs, expansions, or "improvements" beyond what findings require
- Must use GitHub MCP tools for all issue operations
- Document type autodetection uses signal scoring; Low confidence requires user confirmation before proceeding
- None confidence (empty/unparseable content) produces an error — cannot audit
- **Backward compatibility:** `--issue N` produces identical results to previous behavior
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

| v1 (Fixed Chain) | v2 (Orchestrator) | v3 (Auto-Fix Orchestrator) | v4 (Content-Aware) |
|------------------|-------------------|---------------------------|-------------------|
| Three separate auditor skills | Single orchestrator with subtasks | Single orchestrator with subtasks | Single orchestrator with subtasks |
| All auditors always run | Agent decides conditional subtasks | Agent decides conditional subtasks | Agent decides conditional subtasks per document type |
| Baseline runs every time | Baseline always runs (fresh-start, structure, fidelity) | Baseline always runs (fresh-start, structure, fidelity) | Baseline varies by document type |
| Auto-fixes applied automatically | Findings reported, agent decides | Three-tier classification: auto-fix, conditional, flag-for-review | Three-tier classification (unchanged) |
| No traceability check | `traceability` subtask (NEW) | `traceability` subtask | `traceability` subtask |
| No operational requirements check | `operational` subtask (NEW) | `operational` subtask | `operational` subtask |
| plan-fidelity-auditor invoked directly | `fidelity` subtask delegated | `fidelity` subtask delegated | `fidelity` subtask delegated |
| concern-separation-auditor invoked directly | `concerns` subtask delegated | `concerns` subtask delegated | `concerns` subtask delegated |
| No executive summary | No executive summary | Chat executive summary mandatory | Chat executive summary mandatory, includes document type |
| Report format: Recommendation field | Report format: Recommendation field | Report format: Classification + Fix Action fields | Report format: Classification + Fix Action fields |
| Issue-only input | Issue-only input | Issue-only input | `--issue`, `--file`, `--url` input |
| No type detection | No type detection | No type detection | Signal-based autodetection + `--type` override |
| Spec-only auditing | Spec-only auditing | Spec-only auditing | Multi-type: spec, plan, process-flow, runbook, checklist, reference-doc |

Co-authored with AI: <AI-Name> (<model-id>)

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