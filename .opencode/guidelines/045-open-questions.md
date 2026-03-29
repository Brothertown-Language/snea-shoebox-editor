# Open Questions in Plans

Plans with open questions must have all questions answered before any part of the plan can be implemented.

## 1. Mandatory Q&A Phase

When a plan/spec contains an "Open Questions" section:

1. **STOP immediately** — SILENTLY HALT and do not implement any part of the plan. Do NOT prompt for answers.
2. **ASK each question** one at a time using the interviewer approach
3. **WAIT for user answer** before proceeding to the next question
4. **UPDATE the plan** with the answered question before asking the next

## 2. Interviewer Approach

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

## 3. Dynamic Question Management

- **Add new questions** if prior answers reveal new ambiguity
- **Update pending questions** if prior answers change their context
- **Remove questions** if prior answers make them obsolete
- Track the question count: "Question X of N" must always be accurate

## 4. Complete Before Implementation

Implementation is BLOCKED until:
- All open questions have documented answers
- The plan file reflects all decisions
- User confirms "proceed with implementation"

## 5. Example Flow

```
Agent: "Found plan with 3 open questions. Starting Q&A..."

## Open Question 1 of 3

Should we use NCBI E-utilities `esearch` with `field=MeSH` or the dedicated MeSH API for term validation?

Options:
a) Use `esearch` with retmax=1 per MeSH term (simpler, uses existing client)
b) Use dedicated MeSH API (more accurate, requires new integration)
c) Custom answer

Your choice:

User: a

Agent: "Using `esearch` with retmax=1 per MeSH term - simpler and uses existing PubMedClient."

[Updates plan with decision]

## Open Question 2 of 3

[Next question...]
```

## 6. Boundary Rule

🚫 **NEVER start implementation** while open questions remain unanswered.
✅ **ALWAYS complete Q&A first**, then get explicit "approved" confirmation.
