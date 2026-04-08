# Planning: Spec Templates

## Spec Creation Checklist

Before creating or submitting any spec, bug report, or issue, verify ALL required elements are present.

### Mandatory Elements Checklist

Use this checklist for every spec:

```markdown
## Fresh-Start Context Checklist

- [ ] **Problem Statement** — What is broken/needed and WHY (with context)
- [ ] **Affected Files** — List of files with anchors (function/section) and code snippets
- [ ] **Related Issues** — Links + summaries + relevance explanation
- [ ] **Context** — Background on affected systems, prior decisions
- [ ] **Constraints** — Technical, resource, time, compatibility limits
- [ ] **Assumptions** — What we're assuming that may not be true
- [ ] **Success Criteria** — Testable, measurable completion criteria
- [ ] **Edge Cases** — Identified boundary conditions
- [ ] **Dependencies** — External systems, libraries, affected teams
- [ ] **Risk Assessment** — What could go wrong and mitigations
- [ ] **Decision Rationale** — Why this approach was chosen (if applicable)
```

### Self-Containment Rules

Verify the spec is self-contained:

```markdown
## Self-Containment Verification

- [ ] NO "as discussed above" — all context stated inline
- [ ] NO "see previous comment" — information restated
- [ ] NO "as mentioned in chat" — decisions documented
- [ ] File paths use STABLE ANCHORS — function names `process_data()` or section headers `"Section Name"`
- [ ] ⚠️ AVOID line numbers `file.py:42` — they break on every edit
- [ ] Code snippets included for short sections (<20 lines)
- [ ] Issue links include URLs and summaries
```

---

## Spec Template (Feature)

Use this template for new feature specifications.

```markdown
# Spec: [Feature Name]

STATUS: 1.1
CREATED: YYYY-MM-DD

---

## Objective

[What does this feature accomplish? Why is it needed?]

---

## Problem Statement

[What problem does this solve? What pain point does it address? Include context about who is affected and why this matters now.]

---

## Context

**Background:**
[Relevant history, prior decisions, current state]

**Affected Systems:**
[Which components, modules, or services are affected]

**Stakeholders:**
[Who cares about this change? Developers, users, other teams]

---

## Constraints

| Constraint Type | Details |
|-----------------|---------|
| Technical | [e.g., must work with Python 3.10+] |
| Resource | [e.g., no additional dependencies] |
| Time | [e.g., needed by Q2] |
| Compatibility | [e.g., cannot break existing API] |

---

## Assumptions

1. [Assumption 1 - what we're assuming that may not be true]
2. [Assumption 2]
3. [Assumption 3]

---

## Affected Files

| File | Anchor | Description | Code Snippet |
|------|--------|-------------|--------------|
| `path/to/file.py` | `function_name()` or `"Section Name"` | [What this section does] | [Short snippet] |

---

## Related Issues

| Issue | Summary | Relevance |
|-------|---------|-----------|
| [#123](https://github.com/owner/repo/issues/123) | [Brief summary] | [Why it matters to this spec] |

---

## Success Criteria

1. ✅ [Testable criterion 1]
2. ✅ [Testable criterion 2]
3. ✅ [Testable criterion 3]

---

## Edge Cases

1. **[Edge case 1]:** [Description and handling]
2. **[Edge case 2]:** [Description and handling]

---

## Dependencies

| Dependency | Type | Impact |
|------------|------|--------|
| [Library/Service] | [Internal/External] | [What happens if unavailable] |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [What could go wrong] | [Low/Medium/High] | [Low/Medium/High] | [How we handle it] |

---

## Decision Rationale

**Decision:** [What approach was chosen]

**Why:** [Why this approach over alternatives]

**Alternatives Considered:**
1. [Alternative 1] — Rejected because [reason]
2. [Alternative 2] — Rejected because [reason]

---

## Phase 1: [Concern Name] (Gated)

### Steps

1. ☐ [First task for this concern]
2. ☐ [Second task for this concern]
3. ☐ [Third task for this concern]

---

## Phase 2: [Next Concern] (Gated)

### Steps

1. ☐ [First task for this concern]
2. ☐ [Second task for this concern]

---

## Phase 3: [Verification Concern] (Auto-progress)

### Steps

1. ☐ Run automated tests
2. ☐ Verify edge cases

---

## Phase 4: [Review Concern] (Gated)

### Steps

1. ☐ Human review of changes
2. ☐ Approve or request revisions

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI: <Agent> ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

**⚠️ CRITICAL: Phase names MUST describe specific concerns, NOT generic activities.**
- ✅ Good: "Database Schema Setup", "API Endpoint Integration", "Error Handling Layer"
- ❌ Bad: "Implementation", "Testing", "Development", "Build"
```

