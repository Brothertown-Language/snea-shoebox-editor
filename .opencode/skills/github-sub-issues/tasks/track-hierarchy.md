# Task: track-hierarchy

## Purpose

Verify and maintain parent-child issue hierarchy for multi-task plans.

## Entry Criteria

- Plan issue number identified
- Sub-issues created (or need creation)

## Exit Criteria

- Hierarchy tree documented
- All phases have corresponding sub-issues
- Orphan issues identified (if any)

## Procedure

### Step 1: Get Plan Issue

```python
plan = github_issue_read(method="get", issue_number=M)
phases = extract_phases(plan["body"])
```

### Step 2: Get Sub-Issues

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=M)
```

### Step 3: Build Hierarchy Tree

```markdown
PLAN #M: [PLAN] Feature Name
├── Task #P1: [Task: #M] Phase 1 - Description
├── Task #P2: [Task: #M] Phase 2 - Description
└── Task #P3: [Task: #M] Phase 3 - Description
```

### Step 4: Verify Sub-Issue Context Sufficiency

**For each sub-issue:**
- Read the sub-issue body and verify it contains sufficient phase context for a sub-agent to operate independently
- A sub-issue body that contains only `**Parent Plan:** #M` fails this check — it lacks the phase prose needed for autonomous implementation
- Verify that the body communicates: why this phase exists, what it must accomplish, how to verify completion, what could go wrong, and what must be done first
- This check is prose-agnostic — it verifies information presence, not format or section structure

If a sub-issue fails the context check, flag it for re-creation via `create-sub-issue` with phase prose extraction.

### Step 5: Identify Gaps

**For each phase in plan:**
- Check if corresponding sub-issue exists
- If missing: create via `create-sub-issue`

**For each sub-issue:**
- Check if it matches a phase
- If orphan (no matching phase): flag for review

### Step 6: Report in Chat

## Common Issues

| Issue | Resolution |
|-------|------------|
| Sub-issues missing for phases | Auto-create via `create-sub-issue` |
| Sub-issues lack phase context | Re-create via `create-sub-issue` with prose extraction |
| Orphan sub-issues found | Flag for manual review |
| Hierarchy mismatch | Rebuild hierarchy tree |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `create-sub-issue`, `link-sub-issue`