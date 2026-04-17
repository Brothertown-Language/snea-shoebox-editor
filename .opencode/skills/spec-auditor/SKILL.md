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
| `principles` | Engineering principle violations from programming-principles skill | ~350 |
| `ground-truth` | Adversarial verification of metadata claims against direct evidence | ~500 |
| `sub-issue-fidelity` | Verify sub-issue alignment with Plan phases (delegated from plan-fidelity-auditor) | ~350 |
| `concern-coverage` | Verify sub-issue concern boundaries match Plan phases (delegated from concern-separation-auditor) | ~350 |
| `prose-structure` | Anti-prose drift detection — flag rigid structure where prose is expected | ~250 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ~200 |

## Invocation

- `/skill spec-auditor --issue N` — Full audit of a GitHub Issue (determine subtasks automatically)
- `/skill spec-auditor --file path` — Full audit of a local file (determine subtasks automatically)
- `/skill spec-auditor --url URL` — Full audit of a URL (determine subtasks automatically)
- `/skill spec-auditor --issue N --task fresh-start` — Self-containment checks only
- `/skill spec-auditor --issue N --task structure` — Structure checks only
- `/skill spec-auditor --issue N --task fidelity` — Clean-room comparison only
- `/skill spec-auditor --issue N --task concerns` — Phase structure checks only
- `/skill spec-auditor --issue N --task principles` — Engineering principle checks only
- `/skill spec-auditor --issue N --task ground-truth` — Metadata verification checks only
- `/skill spec-auditor --issue N --task sub-issue-fidelity` — Sub-issue alignment with Plan phases only
- `/skill spec-auditor --issue N --task concern-coverage` — Sub-issue concern boundary checks only
- `/skill spec-auditor --issue N --task prose-structure` — Anti-prose drift checks only
- `/skill spec-auditor --task completion` — Invoke when workflow halts at any point
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
   | `STATUS:` header with prose-driven format (`in progress — {concern}`) | Spec | 3 |
   | `STATUS:` header with phase.step format (`1.1`, `1.2`, `2.1`) | Spec | 3 |
   | `STATUS:` header with `(REVISED - NEEDS APPROVAL)` suffix | Spec | 2 |
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
     | Spec | `fresh-start`, `structure`, `fidelity`, `ground-truth`, `principles` | `content-quality`, `traceability`, `operational`, `concerns`, `sub-issue-fidelity`, `concern-coverage`, `prose-structure` |
     | Plan | `fresh-start`, `structure`, `ground-truth`, `principles` | `content-quality`, `concerns`, `sub-issue-fidelity`, `concern-coverage`, `prose-structure` |
    | Process Flow | `fresh-start`, `structure` (adapted), `ground-truth`, `principles` | `operational-flow`, `determinism` |
    | Runbook/SOP | `fresh-start`, `structure` (adapted), `ground-truth`, `principles` | `operational-flow`, `determinism`, `error-recovery` |
    | Checklist | `fresh-start`, `structure` (adapted), `ground-truth`, `principles` | — |
    | Reference Doc | `fresh-start`, `ground-truth`, `principles` | — |

   **Conditional subtask selection guidance (Spec-type only):**

    | Issue Type | Typically Relevant Subtasks |
    |------------|---------------------------|
    | Simple bug fix | Baseline only |
    | Feature with phases | Baseline + `concerns` |
    | Infrastructure change | Baseline + `operational` + `concerns` |
    | Complex multi-phase spec | All subtasks |
    | Spec with external dependencies | Baseline + `traceability` + `operational` |
    | Single-task spec (no phases) | Baseline (skip `concerns`) |
    | Spec with sub-issues | Baseline + `sub-issue-fidelity` + `concern-coverage` |
    | Plan with sub-issues | Baseline + `sub-issue-fidelity` + `concern-coverage` |
    | Spec or Plan with anti-prose patterns | Baseline + `prose-structure` |

4. **All findings are classified and acted on per the auto-fix model.** Safe findings are fixed directly; ambiguous findings are flagged for developer review.

5. **After all subtasks complete, produce a chat executive summary** per the `Chat Executive Summary` section below.

## Minimal Baseline (Varies by Document Type)

