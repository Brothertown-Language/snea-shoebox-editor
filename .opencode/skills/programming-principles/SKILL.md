---
name: programming-principles
description: Use when designing functions, classes, or modules; writing or reviewing implementation code; making architecture decisions; or evaluating tradeoffs between competing approaches. Triggers on: design, implement, refactor, architecture, tradeoff, principle, KISS, DRY, SRP, coupling, cohesion, YAGNI.
type: pattern
license: MIT
compatibility: opencode
---

# Skill: programming-principles

## Overview

20 engineering principles as the **single authoritative source** for design judgment and enforcement rules. Each principle includes both the hard rule (where applicable) and the judgment context (when to apply strongly, when to relax). Other files reference HERE — never the other direction.

**Core ethic: Intelligent judgment, not dogmatism.** Principles are tools, not commandments. Apply them where they improve outcomes; relax them where the cost exceeds the benefit — but always document the tradeoff.

## Relationship to Code Standards

| This Skill | `080-code-standards.md` |
| -- | -- |
| Master source for all 20 principles (rules + judgment) | Project-specific conventions (pathlib, f-strings, no re-exports, numbering, etc.) |
| Both enforcement AND design judgment | Principles REMOVED from here; cross-reference note points to this skill |
| Applies to any codebase | Applies to this repo only |

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `principles` | Complete reference for all 20 principles with enforcement levels, apply/relax context, and tradeoff notes | ~2,200 |
| `application-guide` | How to apply principles during design, implementation, and review; context prioritization table and red flags | ~400 |

## Invocation

This skill is **reference-driven**, not dispatch-triggered. Load via `/skill programming-principles` when the agent needs design judgment.

- `/skill programming-principles` - Load this dispatch document for overview and task index
- `/skill programming-principles --task principles` - Full reference for all 20 principles
- `/skill programming-principles --task application-guide` - Application guide with context table and red flags

| When to Invoke | Example Trigger |
| -- | -- |
| During design decisions | "Which approach has better cohesion?" |
| Before implementation | "Am I violating any principles here?" |
| During code review | "This violates CQS — is the tradeoff documented?" |
| When evaluating alternatives | "Option A has lower coupling but Option B is simpler" |

## Operating Protocol

1. **Reference-first:** Load `--task principles` when you need the full definition of a specific principle
2. **Apply judgment, not dogma:** Principles have apply-strongly and relax-when contexts — use them
3. **Document tradeoffs:** When deliberately relaxing a principle, use the tradeoff note format from `application-guide`
4. **Context-prioritize:** Not all 20 principles matter equally — use the context table in `application-guide`
5. **Enforcement levels differ:** Some principles are enforced (KISS, DRY, SRP, Fail Fast, Defensive Programming), others are design guidance only
6. **Cross-references matter:** Check `080-code-standards.md` for project-specific conventions that reference these principles
7. **Red flags trigger principle checks:** Use the red flags table in `application-guide` when something feels off but you're not sure which principle applies

## Cross-References

| Reference | Relationship |
| -- | -- |
| `080-code-standards.md` | Project-specific conventions (this skill owns principles, that guideline owns conventions) |
| `engineering-approach` skill | Workflow discipline — when to design, verify, communicate (this skill owns *what* principles to apply, that skill owns *when* in the process) |
| `code-size-enforcement` skill | Size limits — SRP and "No Monoliths" have hard limits there |
| `concern-separation-auditor` skill | Structural concern separation — this skill provides the design judgment perspective for SoC and Blast Radius |
| `spec-auditor` skill | Auditing orchestrator — `principles` subtask checks specs against these 20 principles |
| `plan-fidelity-auditor` skill | Plan fidelity — this skill provides design judgment for approach difference findings |
| `issue-review` skill | Issue review — delegates to spec-auditor which uses `principles` subtask |
