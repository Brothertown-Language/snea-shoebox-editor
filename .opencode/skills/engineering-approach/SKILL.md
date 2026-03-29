---
name: engineering-approach
description: Engineering principles and checklists for proper development methodology. Invoked when implementing specs to ensure understanding, design, verification, and scope discipline.
license: MIT
compatibility: opencode
---

# Engineering Approach Checklist

## Core Principles

1. **Understand Before Solving**
   - Read all relevant code before proposing changes
   - Understand the "why" not just "what"
   - Identify stakeholders and their needs

2. **Design Before Implementing**
   - Document the approach in the spec
   - Consider multiple solutions and tradeoffs
   - Get approval on approach before coding

3. **Verify Before Declaring Complete**
   - Run all tests manually
   - Check for edge cases
   - Verify against all success criteria
   - Update documentation

4. **Communicate Changes**
   - Post comments when changes happen (PR created, task completed)
   - DO NOT post comments when creating issues

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

## Anti-Patterns to Avoid

- Jumping straight to implementation without design
- Surface-level analysis without deep understanding
- Missing edge case consideration
- Skipping documentation updates
- Declaring complete without verification
- Posting comments when creating issues
- Being pedantic in communications
- Adding features not in the spec
- Starting work without explicit approval
- "While I'm here" refactoring
- Implementing "nice to haves"

## Requirements Analysis Checklist

Before any implementation:

- [ ] Problem statement documented with full context
- [ ] Constraints and assumptions identified
- [ ] Success criteria are testable and measurable
- [ ] Edge cases identified and documented
- [ ] Dependencies and integrations analyzed
- [ ] Risk assessment completed

## Design Phase Checklist

Before coding:

- [ ] Explored codebase for existing patterns
- [ ] Identified reusable components
- [ ] Documented design decisions
- [ ] Considered alternatives
- [ ] Documented tradeoffs
- [ ] Obtained approval on approach

## Implementation Phase Checklist

During coding:

- [ ] Following spec exactly - no additions
- [ ] Using established patterns from codebase
- [ ] Writing tests alongside implementation
- [ ] Updating documentation as needed

## Verification Phase Checklist

Before declaring complete:

- [ ] All tests pass manually
- [ ] Edge cases verified
- [ ] Success criteria validated
- [ ] Documentation updated
- [ ] No scope creep introduced

## Invocation

Use this skill when:
- Starting implementation of an approved spec
- Before creating a PR
- During code review to check for scope creep
- After completing work to verify completeness

Example: `/skill engineering-approach`