# Task: qa

## Purpose

Handle non-spec issues by asking clarifying questions one at a time in chat. On resolution, post durable outcomes to the issue.

## Entry Criteria

- Triage selected the `qa` path
- Issue data gathered (body, comments, labels)

## Exit Criteria

- Clarifying questions asked one at a time in chat
- Resolution reached OR user ends Q/A
- Exec summary posted to issue (durable outcomes only)
- HALT after posting summary

## Q/A Depth Selection

Analyze content to determine depth:

| Content Type | Depth | Questions Cover |
|--------------|-------|-----------------|
| Simple bug report | Scope only | What's wrong, expected behavior, steps to reproduce |
| Feature with technical implications | Scope + feasibility | Above + constraints, edge cases, integration points |
| Feature idea that could become a spec | Scope + feasibility + scaffold | Above + offer to write a spec from the answers |

Output reasoning for the depth choice before starting Q/A.

## Procedure

### Step 1: Determine Q/A Depth

Analyze the issue content:

- Bug report language ("crash", "error", "broken") → scope only
- Feature request with technical detail → scope + feasibility
- Vague feature idea or "we should..." → scope + feasibility + scaffold offer

Announce the depth choice and reasoning in chat.

### Step 2: Generate Questions

Based on depth, prepare questions. **Ask ONE question at a time in chat.** Do NOT list all questions at once.

**Scope questions:**
- What is the expected behavior?
- What is the current (broken) behavior?
- What are the steps to reproduce?

**Feasibility questions (added for depth 2+):**
- Are there technical constraints?
- What edge cases should be considered?
- What existing systems does this integrate with?

**Scaffold offer (depth 3 only):**
- After scope + feasibility resolved, offer: "Would you like me to create a spec from these answers?"

### Step 3: Ask Questions One at a Time

For each question:
1. Ask in chat
2. Wait for user response
3. Follow up if the answer is unclear
4. Move to next question when satisfied

### Step 4: On Resolution, Compose Exec Summary

When Q/A resolves (or user ends it), compose a prose exec summary capturing:
- Decisions made during Q/A
- Clarifications that emerged
- Scope boundaries confirmed
- Any spec changes suggested

### Step 5: Post Exec Summary to Issue (Conditional)

Post the exec summary as an issue comment ONLY if it conveys substantive information stakeholders need. If the Q/A merely confirms what's already known or resolves minor clarification, skip the comment.

**Only post durable outcomes, NOT the Q&A chatter.** The back-and-forth in chat is operational; the issue comment is the record — but only if there's a meaningful record to create.

### Step 6: HALT

HALT after posting the summary. Wait for the developer to act on the outcomes.

## Edge Cases

| Case | Handling |
|------|----------|
| User doesn't respond to question | HALT; do not repeat or rephrase without prompting |
| User provides incomplete answer | Ask one targeted follow-up in chat |
| Q/A reveals the issue IS a spec | Stop Q/A, suggest re-triage to `audit` path |
| User says "never mind" or "closed" | Post summary noting cancellation, HALT |
| Multiple unrelated questions | Focus on most relevant first; note others for follow-up |

## Cross-References

- `000-critical-rules.md`: Q&A chatter goes to chat; durable outcomes go to issue
- `approval-gate`: If Q/A reveals authorization is needed, note it in summary