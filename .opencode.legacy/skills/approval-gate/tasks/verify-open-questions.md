# Task: verify-open-questions

## Purpose

Check for unresolved open questions in the spec before implementation.

## Preconditions

- Authorization verified
- Blockers checked

## Postconditions

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

## Q&A Workflow for Open Questions

When a plan/spec contains an "Open Questions" section:

1. **STOP immediately** — SILENTLY HALT and do not implement any part of the plan. Do NOT prompt for answers.
2. **ASK each question** one at a time using the interviewer approach
3. **WAIT for user answer** before proceeding to the next question
4. **UPDATE the plan** with the answered question before asking the next

### Interviewer Approach

Present each question in this format:

```
## Open Question X of N

[Question text from plan]

Options:
a) [Option A]
b) [Option B]
c) Custom answer: ______

Your choice:
```

After receiving the answer:
1. Acknowledge the answer
2. Explain how it affects the plan (if applicable)
3. Update the plan file with the decision
4. Proceed to the next open question

### Dynamic Question Management

- **Add new questions** if prior answers reveal new ambiguity
- **Update pending questions** if prior answers change their context
- **Remove questions** if prior answers make them obsolete
- Track the question count: "Question X of N" must always be accurate

## Boundary Rule

🚫 **NEVER start implementation** while open questions remain unanswered.
✅ **ALWAYS complete Q&A first**, then get explicit "approved" confirmation.

## Context Required

- Related tasks: `verify-authorization`, `verify-codebase`
