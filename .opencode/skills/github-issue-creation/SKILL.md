---
name: github-issue-creation
description: Use when creating a GitHub Issue or before any issue creation attempt. Triggers on: create issue, new issue, spec creation, submit issue, GitHub issue, file issue, bug report.
type: technique
license: MIT
compatibility: opencode
---

# Skill: github-issue-creation

## Overview

Issue Creation Enforcer ensuring all GitHub Issues follow spec-first workflow with validation, labels, and auditor integration. The agent MUST invoke this skill before any issue is created.

## Persona

You are an Issue Creation Enforcer. Your focus is ensuring all GitHub issue creation follows the spec-first workflow with proper validation, labeling, and auditor integration.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-creation` | Validate before creating issue (conflicts, superseded, supersede check) | ~240 |
| `creation` | Create issue with proper title, labels, byline | ~200 |
| `post-creation` | Invoke auditors, trigger plan creation for multi-task specs | ~180 |
| `single-task-check` | Determine if spec needs a plan issue (multi-task) or is single-task | ~160 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |

## Invocation

- `/skill github-issue-creation --task pre-creation` - BEFORE creating issue (validation)
- `/skill github-issue-creation --task creation` - Create issue with enforcement
- `/skill github-issue-creation --task post-creation` - After creation (auditors, sub-issues)
- `/skill github-issue-creation --task single-task-check` - Check if spec is single-task
- `/skill github-issue-creation --task completion` - Invoke when workflow halts at any point
- `/skill github-issue-creation` - Overview only

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (labels, auditors, sub-issues, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when:
   - Agent is about to create a GitHub Issue
   - DO NOT create issues via direct `github_issue_write` calls
   - ALWAYS route through this skill for validation

2. **Workflow sequence:**
   - Phase 1: `pre-creation` → Validate spec, check for conflicts/superseded
   - Phase 2: `single-task-check` → Determine if spec needs a plan issue
   - Phase 3: `creation` → Create issue with labels and byline
   - Phase 4: `post-creation` → Invoke auditors, trigger plan creation via writing-plans if multi-task

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
- Single-task spec (one implementation task, plan optional per agent intelligence)
- Multi-task spec (multiple phases, requires plan issue)

**Triggers plan creation** for multi-task specs via `writing-plans` skill. Plan creation handles sub-issue creation under the plan.

### Creation Time Enforcement

**Applies:**
- `needs-approval` label automatically
- Proper title format (`[SPEC]`, `[SPEC-FIX]`, `[Task: #N]`)
- Creation byline in issue body footer

### Post-Creation Audits

**Invokes:**
- `spec-auditor` as orchestrator (selects relevant subtasks: fresh-start, structure, content-quality, traceability, and optionally fidelity, concerns, operational)

## Interdependencies

| Skill | Purpose | Integration Point |
|-------|---------|-------------------|
| `spec-auditor` | Orchestrate spec quality audit (subtasks: fresh-start, structure, content-quality, traceability, fidelity, concerns, operational) | Run BEFORE approval |
| `approval-gate` | Enforce authorization | Run AFTER issue created |
| `github-comments` | Byline format | Use for substantive comments only |
| `writing-plans` | Plan issue creation | Invoke for multi-task specs after creation |

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
- Create sub-issues directly under spec (sub-issues go under plan)

### ✅ ALWAYS DO

- Invoke `pre-creation` task before creating issue
- Apply `needs-approval` label to new specs
- Add creation byline in issue body footer
- Invoke auditors before approval
- Check for superseding/conflicting issues
- For multi-task specs, invoke `writing-plans` for plan creation (not `github-sub-issues` directly)

## Task Dependencies

```
pre-creation → single-task-check → creation → post-creation
                                            ↓
                                     (if multi-task)
                                            ↓
                                      writing-plans skill
                                            ↓
                                      plan issue (with sub-issues under plan)
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

## GitHub MCP Required — No Fallback

**When GitHub MCP tools are NOT available, the agent MUST refuse planning work entirely.**

### NO FALLBACK TO LOCAL FILES

- **PROHIBITED**: Using `plans/SPEC-*.md` files as fallback when GitHub MCP is unavailable
- **PROHIBITED**: Creating local plan files when GitHub MCP is unavailable
- **PROHIBITED**: Proceeding with implementation without GitHub Issue tracking

### REQUIRED ACTION

If GitHub MCP is unavailable:
1. STOP immediately
2. Report: "GitHub MCP tools unavailable. Cannot create or track specs without GitHub Issues."
3. Wait for GitHub MCP to be restored before proceeding

**See `140-planning-spec-creation.md` → "GitHub MCP Required — No Fallback" for the complete rule.**

## Submodule Provenance Issues

Submodule provenance issues are created as part of the `git-workflow` provenance task, not through this skill's standard flow. See `git-workflow/tasks/provenance.md` for the complete implementation.

### Provenance Issue Creation Pathway

When the `git-workflow` provenance task creates an issue in a submodule repository:

| Aspect | Standard | Provenance |
| -- | -- | -- |
| Invocation | Via this skill | Via `git-workflow --task provenance` |
| Target repo | Parent repo (`GIT_OWNER`/`GIT_REPO`) | Submodule repo |
| Labels | `needs-approval` | None (provenance tracking is informational) |
| Title format | `[SPEC]`, `[SPEC-FIX]`, etc. | `Sync from <parent-repo>/<parent-branch>: ...` or `Release ...` |
| Body | Spec content | Provenance metadata (parent refs, tier info) |
| Byline | Required | Required |

### Key Differences

- **No pre-creation validation:** Provenance issues are created automatically during git workflow; they don't conflict with specs
- **No plan creation:** Provenance issues are standalone tracking records, not specs requiring implementation plans
- **No auditor invocation:** Provenance issues are informational records, not work items requiring quality audits
- **Three-tier fallback:** Provenance gracefully falls back through tiers without HALT

### Cross-Reference

For the provenance issue body format and tier-specific details, see `git-workflow/tasks/provenance.md`.

## Cross-References

- Related skills: `spec-auditor`, `approval-gate`, `github-comments`, `github-sub-issues`
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`
- Authorization classification: See `010-approval-gate.md` §Action Authorization Classification
- Related skill tasks: `writing-plans --task create` (plan creation for multi-task specs), `git-workflow --task cleanup` (post-merge closure), `git-workflow --task provenance` (submodule provenance tracking)