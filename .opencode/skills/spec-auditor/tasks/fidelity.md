# Task: fidelity

## Purpose

Generate a clean-room plan from the spec's problem statement and compare it against the existing plan to identify substantive gaps. This subtask delegates clean-room generation to the `writing-plans --task clean-room` skill and performs comparison. All findings are reported, NOT auto-applied.

**Delegated from:** plan-fidelity-auditor (v1). Now a subtask within spec-auditor.

## Procedure

### Step 1: Extract Problem Statement

Read the spec issue and extract:
- Objective
- Problem Statement
- Context
- Constraints
- Success Criteria

Write extracted content to `./tmp/clean-room-input-N.md`.

### Step 2: Generate Clean-Room Plan

Invoke `writing-plans --task clean-room` as a subtask:
```
task(
  subagent_type="general",
  description="Generate clean-room plan for issue N",
  prompt="Use the writing-plans skill --task clean-room to generate a plan from the problem statement in ./tmp/clean-room-input-N.md. worktree.path: <worktree.path value or 'not set'>. If worktree.path is set, all file operations MUST use it as the base directory. Return the generated plan."
)
```

**Key v2 change:** Clean-room generation uses prose-driven approach (no template structure), consistent with the writing-plans skill redesign.

### Step 3: Compare Plans

Compare clean-room plan against existing spec at three levels:

| Level | What's Compared | Example |
|-------|----------------|---------|
| Phase-level | Missing phases, extra phases, phase ordering | Clean-room has phase not in original |
| Step-level | Missing steps, extra steps, step ordering | Clean-room covers edge case not in original |
| Content-level | Different approaches, wrong assumptions | Clean-room uses different strategy |

### Step 3.5: TDD Step Structure Check

During clean-room comparison, verify that the clean-room plan includes TDD step structure (RED checkpoint with missing-test handling) if the spec's problem statement implies code/rule changes.

| Finding | Classification | Action |
| -- | -- | -- |
| MISSING-TDD-CHECKPOINT | conditional | Flag for review if TDD structure is absent |

### Step 4: Semantic Matching

Before reporting differences, attempt semantic matching:
- "User Schema" vs "Database Tables" → matching (same concept)
- "Authentication Setup" vs "OAuth2 Integration" → matching if OAuth2 is the auth method
- "API Endpoints" vs "REST API" → matching (same concept)

Only substantive differences after semantic matching are reported.

### Step 5: Report Findings

Report all findings using the v3 auto-fix format. Auto-fix eligible findings (approach differences) are applied directly.

## Auto-Fix Classification

| Finding Type | Classification | Fix Action |
|-------------|----------------|-----------|
| MISSING_PHASE | auto-fix | Add missing phase to spec |
| MISSING_STEP | auto-fix | Add missing step to spec |
| APPROACH_DIFFERENCE | auto-fix | Add missing approach or clarify difference |
| MISSING_EDGE_CASE | auto-fix | Add edge case handling to relevant step |
| EXTRA_PHASE | flag-for-review | May be intentional; developer decides |
| EXTRA_STEP | flag-for-review | May be intentional; developer decides |
| SCOPE_EXPANSION | conditional | Verify clean-room plan isn't over-scoped before flagging |
| VAGUE_PROBLEM | flag-for-review | Problem statement requires human input |

## Finding Classification

| Finding Type | Severity | Description |
|-------------|----------|-------------|
| MISSING_PHASE | HIGH | Clean-room has phase not in original |
| EXTRA_PHASE | MEDIUM | Original has phase not in clean-room |
| MISSING_STEP | MEDIUM | Clean-room has step not in original |
| EXTRA_STEP | LOW | Original has step not in clean-room |
| APPROACH_DIFFERENCE | HIGH | Same goal, different implementation approach |
| MISSING_EDGE_CASE | MEDIUM | Clean-room covers edge case not in original |
| SCOPE_EXPANSION | MEDIUM | Clean-room is significantly larger than original |
| VAGUE_PROBLEM | HIGH | Problem statement too vague for comparison |

## When Significant Gaps Are Found

When the comparison reveals fundamental misunderstandings or large gaps:

- **Recommend brainstorming** rather than just flagging
- The fidelity subtask can trigger `/skill brainstorming` for the vague or misunderstood area
- This is a v2 improvement: instead of just flagging, actively recommend deeper exploration

## Report Format

```
Subtask: fidelity
Finding: [MISSING_PHASE|EXTRA_PHASE|MISSING_STEP|EXTRA_STEP|APPROACH_DIFFERENCE|MISSING_EDGE_CASE|SCOPE_EXPANSION|VAGUE_PROBLEM] - [summary]
Location: [phase/step where difference found]
Context: [why this matters for implementation fidelity]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review — [reason]"]
Severity: [HIGH|MEDIUM|LOW]
```

## Failure Recovery

If clean-room generation fails:
1. Log the failure in the audit comment
2. Post a warning that plan fidelity could not be verified
3. Continue with remaining subtasks
4. Do NOT block the audit on clean-room generation failure

## Scope Boundaries

- Read-only analysis of spec content
- No auto-updates to the issue
- Clean-room plan is a comparison artifact only
- Must use GitHub MCP tools for issue operations

Co-authored with AI: <AgentName> (<ModelId>)