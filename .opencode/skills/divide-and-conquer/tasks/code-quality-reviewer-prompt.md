# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

**Source attribution:** This prompt pattern is adapted from [obra/superpowers `subagent-driven-development`](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development).

**Dispatch AFTER spec compliance review passes. Never dispatch code quality review before spec compliance is ✅.**

```
Task tool (general-purpose):
  description: "Review code quality for Task N"
  prompt: |
    You are reviewing code quality for an implementation that has passed spec compliance review.

    ## Worktree Context

    worktree.path: <worktree.path value or 'not set'>

    If worktree.path is set, ALL file reads MUST prefix paths with worktree.path/. ALL bash commands MUST use workdir=worktree.path. If worktree.path is not set, use project root.

    ## What Was Requested

    [FULL TEXT of task requirements]

    ## What Was Implemented

    [From implementer's report]

    ## Changes to Review

    Base commit: [commit before task]
    Head commit: [current commit]

    Review the git diff between these commits.

    ## Code Quality Assessment

    ### Critical (Must Fix)
    - Security vulnerabilities
    - Data loss risks
    - Race conditions
    - Breaking changes to public APIs
    - Missing error handling for expected failure modes

    ### Important (Should Fix)
    - Poor names that don't communicate intent
    - Functions that are too long or do too much
    - Missing or insufficient tests for critical paths
    - Dead code or unused imports
    - Magic numbers without named constants
    - Inconsistent error handling patterns

    ### Minor (Nice to Have)
    - Style nitpicks
    - Minor naming improvements
    - Documentation improvements
    - Minor test improvements

    ## File Decomposition Review

    In addition to standard code quality, check:
    - Does each file have one clear responsibility with a well-defined interface?
    - Are units decomposed so they can be understood and tested independently?
    - Is the implementation following the file structure from the plan?
    - Did this implementation create new files that are already large, or significantly
      grow existing files? (Don't flag pre-existing file sizes — focus on what this
      change contributed.)

    ## Branch Model Context

    This project uses the `feature→dev→main` three-branch workflow:
    - Verify changes are on the correct feature branch (spec/ or feature/)
    - Verify no accidental changes to main or dev branches
    - Verify commit messages follow project conventions

    ## Report Format

    **Strengths:** [What's done well]

    **Issues:**
    - Critical: [Must fix before proceeding]
    - Important: [Should fix, may proceed with justification]
    - Minor: [Nice to have]

    **Assessment:** APPROVED | NEEDS_CHANGES

    If NEEDS_CHANGES, list specific items that must be fixed. The implementer will
    fix these and re-dispatch this reviewer.

    If all issues are Minor only, you MAY approve with suggestions noted.
    If ANY Critical or Important issues exist, you MUST mark NEEDS_CHANGES.
```