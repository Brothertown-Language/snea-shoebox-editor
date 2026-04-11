---
name: subagent-driven-development
description: Use when executing an approved implementation plan that benefits from task-level isolation or parallel work. Triggers on: subagent, dispatch task, implement plan tasks, task-by-task implementation, subagent development, parallel implementation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: subagent-driven-development

Execute an approved implementation plan by dispatching fresh subagents per task, with two-stage review after each: spec compliance review first, then code quality review.

**Source attribution:** This skill is adapted from [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development). The implementer, spec-reviewer, and code-quality-reviewer prompt patterns are adapted from the [original prompt templates](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development). The two-stage review workflow, model selection guidance, and implementer status handling are derived from the original skill.

## Why Subagents

Fresh subagent per task = no context pollution between tasks. You precisely craft instructions and context for each subagent. This preserves your own context for coordination work.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration

## When to Use This Skill vs Implementation-Workflow

| Situation | Use |
|-----------|-----|
| Plan with independent tasks, same session | `subagent-driven-development` |
| Plan with tightly coupled tasks | `executing-plans` or manual execution |
| Parallel session needed | `executing-plans` |
| Need fresh context per task | `subagent-driven-development` |
| Small single-task implementation | `implementation-workflow` |

## Pre-Implementation Gates (MANDATORY)

**Before dispatching any subagent, these gates MUST be satisfied:**

1. **approval-gate** — Authorization verified (`approved` or `go` received)
2. **git-workflow --task pre-work** — Branch created, working tree clean (includes Worktree Gate: feature branches MUST use `using-git-worktrees`)
3. **Plan exists** — Writing-plans output available with TDD tasks

**After all tasks complete, these gates are MANDATORY:**

4. **verification-before-completion --task verify** — Evidence collected for success criteria
5. **finishing-a-development-branch --task checklist** — Branch readiness verified
6. **git-workflow --task review-prep** — Push, URL, HALT

**These gates are NOT optional.** Skipping them is a CRITICAL GUIDELINE VIOLATION.

## Tasks

| Task | Purpose |
|------|---------|
| `implementer-prompt.md` | Dispatch implementer subagent |
| `spec-reviewer-prompt.md` | Dispatch spec compliance reviewer subagent |
| `code-quality-reviewer-prompt.md` | Dispatch code quality reviewer subagent |

## The Process

```
Read plan, extract all tasks with full text and context
    ↓
Create TodoWrite with all tasks
    ↓
For each task:
    ↓
    Dispatch implementer subagent (tasks/implementer-prompt.md)
        ↓ (if implementer asks questions → answer, re-dispatch)
        ↓ (implementer implements, tests, commits, self-reviews)
    ↓
    Dispatch spec reviewer subagent (tasks/spec-reviewer-prompt.md)
        ↓ (if spec compliance fails → implementer fixes → re-review)
    ↓
    Dispatch code quality reviewer subagent (tasks/code-quality-reviewer-prompt.md)
        ↓ (if quality fails → implementer fixes → re-review)
    ↓
    Mark task complete in TodoWrite
    ↓
After all tasks:
    ↓
    Dispatch final code reviewer for entire implementation
    ↓
    Invoke verification-before-completion --task verify (MANDATORY)
    ↓
    Invoke finishing-a-development-branch --task checklist (MANDATORY)
    ↓
    Invoke git-workflow --task review-prep (MANDATORY)
    ↓
    HALT (no PR without explicit "create a PR")
```

## Model Selection

Use the least powerful model that can handle each role to conserve cost and increase speed.

| Task Type | Model Level | Examples |
|-----------|-------------|----------|
| Mechanical implementation (1-2 files, clear spec) | Cheap/fast | Typo fixes, isolated functions |
| Integration (multi-file, pattern matching) | Standard | API integration, refactoring |
| Architecture, design, review | Most capable | System design, complex reviews |

**Task complexity signals:**
- Touches 1-2 files with a complete spec → cheap model
- Touches multiple files with integration concerns → standard model
- Requires design judgment or broad codebase understanding → most capable model

## Handling Implementer Status

Implementer subagents report one of four statuses:

| Status | Meaning | Action |
|--------|---------|--------|
| **DONE** | Work complete | Proceed to spec compliance review |
| **DONE_WITH_CONCERNS** | Work complete but flagged doubts | Read concerns. If about correctness/scope → address before review. If observations → note and proceed |
| **NEEDS_CONTEXT** | Missing information | Provide context and re-dispatch same model |
| **BLOCKED** | Cannot complete | Provide context and re-dispatch, or escalate model, or break task into smaller pieces |

