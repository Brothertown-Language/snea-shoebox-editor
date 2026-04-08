# Task: analyze-phase-structure

## Purpose

Analyze spec phase structure for concern separation quality - deployment independence, risk profile, blast radius.

## Entry Criteria

- Spec Issue number provided
- Called automatically by `spec-auditor` skill (runs FIRST before spec-auditor task)

## Exit Criteria

- Phase concerns identified
- Deployment independence assessed per phase
- Risk profile documented per phase
- Blast radius estimated
- Findings posted to GitHub Issue

## Procedure

### Step 1: Get Spec Content

```python
issue = github_issue_read(method="get", issue_number=N)
body = issue["body"]
```

### Step 2: Extract Phase Structure

Parse spec for phase blocks:

```markdown
## Phase 1: [Concern Name]
## Phase 2: [Concern Name]
```

**Validate phase names:**
- ✅ Good: "Database Schema Setup", "API Endpoint Integration", "Error Handling Layer"
- ❌ Bad: "Implementation", "Testing", "Development", "Build"

### Step 3: Identify Phase Concerns

**For each phase, identify:**
1. What concern does this phase address?
2. What files/systems does it touch?
3. Can it be deployed independently?

### Step 4: Assess Deployment Independence

| Score | Criteria |
|-------|----------|
| HIGH | Can deploy to production standalone |
| MEDIUM | Can deploy with minimal integration |
| LOW | Requires other phases deployed first |

### Step 5: Assess Risk Profile

| Score | Impact |
|-------|--------|
| LOW | Isolated failure, easy rollback |
| MEDIUM | Limited blast radius, moderate recovery |
| HIGH | System-wide impact, difficult recovery |

### Step 6: Estimate Blast Radius

| Score | Scope |
|-------|-------|
| LOW | Single component/service |
| MEDIUM | Multiple components in same boundary |
| HIGH | Cross-cutting, affects many systems |

### Step 7: Generate Report

```markdown
## Concern Separation Audit

**Spec:** #N
**Auditor:** concern-separation-auditor
**Date:** YYYY-MM-DD

### Phase Analysis

#### Phase 1: [Concern Name]

**Concern:** [What this phase addresses]
**Deployment Independence:** HIGH/MEDIUM/LOW
**Risk Profile:** LOW/MEDIUM/HIGH
**Blast Radius:** LOW/MEDIUM/HIGH

**Recommendations:**
- [Specific improvement suggestions]

[Repeat for each phase]

## Overall Assessment

[Summary of concern separation quality]
```

### Step 8: Post to GitHub Issue

```python
github_add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=N,
    body=report
)
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Phase named "Implementation" | Request rename to specific concern |
| Phases highly coupled | Recommend splitting or reordering |
| Blast radius HIGH for early phase | Flag as risky, suggest safeguards |
| No phase names provided | Cannot analyze, request clarification |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Runs BEFORE spec-auditor (mandatory order)
- Related skill: spec-auditor
