# Task: post-creation

## Purpose

Invoke auditors and trigger plan creation for multi-task specs after issue creation, ensuring spec quality before approval.

## Operating Protocol

1. **Run after issue is created.**
2. **Invoke auditors BEFORE approval.**

## Entry Criteria

- Issue created successfully
- Issue number available
- Creation byline added

## Exit Criteria

- Auditors invoked (spec-auditor orchestrator — determines subtasks automatically)
- Plan creation triggered (if multi-task) via writing-plans skill
- Issue ready for approval workflow

## Procedure

### Step 1: Determine Single-Task vs Multi-Task

**Use `single-task-check` task to determine:**
- Single-task spec (ONE phase, plan optional per agent intelligence)
- Multi-task spec (multiple phases, requires plan issue)

**Export the determination** as `single_task_determination` with value `single-task` or `multi-task`. Also export `single_task` as a boolean (`true` for single-task, `false` for multi-task). These values are passed to `writing-plans --task create` so the decision gate can evaluate combined vs separate plan without re-running the single-task analysis.

### Step 2: Trigger Plan Creation (All Specs)

**Invoke `writing-plans --task create` for ALL specs**, passing the `single_task_determination` from Step 1. The `writing-plans` skill's decision gate evaluates whether to produce a combined spec+plan or a separate [PLAN] issue.

**If multi-task spec:**

The writing-plans decision gate will create a separate [PLAN] issue with sub-issues (current behavior).

**If single-task spec:**

The writing-plans decision gate evaluates whether to combine the plan into the spec body or create a separate plan — agent intelligence decides, not a rigid rule.

```python
# Post-creation triggers writing-plans with single-task determination:
# writing-plans --task create --context single_task_determination=single-task|multi-task single_task=true|false
#   → decision gate at Step 1.5 evaluates combined vs separate
#   → if separate: creates [PLAN] issue + sub-issues
#   → if combined: appends ## Implementation Plan to spec body
```

### Step 3: Invoke Spec-Auditor Orchestrator

**Run spec-auditor as the single audit entry point:**

```
1. spec-auditor --issue <number>
   - Orchestrator determines which subtasks to run
   - Baseline always runs: fresh-start, structure, fidelity
   - Agent decides conditional subtasks based on issue nature
   - All findings are reported (not auto-applied)
```

**The orchestrator replaces the old three-auditor chain.**
Previous workflow (DEPRECATED):
~~~
1. plan-fidelity-auditor --issue <number>
2. concern-separation-auditor --issue <number>
3. spec-auditor --issue <number>
~~~

**New workflow:**
```
1. spec-auditor --issue <number>
   (internally runs baseline + conditional subtasks)
```

**Auditors MUST run BEFORE approval.**

## Single-Task Exemption

**If single-task:**
- Plan strategy is determined by writing-plans decision gate (combined spec+plan or separate plan)
- Writing-plans receives `single_task_determination=single-task` and `single_task=true` and evaluates the best document structure
- If combined: no sub-issues, plan content lives in spec body under `## Implementation Plan`
- If separate: standard [PLAN] issue with sub-issues
- Proceed to auditor invocation

## Safety Checks

Before proceeding, verify ALL:

- Auditors invoked (spec-auditor orchestrator — determines subtasks automatically)
- Plan creation triggered via writing-plans (for all specs, with `single_task_determination` and `single_task` passed)

**If ANY check fails → HALT and report.**

## Context Required

- Related tasks: `creation` (runs first), `single-task-check` (determination logic), `writing-plans --task create` (plan creation — decision gate at Step 1.5 handles combined vs separate)