| Document Type | Baseline Subtasks | Why These |
|---------------|-------------------|-----------|
| Spec | `fresh-start`, `structure`, `fidelity`, `ground-truth`, `principles` | Every spec must be self-contained, properly structured, faithful to its problem, metadata-verified, and principle-compliant |
| Plan | `fresh-start`, `structure`, `ground-truth`, `principles` | Plans need self-containment, structure, metadata verification, and principle compliance; `fidelity` applies only to specs |
| Process Flow | `fresh-start`, `structure` (adapted), `ground-truth`, `principles` | Flows need self-containment, adapted structure checks, metadata verification, and principle compliance |
| Runbook/SOP | `fresh-start`, `structure` (adapted), `ground-truth`, `principles` | Runbooks need self-containment, adapted structure checks, metadata verification, and principle compliance |
| Checklist | `fresh-start`, `structure` (adapted), `ground-truth`, `principles` | Checklists need self-containment, adapted structure checks, metadata verification, and principle compliance |
| Reference Doc | `fresh-start`, `ground-truth`, `principles` | Reference docs need self-containment, metadata verification, and principle compliance |

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
| SRP_VIOLATION (phase rename) | Rename phase/step to describe the single specific responsibility | Specific responsibility names are always better than generic ones |
| ANTI-PROSE-DRIFT | Rewrite rigid structure as flowing prose | Prose is always more readable than mechanical enumeration where narrative is expected; conversion is mechanical |
| PLAN-BLEED | Replace code/DDL with requirements table; note moved content for plan | Spec boundary is always correct; HOW belongs in the plan, not the spec |
| GROUND-TRUTH-MISMATCH (STATUS) | Update STATUS marker to reflect actual content maturity (prose or numeric format, matching the document's convention) | STATUS is metadata, not content; correcting it removes false tracking |
| GROUND-TRUTH-MISMATCH (auth superseded) | Add re-approval note to document body | Revision revokes approval is a mandatory rule; noting it is mechanical |
| INCOMPLETE_SUB_ISSUE_BODY | Update sub-issue body with Plan phase prose | Sub-issue should reflect Plan phase prose per the spec; alignment is always correct |
| TASK_NOT_IN_SUB_ISSUE | Add traceable task from Plan phase to sub-issue | Traceability is always correct; adding tasks aligns sub-issues with phases |

**Conditional findings:**

| Problem Class | Safety Check Before Auto-fix | Rationale |
|---------------|------------------------------|-----------|
| SCOPE-CREEP-RISK | Verify removed scope doesn't break dependencies | Removing scope could orphan other steps |
| CONTEXT-OVERFLOW | Verify section reduction preserves all requirements | Shortening sections could lose critical details |
| YAGNI_VIOLATION | Verify removed features/abstractions have no dependents | Removing unrequired features could orphan other steps |
| SOC_VIOLATION (phase split) | Verify split preserves all step content | Splitting phases could lose cross-concern context |
| GROUND-TRUTH-MISMATCH (stale label) | Verify auth scope covers current document before removing label | Removing label without confirming auth scope could misrepresent approval state |

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
| KISS_VIOLATION | Simplicity vs. design intent requires domain judgment |
| COUPLING_VIOLATION | Decoupling strategy depends on architecture context |
| BLAST_RADIUS_VIOLATION | Isolation scope depends on deployment architecture |
| TESTABILITY_VIOLATION | Testability tradeoffs require understanding of project constraints |
| PRINCIPLE_VIOLATION | Generic principle violation requires domain judgment |
| PLAN-BLEED-AMBIGUOUS | Content could be requirement or implementation detail; requires domain judgment |
| GROUND-TRUTH-MISMATCH (cross-ref missing) | Referenced issue may have been deleted or renumbered; requires developer to resolve |
| GROUND-TRUTH-MISMATCH (cross-ref mismatch) | Referenced issue exists but content differs from claim; intent requires domain judgment |
| GROUND-TRUTH-MISMATCH (code ref missing) | Referenced file/function may be planned but not implemented; requires developer to confirm |
| GROUND-TRUTH-MISMATCH (STATUS inflated) | STATUS says COMPLETE but content is immature; may be intentional tracking |
| MISSING_SUB_ISSUE | Creating sub-issues requires authorization per approval-gate |
| MISMATCHED_PHASE_NAME | Renaming requires author judgment about scope |
| CONCERN_SCOPE_NARROWER | Narrower scope may be valid scoping decision |
| CONCERN_SCOPE_WIDER | Wider scope may intentionally group coupled tasks |
| CONCERN_BOUNDARY_CROSSED | Cross-boundary tasks may reflect legitimate dependencies |

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
├── error-recovery.md       — Runbook error recovery and rollback checks (NEW)
├── principles.md           — Engineering principle violations from programming-principles skill (NEW)
├── ground-truth.md         — Adversarial verification of metadata claims against direct evidence (NEW)
├── sub-issue-fidelity.md   — Verify sub-issue alignment with Plan phases (delegated from plan-fidelity-auditor) (NEW)
└── concern-coverage.md     — Verify sub-issue concern boundaries match Plan phases (delegated from concern-separation-auditor) (NEW)
└── prose-structure.md      — Anti-prose drift detection (NEW)
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
| **SRP_VIOLATION** | Phase/step/module with multiple reasons to change |
| **SOC_VIOLATION** | Mixed concerns in a single phase or step |
| **YAGNI_VIOLATION** | Features or abstractions without current requirement |
| **KISS_VIOLATION** | Unnecessarily complex approach when simpler solution exists |
| **COUPLING_VIOLATION** | Tight coupling between phases or steps that should be independent |
| **BLAST_RADIUS_VIOLATION** | Change scope wider than necessary; failure isolation absent |
| **TESTABILITY_VIOLATION** | Design that makes testing difficult without explicit tradeoff note |
| **PRINCIPLE_VIOLATION** | Any of the 20 engineering principles violated without documented tradeoff note (fallback) |
| **PLAN-BLEED** | Spec prescribing HOW instead of WHAT; implementation details belong in the plan |
| **PLAN-BLEED-AMBIGUOUS** | Content that could be either a requirement or implementation detail; requires domain judgment |
| **GROUND-TRUTH-MISMATCH** | Metadata claim (STATUS, label, cross-ref, code ref, auth) contradicts actual state |
| **MISSING_SUB_ISSUE** | Plan phase has no corresponding sub-issue (from sub-issue-fidelity) |
| **MISMATCHED_PHASE_NAME** | Sub-issue name doesn't semantically match Plan phase name (from sub-issue-fidelity) |
| **INCOMPLETE_SUB_ISSUE_BODY** | Sub-issue body missing substantial Plan phase content (from sub-issue-fidelity) |
| **TASK_NOT_IN_SUB_ISSUE** | Plan phase task not represented in sub-issue (from sub-issue-fidelity) |
| **CONCERN_SCOPE_NARROWER** | Sub-issue body omits tasks within Plan phase's concern boundary (from concern-coverage) |
| **CONCERN_SCOPE_WIDER** | Sub-issue body includes tasks outside Plan phase's concern boundary (from concern-coverage) |
| **CONCERN_BOUNDARY_CROSSED** | Sub-issue body mixes tasks from multiple Plan phase concerns (from concern-coverage) |
| **ANTI-PROSE-DRIFT** | Rigid enumeration, tabular mapping, or fixed checklist where flowing prose is expected (from prose-structure) |

## Audit Findings Handling

After the audit session completes, findings are acted on per the auto-fix model: safe fixes are applied directly, conditional fixes are applied after safety checks, and ambiguous findings are flagged for review.

**Findings are NOT posted as GitHub comments.** Audit findings are analogous to linter output: auto-fixes are applied silently (like `ruff --fix`), and flagged findings are reported in the executive summary. The correct workflow is:

1. **Audit** → run subtasks, collect findings
2. **Classify** → assign each finding to auto-fix, conditional, or flag-for-review
3. **Act** → apply auto-fixes directly; apply conditional fixes after safety checks; leave flag-for-review findings for developer action
4. **Comment ONLY for substantive revisions** → if the combined auto-fixes and conditional fixes change requirements, phases, success criteria, or scope, post one revision comment following `issue-operations` skill `comment` task format. Non-substantive changes (STATUS markers, boilerplate additions, numbering fixes, trace links) get NO comment.
5. **Post executive summary to chat** → per the `Chat Executive Summary` section below

**When NO comment is posted:**
- Audit finds zero issues (all PASS) — move on, no comment
- Agent only makes non-substantive auto-fixes (STATUS updates, boilerplate, numbering, trace links, typo fixes) — no comment
- Flag-for-review findings exist but no substantive changes made — no comment (flagged in executive summary instead)

**When a comment IS posted:**
- Agent makes substantive spec changes (adding/removing phases, changing requirements, altering approach) — post one revision comment per `issue-operations` skill `comment` task

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
- Issue URL is constructed from session init values (`<GitOwner>`, `<GitRepo>`)

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

## Sub-Agent Tasks

### Execution Mode Table

| Task | Words | Mode |
|------|-------|------|
| `structure` | ~400 | inline |
| `content-quality` | ~500 | inline |
| `traceability` | ~300 | inline |
| `operational` | ~300 | inline |
| `fidelity` | ~600 | sub-agent |
| `concerns` | ~400 | inline |
| `operational-flow` | ~400 | inline |
| `determinism` | ~300 | inline |
| `error-recovery` | ~350 | inline |
| `principles` | ~350 | inline |
| `ground-truth` | ~500 | sub-agent |
| `sub-issue-fidelity` | ~350 | inline |
| `concern-coverage` | ~350 | inline |
| `prose-structure` | ~250 | inline |
| `fresh-start` | ~400 | inline |
| `completion` | ~200 | inline |

**Note:** Individual subtasks are lightweight. Sub-agent dispatch is recommended for the full audit (all subtasks per document type) when running 3+ subtasks together, not for individual subtasks.

### Dispatch Context Schema (Full Audit as Sub-Agent)

```yaml
source: {type: issue|file|url, identifier: <str>}
document_type: <auto|spec|plan|process-flow|runbook|checklist|reference-doc>
subtasks: [<task_name>]
session_vars:
  GitOwner: <from-session>
  GitRepo: <from-session>
  DevName: <from-session>
  DevEmail: <from-session>
  WorktreePath: <from-session>
```

### Result Contract (Full Audit)

```yaml
status: DONE | DONE_WITH_CONCERNS | OVERFLOW
task: spec-auditor
document_type: <str>
confidence: High | Medium | Low
changes_made: [{subtask: <str>, problem_class: <str>, fix: <str>, classification: auto-fix|conditional}]
findings_not_acted_on: [{subtask: <str>, problem_class: <str>, reason: <str>}]
issue_url: <url|null>
```

## Sub-Agent Spawning

This skill is a **heavy skill** — quality audits with all subtasks consume significant context. When the main agent needs a spec audit, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~1,278 words)
2. Main agent identifies which subtasks to run (baseline + conditional)
3. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use spec-auditor skill --issue N --task <subtask> with context: <session-context>")`
4. Sub-agent loads: this SKILL.md + relevant task file(s) + required guidelines
5. Sub-agent executes audit in isolation, returns findings as structured report
6. Main agent receives findings — no full audit content in main context

