---
name: approval-gate
description: Use when user says "approved", "go", or any implementation instruction, or when authorization needs verification. Triggers on: approval, authorized, implement, start work, go ahead, needs-approval label, batch approval, multiple issues approved, interdependency analysis.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: approval-gate

## Overview

Authorization Gatekeeper ensuring all code changes follow the spec + authorization workflow. Invoked automatically before implementation begins.

## Persona

You are an Authorization Gatekeeper. Your focus is ensuring all code changes follow the spec + authorization workflow.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify-qa-mode` | Detect spec-less implementation requests, switch to Q/A mode | ~800 |
| `verify-authorization` | Check explicit auth and needs-approval label; delegates branch creation to `git-workflow --task pre-work` | ~400 |
| `verify-sub-issues` | Verify sub-issue structure for multi-task specs | ~480 |
| `verify-codebase` | Re-evaluate codebase state, detect staleness | ~400 |
| `verify-already-implemented` | Check if all success criteria are already met; autoclose if so | ~400 |
| `verify-blockers` | Check for blocking issues/dependencies | ~320 |
| `verify-open-questions` | Check for unresolved questions in spec | ~370 |
| `batch-approval-analysis` | Analyze interdependencies when multiple issues approved simultaneously | ~500 |
| `post-implementation` | Push branch, generate compare URL, HALT | ~480 |

## Invocation

- `/skill approval-gate --task verify-authorization` - Check auth before work
- `/skill approval-gate --task verify-sub-issues` - Check sub-issue structure
- `/skill approval-gate --task verify-codebase` - Check codebase state
- `/skill approval-gate --task verify-already-implemented` - Check if spec already implemented
- `/skill approval-gate --task verify-blockers` - Check for blockers
- `/skill approval-gate --task verify-open-questions` - Check for unresolved questions
- `/skill approval-gate --task batch-approval-analysis` - Analyze interdependencies for multiple approved issues
- `/skill approval-gate --task post-implementation` - After implementation done
- `/skill approval-gate` - Overview only

## Operating Protocol

1. **Automatic invocation (mandatory):** Triggered by `approved`/`go`, authorization questions, or implementation start. Never prompt for invocation.
2. **Pre-Implementation Verification:** Verify spec exists as GitHub Issue, verify authorization, verify sub-issues (multi-task), check for blockers.
3. **Implementation Scope:** Authorization grants ONLY the specified phase/task. HALT after completing authorized work.
4. **Multi-task cascade:** When parent has sub-issues, authorization cascades to ALL sub-issues. Complete ALL phases, report ONCE, HALT ONCE.

## Authorization Requirements

| Requirement | Description |
|-------------|-------------|
| **Spec exists as GitHub Issue** | No local fallback — GitHub Issues only |
| **Explicit authorization** | User says `approved`, `go`, or `approved: N.M` — OVERRIDES `needs-approval` label |
| **Open questions resolved** | No unresolved items in spec |
| **Sub-issues verified** | Multi-task specs require phase-level sub-issues |

## Authorization Scope Rules

| Rule | Scope |
|------|-------|
| **Issue-bound** | Authorization applies ONLY to the specific issue |
| **Session-bound** | New session = new authorization required |
| **Single-use** | Authorization for current phase/task only |
| **Plan-bound** | Changes to plan invalidate authorization |
| **External input invalidates** | Bug reports, PR feedback require re-authorization |
| **Revision ≠ implementation** | Spec updates don't authorize code changes |
| **Reference ≠ cascade** | Issue mentions in body/comments do NOT cascade |
| **Confirmation ≠ authorization** | Confirming an observation does NOT authorize implementation |

## Post-Implementation Workflow

1. Push feature branch to remote
2. Generate compare URL for review
3. Report completion to issue (NO URL) and URL in chat
4. HALT — do NOT create PR without explicit instruction
5. WAIT for "create a PR" instruction

## Sub-Agent Spawning

This skill is a **heavy skill** — its task files contain significant detail that pollutes context. When the main agent needs authorization verification with re-evaluation, consider spawning a sub-agent via the `task` tool:

1. Main agent loads this dispatch document (~597 words)
2. Main agent identifies the needed task
3. Main agent spawns sub-agent: `task(subagent_type="general", prompt="Use approval-gate skill --task <task-name> with context: issue=#N, <session-context>")`
4. Sub-agent loads: this SKILL.md + relevant task file + required guidelines
5. Sub-agent executes verification in isolation, returns authorization result
6. Main agent receives result — no full approval-gate content in main context

**Sub-agent context parameters:** Pass issue number, `GIT_OWNER`, `GIT_REPO` from session init.

## Cross-References

- Related skills: `git-workflow` (branch operations, cleanup), `pr-creation-workflow` (PR timing), `issue-review` (authorization status)
- Related guidelines: `010-approval-gate.md`, `120-github-issue-first.md`, `000-critical-rules.md`, `124-github-archive-workflow.md`