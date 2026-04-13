# Task: qa

## Purpose

Handle non-bug, non-spec issues by asking clarifying questions one at a time in chat. Bug reports are routed to `analyze-and-spec` instead.

## Entry Criteria

- Triage selected the `qa` path
- Issue data gathered (body, comments, labels)
- Issue is NOT a bug report (bug reports go to `analyze-and-spec`)

## Exit Criteria

- Clarifying questions asked one at a time in chat
- Resolution reached OR user ends Q/A
- Exec summary posted to issue (durable outcomes only)
- HALT after posting summary

## Q/A Depth Selection

Analyze content to determine depth:

| Content Type | Depth | Questions Cover |
|--------------|-------|-----------------|
| Feature with technical implications | Scope + feasibility | Constraints, edge cases, integration points |
| Feature idea that could become a spec | Scope + feasibility + scaffold | Above + offer to write a spec from the answers |
| Vague or unclear request (not a bug) | Scope clarification only | What is being requested, expected outcome |

**Note:** Bug reports are NOT handled by this task. If bug language is detected during Q/A, stop and suggest re-triage to `analyze-and-spec`.

## Procedure

### Step 1: Determine Q/A Depth

Analyze the issue content:

- Feature request with technical detail → scope + feasibility
- Vague feature idea or "we should..." → scope + feasibility + scaffold offer
- Bug report language detected → STOP, suggest re-triage to `analyze-and-spec`

Announce the depth choice and reasoning in chat.

### Step 2: Generate Questions

Based on depth, prepare questions. **Ask ONE question at a time in chat.** Do NOT list all questions at once.

**Scope questions:**
- What is the expected behavior?
- What is the scope of this request?

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
| Q/A reveals the issue IS a bug | Stop Q/A, suggest re-triage to `analyze-and-spec` path |
| User says "never mind" or "closed" | Post summary noting cancellation, HALT |
| Multiple unrelated questions | Focus on most relevant first; note others for follow-up |

## Cross-References

- `000-critical-rules.md`: Q&A chatter goes to chat; durable outcomes go to issue
- `approval-gate`: If Q/A reveals authorization is needed, note it in summary
- `analyze-and-spec`: Bug reports are NOT handled by this task; redirect to `analyze-and-spec`