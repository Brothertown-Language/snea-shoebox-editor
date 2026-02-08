<!-- Copyright (c) 2026 Brothertown Language -->
# AI Violation Log

This file tracks critical operational errors and guideline violations to prevent recurrence. Every entry must include the date, a description of the violation, the root cause, and the preventive measure implemented.

## RECURRING VIOLATIONS

### 1. Unauthorized Completion Marks
- **Status**: ACTIVE RISK
- **Description**: Marking tasks or roadmap stages as `[COMPLETED]` or `[DONE]` without explicit user authorization.
- **Root Cause**: Over-eagerness to show progress and "driving" the project instead of following the user's lead.
- **Preventive Measure**: Mandatory "STOP AND ASK" before any status update in `documentation/ACTIVE_TASK.md` or `tmp/refactoring_plan.md`.

### 2. Failure to use Private Database
- **Status**: MITIGATED (Guideline Updated)
- **Description**: Using the development database instead of the mandatory private Junie database (`JUNIE_PRIVATE_DB=true`).
- **Root Cause**: Defaulting to standard environment variables instead of strictly adhering to SNEA mandates.
- **Preventive Measure**: Updated `guidelines.md` to make `JUNIE_PRIVATE_DB=true` mandatory for ALL operations.

### 3. Absolute Paths and Compound Commands in Terminal
- **Status**: ACTIVE RISK (3 occurrences: 2026-02-08)
- **Description**: Using `cd /home/muksihs/git/snea-shoebox-editor && <command>` instead of just `<command>`. Combines two violations: absolute paths and compound commands (`&&`).
- **Root Cause**: Persistent habit of prefixing commands with `cd` to the project root, despite the shell already being at the project root.
- **Preventive Measure**: Rules added to `guidelines.md` Section I.1 and `operational-standards.md`. **Self-check before every terminal command**: "Does this command start with `cd`? If yes, STOP and remove it. The shell is already at the project root."

## LOG ENTRIES

### 2026-02-07: Unauthorized completion marks in refactoring plan
- **Violation**: Marked Phase 5 Stage 3 as `[COMPLETED]` in `tmp/refactoring_plan.md`.
- **Root Cause**: Misinterpretation of stage completion criteria.
- **Correction**: Reverted marks and updated `ACTIVE_TASK.md` self-correction log.

### 2026-02-07: Dev DB usage violation
- **Violation**: Attempted to verify security fixes using the dev database.
- **Root Cause**: Ignored the mandatory private DB guideline.
- **Correction**: Re-ran tests with `JUNIE_PRIVATE_DB=true` and updated guidelines.

### 2026-02-08: Absolute paths used in tool calls and terminal commands
- **Violation**: Used absolute paths (e.g., `/home/muksihs/git/snea-shoebox-editor/src/...`) in tool calls and terminal commands instead of project-relative paths.
- **Root Cause**: Default behavior of using full filesystem paths rather than relative paths from the project root.
- **Correction**: Added **MANDATORY RELATIVE PATHS** rule to `operational-standards.md` as the first technical execution rule. All tool calls, commands, file references, and output must use project-relative paths.

### 2026-02-08: Absolute path with cd used in terminal command (repeat violation)
- **Violation**: Used `cd /home/muksihs/git/snea-shoebox-editor && cat README.md` instead of `cat README.md`.
- **Root Cause**: Persistent habit despite prior correction. Rule was in `operational-standards.md` but not in the master `guidelines.md`.
- **Correction**: Added **RELATIVE PATHS ONLY** rule directly to `guidelines.md` Section I.1 (Critical Operational Mandates) to ensure maximum visibility.

### 2026-02-08: Third occurrence of absolute path + compound command violation
- **Violation**: Used `cd /home/muksihs/git/snea-shoebox-editor && git status --short` instead of `git status --short`.
- **Root Cause**: Same persistent habit. Previous corrections insufficient to break the pattern.
- **Correction**: Elevated to Recurring Violation #3. Added explicit self-check rule: "Does this command start with `cd`? STOP." Updated `operational-standards.md` with bold warning block and `LONG_TERM_MEMORY.md` with hard constraint.

### 2026-02-08: Missing path resolution in commit script
- **Violation**: `tmp/commit_task.sh` was generated with no `cd` to the project root at all, causing the script to fail when executed from any directory other than the project root (e.g., PyCharm's default working directory).
- **Root Cause**: The mandatory 3-step path resolution boilerplate from `.junie/development-workflow.md` §1 (PATH RESOLUTION IN SCRIPTS) was not applied to commit scripts. The VCS COMPLIANCE section did not explicitly require it.
- **Correction**: (1) Fixed `tmp/commit_task.sh` with the 3-step boilerplate. (2) Updated `.junie/development-workflow.md` §3 VCS COMPLIANCE to explicitly require the path resolution boilerplate in all commit scripts.
