---
name: github-issue-creation
description: Issue Creation Enforcer ensuring all GitHub Issues follow spec-first workflow with validation, labels, and auditor integration. Invoked automatically before any issue is created.
license: MIT
compatibility: opencode
---

# Skill: github-issue-creation

## Overview

Issue Creation Enforcer ensuring all GitHub Issues follow spec-first workflow with validation, labels, and auditor integration. Invoked automatically before any issue is created.

## Persona

You are an Issue Creation Enforcer. Your focus is ensuring all GitHub issue creation follows the spec-first workflow with proper validation, labeling, and auditor integration.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-creation` | Validate before creating issue (conflicts, superseded, supersede check) | ~240 |
| `creation` | Create issue with proper title, labels, byline | ~200 |
| `post-creation` | Invoke auditors, create sub-issues for multi-task specs | ~180 |
| `single-task-check` | Determine if spec needs sub-issues or is single-task | ~160 |

## Invocation

- `/skill github-issue-creation --task pre-creation` - BEFORE creating issue (validation)
- `/skill github-issue-creation --task creation` - Create issue with enforcement
- `/skill github-issue-creation --task post-creation` - After creation (auditors, sub-issues)
- `/skill github-issue-creation --task single-task-check` - Check if spec is single-task
- `/skill github-issue-creation` - Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is invoked when:
   - Agent is about to create a GitHub Issue
   - DO NOT create issues via direct `github_issue_write` calls
   - ALWAYS route through this skill for validation

2. **Workflow sequence:**
   - Phase 1: `pre-creation` → Validate spec, check for conflicts/superseded
   - Phase 2: `single-task-check` → Determine if spec needs sub-issues
   - Phase 3: `creation` → Create issue with labels and byline
   - Phase 4: `post-creation` → Invoke auditors, create sub-issues if multi-task

## What This Skill Does

### Pre-Creation Validation

**Prevents:**
- Creating specs that conflict with existing open specs
- Creating specs that are superseded by newer issues
- Creating specs with missing essential sections

**Checks:**
- Superseded issues (later issues that might invalidate this spec)
- Conflicting specs (overlapping objectives)
- Spec template completeness

### Single-Task vs Multi-Task Detection

**Determines:**
- Single-task spec (one implementation task, no sub-issues needed)
- Multi-task spec (multiple phases, requires sub-issues)

**Auto-creates sub-issues** for multi-task specs via `github-sub-issues` skill.

### Creation Time Enforcement

**Applies:**
- `needs-approval` label automatically
- Proper title format (`[SPEC]`, `[SPEC-FIX]`, `[Task: #N]`)
- Creation byline in initial comment

### Post-Creation Audits

**Invokes:**
- `concern-separation-auditor` for phase structure validation
- `spec-auditor` for spec quality validation

## Interdependencies

| Skill | Purpose | Integration Point |
|-------|---------|-------------------|
| `concern-separation-auditor` | Validate phase structure | Run BEFORE approval |
| `spec-auditor` | Validate spec quality | Run BEFORE approval |
| `approval-gate` | Enforce authorization | Run AFTER issue created |
| `github-comments` | Byline format | Use for creation comment |
| `github-sub-issues` | Sub-issue creation | Invoke for multi-task specs |

## When to Invoke

| Trigger | Task |
|---------|------|
| Creating new `[SPEC]` issue | `pre-creation` → `single-task-check` → `creation` → `post-creation` |
| Creating new `[Task]` issue | `creation` (skip validation) |
| Agent about to call `github_issue_write` | STOP → invoke this skill instead |

## Critical Rules

### 🚫 NEVER DO

- Create issues via direct `github_issue_write` calls (bypasses validation)
- Skip `needs-approval` label for new specs
- Create sub-issues for single-task specs
- Skip auditor invocation for multi-task specs
- Create issues with conflicting/overlapping objectives

### ✅ ALWAYS DO

- Invoke `pre-creation` task before creating issue
- Apply `needs-approval` label to new specs
- Add creation byline in initial comment
- Invoke auditors before approval
- Check for superseding/conflicting issues

## Task Dependencies

```
pre-creation → single-task-check → creation → post-creation
                                           ↓
                                    (if multi-task)
                                           ↓
                                     github-sub-issues skill
```

## Enforcement

**This skill is MANDATORY for all issue creation.**

Direct `github_issue_write` calls bypassing this skill are a CRITICAL GUIDELINE VIOLATION.

When creating a new issue:
1. STOP before calling `github_issue_write`
2. Invoke `/skill github-issue-creation --task pre-creation`
3. Follow validation results (HALT if conflicts)
4. Invoke `/skill github-issue-creation --task creation`
5. Invoke `/skill github-issue-creation --task post-creation`

## Cross-References

- Related skills: `concern-separation-auditor`, `spec-auditor`, `approval-gate`, `github-comments`, `github-sub-issues`
- Related guidelines: `010-approval-gate.md`, `120-github-issue-first.md`, `124-github-archive-workflow.md`