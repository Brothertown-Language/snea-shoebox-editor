# Task: post-completion

## Purpose

Post completion comment to GitHub Issue when task is finished — ONLY if the comment is substantive (conveys information stakeholders need to understand what changed or why).

## Entry Criteria

- Task completed successfully
- All sub-tasks finished
- Issue number identified
- Comment content is substantive per the Substantive Comment Gate in SKILL.md

## Exit Criteria

- If substantive: completion comment posted to GitHub Issue with summary, outcome, and byline
- If not substantive: comment skipped (no posting)

## Procedure

### Step 1: Substantiveness Gate

Before posting, evaluate: Does this comment convey information a stakeholder needs to understand what changed or why?

| If | Action |
|----|--------|
| Comment explains substantive change stakeholders need to know | **Post with byline** |
| Comment is merely "Task complete" or status update | **SKIP — do not post** |
| Comment explains what changed during closure (beyond status) | **Post with byline** |

### Step 2: Gather Completion Information

What was accomplished?
What changed for stakeholders?
Were there any blockers resolved?

### Step 3: Format Completion Comment

See `format-comment` task for template.

### Step 4: Post Comment (if substantive)

```python
github_add_issue_comment(
    owner=GIT_OWNER,
    repo=GIT_REPO,
    issue_number=N,
    body=formatted_comment
)
```

### Step 5: Note Completion

If all tasks complete from this spec, include "All tasks complete from this specification."

## Common Issues

| Issue | Resolution |
|-------|------------|
| Non-substantive content | Skip posting entirely — progress goes to chat only |
| Missing summary | Add 1-2 sentence impact |
| No outcome | State what changed |
| Premature completion | Verify all sub-tasks done |

## Context Required

- Session values: GIT_OWNER, GIT_REPO
- Related tasks: `format-comment`