# Adversarial Verification Module

## Evidence Artifact Format

Every verification checkpoint in approval-gate tasks MUST produce a tool-call artifact demonstrating the verification was performed. Assertions without tool-call artifacts are verification honesty violations per `065-verification-honesty.md`.

### Required Format

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

### Evidence Rules

1. Every fact assertion about GitHub state, file existence, or code behavior MUST have a tool-call artifact
2. Cache invalidation: re-verify before significant actions, never trust cached values
3. Staleness rule: evidence from previous exchanges is stale; re-verify before acting
4. Single exchange window: tool-call evidence from the immediately preceding exchange MAY be trusted without re-verification

## Finding Classification

Findings from verification follow the three-tier model:

| Classification | When | Action |
|----------------|------|--------|
| auto-fix | Safe, mechanical correction (stale reference, wrong issue number) | Apply fix, note in evidence |
| conditional | Requires scope/safety check (authorization from wrong person, wrong issue) | Verify scope, then proceed if safe |
| flag-for-review | Requires domain judgment (conflicting authorization, ambiguous approval) | Report in findings, HALT for human review |

### Tier Actions

- **auto-fix**: Apply the fix directly, include in evidence table
- **conditional**: Verify scope and safety before applying; if safe, apply; if not, HALT
- **flag-for-review**: Report in findings, do NOT apply, HALT for developer review