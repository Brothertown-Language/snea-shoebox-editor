______________________________________________________________________

## name: subagent-driven-development description: Use when executing an approved implementation plan that benefits from task-level isolation or parallel work. Triggers on: subagent, dispatch task, implement plan tasks, task-by-task implementation, subagent development, parallel implementation, batch execution plan. type: technique license: MIT compatibility: opencode

# Skill: subagent-driven-development

## Overview

Execute an approved implementation plan by dispatching fresh subagents per task, with two-stage review after each: spec compliance review first, then code quality review. Fresh subagent per task = no context pollution between tasks. Uses branch-per-issue with merge-based dependency resolution for batch execution.

**Source attribution:** Adapted from [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development).

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `implementer-prompt` | Dispatch implementer subagent | ~300 |
| `spec-reviewer-prompt` | Dispatch spec compliance reviewer subagent | ~300 |
| `code-quality-reviewer-prompt` | Dispatch code quality reviewer subagent | ~300 |
| `batch-execution` | Accept batch execution plans with branch-per-issue and merge-based dependency resolution | ~500 |

## Invocation

- `/skill subagent-driven-development` - Overview only
- `/skill subagent-driven-development --task batch-execution` - For batch approval plans

## When to Use This Skill vs Implementation-Workflow

| Situation | Use |
|-----------|-----|
| Plan with independent tasks, same session | `subagent-driven-development` |
| Plan with tightly coupled tasks | `executing-plans` or manual execution |
| Need fresh context per task | `subagent-driven-development` |
| Dependencies between tasks (must-precede) | `subagent-driven-development` with merge-based dependency resolution |
| Any batch implementation | `subagent-driven-development` (always batch mode) |

## The Process

```
Read plan, extract all tasks with full text and context
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
After all tasks:
    ↓
    verification-before-completion --task verify (MANDATORY)
    ↓
    finishing-a-development-branch --task checklist (MANDATORY)
    ↓
    git-workflow --task review-prep (MANDATORY)
    ↓
    HALT (no PR without explicit "create a PR")
```

## Pre-Implementation Gates (MANDATORY)

1. **approval-gate** — Authorization verified
1. **git-workflow --task pre-work** — Branch created via worktree
1. **Plan exists** — Writing-plans output available

**After all tasks complete, these gates are MANDATORY:**

4. **verification-before-completion --task verify**
1. **finishing-a-development-branch --task checklist**
1. **git-workflow --task review-prep**

## Sub-Agent Dispatch Context

Each sub-agent MUST receive complete worktree context:

```yaml
issue: <number>
branch: "spec/<short-name>"
worktree_path: ".worktrees/spec-<short-name>"
dev_base_hash: "<7-char-sha>"
prior_context: "<AI-composed intent and context>"
dependency_branches: ["spec/<prior-branch>"]
env_vars:
  WORKTREE_PATH: ".worktrees/spec-<short-name>"
  BRANCH_NAME: "spec/<short-name>"
  GIT_OWNER: "<from-session>"
  GIT_REPO: "<from-session>"
  DEV_NAME: "<from-session>"
  DEV_EMAIL: "<from-session>"
```

**Invariants:** `WORKTREE_PATH` is MANDATORY — no exceptions. If empty: FATAL ERROR → FLAG DEV → HALT.

**`prior_context`** replaces the old `prior_results` field. It is AI-composed prose focused on **intent and context** (why decisions were made, what assumptions hold, what interfaces matter) — NOT a change summary (what changed is in git).

## Handling Implementer Status

| Status | Meaning | Action |
|--------|---------|--------|
| **DONE** | Work complete | Proceed to spec compliance review |
| **DONE_WITH_CONCERNS** | Work complete but flagged doubts | Read concerns, address if about correctness/scope |
| **NEEDS_CONTEXT** | Missing information | Provide context and re-dispatch same model |
| **BLOCKED** | Cannot complete | Provide context, escalate model, or break task smaller |

**Never** ignore an escalation or force the same model to retry without changes.

## Red Flags

Never skip approval-gate, never skip reviews, never dispatch multiple implementation subagents in parallel, never accept "close enough" on spec compliance, never skip verification-before-completion, never skip review-prep before HALT, never create PR without explicit instruction.

## Sub-Agent Spawning

This skill is a **heavy skill** — task dispatching and orchestration can run in isolation. When the main agent needs to dispatch implementation tasks to sub-agents, consider spawning via the `task` tool:

1. Main agent loads this dispatch document (~558 words)
1. Main agent identifies which tasks to dispatch and their dependencies
1. Main agent spawns sub-agents: `task(subagent_type="general", prompt="Use subagent-driven-development skill --task <task-name> with context: <session-context>")`
1. Sub-agent loads: this SKILL.md + relevant task files + required guidelines
1. Sub-agent dispatches implementation tasks to further sub-agents or executes directly
1. Main agent receives aggregated result — no orchestration detail in main context

**Sub-agent context parameters:** Pass all session init values plus issue-specific context.

## Cross-References

- Related skills: `approval-gate` (authorization), `git-workflow` (git ops), `implementation-workflow` (alternative orchestration), `verification-before-completion` (evidence), `finishing-a-development-branch` (branch readiness), `using-git-worktrees` (worktree creation with BASE_BRANCH)

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)
