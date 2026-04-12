# Task: verify-understanding

## Purpose

Ensure engineering discipline: confirm problem understanding before design or implementation.

## Entry Criteria

- Spec Issue number provided
- User asks for implementation or design

## Exit Criteria

- Problem statement verified
- Success criteria defined
- Edge cases identified
- Dependencies mapped
- Risk assessment documented

## Procedure

### Step 1: Read Problem Statement

```python
issue = github_issue_read(method="get", issue_number=N)
body = issue["body"]
```

**Extract:** 
- Problem Statement section
- Context section
- Expected Behavior section

### Step 2: Verify Problem Understanding

**Ask clarifying questions if:**
- Problem statement is vague ("make it better")
- Context missing (stakeholders, affected systems)
- Success criteria undefined
- No edge cases identified

**Questions format:**
```
## Understanding Verification

**Problem:** [Restated problem]
**Context:** [Identified context]
**Success Criteria:** [Defined criteria]

**Clarification needed:**
1. [Question 1]
2. [Question 2]

Shall I proceed with current understanding, or provide clarifications?
```

### Step 3: Map Dependencies

**Identify:**
- External systems affected
- Libraries required
- Database changes needed
- API contracts impacted

**Document in comment:**
```markdown
### Dependencies

**External Systems:**
- [System]: [Impact]

**Libraries:**
- [Library]: [Version requirement]

**Database:**
- [Table]: [Change type]

**APIs:**
- [Endpoint]: [Contract change]
```

### Step 4: Risk Assessment

**Assess:**
- What could go wrong?
- How recoverable is each failure mode?
- What mitigations exist?

**Document:**
```markdown
### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | Low/Medium/High | Low/Medium/High | [Mitigation] |
```

### Step 5: Report Understanding

Report understanding verification to chat (NOT as GitHub Issue comment). The understanding report is internal agent context, not stakeholder communication.

## Common Issues

| Issue | Resolution |
|-------|------------|
| Problem statement vague | Request clarification before proceeding |
| No success criteria | Ask user to define measurable criteria |
| Missing dependencies | List assumed dependencies, request confirmation |
| Risks undefined | Document obvious risks, ask for confirmation |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `verify-design` (next step), `verify-implementation` (final step)