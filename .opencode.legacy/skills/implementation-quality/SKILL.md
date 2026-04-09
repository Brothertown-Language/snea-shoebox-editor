---
name: implementation-quality
description: Pattern verification for file locations, code structure, environment, and data integrity. Invoked at implementation gates to prevent pattern violations.
license: MIT
compatibility: opencode
---

# Skill: implementation-quality

Pattern verification for file locations, code structure, environment, and data integrity. Invoke at workflow gates to catch violations before they reach production.

## When to Invoke

**See `AGENTS.md` → "Skill Invocation Guidance" for the complete trigger table.**

This skill is invoked at these workflow triggers:

| Workflow Trigger | Invocation | Purpose |
|------------------|------------|---------|
| Before creating ANY file | `/skill implementation-quality --task file-locations` | Verify file location patterns |
| At implementation start | `/skill implementation-quality --task code-structure` | Verify code structure patterns |
| Before running commands | `/skill implementation-quality --task environment` | Verify environment patterns |
| Before handling data | `/skill implementation-quality --task data-integrity` | Verify data integrity patterns |
| After implementation completes | Automatic: review-prep workflow | Post-implementation verification |

## This Skill's Tasks

| Task | Blast Radius | When to Invoke |
|------|--------------|----------------|
| `file-locations` | HIGH | Before every file creation |
| `code-structure` | MEDIUM | Once at implementation start |
| `environment` | LOW | Before running commands |
| `data-integrity` | HIGH | Before data operations |

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `file-locations` | WHERE files go - pattern verification | ~60 |
| `code-structure` | HOW code is organized - pattern verification | ~70 |
| `environment` | WHAT runtime - pattern verification | ~40 |
| `data-integrity` | HOW data is handled - pattern verification | ~50 |
| `post-implementation` | **MANDATORY review-prep after implementation** | ~80 |

## Invocation

**MANDATORY AUTOMATIC invocation:**

| Trigger | Task | Why |
|---------|------|-----|
| After implementation completes | `post-implementation` | **ZERO TOLERANCE** - must invoke review-prep workflow |

**Selective loading by blast radius:**

- `/skill implementation-quality --task file-locations` - Before creating files
- `/skill implementation-quality --task code-structure` - Once at implementation start
- `/skill implementation-quality --task environment` - Before running commands
- `/skill implementation-quality --task data-integrity` - Before data operations

**Note:** The `post-implementation` task is automatically invoked after every implementation. Do NOT skip it.

## Workflow

1. **Automatic invocation:** Load at workflow gates (see `010-approval-gate.md`)
2. **Selective loading:** Load only the task needed for current concern
3. **Pattern reference:** Use tables for fast lookup during implementation
4. **Violation recovery:** Follow correction tables when violations detected

## Relationship to Guidelines

This skill references `085-engineering-approach.md` for pattern tables. The guideline remains the authoritative source; this skill provides task-level organization for selective loading.

## Cross-References

- `085-engineering-approach.md` - Pattern definitions (authoritative)
- `010-approval-gate.md` - Invocation gates
- `AGENTS.md` - Skills section reference