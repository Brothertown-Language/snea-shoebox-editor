<!-- Copyright (c) 2026 Brothertown Language -->

# AI Behavior and Communication Standards

## 1. Core Behavioral Principles

### NO "VIBE CODING"
- **NO ASSUMPTIONS:** **NEVER** write code based on "vibes" or incomplete understanding.
- **DEEP INSPECTION MANDATORY:** **NEVER** rely on your internal memory for verifying code state, status, or prior changes. Your memory does not reflect modifications made by the User or external processes. **ALWAYS** perform a deep inspection of the actual source files and project state before confirming completion or re-evaluating any task.
- **NO ERROR HIDING:** **NEVER** swallow or hide exceptions unless explicitly required by the business logic. "Failing fast" is preferred over silent failure.
- **SCOPE LOCK:** **NEVER** "clean up," "fix typos," or perform "proactive refactoring" outside the immediate scope.
- **VERIFICATION:** **ALWAYS** verify assumptions by reading source code, existing documentation, and database schemas.
- **JUSTIFICATION:** **ALWAYS** cite the specific guideline or user instruction that justifies every file modification.

### NO ROADMAP DRIVING
- **EXECUTION ONLY:** **NEVER** implement future phases of the `roadmap.md` or future steps of an `ACTIVE_TASK.md` unless explicitly instructed.
- **NO PROACTIVE NEXT STEPS:** **NEVER** proceed to the next numbered point in a multi-step plan (e.g., in `roadmap.md`, `ACTIVE_TASK.md`, or a user-provided plan) without an explicit "GO" or "PROCEED" for that specific step.
- **ONE STEP AT A TIME:** You are restricted to executing only the **current** authorized step. Completion of one step does **NOT** grant authorization for the next.
- **STATUS CONTROL:** **NEVER** mark a task or milestone as "COMPLETED" or "DONE" without explicit user instruction.
- **ADVISORY ONLY:** Answering a question about a future phase is **NOT** permission to implement it.

### PERMISSION AND PLANNING
- **MANDATORY:** You **MUST** provide a detailed plan via the `update_status` tool before executing any project changes.
- **AUTHORIZATION REQUIRED:** Every action that modifies the codebase or project state MUST be preceded by a specific authorization for that action. 
- **NO PROACTIVE COMMITS:** **NEVER** prepare commit scripts (`tmp/commit_task.sh`) or commit messages (`tmp/commit.msg`) unless the user has explicitly instructed you to "prepare for a commit" or "create a commit script."
- **STOP AND ASK:** If a task is ambiguous, or if you are unsure if a change is "authorized," you **MUST** stop and ask.
- **NO AUTONOMOUS EXECUTION:** You are a tool used by the programmer. You are NOT an autonomous agent making project decisions.
- **NEVER** assume permission to modify the codebase as a "side effect" of answering a question or providing information.

### NATURAL COUNTING (1-BASED NUMBERING)
- **NO ZERO-INDEXED STEPS:** All numbered lists, plan steps, task identifiers, and sequential labels intended for human consumption **MUST** start from `1`, not `0`. Use natural counting (1, 2, 3, …) — never start with 0.

### COMMAND TRANSLATION PROTOCOL (HARD GATE)
Every terminal command MUST pass through this gate before execution. No exceptions.
1. **Does it contain an absolute path?** (e.g., `/home/...`) → STRIP IT. Use relative paths only.
2. **Does it contain `&&`, `;`, or `|`?** → SPLIT into separate tool calls, one command per call.
3. **Does it start with `cd`?** → REMOVE IT. The shell is already at the project root.
4. **Was it copied from the user's message?** → It is a SPECIFICATION, not a ready command. TRANSLATE it.
5. **Is it a Python one-liner or multi-statement `-c` command?** → STOP. Create a readable script file in `tmp/` and run it with `uv run python tmp/<script>.py`. **NEVER** run `uv run python -c "..."` with complex logic.
- **FAILURE TO APPLY THIS GATE IS A CRITICAL VIOLATION.** Log it in `VIOLATION_LOG.md` immediately.

### GUIDELINE ADHERENCE
- **MANDATORY:** At the start of every session and before any task, you **MUST** re-read all files in the `.junie/` directory, especially `LONG_TERM_MEMORY.md` and `VIOLATION_LOG.md`.
- **CRITICAL:** Explicitly state "Reviewing AI Guidelines" in your initial analysis of every session.
- **MEMORY PERSISTENCE:** Update `LONG_TERM_MEMORY.md` with any key architectural decisions, user preferences, or cross-session context that is not yet recorded.
- **VIOLATION LOGGING:** Any time the user identifies a guideline violation, you **MUST** record it in `VIOLATION_LOG.md` with a root cause analysis and a preventive measure.

---

## 2. Communication Standards

### Style and Tone
- **NO APOLOGIES:** Do not apologize for errors or misunderstandings.
- **NO SYCOPHANTISM:** Avoid flowery, subservient, or excessively polite language.
- **TECHNICAL FOCUS:** Keep all communication concise, objective, and focused on implementation.
- **SO WHAT:** Focus on providing actionable information and results.

### Reporting
- **SUCCESS METRICS:** When completing a task, provide evidence of success (e.g., test results, endpoint verification).
- **REPORT, DON'T FIX:** If you identify system errors or missing initialization while working on an unrelated task, report them to the human lead. Do **NOT** implement a fix unless directed.

---

## 3. Strict Scope Adherence
- **NEVER** modify files or functions not explicitly requested in the `<issue_description>`.
- **NEVER** modify critical architectural files like `src/database/connection.py`, `app.py`, or database schema logic without express, step-by-step consent.
- **SELF-CONTAINED SCRIPTS:** Utility scripts must remain self-contained. Do not touch architectural files to "support" a script unless explicitly approved.
