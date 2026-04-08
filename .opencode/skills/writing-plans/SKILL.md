---
name: writing-plans
description: Plan creation workflow that transforms approved specs into structured, actionable implementation plans with completeness validation.
license: MIT
compatibility: opencode
---

# Skill: writing-plans

## Overview

Plan creation workflow that transforms approved specs into structured, actionable implementation plans. This skill ensures plans are complete, placeholder-free, and ready for execution. It is adapted from the NewsRx/opencode-gitbucket-superpowers workflow.

**Source Attribution:** This skill is adapted from NewsRx/opencode-gitbucket-superpowers workflow (branch: newsrx).

## Persona

You are an Implementation Planner. Your focus is transforming approved design specs into complete, actionable implementation plans with clear steps, testability, and verification evidence.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `create` | Create plan from approved spec | ~1000 |
| `validate` | Check for placeholders and completeness | ~600 |
| `retroactive` | Create plan for existing spec | ~800 |
| `clean-room` | Generate independent plan from problem statement only (for comparison) | ~500 |

## Invocation

- `/skill writing-plans` - Overview only
- `/skill writing-plans --task create` - Create plan from current spec
- `/skill writing-plans --task validate` - Validate existing plan
- `/skill writing-plans --task retroactive` - Create plan for existing spec
- `/skill writing-plans --task clean-room` - Generate clean-room plan from problem statement only (for plan-fidelity-auditor comparison)

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked by dispatch-table.yaml when:
   - Spec receives explicit approval (`approved` or `go`)
   - User asks about plan creation workflow
   - After approval-gate verifies authorization
   - DO NOT proceed to implementation until plan is approved

2. **Plan Structure Requirements:**
   - Plans stored as GitBucket issues
   - Each plan linked to its parent spec via sub-issues
   - Plans contain ONLY implementation steps (no investigation/planning phases)
   - Plans are COMPLETE with no TBD/TODO placeholders

3. **Exit conditions:** Plan creation is COMPLETE when:
   - Plan created as GitBucket issue
   - Plan linked to parent spec (sub-issue)
   - Plan has no placeholders
   - HALT and wait for plan approval

## Plan Creation Workflow

### Prerequisites
1. Approved spec (verified by approval-gate)
2. Spec stored as GitBucket issue
3. Spec has explicit approval (`approved` or `go`)

### Creation Steps

1. **Read approved spec:**
   - Query GitBucket issue for spec content
   - Extract objectives, constraints, success criteria
   - Identify affected files and dependencies

2. **Transform to plan structure:**
   - Convert spec phases to implementation steps
   - Ensure each step is actionable and testable
   - Add verification methods for each step

3. **Create plan issue:**
   - Title: `[PLAN] <Feature Name>`
   - Body: Structured implementation plan
   - Link to parent spec (sub-issue)

4. **Validate plan:**
   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify all success criteria are testable

### Plan Template

```markdown
# Plan: [Feature Name]

STATUS: 1.1
CREATED: YYYY-MM-DD
PARENT: #<Spec Issue Number>

---

## Objective

[What does this plan accomplish? Reference parent spec objectives]

---

## Implementation Steps

### Step 1: [Concern Name]
- ☐ [Specific task 1]
- ☐ [Specific task 2]
- ☐ Verification: [How to verify this step]

### Step 2: [Next Concern]
- ☐ [Specific task 1]
- ☐ [Specific task 2]
- ☐ Verification: [How to verify this step]

---

## Success Criteria

1. ✅ [Testable criterion 1]
2. ✅ [Testable criterion 2]

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| [What could go wrong] | [How to handle it] |

---

## Dependencies

| Dependency | Status |
|------------|--------|
| [External system] | [Ready/Blocked] |

---

> **Approval Tracking:** Plan approvals tracked via GitBucket issue comments.
```

## Placeholder Detection (CRITICAL)

**⚠️ Plans with placeholders are INVALID and must not be approved.**

### Prohibited Patterns

| Pattern | Why Prohibited |
|---------|----------------|
| `TBD` | Incomplete plan |
| `TODO` | Incomplete plan |
| `[to be determined]` | Incomplete plan |
| `[needs investigation]` | Investigation should be in spec |
| `[placeholder]` | Incomplete plan |
| `[requires research]` | Research should be in spec |

### Validation Logic

```python
INVALID_PATTERNS = [
    "TBD", "TODO", "tbd", "todo",
    "[to be determined]", "[needs investigation]",
    "[placeholder]", "[requires research]",
]

def validate_plan(plan_content: str) -> bool:
    for pattern in INVALID_PATTERNS:
        if pattern in plan_content:
            return False  # Invalid
    return True  # Valid
```

## Retroactive Plan Creation

For existing specs without plans:

1. **Query existing spec:**
   - Get spec from GitBucket issue
   - Check for linked plan (sub-issues)

2. **If no plan exists:**
   - Create plan from spec phases
   - Link as sub-issue
   - HALT and wait for plan approval

3. **If plan exists:**
   - Validate plan (check for placeholders)
   - If invalid → Report issues
   - If valid → Proceed to implementation

## Enforcement Mechanism

**⚠️ CRITICAL: Skills MUST enforce plan completeness — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before implementation:**
   - Does plan exist?
   - Is plan approved?
   - Is plan valid (no placeholders)?

2. **Enforcement matrix:**
   - No plan → CREATE plan (writing-plans skill)
   - Plan exists but unapproved → HALT, wait for approval
   - Plan approved but has placeholders → REJECT plan, require completion
   - Plan approved and complete → PROCEED to implementation

### Enforcement Messages

**Missing plan:**
```
Implementation requires an approved plan.

Spec #N is approved but has no implementation plan.

To create plan: Invoke writing-plans skill or wait for automatic invocation.
```

**Plan has placeholders:**
```
Plan contains incomplete sections (placeholders detected):

- [TBD in Step 3]
- [TODO in verification]

Plans must be complete before approval. Please fill in all placeholders.
```

## Integration with Existing Workflow

### Dispatch Order
```
approval-gate → writing-plans (create) → approval-gate (plan) → git-workflow
```

### GitBucket Platform Adaptations
- Use GitBucket API for plan issue creation
- Link plans to specs via GitBucket Python client (`api.create_issue()` + `api.add_issue_comment()`)
- Parent spec linked in plan body

### Approval Gate Integration
- Plan creation happens AFTER spec approval
- Plan requires separate approval (`approved: plan`)
- Implementation cannot start until BOTH spec AND plan are approved

## Quality Gates

### Plan Completeness Checklist

Before plan approval, verify:

- [ ] All steps are actionable (no TBD/TODO)
- [ ] Each step has verification method
- [ ] Success criteria are testable
- [ ] Risks are documented
- [ ] Dependencies are listed
- [ ] Plan is linked to parent spec

### Step Quality Requirements

Each step must:

1. **Be actionable:** Clear action, not abstract goal
2. **Be testable:** Can verify completion
3. **Have verification:** How to check it works
4. **Be atomic:** Single concern, not multiple

## Cross-References

- Related skills: `brainstorming` (pre-spec), `approval-gate` (authorization), `executing-plans` (implementation)
- Related guidelines: `140-planning-spec-creation.md`, `142-planning-archive-workflow.md`

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the NewsRx/opencode-gitbucket-superpowers repository (branch: newsrx). The original workflow enforces complete, placeholder-free plans before implementation begins.

**Key adaptations for OpenCode:**
- Integration with existing approval-gate and git-workflow skills
- GitBucket platform support via MCP tools
- Dispatch table integration for automatic invocation
- Placeholder detection and rejection logic