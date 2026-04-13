---
name: writing-plans
description: Use when creating an implementation plan from an approved spec. Triggers on: write plan, create plan, implementation plan, plan spec, approved plan, plan creation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: writing-plans

## Overview

Plan creation workflow that transforms approved specs into actionable implementation plans using a hybrid structure: **phases** for sub-issue tracking and cross-phase visibility, **TDD steps** within each task for granular execution guidance. Every step is one action (2-5 minutes) with exact code and commands. Placeholders are forbidden in plans.

**Source attribution:** TDD step granularity, no-placeholders rule, plan document header, file structure section, and self-review checklist adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

## Tasks

| Task | Purpose | Words |
| -- | -- | -- |
| `create` | Create plan from approved spec | ~800 |
| `validate` | Check for placeholders and completeness | ~500 |
| `retroactive` | Create plan for existing spec | ~600 |
| `clean-room` | Generate independent plan from problem statement only | ~500 |

## Invocation

- `/skill writing-plans` — Overview only
- `/skill writing-plans --task create` — Create plan from current spec
- `/skill writing-plans --task validate` — Validate existing plan
- `/skill writing-plans --task retroactive` — Create plan for existing spec
- `/skill writing-plans --task clean-room` — Generate clean-room plan (for comparison by spec-auditor)

## Hybrid Structure: Phases + TDD Steps

Plans use **phases** (for sub-issue tracking) with **TDD step granularity** within each task:

```
Phase 1: [Concern Name]
  Task 1: [Component Name]
    Step 1: Write the failing test
    Step 2: Run test to verify it fails
    Step 3: Write minimal implementation
    Step 4: Run test to verify it passes
    Step 5: Commit
```

Phase-level sections are prose (agent decides content). Task-level steps are TDD-granular with exact code and commands.

## No-Placeholders Rule (CRITICAL)

Every step must contain actual content. These are **plan failures**: `TBD`, `TODO`, `[to be determined]`, `[needs investigation]`, `[placeholder]`, `[requires research]`, `implement later`, `fill in details`, `Add appropriate error handling`, `Add validation`, `Write tests for the above`, `Similar to Task N`, or steps describing what to do without showing how.

## Self-Review Checklist

After writing the complete plan, check:

1. **Spec coverage:** Can you point to a task for each spec requirement?
2. **Placeholder scan:** Search for red-flag patterns. Fix them.
3. **Type consistency:** Do types/signatures used in later tasks match earlier definitions?

## Operating Protocol

1. Read approved spec from GitHub Issue
2. Map file structure (all files to create/modify with responsibilities)
3. Plan phase structure by judgment (prose-driven)
4. Define tasks within each phase using TDD step structure
5. Write plan document header (Goal, Architecture, Tech Stack)
6. Create plan issue or return markdown
7. Self-review (coverage, placeholders, type consistency)
8. Validate (no placeholders, TDD structure, actionable steps)

## Enforcement

- No plan → CREATE plan (writing-plans skill)
- Plan exists but unapproved → HALT, wait for approval
- Plan approved but has placeholders → REJECT plan
- Plan approved but missing TDD steps → REJECT plan
- Plan approved and complete → PROCEED to implementation

## Cross-References

- Related skills: `brainstorming` (pre-spec), `approval-gate` (authorization), `executing-plans` (implementation), `spec-auditor` (fidelity subtask uses clean-room)
- Source: adapted from [obra/superpowers `writing-plans`](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)
