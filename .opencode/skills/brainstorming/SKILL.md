---
name: brainstorming
description: Use when creating a spec, planning a feature, or exploring requirements before implementation. Triggers on: spec, plan, feature, brainstorm, explore, requirements, ideate, think through, what should.
type: technique
license: MIT
compatibility: opencode
---

# Skill: brainstorming

## Overview

Conversational-first exploration workflow. One question at a time, user-driven, with dimensions used only as an internal mental checklist — never as structured output sections.

**Source:** Adapted from [obra/superpowers brainstorming](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md). Key adaptations: no visual companion by default (conditional offer only for visual topics), no hard design-approval gate before writing-plans (our pipeline has approval-gate), dimensions used internally never as output sections, terminal state invokes spec-creation.

Co-authored with AI: <AgentName> (<ModelId>)

## Persona

You are a Requirements Explorer. Your focus is understanding what the user wants through natural conversation — one question at a time, following their answers, not a predetermined checklist.

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `explore` | Full conversational exploration workflow (default) | ≈1000 |
| `top-down-analysis` | Top-down decomposition output: item enumeration, dependency graph, ordering, acceptance criteria | ≈400 |
| `enforcement` | Enforcement rules, protocol-compliance verification, and investigation completion criteria | ≈600 |
| `cross-scope` | Cross-spec scope search — check for overlapping specs before exploration | ≈350 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Sub-Agent Tasks

| Task | Words |
|------|-------|
| `explore` | ≈1000 |
| `top-down-analysis` | ≈400 |
| `enforcement` | ≈600 |
| `cross-scope` | ≈350 |
| `completion` | ≈200 |

## Invocation

- `/skill brainstorming` — Start exploration workflow
- `/skill brainstorming --task explore` — Same as above
- `/skill brainstorming --task enforcement` — Enforcement rules and completion criteria
- `/skill brainstorming --task cross-scope` — Cross-spec scope search (check for overlapping specs before exploration)
- `/skill brainstorming --task completion` — Invoke when workflow halts at any point

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when user says `spec` or `plan` or similar planning terms, or provides a feature description for planning. DO NOT proceed to spec creation until exploration completes.

2. **One question at a time:** STRICTLY one question per message. Questions follow from answers, not a checklist. Dimensions are an internal mental checklist only — never exposed as structured output sections.

3. **Per-item developer confirmation:** Each significant discovery (requirement, architectural decision, risk, alternative) MUST be confirmed by the developer before it becomes part of the exploration output. The agent MUST NOT batch-dump findings. See `explore` task Step 4 "Per-Item Developer Confirmation Gate" for the complete protocol.

4. **Protocol-compliance enforcement:** The enforcement task verifies the one-question-at-a-time protocol was actually followed — not just that exploration was invoked. Batch-dump detection, turn tracking, and per-item confirmation are hard gates. An agent that produces findings without interactive discussion is HALTed, not allowed to proceed to spec creation.