---

## Spec Template (Bug Fix)

Use this template for bug fix specifications.

```markdown
# Spec: [Bug Description]

STATUS: 1.1
CREATED: YYYY-MM-DD

---

## Objective

[What does this bug fix accomplish?]

---

## Problem Statement

**Symptom:** [What is the observed incorrect behavior?]

**Expected Behavior:** [What should happen instead?]

**Impact:** [Who is affected and how severely?]

---

## Context

**Where the bug occurs:**
[Which component, module, or user flow]

**When the bug occurs:**
[What conditions trigger the bug]

**Discovery:**
[How was the bug found? User report, automated test, etc.]

---

## Root Cause Analysis

**Investigation:**
[What was discovered during analysis]

**Cause:**
[What is the underlying cause]

**Evidence:**
[Code snippets, logs, or other evidence]

```python
# Relevant code at path/to/file.py in `function_name()` or "Section Name"
def broken_function():
    # BUG: Off-by-one error in loop
    for i in range(len(items)):  # Should be range(len(items) - 1)
        process(items[i])
```

---

## Affected Files

| File | Anchor | Description |
|------|--------|-------------|
| `path/to/file.py` | `function_name()` or `"Section Name"` | [Function with bug] |

---

## Related Issues

| Issue | Summary | Relevance |
|-------|---------|-----------|
| [#123](https://github.com/owner/repo/issues/123) | [Related bug or feature] | [Connection to this fix] |

---

## Fix Approach

**Solution:** [What change will fix the bug]

**Why this approach:** [Why this is the minimal correct fix]

**Side effects:** [What else might be affected]

---

## Success Criteria

1. ✅ Bug is fixed and test passes
2. ✅ No regression in existing tests
3. ✅ Edge case handling verified

---

## Edge Cases

1. **[Edge case 1]:** [How the fix handles it]
2. **[Edge case 2]:** [How the fix handles it]

---

## Phase 1: [Bug Fix Concern] (Gated)

### Steps

1. ☐ Implement fix for [bug description]
2. ☐ Add test case for [specific scenario]
3. ☐ Run full test suite to verify no regression

---

## Phase 2: [Verification Concern] (Auto-progress)

### Steps

1. ☐ Verify original bug scenario passes
2. ☐ Verify edge cases pass
3. ☐ Verify no regression in related tests

---

## Phase 3: [Review Concern] (Gated)

### Steps

1. ☐ Code review
2. ☐ Approve or request revisions

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI: <Agent> ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.

**⚠️ CRITICAL: Phase names MUST describe specific concerns, NOT generic activities.**
- ✅ Good: "Database Schema Fix", "Authentication Logic Fix", "Error Handling Update"
- ❌ Bad: "Implementation", "Testing", "Bug Fix", "Development"
```

---

## Spec Template (Guideline Update)

Use this template for changes to `.opencode/guidelines/`.

```markdown
# Spec: Guidelines: [Topic]

STATUS: 1.1
CREATED: YYYY-MM-DD

---

## Objective

[What guideline change is being made? Why?]

---

## Problem Statement

**Current State:** [What do the guidelines currently say or not say?]

**Issue:** [What problem does this cause? Why is the current state insufficient?]

**Impact:** [Who is affected? What mistakes happen without this guidance?]

---

## Context

**Background:**
[Why is this guideline needed now? What triggered this change?]

**Stakeholders:**
[Which agents/developers need this guidance]

---

## Proposed Change

**File(s) to modify:**
- `.opencode/guidelines/planning/00-spec-creation.md`

**Change summary:**
[What sections are being added or modified]

---

## Decision Rationale

**Why this approach:**
[Why this specific change over alternatives]

**Alternatives considered:**
1. [Alternative 1] — Rejected because [reason]
2. [Alternative 2] — Rejected because [reason]

---

## Success Criteria

1. ✅ Guideline documentation updated
2. ✅ Changes load correctly in `ai_bin/guidelines`
3. ✅ All files pass linting

---

## Phase 1: [Guideline Module Update] (Gated)

### Steps

1. ☐ [Update guideline file]
2. ☐ [Verify with ai_bin tools]

---

## Phase 2: Guideline Verification (Auto-progress)

### Steps

1. ☐ Verify guidelines load correctly
2. ☐ Verify search finds new content

---

## Phase 3: Human Approval (Gated)

### Steps

1. ☐ Human review of changes
2. ☐ Approve or request revisions

---

> **Approval Tracking**: Approvals are tracked via GitHub Issue comments (e.g., `AI: <Agent> ✅ Approved: Phase 1`), NOT in the issue body. Issue body edits destroy history.
```

---

*Source: Created to support fresh-start context requirements*