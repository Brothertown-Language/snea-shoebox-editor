# Task: post-creation

## Purpose

Invoke auditors and create sub-issues after issue creation, ensuring spec quality before approval.

## Operating Protocol

1. **Run after issue is created.**
2. **Invoke auditors BEFORE approval.**

## Entry Criteria

- Issue created successfully
- Issue number available
- Creation byline added

## Exit Criteria

- Auditors invoked (spec-auditor orchestrator — determines subtasks automatically)
- Sub-issues created (if multi-task)
- Issue ready for approval workflow

## Procedure

### Step 1: Determine Single-Task vs Multi-Task

**Use `single-task-check` task to determine:**
- Single-task spec (ONE phase, no sub-issues needed)
- Multi-task spec (multiple phases, requires sub-issues)

### Step 2: Create Sub-Issues (Multi-Task Only)

**If multi-task spec:**

```python
# For each phase in spec:
sub_issue = github_issue_write(
    method="create",
    owner=owner,
    repo=repo,
    title=f"[Task: #{parent_number}] {phase_title}",
    body=phase_content,
    labels=["needs-approval"]
)

# Link as sub-issue:
github_sub_issue_write(
    method="add",
    owner=owner,
    repo=repo,
    issue_number=parent_number,
    sub_issue_id=sub_issue["id"]  # Use DATABASE ID
)
```

**Phase-level sub-issues:**
- One sub-issue per phase
- NOT one per step
- Use database ID (not issue number) for linking

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

### Step 4: Post Completion Comment

**After auditors complete:**

```markdown
🤖 ✨ Created by <AgentName> (<ModelID>)

**Status:** Ready for approval workflow.

**Workflow:**
1. Review auditor findings above
2. Authorize with "approved" or "go"
3. Agent will begin implementation
```

## Single-Task Exemption

**If single-task:**

```markdown
🤖 ✨ Created by <AgentName> (<ModelID>)

**Status:** Single-task spec. No sub-issues needed.

**Workflow:**
1. Review auditor findings
2. Authorize with "approved" or "go"
3. Agent will begin implementation
```

## Safety Checks

Before proceeding, verify ALL:

- Auditors invoked (spec-auditor orchestrator — determines subtasks automatically)
- Sub-issues created (if multi-task)
- Completion comment posted

**If ANY check fails → HALT and report.**

## Context Required

- Related tasks: `creation` (runs first), `single-task-check` (determination logic)