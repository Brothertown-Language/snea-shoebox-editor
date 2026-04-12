# Task: create

## Purpose

Create an implementation plan from an approved spec.

## Prerequisites

1. Approved spec (verified by approval-gate)
2. Spec stored as GitHub Issue
3. Spec has explicit approval (`approved` or `go`)

## Creation Steps

1. **Read approved spec:**
   - Query GitHub Issue for spec content
   - Extract objectives, constraints, success criteria
   - Identify affected files and dependencies

2. **Map file structure:**
   - List all files that will be created or modified
   - Define each file's responsibility
   - Ensure decomposition has clear boundaries

3. **Plan phase structure by judgment:**
   - Determine which phases the plan needs
   - Organize by concern flow, not template order
   - Write prose for phase descriptions

4. **Define tasks within each phase:**
   - Each task uses the TDD step structure
   - Each step is one action (2-5 minutes)
   - Exact code, exact commands, exact file paths

5. **Write plan document header:**
   - Goal, Architecture, Tech Stack

6. **Create plan issue:**
   - Title: `[PLAN] <Feature Name>`
   - Body: Plan with header, file structure, phases with TDD tasks
   - Link to parent spec (sub-issue)

7. **Self-review:**
   - Spec coverage check
   - Placeholder scan
   - Type consistency check
   - Fix any issues found

8. **Validate plan:**
   - Check for TBD/TODO placeholders
   - Verify all steps are actionable
   - Verify success criteria are testable