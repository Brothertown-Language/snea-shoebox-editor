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
   - DO NOT post comments for non-substantive updates (cross-references, origin links, STATUS updates)

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
- [ ] **All temp files in `./tmp/` ONLY** — never `/tmp/` or project root

## Pre-Implementation Verification Checklist

Before writing ANY implementation code:

1. **Verify API Signatures**
   - [ ] Check official documentation for correct parameters
   - [ ] Use `srclight_get_signature` or type hints for function signatures
   - [ ] Confirm library version matches documentation

2. **Verify Environment Variables**
   - [ ] Check `.env.example` for correct names
   - [ ] Confirm from config documentation
   - [ ] Use exact names (no guessing)

3. **Verify Configuration Formats**
   - [ ] Check schema definitions
   - [ ] Review example configs
   - [ ] Confirm field names and types

4. **Document Verification Source**
   - [ ] Note where you verified (docs URL, source file, etc.)
   - [ ] Include verification reference in implementation comments if helpful

## During Implementation Verification

When actively writing code:

1. **Before EACH API Call:**
   - [ ] Verify parameter names from official docs or source
   - [ ] Confirm method/function exists (no invented APIs)
   - [ ] Check return types match expected usage

2. **Before EACH Environment Variable:**
   - [ ] Confirm exact name from `.env.example` or docs
   - [ ] Verify handling of missing values (required vs optional)

3. **Before EACH Library Import:**
   - [ ] Confirm import path matches current library version
   - [ ] Check for deprecation warnings in migration guides

4. **MCP Tool Usage:**
   - [ ] Use PyCharm MCP for file operations (not read/write/edit tools)
   - [ ] Use srclight for Python semantic analysis
   - [ ] Use notebook MCP for `.ipynb` files (never raw file tools)

5. **Temp File Location:**
   - [ ] All temp files go to `./tmp/` — NEVER `/tmp/` system temp
   - [ ] NEVER create temp files at project root
   - [ ] Use `./tmp/` for investigation scripts, test outputs, scratch files

## Post-Implementation Review

After implementation, before marking complete:

1. **Self-Review:**
   - [ ] All API calls verified against docs
   - [ ] All environment variables match config
   - [ ] No assumed or guessed parameter names
   - [ ] Library usage matches current version

2. **Evidence of Verification:**
   - [ ] Comments reference documentation sources where helpful
   - [ ] Complex APIs include doc references for future maintainers

3. **Temp File Cleanup:**
   - [ ] All temp scripts removed from `./tmp/` (unless intentionally cached)
   - [ ] No temp files left at project root
   - [ ] `ls ./tmp/` shows only intentional persistent files

## Verification Phase Checklist

Before declaring complete:

- [ ] All tests pass manually
- [ ] Edge cases verified
- [ ] Success criteria validated
- [ ] Documentation updated
- [ ] No scope creep introduced
- [ ] **Temp files cleaned up** — no `temp_*.py` or `*.json` left in `./tmp/`
- [ ] **No temp files at project root** — confirm with `ls *.py *.json 2>/dev/null`

## Invocation

Use this skill when:
- Starting implementation of an approved spec
- Before creating a PR
- During code review to check for scope creep
- After completing work to verify completeness

Example: `/skill engineering-approach`