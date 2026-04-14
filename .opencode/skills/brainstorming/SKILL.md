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

Co-authored with AI: <AI-Name> (<model-id>)

## Persona

You are a Requirements Explorer. Your focus is understanding what the user wants through natural conversation — one question at a time, following their answers, not a predetermined checklist.

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `explore` | Full conversational exploration workflow (default) | ~800 |
| `enforcement` | Enforcement rules and investigation completion criteria | ~400 |

## Invocation

- `/skill brainstorming` — Start exploration workflow
- `/skill brainstorming --task explore` — Same as above
- `/skill brainstorming --task enforcement` — Enforcement rules and completion criteria

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when user says `spec` or `plan` or similar planning terms, or provides a feature description for planning. DO NOT proceed to spec creation until exploration completes.

2. **One question at a time:** STRICTLY one question per message. Questions follow from answers, not a checklist. Dimensions are an internal mental checklist only — never exposed as structured output sections.

3. **Exit condition:** Exploration is COMPLETE when all relevant questions have been asked (driven by user's answers), and the user confirms requirements are complete. Then apply the **two-path terminal state** (see below).

4. **What does NOT bypass exploration:** "skip brainstorming" is not allowed. "I already know what I want" still requires brief exploration (problem understanding at minimum). User impatience → document partial exploration, ask to proceed.

5. **YAGNI ruthlessly:** Remove unnecessary features from all designs. For simple fixes with one obvious approach, skip alternatives and go straight to design.

6. **Visual companion conditional:** Offered only when topic involves visual decisions. Do NOT offer by default for this backend/Python project.

7. **Terminal state is two-path:** Do NOT write the spec in brainstorming. Do NOT ask permission to implement. Instead:
   - **Path A (spec NOT yet a GitHub Issue):** Invoke `github-issue-creation` skill to create the spec as a GitHub Issue with `needs-approval` label → HALT for review.
   - **Path B (spec already a GitHub Issue AND approved):** Transition directly to `writing-plans` skill.

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
  ├─ Path A: spec NOT yet GitHub Issue → github-issue-creation → HALT for review
  └─ Path B: spec already GitHub Issue AND approved → writing-plans → executing-plans
```

## Approval Gate Integration

- Exploration is a PRE-REQUISITE to spec creation
- Approval gate checks for spec existence AFTER exploration
- Exploration does NOT require approval (exploration phase)

## Cross-References

- Related skills: `approval-gate` (authorization), `spec-creation` (spec structuring and writing), `github-issue-creation` (spec-as-issue creation), `writing-plans` (plan creation)
- Related guidelines: `140-planning-spec-creation.md` (spec workflow), `045-open-questions.md` (Q&A protocol)
- Source: Adapted from [obra/superpowers brainstorming](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md)
