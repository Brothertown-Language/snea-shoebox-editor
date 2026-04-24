# Task: create/create-and-validate

## Purpose

Write plan document, store as combined section or separate issue, validate structure, and handle approval cascade with scope-aware auto-approval.

## Entry Criteria

- Plan structure completed (plan-structure sub-task)
- Combined/separate decision made
- TDD tasks defined with checkpoints

## Exit Criteria

- Plan document written and stored (combined or separate)
- Self-review and validation complete
- Verification revisit passed
- Plan reported in chat with URL
- Approval cascade applied (auto-approval for pipeline scope)

## Procedure

### Step 6: Write Plan Document Header

- Goal, Architecture, Tech Stack
- File structure with clear responsibilities

### Step 7: Store Plan Document

**If COMBINED (from Step 1.5):**
- Append `## Implementation Plan` section to spec issue body
- Retain `[SPEC]` title prefix
- Proceed to Step 8

**If SEPARATE:**
- Create GitHub Issue:
  - Title: `[PLAN] <Feature Name>`
  - Labels: `plan`, `needs-approval`
  - Body: `Spec: #<N>` prose reference, then plan (header, file structure, phases with TDD tasks)
  - STATUS: prose-driven format: `STATUS: in progress — {first concern}, Step 1`
  - Do NOT link plan as sub-issue of spec — reference only via body text

**Phase body requirements (each phase MUST include):**
- Why this phase exists (concern it addresses)
- What it must accomplish (tasks, deliverables, behavioral requirements)
- How to verify completion (success criteria)
- What could go wrong (edge cases, risks)
- What must be done first (dependencies)

**Concern boundary annotations (prose-driven):**
When transitioning concerns: describe what is being left, what is being entered, what information is needed for handoff.

### Step 6a: Create Sub-Issues (SEPARATE only)

After plan issue created:
- Create sub-issue for each phase via `issue-operations --task link-sub-issue`
- Sub-issues are children of the plan, NOT the spec

### Step 8: Self-Review

- Spec coverage check
- Placeholder scan
- Type consistency check
- Fix any issues found

### Step 9: Validate Plan

- Check for TBD/TODO placeholders
- Verify all steps are actionable
- Verify success criteria are testable
- Prose-structure check: phase descriptions remain prose

### Step 10: Verification Revisit (MANDATORY)

Invoke: `/skill verification-enforcement --task revisit`

Scans for `⚠️ UNVERIFIED` markers. Resolves if possible; escalates unresolvable claims.

### Step 11: Report Plan Creation in Chat (MANDATORY)

**Format (separate plan):**
```
Created separate implementation plan for #<N> (<description>). <N> tasks across <N> files.

https://github.com/<owner>/<repo>/issues/<N>
🤖 <AgentName> (<ModelId>)
```

**Format (combined spec+plan):**
```
Created combined spec+plan for #<N> (<description>). Plan appended under `## Implementation Plan`.

https://github.com/<owner>/<repo>/issues/<N>
🤖 <AgentName> (<ModelId>)
```

### Step 12: Cross-Reference Verification (MANDATORY)

Verify referenced skills exist:
```bash
ls .opencode/skills/approval-gate/SKILL.md && grep -c "verify-authorization" .opencode/skills/approval-gate/SKILL.md
ls .opencode/skills/issue-operations/SKILL.md && grep -c "link-sub-issue" .opencode/skills/issue-operations/SKILL.md
```

If any verification fails: flag as MISSING-TRACEABILITY.

### Step 13: Approval Cascade Check (MANDATORY)

**Scope-aware auto-approval:**

```python
SCOPE_LEVELS = {
    "standard": 0, "for_spec": 1, "for_plan": 2,
    "for_implementation": 3, "for_code_review": 4,
    "for_pr": 5, "pr_only": 5, "review_only": 4
}

if scope_level >= SCOPE_LEVELS["for_plan"]:
    # Pipeline authorization covers plan approval
    github_issue_write(method="update", issue_number=<plan>,
                      labels=[l for l in plan_labels if l != "needs-approval"])
    github_add_issue_comment(
        issue_number=<plan>,
        body=f"Plan auto-approved via pipeline scope (authorization_scope={scope})."
    )
```

**For combined spec+plan:** Only auto-remove `needs-approval` if `scope_level >= for_plan`.

**If `halt_at == plan_created`:** HALT after plan creation. Do NOT proceed to implementation.

## Acceptance Criteria

| ID | Criterion |
| -- | -- |
| C1 | Plan header includes Goal, Architecture, Tech Stack |
| C2 | File structure lists all files with responsibilities |
| C3 | TDD tasks include mandatory Step 2 RED checkpoint |
| C4 | Phase descriptions include concern boundary annotations |
| C5 | Sub-issues linked only under plan (not spec) for separate plans |
| C6 | No TBD/TODO placeholders remain |
| C7 | Combined plans retain `[SPEC]` prefix; separate plans use `[PLAN]` |
| C8 | Status marker uses prose-driven format |
| C9 | Approval cascade honors `authorization_scope` |

## Context Required

- Related tasks: `create/plan-structure`
- Related skills: `verification-enforcement`, `issue-operations`
- Related guidelines: `000-critical-rules.md` (URL sourcing, chat format)