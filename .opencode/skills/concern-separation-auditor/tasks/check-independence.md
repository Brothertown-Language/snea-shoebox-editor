# Task: check-independence

## Purpose

Validate deployment independence between phases - can each phase be deployed independently?

## Entry Criteria

- Phase analysis completed (audit-phases)
- Phase dependencies identified

## Exit Criteria

- Each phase's deployment independence verified
- Dependency graph created
- Integration points documented
- Recommendations posted to GitHub Issue

## Procedure

### Step 1: Build Dependency Graph

For each phase, identify:

```python
dependencies = {
    "Phase 1": [],  # No dependencies
    "Phase 2": ["Phase 1"],  # Depends on Phase 1
    "Phase 3": ["Phase 1", "Phase 2"],  # Depends on both
}
```

### Step 2: Test Independence Assumptions

**For each phase, verify:**

1. **Can deploy standalone?**
   - No database migration required from other phases
   - No config changes required from other phases
   - No service dependencies on other phases

2. **If standalone deployment fails:**
   - Can rollback cleanly?
   - Does not affect other deployed phases?

3. **Integration points:**
   - Where does this phase integrate with others?
   - Are integration points backward compatible?

### Step 3: Generate Dependency Matrix

```
| Phase | Depends On | Deployable Alone? | Notes |
|-------|------------|-------------------|-------|
| 1 | - | YES | Initial setup |
| 2 | 1 | NO | Uses DB from Phase 1 |
| 3 | 1, 2 | NO | API depends on both |
```

### Step 4: Post Findings

```python
github_add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=N,
    body=f"AI: {AgentName} {ModelID}\n\n{independence_report}"
)
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Circular dependencies detected | Flag CRITICAL - must restructure |
| Phase 2 depends on Phase 5 | Flag - dependency order wrong |
| Cannot deploy standalone | Document integration requirements |
| Rollback unclear | Add rollback plan to phase |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `audit-phases` (provides phase structure)