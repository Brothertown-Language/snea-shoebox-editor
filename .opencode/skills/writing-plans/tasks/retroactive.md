# Task: retroactive

## Purpose

Create a plan for an existing spec that does not yet have one.

## Procedure

1. **Query existing spec:**
   - Get spec from GitHub Issue
   - Check for linked plan (sub-issues)

2. **If no plan exists:**
   - Create plan from spec using hybrid approach (phases + TDD steps)
   - Include header, file structure, self-review
   - Link as sub-issue
   - HALT and wait for plan approval

3. **If plan exists:**
   - Validate plan (check for placeholders, TDD structure)
   - If invalid → Report issues
   - If valid → Proceed to implementation