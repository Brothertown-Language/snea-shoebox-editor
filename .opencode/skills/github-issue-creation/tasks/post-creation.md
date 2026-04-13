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

### Step 2: Trigger Plan Creation (Multi-Task Only)

**If multi-task spec:**

Invoke `writing-plans --task create` to create the plan issue. Plan creation handles:
- Creating the `[PLAN]` issue with `plan` label
- Adding a linked reference to the spec in the plan body
- Creating sub-issues under the plan (via `github-sub-issues` skill)

**Do NOT create sub-issues directly under the spec.** Sub-issues belong under the plan, not the spec.

```python
# Post-creation triggers writing-plans:
# writing-plans --task create
#   → creates [PLAN] issue referencing spec #N in body
#   → creates sub-issues under the plan
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
- Plan issue optional (per agent intelligence — agent may create one if it adds clarity)
- No sub-issues needed under any plan
- Proceed to auditor invocation

## Safety Checks

Before proceeding, verify ALL:

- Auditors invoked (spec-auditor orchestrator — determines subtasks automatically)
- Plan creation triggered (if multi-task)

**If ANY check fails → HALT and report.**

## Context Required

- Related tasks: `creation` (runs first), `single-task-check` (determination logic), `writing-plans --task create` (plan creation for multi-task)