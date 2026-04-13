---
name: executing-plans
description: Use when executing an approved plan step-by-step or moving through implementation gates sequentially. Triggers on: execute plan, next step, continue implementation, plan approved, start implementation.
type: technique
license: MIT
compatibility: opencode
---

# Skill: executing-plans

## Overview

Plan execution skill that dispatches to `divide-and-conquer/assemble-batch` for implementation. This skill is a thin dispatch layer — all implementation logic flows through the unified batch workflow.

**Every approval follows one path:** `executing-plans` → `divide-and-conquer/assemble-batch` → batch branch → pr-creation → one PR.

**There is no single-issue bypass.** Single issue = batch of one = one sub-agent.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `start` | Dispatch to divide-and-conquer/assemble-batch for implementation | ~200 |
| `step` | Legacy — redirects to divide-and-conquer/orchestrate | ~100 |
| `progress` | Legacy — redirects to divide-and-conquer/orchestrate | ~100 |
| `verify` | Redirects to verification-before-completion | ~100 |

## Invocation

- `/skill executing-plans` — Overview only
- `/skill executing-plans --task start` — Dispatch to divide-and-conquer/assemble-batch
- `/skill executing-plans --task step` — Redirects to divide-and-conquer/orchestrate
- `/skill executing-plans --task progress` — Redirects to divide-and-conquer/orchestrate
- `/skill executing-plans --task verify` — Redirects to verification-before-completion

## Operating Protocol

1. **Dispatch to divide-and-conquer:** The `start` task invokes `divide-and-conquer --task assemble-batch` which handles all implementation — single issue or batch — through the unified workflow.

2. **No direct implementation:** This skill does not implement directly. It dispatches.

3. **Single issue = batch of one:** There is no separate path for single issues. The `assemble-batch` task handles single-issue dispatch as the default code path.

## Dispatch Order

```
Plan approved (approval-gate)
  → executing-plans --task start
  → divide-and-conquer --task assemble-batch
  → verification-before-completion
  → finishing-a-development-branch
  → git-workflow/review-prep
```

## Cross-References

- Related skills: `divide-and-conquer` (implementation orchestration), `approval-gate` (authorization), `verification-before-completion` (evidence), `finishing-a-development-branch` (branch readiness), `git-workflow` (branch/PR/cleanup)

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)