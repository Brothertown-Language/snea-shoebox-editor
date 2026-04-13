# Task: context-passing

Migrated from `implementation-workflow` task context-passing.

## Purpose

Reference document for yield-back context patterns between subtasks in the divide-and-conquer orchestration chain.

## Entry Criteria

- Orchestration is in progress
- A subtask is about to be invoked and needs context

## Exit Criteria

- Correct context shape is passed to the next subtask

## Procedure

### What Pre-Work Needs FROM Authorization

```yaml
authorization: confirmed (bool)
issue_number: int
```

### What Implementation Needs FROM Pre-Work

```yaml
branch: string
working_tree_clean: bool
```

### What Review-Prep Needs FROM Implementation

```yaml
files_changed: list
commit_summary: string
implementation_status: success | failure
```

### What Verification Gate Needs FROM Implementation

```yaml
issue_number: int
phase: string
success_criteria: list
files_changed: list
```

### What Finishing Checklist Needs FROM Verification

```yaml
branch: string
verification_passed: true
implementation_complete: true
```

### What Chat Needs FROM Review-Prep

```yaml
compare_url: string (actionable link)
exec_summary: string (markdown, human-readable)
```

## Edge Cases

### Context Lost Between Steps

If a yield-back produces empty or missing fields:

1. HALT orchestration
2. Report which context field is missing
3. Wait for manual intervention

### Pre-Work Asks for Auth Again

Pre-work receives context from orchestrator — no re-authorization check needed. If pre-work prompts for auth, it received stale context. Re-invoke with fresh context from approval-gate.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)