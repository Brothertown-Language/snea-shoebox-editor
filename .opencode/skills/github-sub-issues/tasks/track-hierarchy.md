# Task: track-hierarchy

## Purpose

Verify and maintain parent-child issue hierarchy for multi-task specs.

## Entry Criteria

- Parent issue number identified
- Sub-issues created (or need creation)

## Exit Criteria

- Hierarchy tree documented
- All phases have corresponding sub-issues
- Orphan issues identified (if any)

## Procedure

### Step 1: Get Parent Issue

```python
parent = github_issue_read(method="get", issue_number=N)
phases = extract_phases(parent["body"])
```

### Step 2: Get Sub-Issues

```python
sub_issues = github_issue_read(method="get_sub_issues", issue_number=N)
```

### Step 3: Build Hierarchy Tree

```markdown
SPEC #N: [Title]
├── Task #[M1]: Phase 1 - [Description]
├── Task #[M2]: Phase 2 - [Description]
└── Task #[M3]: Phase 3 - [Description]
```

### Step 4: Identify Gaps

**For each phase in spec:**
- Check if corresponding sub-issue exists
- If missing: create via `create-sub-issue`

**For each sub-issue:**
- Check if it matches a phase
- If orphan (no matching phase): flag for review

### Step 5: Report in Chat

## Common Issues

| Issue | Resolution |
|-------|------------|
| Sub-issues missing for phases | Auto-create via `create-sub-issue` |
| Orphan sub-issues found | Flag for manual review |
| Hierarchy mismatch | Rebuild hierarchy tree |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `create-sub-issue`, `link-sub-issue`