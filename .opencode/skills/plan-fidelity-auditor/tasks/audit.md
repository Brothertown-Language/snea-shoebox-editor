# Task: audit

## Purpose

Full audit workflow: extract problem statement, generate clean-room plan, compare against existing plan, auto-fix or flag discrepancies.

## Operating Protocol

1. **Mandatory invocation:** This task MUST run when plan-fidelity-auditor is invoked without `--check-only`.

## Entry Criteria

- Issue number provided via `--issue N`
- Issue exists on GitHub and contains `[SPEC]` content
- `writing-plans` skill is available for subtask invocation

## Exit Criteria

- Clean-room plan generated (or failure documented)
- Comparison completed
- Auto-fixes applied (unless `--check-only`)
- Findings posted as GitHub comment
- Remaining auditors can proceed

## Procedure

### Step 1: Read and Extract Problem Statement

**Read the spec issue:**
```
github_issue_read(method="get", owner=OWNER, repo=REPO, issue_number=N)
```

**Extract ONLY the following sections:**
- Objective
- Problem Statement
- Context
- Constraints
- Assumptions
- Success Criteria
- Edge Cases
- Dependencies
- Risk Assessment

**Do NOT extract:**
- Existing phases/steps (we want a clean-room perspective)
- Implementation details
- Code snippets from the spec body

### Step 2: Assess Problem Statement Clarity

**Evaluate the extracted problem statement:**

| Clarity Level | Criteria | Action |
|---------------|----------|--------|
| **Clear** | Problem, context, constraints, and success criteria are all well-defined | Proceed to clean-room generation |
| **Somewhat vague** | Missing some context or constraints, but core problem is understandable | Proceed with noted limitations |
| **Too vague** | Problem statement is ambiguous, missing context, or too brief | Trigger brainstorming |

**If too vague:**
1. Invoke `/skill brainstorming` in one-question-at-a-time mode
2. Post brainstorming questions to the issue as comments
3. Wait for resolution (or use the brainstorming skill's exploration)
4. Use clarified problem statement for generation
5. Post clarified statement as comment on the issue

### Step 3: Write Clean-Room Input

**Write the extracted content to temp file:**
```
Write to: ./tmp/clean-room-input-N.md
Content: Structured markdown with extracted sections only
```

**Format of clean-room input:**
```markdown
# Clean-Room Input for Issue #N

## Objective
<extracted objective>

## Problem Statement
<extracted problem statement>

## Context
<extracted context>

## Constraints
<extracted constraints>

## Assumptions
<extracted assumptions>

## Success Criteria
<extracted success criteria>

## Edge Cases
<extracted edge cases>

## Dependencies
<extracted dependencies>

## Risk Assessment
<extracted risk assessment>
```

### Step 4: Generate Clean-Room Plan

**Invoke writing-plans subtask:**
```
task(
  subagent_type="general",
  description="Generate clean-room plan for issue N",
  prompt="Use the writing-plans skill --task clean-room to generate an implementation plan from the problem statement in ./tmp/clean-room-input-N.md. The plan must address ONLY the problem stated, with NO knowledge of any existing plan. Generate phases with specific concern names, actionable steps, and verification methods. Return the complete plan as structured markdown."
)
```

**If subtask fails:**
1. Log the failure
2. Post warning comment on issue: "Plan fidelity audit could not generate clean-room plan. Skipping fidelity check. Remaining auditors will continue."
3. **Continue to next auditor** — do NOT block the chain

### Step 5: Invoke Compare Task

**Load the compare task:**
```
/skill plan-fidelity-auditor --task compare
```

Pass context:
```yaml
# Context received
issue_number: N
clean_room_plan: "<markdown from subtask>"
existing_plan: "<extracted from issue>"
mode: "auto-fix"  # or "check-only" if flag was set
```

### Step 6: Invoke Auto-Fix Task (if not check-only)

**If auto-fix mode:**
```
/skill plan-fidelity-auditor --task auto-fix
```

Pass comparison results and discrepancy list.

**If check-only mode:**
- Skip this task
- Post findings as comment only

### Step 7: Post Audit Comment

**Post executive summary comment on the issue.**

**Auto-fix mode:**
```markdown
## Plan Fidelity Audit

**Summary:** <1-2 sentences describing findings>

**Outcome:** <Link to revised spec OR "no changes needed">

### Auto-Fixed
- <list of simple fixes applied>

### Flagged for Review
- <list of substantive changes requiring human decision>

---
🤖 ✅ Completed by <AgentName> (<ModelID>): Plan Fidelity Auto-Audit
```

**Check-only mode:**
```markdown
## Plan Fidelity Check (Report Only)

**Summary:** <1-2 sentences>

**Outcome:** No changes applied (--check-only mode)

### Discrepancies Found
- <list of all discrepancies>

---
🤖 📝 Updated by <AgentName> (<ModelID>): Plan Fidelity Check
```

### Step 8: Clean Up Temp Files

```bash
rm ./tmp/clean-room-input-N.md
```

**Do NOT delete clean-room plan output** if it was written to a temp file — it may be needed for reference.

## Context Yielded

```yaml
status: "success|failure|partial"
discrepancies_found: N
auto_fixes_applied: M
flagged_for_review: K
clean_room_generated: true|false
brainstorming_triggered: true|false
next_auditor: "concern-separation-auditor"
```

## Context Required

- Related tasks: `compare` (comparison logic), `auto-fix` (fix application)
- Related skills: `writing-plans` (clean-room generation), `brainstorming` (vague input resolution)