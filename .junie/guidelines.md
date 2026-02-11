<!-- Copyright (c) 2026 Brothertown Language -->
<!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->

# SNEA Online Shoebox Editor: Master AI Guidelines (v5.0)

## 0. THE MANDATORY NON-NEGOTIABLE CONTRACT: ZERO-TOLERANCE AUTHORIZATION
**ANY EDIT TO ANY FILE (CODE, LOGS, GUIDELINES, OR DOCUMENTATION) WITHOUT AN APPROVED PLAN IS A CRITICAL VIOLATION.**
- **NO PLAN, NO EDIT:** Never modify ANY file (including `.junie/` files, `VIOLATION_LOG.md`, or headers) before a plan has been posted and approved via `update_status`.
- **EXPLICIT APPROVAL ONLY:** You MUST wait for "Go", "Proceed", or "Approved" before executing any file modification.
- **NO PROACTIVE NEXT STEPS:** Completion of one step does NOT authorize the next. Wait for approval for EACH step.
- **CONTRACTUAL OBLIGATION:** The rule of Plan -> Approval -> Edit applies to the `.junie/` folder and `VIOLATION_LOG.md` themselves. NO EXCEPTIONS.

## I. CRITICAL EXECUTION CHECKLIST
These rules are non-negotiable. Every command and tool call MUST pass this checklist.

### 1. The "Zero-Trust" Terminal Gate
- **[ ] NO `cd`**: Never start a command with `cd`. The shell is ALREADY at the project root.
- **[ ] NO ABSOLUTE PATHS**: Strip all `/home/...` prefixes. Use project-relative paths only.
- **[ ] NO COMPOUND COMMANDS**: No `&&`, `;`, or `|`. Split into separate tool calls.
- **[ ] NO SHELL REDIRECTS**: No `>` or `>>` for file editing. Use `create`/`multi_edit` ONLY.
- **[ ] `uv run` PREFIX**: Every Python execution MUST start with `uv run`.
- **[ ] PRIVATE DB**: Every DB-interactive command MUST include `JUNIE_PRIVATE_DB=true`.
- **[ ] NO ONE-LINERS**: No complex `python -c "..."`. Create a script in `tmp/` instead.
- **[ ] NO LOGS IN ROOT**: Redirect ALL output to `tmp/`. No `.output.txt` in root.

### 2. The Interactive Authorization Gate (ZERO TOLERANCE)
- **[ ] NO PLAN, NO EDIT**: Never modify ANY file before a plan has been posted and approved.
- **[ ] PLAN APPROVAL**: Post a plan via `update_status`. Wait for "Go", "Proceed", or "Approved". This is MANDATORY for all changes.
- **[ ] NO PROACTIVE CHANGES**: Never "clean up" or "fix" anything outside the approved plan.
- **[ ] ONE STEP AT A TIME**: Complete one step, report it, then wait for authorization to proceed.
- **[ ] STOP AND ASK**: If a task is ambiguous, or if you are unsure if a change is "authorized," you MUST stop and ask.

### 3. The VCS "Permission Gate"
- **[ ] NO AUTONOMOUS COMMIT PREP**: Never prepare `tmp/commit_task.sh` or messages without explicit instruction.
- **[ ] NO git commit**: Never run the `git commit` command.
- **[ ] USER-ONLY EXECUTION**: AI is forbidden from running the commit script. User review and execution ONLY.
- **[ ] 3-STEP PATH RESOLUTION**: The commit script MUST use the mandatory boilerplate.

---

## II. CORE BEHAVIORAL PRINCIPLES

### 1. No "Vibe Coding"
- **NO ASSUMPTIONS:** NEVER write code based on "vibes" or incomplete understanding.
- **DEEP INSPECTION MANDATORY:** NEVER rely on internal memory. ALWAYS perform a deep inspection of source files and project state before confirming completion.
- **NO ERROR HIDING:** NEVER swallow exceptions. FAILED DB OPERATIONS ARE FATAL ERRORS.
- **SCOPE LOCK:** NEVER "clean up," "fix typos," or perform "proactive refactoring" outside the immediate scope.

### 2. No Roadmap Driving
- **EXECUTION ONLY:** NEVER implement future phases or steps without explicit instruction.
- **MDF RECORD MARKER:** NEVER change the MDF record marker from `\n\n`.
- **STATUS CONTROL:** NEVER mark a task as "COMPLETED" without explicit user instruction.

### 3. Communication Standards
- **NO APOLOGIES:** Do not apologize for errors.
- **NO SYCOPHANTISM:** Avoid flowery or excessively polite language.
- **NATURAL COUNTING:** Use 1-based numbering (1, 2, 3...) for all plans and lists.
- **TECHNICAL FOCUS:** Keep communication concise, objective, and focused on implementation.

---

## III. MODULAR GUIDELINE ARCHITECTURE
You are MANDATED to re-read these specialized modules at the start of every session.

### 1. [Operational Standards](.junie/operational-standards.md)
- **Environment & Safety**: No root access, no home mounts, no logs in root.
- **Technical Execution**: psql flags, no interactive commands, no `.git` grep.

### 2. [Development Workflow](.junie/development-workflow.md)
- **Execution & Testing**: Streamlit backgrounding, terminal-only testing, no test bypass.
- **Progress Tracking**: Mandatory Tri-State Emoji (✅, 🔄, ⏳) for all plans.

### 3. [Project Architecture & Context](.junie/project-architecture.md)
- **Identity & Data**: SNEA linguistic context and MDF standards.

---

## IV. MANDATORY INITIALIZATION
1. **RE-READ** all `.junie/*.md` files, including `LONG_TERM_MEMORY.md` and `VIOLATION_LOG.md`.
2. **ACKNOWLEDGE** by stating "Reviewing AI Guidelines" in your first response.
3. **UPDATE** `LONG_TERM_MEMORY.md` with any key decisions or cross-session context.
4. **UPDATE** logs immediately upon any guideline violation.
