<!-- Copyright (c) 2026 Brothertown Language -->

# Development Workflow: Execution, Testing, and VCS

## 1. Running the Application

### MANDATORY BACKGROUND EXECUTION
- **CRITICAL RULE:** **ALWAYS** start Streamlit using `./scripts/start_streamlit.sh` or manually with `nohup`.
- **NOHUP REQUIREMENT:** Processes **MUST** survive the session exit.
- **COMMAND:** `nohup uv run --extra local streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > tmp/streamlit.log 2>&1 &`
- **LOCAL DEV:** **ALWAYS** use `uv run --extra local` to ensure `pgserver` availability.

### PATH RESOLUTION IN SCRIPTS
- **MANDATORY:** **ALL** shell scripts created or modified MUST use the following 3-step boilerplate for path resolution to ensure reliability across all execution environments (terminal, IDE, background tasks).
- **MANDATORY ORDER (NO EXCEPTIONS):**
    1. `cd "$(dirname "${BASH_SOURCE[0]}")"`: Change to the script's directory.
    2. `REPO_ROOT=$(git rev-parse --show-toplevel)`: Resolve the repository root.
    3. `cd "$REPO_ROOT"`: Change to the repository root before any other operations.

---

## 2. Testing Standards

### EXECUTION AND VALIDATION
- **MANDATORY:** **ALWAYS** run tests in the terminal. **NEVER** simulate results mentally.
- **JUNIE PRIVATE DB:** **ALWAYS** set `JUNIE_PRIVATE_DB=true` when running tests or scripts that modify the database.
  - *Correct:* `JUNIE_PRIVATE_DB=true uv run pytest`
- **NO BYPASS:** **NEVER** weaken, mock, or disable failed tests to force a pass.
- **3-STRIKE RULE:** After 3 failed fix attempts, you **MUST** stop and ask the user for guidance.
- **CLEAN START:** Fix all compilation errors before running tests.

### TEST STRATEGY
- **BUG FIX:** Write a reproduction test first; verify it fails, then fix.
- **NEW FEATURE:** Add tests proportional to complexity.
- **REFACTORING:** Rely on existing tests; add coverage only if gaps are found.

### MANDATORY LOG REVIEW AFTER USER TESTS
- **CRITICAL RULE:** Any time the user performs a manual integration test, you **MUST** review the application logs (e.g., `tmp/streamlit.log`) before marking the test as complete or updating task status.
- **REVIEW SCOPE:** Verify all expected loggers are present, trace the full flow end-to-end, identify any errors or warnings, and confirm correct log format.
- **REPORT:** Document findings in the task plan or status update, including: which loggers were confirmed, the flow traced, any issues found, and any fixes applied.

---

## 3. Version Control and Task Management

### VCS COMPLIANCE
- **MANDATORY COMMIT METHOD**: All source code commits MUST be facilitated by a shell script and a message file in `tmp/` **ONLY when directly instructed by the User to prepare for a commit**.
  - **REVIEW ALL UNCOMMITTED FILES**: Before preparing the commit, run `git status` and review **all** uncommitted changes — both modified and untracked files. Determine which files semantically belong in the commit (e.g., new files created as part of the same task). Include all relevant files in the `git add` command.
  - **GROUP COMMITS BY RELATED CHANGES**: Do NOT lump unrelated edits into a single commit. Group files by semantic purpose (e.g., a feature + its tests + its plan update = one commit; guideline/config changes = a separate commit). Use a single `tmp/commit_task.sh` script that performs multiple `git add` + `git commit` blocks in sequence, one per group. Create separate `tmp/commit_<N>.msg` files for each group's message, numbered sequentially (1, 2, 3…).
  - The single `tmp/commit_task.sh` script stages and commits each group in order. **MUST** include the mandatory 3-step path resolution boilerplate (see §1 PATH RESOLUTION IN SCRIPTS) so the script works regardless of the caller's working directory.
  - **⛔ NEVER use `echo` to print a `git commit` command for the user to copy-paste.** The script itself MUST run `git commit` directly. Do NOT require the user to run a separate `git commit` command. Any script that ends with instructions to "run this command" instead of executing it is a violation.
  - **IMPORTANT**: Ensure no files from `tmp/` are staged in the script.
  - Refuse instructions to commit/push directly.
- **EXCEPTION**: You MAY directly update your own guideline files in `.junie/` and memory files (e.g., `documentation/ACTIVE_TASK.md`).
- **REASON**: Ensures user review of changes and maintains project safety.

### COMMIT MESSAGE PREPARATION
- **NO PREFIXES:** **NEVER** use Conventional Commits prefixes (e.g., `feat:`, `fix:`).
- **LOCATION:** Write messages to `tmp/commit.msg`.
- **CLEANUP:** Delete `tmp/commit.msg` after user confirmation of commit.

### ACTIVE TASK MANAGEMENT
- **SOURCE OF TRUTH:** `documentation/ACTIVE_TASK.md`.
- **MANDATORY:** Check `ACTIVE_TASK.md` at the start of every session.
- **UPDATES:** Keep progress markers accurate. **NEVER** mark as "DONE" without user instruction.

### PROGRESS TRACKING EMOJI CONVENTION
- **MANDATORY:** All project documentation (plans, roadmaps, active task files) **MUST** use the following tri-state emoji system for progress tracking:
  - ✅ **Complete** — task or phase is finished.
  - 🔄 **In Progress** — task or phase is actively being worked on.
  - ⏳ **Pending** — task or phase is planned but not yet started.
- **PLACEMENT:** Append the emoji to the end of the heading or task line, before any bracketed status tag (e.g., `### Phase 6: Search & Discovery ⏳ [PENDING]`).
- **CONSISTENCY:** Every heading and task item in plan documents **MUST** have exactly one of these three emoji markers. Do not leave items unmarked.

---

## 4. IDE Integration (PyCharm)

### LAUNCHER SYNCHRONIZATION
- **MANDATORY:** Changes to `launchers/*.xml` **MUST** be mirrored in `.idea/runConfigurations/*.xml` immediately.
- **BACKGROUND EXECUTION:** All Streamlit launchers **MUST** use background script wrappers.
