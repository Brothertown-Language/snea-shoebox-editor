# Task: verify-open-questions

## Purpose

Check for unresolved open questions in the spec before implementation.

## Entry Criteria

- Authorization verified
- Blockers checked

## Exit Criteria

- All open questions resolved
- Ready to proceed with implementation

## Procedure

### Step 1: Check Spec for Open Questions

Read spec body for "Open Questions" section or `?` markers indicating unresolved items.

### Step 2: Verify Resolution

For each open question found:
- Verify answer is documented in spec
- Verify answer is not "TBD" or placeholder
- Document any unresolved questions

### Step 3: HALT if Unresolved

If ANY open questions remain unresolved:
- Post comment listing unresolved questions
- HALT and wait for answers

## Handling Open Questions

| Status | Action |
|--------|--------|
| All resolved | Proceed to implementation |
| Some unresolved | HALT and post questions |
| Answers unclear | Ask for clarification |

## Adversarial Verification: Question Resolution State

**Before trusting that open questions are unresolved, verify against ALL comments on the issue.** A question listed as "open" in the spec body may have been answered in a subsequent comment — without the spec body being updated.

### Verify Open Questions Against All Comments

```
issue = github_issue_read(method="get", issue_number=N)
comments = github_issue_read(method="get_comments", issue_number=N)

For each open question found in spec body:
  - Search ALL comments for answers or discussions resolving the question
  - Look for developer (MEMBER/OWNER/COLLABORATOR) responses that answer the question
  - If answer found in comments but not reflected in spec body → STRUCTURE-VIOLATION
    (auto-fix: note that question is resolved in comments, recommend spec update)
  - If no answer found in any comment → question is genuinely unresolved
```

**Evidence artifact:** `github_issue_read(method=get_comments)` search results showing whether answers exist for each open question.

### Verify Question Is Genuinely a Blocker

```
For each unresolved open question:
  - Is the question blocking implementation, or is it a design preference?
  - If implementation can proceed regardless of the answer → NOT a blocker
  - If the answer changes the implementation approach → IS a blocker
  - Do NOT treat all open questions as implementation blockers
```

**Evidence artifact:** Analysis of each question showing whether it blocks implementation.

### Verify No New Questions in Comments

```
comments = github_issue_read(method="get_comments", issue_number=N)

- Check ALL comments for questions not listed in the spec's "Open Questions" section
- Developer may have raised new questions in comments
- If new questions found → MISSING-ELEMENT (conditional: add to open questions)
```

**Evidence artifact:** Comment scan results showing any unlisted questions.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Question resolved in comments but spec says open | STRUCTURE-VIOLATION | auto-fix | Note resolution, recommend spec update |
| Question is non-blocking preference | VERIFICATION-GAP | auto-fix | Reclassify as non-blocking, proceed |
| New questions in comments not in spec | MISSING-ELEMENT | conditional | Add to open questions if blocking |
| Genuinely unresolved blocking question | — | — | Properly identified, HALT for answer |

## Context Required

- Related tasks: `verify-authorization`, `verify-codebase`
- `065-verification-honesty.md`: Verification claims must be backed by tool call evidence
- `spec-auditor --task ground-truth`: Adversarial verification model