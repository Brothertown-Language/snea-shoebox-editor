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

## Live Verification: Understanding Claims (MANDATORY)

**Each understanding verification MUST produce a tool-call artifact. Assertions without artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Codebase understands confirmed" | Verify relevant code was actually read | `srclight_get_symbol(name="target")` → confirm non-empty | VERIFICATION-GAP |
| "Dependencies verified" | Verify import/call chains checked | `srclight_get_callers(symbol_name="target")` | VERIFICATION-GAP |
| "Problem statement accurate" | Verify problem matches actual code state | `srclight_get_callees(symbol_name="target")` → confirm | CONFLICTING |
| "Success criteria testable" | Verify criteria reference actual measurable artifacts | Review criteria against codebase via `grep` or `srclight` | STRUCTURE-VIOLATION |

**Evidence artifact:** Tool call results for each understanding verification step.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Code not actually read | VERIFICATION-GAP | conditional | Read relevant code now |
| Dependency unverified | VERIFICATION-GAP | conditional | Verify dependency chain |
| Problem statement contradicted by code | CONFLICTING | flag-for-review | HALT — revise understanding |
| Success criteria not testable | STRUCTURE-VIOLATION | flag-for-review | Request measurable criteria |