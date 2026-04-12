# Task: start

Begin plan execution and verify prerequisites before implementation.

## Prerequisites

1. Approved plan (verified by approval-gate)
2. Plan stored as GitHub/GitBucket issue
3. Feature branch created (by git-workflow)

## Start Execution

### 1. Verify Plan Approval

- Query the plan issue for plan content
- Check for explicit approval in comments
- Verify plan has no placeholders (writing-plans validation)

### 2. Verify Prerequisites

- Feature branch exists
- Working tree clean
- All dependencies ready

### 3. Initialize Tracking

- Set current step to 1
- Post "Starting execution" comment to plan issue
- HALT and wait for `next step` or `continue`

### Enforcement

- No approval → HALT (approval-gate blocks)
- Placeholders in plan → HALT (writing-plans blocks)
- No feature branch → HALT (git-workflow creates)