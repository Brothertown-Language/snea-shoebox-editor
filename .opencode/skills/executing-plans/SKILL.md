---
name: executing-plans
description: Use when executing an approved plan step-by-step or moving through implementation gates sequentially. Triggers on: execute plan, next step, continue implementation, plan approved, start implementation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: executing-plans

## Overview

Plan execution workflow that implements approved plans step-by-step with verification at each stage. This skill ensures systematic implementation, evidence collection, and quality gates.

**Source Attribution:** Adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are an Implementation Executor. Your focus is executing approved plans systematically, collecting evidence, and maintaining progress tracking.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `start` | Begin plan execution, verify prerequisites | ~300 |
| `step` | Execute single step, collect evidence | ~500 |
| `progress` | Report current progress | ~400 |
| `verify` | Run verification for current step | ~350 |

## Invocation

- `/skill executing-plans` — Overview only
- `/skill executing-plans --task start` — Begin execution
- `/skill executing-plans --task step` — Execute next step
- `/skill executing-plans --task progress` — Show progress
- `/skill executing-plans --task verify` — Verify current step

## Operating Protocol

1. **Automatic invocation (mandatory):** Auto-invoked when plan receives explicit approval (`approved: plan`), user says `execute plan` or `start implementation`, or after writing-plans creates approved plan. DO NOT skip steps or proceed without verification.

2. **Step-by-Step Execution:** Execute ONE step at a time. Collect evidence for each step. Verify before marking complete. HALT after each step completion.

3. **Progress Tracking:** Update plan issue with step status. Post progress comments with evidence. Mark steps as ☑ when verified complete.

4. **Exit conditions:** Execution HALTS when: current step complete → HALT and wait for user; all steps complete → transition to verification; user says `next step` → execute next step.

5. **Evidence is mandatory:** No step is complete without verifiable evidence. "Trust me" is not evidence. Placeholders ("TBD", "TODO") are not evidence.

## Dispatch Order

```
writing-plans (approved) → approval-gate (plan) → executing-plans → verification-before-completion
```

## Integration

### GitBucket Platform Adaptations

- Post progress comments to plan issue
- Update STATUS markers in issue body
- Link evidence to plan via comments

### Git-Workflow Integration

- Feature branch created by git-workflow
- Commits pushed after each step
- PR created after all steps complete (by user instruction only)

## Cross-References

- Related skills: `writing-plans` (plan creation), `verification-before-completion` (final verification), `git-workflow` (branch/PR), `subagent-driven-development` (alternative: dispatch subagents per task)
- Related guidelines: `142-planning-archive-workflow.md` (plan structure), `000-critical-rules.md` (evidence requirements)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> (branch: newsrx). Key adaptations: integration with git-workflow skill for branch management, GitBucket platform support, dispatch table integration, structured evidence collection and verification gates.