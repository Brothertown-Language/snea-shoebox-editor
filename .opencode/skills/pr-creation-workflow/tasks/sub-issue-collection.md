# Task: sub-issue-collection

## Purpose

Fetch sub-issues for a parent issue and build the autoclose list for the PR body.

## Procedure

### Detect Branch Type

First, detect whether this is a single-issue or batch PR:

```bash
# Check if batch state file exists
ls .opencode/tmp/batch-*.md 2>/dev/null

# If exists → batch PR format
# If not exists → single/multi-task PR format
```

**Note:** GitHub autoclose (`Fixes #N`/`Closes #N`) does NOT trigger for PRs merging into `dev`. The cleanup task (`git-workflow --task cleanup`) is the sole closure mechanism. PR body keywords are informational labels for human readers.

### Single-Task Spec

If the spec has no sub-issues (single-task), include only the parent issue in the PR body:

```
Fixes #<parent>
```

### Multi-Task Spec with Sub-Issues

1. **Fetch sub-issues:**
   ```python
   sub_issues = github_issue_read(method="get_sub_issues", issue_number=<parent>)
   ```

2. **Build autoclose list:** parent + all sub-issues
   ```python
   autoclose_issues = [<parent>] + [sub["number"] for sub in sub_issues]
   ```

3. **Include ALL issues in PR body:**
   ```markdown
   ## Summary
   <description of what changed>

   Fixes #<parent>
   Fixes #<child1>
   Fixes #<child2>
   ```

### Batch PR

For batch PRs (assembled from multiple issues via `assemble-batch`):

1. **Read batch state file** (`.opencode/tmp/batch-*.md`) to get list of all issues in the batch
2. **Build both sections:**
   - `## Batch Issues` section listing each issue with its description
   - `Fixes #N` annotations for all issues at the bottom

```markdown
**Summary:**

<1-2 sentences describing the overall impact of the batch>

**Outcome:** <What changed for stakeholders>

## Batch Issues

#660 — Add pre-implementation analysis task
#662 — Fix batch branch squash verification
#621 — Collapse executing-plans into divide-and-conquer

Fixes #660
Fixes #662
Fixes #621
```

### Multi-Task Spec WITHOUT Sub-Issues

If `get_sub_issues` returns empty for a multi-task spec, this is a CRITICAL VIOLATION — sub-issues should have been created before implementation. Halt and create sub-issues first.

## Example PR Bodies

**Single-task:**
```markdown
## Summary
Add OAuth2 authentication to the API layer.

Fixes #42
```

**Multi-task:**
```markdown
## Summary
Implement user authentication feature: database schema, API endpoints, and UI components.

Fixes #100
Fixes #101
Fixes #102
Fixes #103
```

**Batch:**
```markdown
**Summary:**

Unified five approved issues into a single batch implementation, eliminating forked execution paths.

**Outcome:** All approvals now follow one consistent workflow: sub-issue expansion → assemble-batch → batch branch → single PR.

## Batch Issues

#660 — Add pre-implementation analysis task
#662 — Fix batch branch squash verification
#621 — Collapse executing-plans into divide-and-conquer

Fixes #660
Fixes #662
Fixes #621
```

## After PR Creation

- Report URL in chat ONLY (never to GitHub Issues)
- HALT — wait for human to merge
- Never merge PRs — HUMAN-ONLY operation