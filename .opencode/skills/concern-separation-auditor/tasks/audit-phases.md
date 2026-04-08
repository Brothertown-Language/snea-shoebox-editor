# Task: audit-phases

## Purpose

Analyze spec phase structure for concern separation quality - deployment independence, risk profile, and blast radius.

## Entry Criteria

- Spec Issue number provided
- Phases defined in spec body

## Exit Criteria

- Phase concerns identified
- Deployment independence assessed
- Risk profile documented
- Blast radius estimated
- Findings posted to GitHub Issue

## Procedure

### Step 1: Get Spec Content

```python
issue = github_issue_read(method="get", issue_number=N)
body = issue["body"]
```

### Step 2: Extract Phases

Parse spec body for phase structure:

```markdown
## Phase 1: [Concern Name]
## Phase 2: [Concern Name]
```

**Validation:**
- Each phase MUST have a concern name (not "Implementation", "Testing", etc.)
- Each phase MUST have steps

### Step 3: Analyze Concern Separation

**For each phase, assess:**

#### Deployment Independence

Can this phase be deployed independently?

| Score | Criteria |
|-------|----------|
| HIGH | Can deploy to production standalone |
| MEDIUM | Can deploy with minimal integration |
| LOW | Requires other phases deployed first |

#### Risk Profile

What goes wrong if this phase fails?

| Score | Impact |
|-------|--------|
| LOW | Isolated failure, easy rollback |
| MEDIUM | Limited blast radius, moderate recovery |
| HIGH | System-wide impact, difficult recovery |

#### Blast Radius

How many other components/systems affected?

| Score | Scope |
|-------|-------|
| LOW | Single component |
| MEDIUM | Multiple components in same boundary |
| HIGH | Cross-cutting, affects many systems |

### Step 4: Generate Report

```markdown
## Concern Separation Audit

**Spec:** #N
**Auditor:** concern-separation-auditor
**Date:** YYYY-MM-DD

### Phase Analysis

#### Phase 1: [Concern Name]

**Concern:** [What this phase addresses]

**Deployment Independence:** HIGH/MEDIUM/LOW
- [Reasoning]

**Risk Profile:** LOW/MEDIUM/HIGH
- [Reasoning]

**Blast Radius:** LOW/MEDIUM/HIGH
- [Reasoning]

**Recommendations:**
- [Specific improvement suggestions]

[Repeat for each phase]

### Cross-Phase Dependencies

[Which phases depend on others]

### Overall Assessment

[Summary of concern separation quality]
```

### Step 5: Post to GitHub Issue

```python
github_add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=N,
    body=f"AI: {AgentName} {ModelID}\n\n{report}"
)
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Phase named "Implementation" | Request rename to specific concern |
| No concern name provided | Cannot assess without clear purpose |
| Phases highly coupled | Recommend splitting or reordering |
| Blast radius HIGH for early phase | Flag as risky, suggest safeguards |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `check-independence` (detailed deployment analysis)