**Sub-agent context parameters:** Pass issue number, `<WorktreePath>`, `<GitOwner>`, `<GitRepo>` from session init. When `<WorktreePath>` is set, sub-agents MUST receive it and use it as the base directory for all file operations and git commands.

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `brainstorming` in Cross-References section | File exists at `.opencode/skills/brainstorming/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-creation` in Cross-References section | File exists at `.opencode/skills/spec-creation/SKILL.md` | MISSING-TRACEABILITY if missing |
| `writing-plans` in Cross-References section | File exists at `.opencode/skills/writing-plans/SKILL.md` | MISSING-TRACEABILITY if missing |
| `issue-review` in Cross-References section | File exists at `.opencode/skills/issue-review/SKILL.md` | MISSING-TRACEABILITY if missing |
| `programming-principles` in Cross-References section | File exists at `.opencode/skills/programming-principles/SKILL.md` | MISSING-TRACEABILITY if missing |
| `plan-fidelity-auditor` in delegated-from | File exists at `.opencode/skills/plan-fidelity-auditor/SKILL.md` | MISSING-TRACEABILITY if missing |
| `concern-separation-auditor` in delegated-from | File exists at `.opencode/skills/concern-separation-auditor/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `fresh-start` | File exists at `.opencode/skills/spec-auditor/tasks/fresh-start.md` | MISSING-TRACEABILITY if missing |
| Task table entry `structure` | File exists at `.opencode/skills/spec-auditor/tasks/structure.md` | MISSING-TRACEABILITY if missing |
| Task table entry `content-quality` | File exists at `.opencode/skills/spec-auditor/tasks/content-quality.md` | MISSING-TRACEABILITY if missing |
| Task table entry `traceability` | File exists at `.opencode/skills/spec-auditor/tasks/traceability.md` | MISSING-TRACEABILITY if missing |
| Task table entry `operational` | File exists at `.opencode/skills/spec-auditor/tasks/operational.md` | MISSING-TRACEABILITY if missing |
| Task table entry `fidelity` | File exists at `.opencode/skills/spec-auditor/tasks/fidelity.md` | MISSING-TRACEABILITY if missing |
| Task table entry `concerns` | File exists at `.opencode/skills/spec-auditor/tasks/concerns.md` | MISSING-TRACEABILITY if missing |
| Task table entry `operational-flow` | File exists at `.opencode/skills/spec-auditor/tasks/operational-flow.md` | MISSING-TRACEABILITY if missing |
| Task table entry `determinism` | File exists at `.opencode/skills/spec-auditor/tasks/determinism.md` | MISSING-TRACEABILITY if missing |
| Task table entry `error-recovery` | File exists at `.opencode/skills/spec-auditor/tasks/error-recovery.md` | MISSING-TRACEABILITY if missing |
| Task table entry `principles` | File exists at `.opencode/skills/spec-auditor/tasks/principles.md` | MISSING-TRACEABILITY if missing |
| Task table entry `ground-truth` | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| Task table entry `sub-issue-fidelity` | File exists at `.opencode/skills/spec-auditor/tasks/sub-issue-fidelity.md` | MISSING-TRACEABILITY if missing |
| Task table entry `concern-coverage` | File exists at `.opencode/skills/spec-auditor/tasks/concern-coverage.md` | MISSING-TRACEABILITY if missing |
| Task table entry `prose-structure` | File exists at `.opencode/skills/spec-auditor/tasks/prose-structure.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/spec-auditor/tasks/completion.md` | MISSING-TRACEABILITY if missing |
| Described behavior of `issue-review` | Matches actual SKILL.md: `audit` task delegates to spec-auditor | CONFLICTING if mismatched |
| Described behavior of `writing-plans` | Matches actual SKILL.md: `clean-room` task generates plans | CONFLICTING if mismatched |
| Described behavior of `programming-principles` | Matches actual SKILL.md: defines engineering principles | CONFLICTING if mismatched |
| `brainstorming` invocation in Invocation section | Skill has corresponding invocation entry | MISSING-TRACEABILITY if missing |
| `spec-creation` invocation context | Skill describes creation-time discipline for traceability | CONFLICTING if mismatched |

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

- Related skills: `brainstorming` (exploration), `spec-creation` (creation-time discipline for traceability and operational requirements), `writing-plans` (clean-room generation for fidelity subtask), `issue-review` (delegates to spec-auditor via audit task), `programming-principles` (authoritative principle definitions for principles subtask — this subtask checks compliance, that skill defines the principles), `verification-enforcement` (pre-generation verification gate that prevents the problems spec-auditor would find)
- Related guidelines: `000-critical-rules.md` (auditor enforcement), `140-planning-spec-creation.md`
- Label state machine: `141-planning-status-tracking.md §10` (add `needs-revision` when audit requires changes; replace with `needs-approval` on re-submission)
- Delegated from: `plan-fidelity-auditor` (now `fidelity` and `sub-issue-fidelity` subtasks), `concern-separation-auditor` (now `concerns` and `concern-coverage` subtasks)

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
| No principle compliance check | — | — | `principles` subtask (NEW) — baseline for all types |
| No ground-truth verification | — | — | `ground-truth` subtask (NEW) — baseline for all types |
| No executive summary | No executive summary | Chat executive summary mandatory | Chat executive summary mandatory, includes document type |
| Report format: Recommendation field | Report format: Recommendation field | Report format: Classification + Fix Action fields | Report format: Classification + Fix Action fields |
| Issue-only input | Issue-only input | Issue-only input | `--issue`, `--file`, `--url` input |
| No type detection | No type detection | No type detection | Signal-based autodetection + `--type` override |
| Spec-only auditing | Spec-only auditing | Spec-only auditing | Multi-type: spec, plan, process-flow, runbook, checklist, reference-doc |

Co-authored with AI: <AgentName> (<ModelId>)

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.

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