**Never** ignore an escalation or force the same model to retry without changes.

## Branch Model

This project uses the `feature→dev→main` three-branch workflow:

- Feature branches (`spec/` or `feature/`) branch FROM `dev`
- Feature branches merge INTO `dev` via PR
- Releases merge from `dev` to `main` (human-triggered)
- Use `using-git-worktrees` skill for subagent isolation

## Integration with Repo Workflow Skills

| Phase | Skill | Purpose |
|-------|-------|---------|
| Pre-implementation | `approval-gate` | Verify authorization |
| Branch creation | `git-workflow --task pre-work` (includes Worktree Gate) | Create feature branch (ALWAYS via worktree) |
| Per-task | Implementer → spec review → code quality review loop | Execute tasks |
| Post-implementation | `verification-before-completion --task verify` | Evidence collection |
| Completion | `finishing-a-development-branch --task checklist` | Branch readiness |
| Review prep | `git-workflow --task review-prep` | Push, URL, HALT |

**Plans come from `writing-plans` skill output (not standalone).**

## Prompt Templates

- `tasks/implementer-prompt.md` — Dispatch implementer subagent
- `tasks/spec-reviewer-prompt.md` — Dispatch spec compliance reviewer subagent
- `tasks/code-quality-reviewer-prompt.md` — Dispatch code quality reviewer subagent

## Example Workflow

```
1. Read plan, extract 5 tasks with full text
2. Create TodoWrite with all 5 tasks

Task 1: Hook installation script
   → Dispatch implementer (cheap model, 1-2 files)
   → Implementer self-reviews, commits
   → Dispatch spec reviewer: ✅ compliant
   → Dispatch code quality reviewer: ✅ approved
   → Mark Task 1 complete

Task 2: Recovery modes (integration concerns)
   → Dispatch implementer (standard model)
   → Implementer: DONE_WITH_CONCERNS (noted file size)
   → Read concerns — observation only, proceed
   → Dispatch spec reviewer: ❌ missing progress reporting
   → Implementer fixes: adds progress reporting
   → Spec reviewer: ✅ compliant now
   → Dispatch code quality reviewer: ⚠️ magic number
   → Implementer fixes: extracts constant
   → Code reviewer: ✅ approved
   → Mark Task 2 complete

... (Tasks 3-5 similar)

After all tasks:
   → Dispatch final code reviewer (most capable model)
   → All requirements met, ready for merge
   → verification-before-completion --task verify (MANDATORY)
   → finishing-a-development-branch --task checklist (MANDATORY)
   → git-workflow --task review-prep (MANDATORY)
   → Report completion + HALT
```

## Red Flags

**Never:**
- Skip approval-gate before starting
- Skip git-workflow pre-work or worktree setup
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed review issues
- Start code quality review before spec compliance passes
- Dispatch multiple implementation subagents in parallel (conflicts)
- Make subagent read plan file (provide full text instead)
- Skip scene-setting context
- Ignore subagent questions
- Accept "close enough" on spec compliance
- Skip review loops
- Let implementer self-review replace actual review (both needed)
- Skip verification-before-completion after all tasks
- Skip finishing-a-development-branch checklist
- Skip review-prep before HALT
- Create PR without explicit "create a PR" instruction

**If reviewer finds issues:**
- Implementer (same subagent) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip re-review

**If subagent fails (BLOCKED or NEEDS_CONTEXT):**
- Provide context and re-dispatch
- Escalate to more capable model if needed
- Break task into smaller pieces if too large
- Don't try to fix manually (context pollution)

## Dispatch Table Integration

This skill integrates with the repo's mandatory workflow:

```
approval-gate (authorization)
    ↓
subagent-driven-development (this skill)
    → pre-work: git-workflow --task pre-work (includes Worktree Gate)
    → per-task: implementer → spec review → code quality review
    → post-implementation: verification-before-completion
    → completion: finishing-a-development-branch
    → review-prep: git-workflow
    ↓
Wait for "create a PR" (explicit instruction)
```

## Coexistence with Implementation-Workflow

- **`subagent-driven-development`**: For plans with independent tasks where fresh context per task is beneficial
- **`implementation-workflow`**: For sequential orchestration with yield-back context passing
- Both enforce the same mandatory post-implementation gates
- Both use `git-workflow` for git operations
- Choice depends on task independence and context isolation needs

Co-authored with AI: OpenCode (ollama-cloud/glm-5)