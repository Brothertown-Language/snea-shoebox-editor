# Work State File Schema — Chain-of-Responsibility Extension

## Purpose

Define the work state file schema extension for chain-of-responsibility orchestration. Each atomic task in the `verify-authorization/`, `pre-impl/`, and `screen/` chains writes results as a dedicated section in the work state file (`.opencode/tmp/work-<timestamp>.md`).

## Header Section

```yaml
## chain-context
authorization_scope: <scope_value>
halt_at: <pipeline_stage>
pr_strategy: stacked | individual | none
issue_numbers: [<N>]
created_at: <ISO-8601>
```

## Per-Task Result Section

Each atomic task creates a `## <section-name>` heading. The section body is YAML-structured:

```yaml
## <section-name>
inputs_from: [<section-name> | null]
status: pending | in_progress | done | failed | skipped
started_at: <ISO-8601 | null>
completed_at: <ISO-8601 | null>
result: <YAML-structured task output>
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `inputs_from` | Yes | List of section names this task reads from. `[]` for first task in chain. |
| `status` | Yes | Current execution status. Updated by the task on start/completion. |
| `started_at` | Yes | ISO-8601 timestamp when task begins; `null` if pending. |
| `completed_at` | Yes | ISO-8601 timestamp when task finishes; `null` if not done. |
| `result` | Yes | Task-specific YAML output. Schema varies per task. |

### Section Names

| Chain | Section Names |
|-------|---------------|
| `verify-authorization/` | `scope-auto-resolve`, `item-decomposition-check`, `sc-traceability-check`, `sub-issue-verification`, `spec-to-plan-cascade`, `gap-fill-cascade`, `auto-dispatch` |
| `pre-impl/` | `collect-screening-results`, `reconcile-status`, `build-dependency-graph`, `check-cross-spec-overlap`, `write-work-state`, `yield-to-assemble-work` |
| `screen/` | `screen-gate1-<issue_number>`, `screen-gate2-<issue_number>` |

## Constraints

- Each section appears at most once per work state file (except `screen-gate1-`/`screen-gate2-` which are per-issue).
- Task results MUST be compact (≤500 words per section).
- Status transitions: `pending → in_progress → done | failed | skipped`.
- Failed tasks set `status: failed` with error detail in `result.error`.