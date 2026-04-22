# Task: sc-precision

## Purpose

Verify that every success criterion in the audited spec includes executable verification commands, semantic intent, and no vague verification methods.

## Checks

1. **Executable verification command** — Each SC has a shell command or test assertion with exact expected value (per `140-planning-spec-creation.md` mandate)
2. **Semantic intent** — Each SC has a prose annotation explaining why the exact value matters and what semantic distinction it represents (per `spec-creation/tasks/write.md` Step 3)
3. **No vague verification methods** — No SC uses "check exit code" without specifying the expected code, "validate JSON schema" without listing required fields, etc.

## Classification Rules

| Finding | Classification | Rationale |
| -- | -- | -- |
| Missing semantic intent where the intent is unambiguous from context | **Auto-fix** | Agent can add a brief "why" explanation safely — the distinction is clear from the criterion text |
| Vague verification method where the exact expected value is inferable | **Conditional** | Agent rewrites with executable command, but must confirm the inferred exact value is correct |
| Ambiguous semantic distinction between specified value and similar value | **Flag-for-review** | Developer judgment required — agent cannot determine the correct value without domain context |

## Finding Format

```
Subtask: sc-precision
Finding: [VAGUE-VERIFICATION|MISSING-SEMANTIC-INTENT|VAGUE-VERIFICATION-AMBIGUOUS] - [SC ID and summary]
Location: Success criteria table, row [SC ID]
Context: [why this matters for this specific spec]
Classification: [auto-fix|conditional|flag-for-review]
Fix Action: [what was done OR "flagged for review"]
Severity: [HIGH|MEDIUM|LOW]
```