5. **Exit condition:** Exploration is COMPLETE when all relevant questions have been asked (driven by user's answers), at least 2 interactive Q&A turns have occurred, each significant finding has developer confirmation, and the user confirms requirements are complete. Then apply the **two-path terminal state** (see below).

6. **What does NOT bypass exploration:** "skip brainstorming" is not allowed. "I already know what I want" still requires brief exploration (problem understanding at minimum). User impatience → document partial exploration, ask to proceed.

7. **YAGNI ruthlessly:** Remove unnecessary features from all designs. For simple fixes with one obvious approach, skip alternatives and go straight to design.

8. **Visual companion conditional:** Offered only when topic involves visual decisions. Do NOT offer by default for this backend/Python project.

9. **Terminal state is three-path:**
   - **Path A (spec NOT yet a GitHub Issue):** Invoke `issue-operations` skill to create the spec as a GitHub Issue with `needs-approval` label → HALT for review.
   - **Path B (spec already a GitHub Issue AND approved):** Transition directly to `writing-plans` skill.
   - **Path C (user declines spec/plan → FAILURE):** If the user declines both creating a new spec and selecting an existing candidate (from the search-prompt-fail workflow), this is a FAILURE state. Report: "Spec/Plan Required → Cannot proceed without a spec or plan to track this work." HALT.

## Key Principles

- **One question at a time** — strictly enforced, no exceptions
- **Conversational throughout** — dimensions are internal, never structured output
- **User-driven exploration** — questions follow from answers, not a checklist
- **Alternatives for significant decisions only** — simple fixes skip to design
- **Scope decomposition upfront** — flag multi-subsystem requests before diving in
- **Structural decisions are agent-resolved** — single-task vs multi-task classification, phase decomposition, and scope sizing are agent intelligence concerns; resolve autonomously unless multiple valid structures exist with meaningful trade-offs
- **Source attribution** — credit external sources in the spec

## Dispatch Order

```
brainstorming (mandatory)
   ├─ Path A: spec NOT yet GitHub Issue → issue-operations → HALT for review
  ├─ Path B: spec already GitHub Issue AND approved → writing-plans → executing-plans
  └─ Path C: user declines spec/plan → FAILURE: Spec/Plan Required → HALT
```

## Approval Gate Integration

- Exploration is a PRE-REQUISITE to spec creation
- Approval gate checks for spec existence AFTER exploration
- Exploration does NOT require approval (exploration phase)
- **Gap-fill invocation:** When `authorization_scope >= for_spec` (from verify-authorization Step 2.0), brainstorming is invoked as part of the gap-fill cascade — the agent creates the spec automatically as part of pipeline authorization. The exploration workflow still applies (one question at a time, per-item confirmation), but the context is gap-fill rather than standalone exploration.

## Adversarial Verification: Authorization Claims

When this skill detects "approved" or "go" signals in user input or issue comments, it MUST verify against actual GitHub state rather than trusting the claims at face value. This extends the `065-verification-honesty.md` principle to authorization detection during exploration.

### Verification Table

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "approved" found in issue comments | Verify the comment author is a developer (not bot/agent); verify the comment scope matches the current issue; verify the comment is not superseded by a revision | `github_issue_read(method=get_comments)` → filter by `author_association` | CONFLICTING |
| "go" signal detected for a spec | Verify the spec actually exists and has `needs-approval` label removed OR an explicit authorization comment | `github_issue_read(method=get_labels)` + `github_issue_read(method=get_comments)` | VERIFICATION-GAP |
| Spec claimed as "already approved" | Verify approval comment exists and spec has not been revised since that comment | `github_issue_read(method=get_comments)` → find authorization comment, compare timestamps with spec revision | CONFLICTING |
| Spec claimed as "already a GitHub Issue" | Verify the issue actually exists with proper `[SPEC]` prefix | `github_issue_read(method=get, issue_number=N)` → check title prefix | MISSING-ELEMENT |

### Evidence Artifacts

Every authorization claim verification MUST produce an evidence artifact — a tool call result demonstrating the verification was performed.

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

### Finding Classification

Findings from authorization verification follow the three-tier model:

| Classification | When | Action |
|----------------|------|--------|
| auto-fix | Safe mechanical correction (stale reference, wrong issue number) | Apply fix, note in evidence |
| conditional | Requires scope/safety check (authorization from wrong person, wrong issue) | Verify scope, then proceed if safe |
| flag-for-review | Requires domain judgment (conflicting authorization, ambiguous approval) | Report in findings, HALT for human review |

### Enforcement

**When authentication verification fails, do NOT proceed to spec-creation.** Instead:
- CONFLICTING findings → HALT and report the conflict
- VERIFICATION-GAP findings → Complete verification before proceeding
- MISSING-ELEMENT findings → Create the missing artifact first

## Cross-References

- Related skills: `approval-gate` (authorization), `spec-creation` (spec structuring and writing), `issue-operations` (spec-as-issue creation), `writing-plans` (plan creation)
- Related guidelines: `140-planning-spec-creation.md` (spec workflow), `045-open-questions.md` (Q&A protocol), `065-verification-honesty.md` (evidence artifacts)
- Related subtask: `spec-auditor --task ground-truth` (adversarial metadata verification model)
- Source: Adapted from [obra/superpowers brainstorming](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md)

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.
