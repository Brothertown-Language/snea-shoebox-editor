---
name: implementation-quality
description: Pattern verification for file locations, code structure, environment, and data integrity. Invoked at implementation gates to prevent pattern violations.
license: MIT
compatibility: opencode
---

# Skill: implementation-quality

Pattern verification for file locations, code structure, environment, and data integrity. Invoke at workflow gates to catch violations before they reach production.

## When to Use

| Gate | Invocation |
|------|------------|
| Before creating ANY file | `/skill implementation-quality --task file-locations` |
| At implementation start | `/skill implementation-quality --task code-structure` (load once, reference continuously) |
| Before running commands | `/skill implementation-quality --task environment` |
| Before handling data | `/skill implementation-quality --task data-integrity` |
| **After implementation completes** | **MANDATORY: Automatically invoke review-prep workflow** (see `post-implementation` task) |

## Blast Radius

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

## Operating Protocol

### ⚠️ VERIFICATION STEPS (MANDATORY FIRST)

**Before ANY skill operation, verify:**

1. **Session Init Check:**
   - Has `ai_bin/session_init.py` run?
   - Store: `GIT_OWNER`, `GIT_REPO`, `DEV_NAME`, `DEV_EMAIL`
   - If NOT run → STOP, run session init FIRST

2. **Codebase Verification:**
   - Is codebase state current?
   - Run: `srclight_codebase_map` or `srclight_index_status`
   - Verify: No stale assumptions from previous sessions

3. **Issue Conflict Check:**
   - Query open `[SPEC]` issues for conflicts
   - Check for superseding/invalidating issues
   - If conflict found → HALT, report conflict

**Exemption Conditions:**
- file-locations: REQUIRES all checks (file creation)
- code-structure: EXEMPT from issue check (code pattern reference)
- environment: EXEMPT from issue check (runtime check)
- data-integrity: EXEMPT from issue check (data pattern check)

### Automatic Invocation

## Relationship to Guidelines

This skill references `085-engineering-approach.md` for pattern tables. The guideline remains the authoritative source; this skill provides task-level organization for selective loading.

## Cross-References

- `085-engineering-approach.md` - Pattern definitions (authoritative)
- `010-approval-gate.md` - Invocation gates
- `AGENTS.md` - Skills section reference