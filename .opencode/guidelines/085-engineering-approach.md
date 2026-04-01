# Engineering Approach Mandate

> **See:** `/skill engineering-approach` for detailed checklists and anti-patterns.

## Core Principles

1. **Understand Before Solving** — Read all relevant code before proposing changes. Understand the "why" not just "what". Identify stakeholders and their needs.

2. **Design Before Implementing** — Document the approach in the spec. Consider multiple solutions and tradeoffs. Get approval on approach before coding.

3. **Verify Before Declaring Complete** — Run all tests manually. Check for edge cases. Verify against all success criteria. Update documentation.

4. **Communicate Changes** — Post comments when changes happen (PR created, task completed). DO NOT post comments when creating issues. DO NOT post comments for non-substantive updates (cross-references, origin links, STATUS updates).

## Scope Discipline (Critical)

### No Feature Creep

- Implement ONLY what is specified in the approved spec
- No additions, enhancements, or "improvements" beyond scope
- No refactoring unless explicitly requested
- No unrelated fixes discovered during work (file separate issue)

### No Unapproved Work

- Never start implementation without explicit authorization
- "Should I do X?" is a question, not authorization
- Wait for clear "proceed" or "yes" before starting
- If unclear, ask - do not assume