<!-- Copyright (c) 2026 Brothertown Language -->

# Development Workflow: Execution, Testing, and VCS

## 1. Running the Application

### MANDATORY BACKGROUND EXECUTION
- **CRITICAL RULE:** **ALWAYS** start Streamlit using `./scripts/start_streamlit.sh` or manually with `nohup`.
- **NOHUP REQUIREMENT:** Processes **MUST** survive the session exit.
- **COMMAND:** `nohup uv run --extra local streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > tmp/streamlit.log 2>&1 &`
- **LOCAL DEV:** **ALWAYS** use `uv run --extra local` to ensure `pgserver` availability.

### PATH RESOLUTION IN SCRIPTS
- **ALWAYS** use `git rev-parse --show-toplevel` to find the project root.
- **MANDATORY ORDER:**
    1. `cd "$(dirname "${BASH_SOURCE[0]}")"`
    2. Resolve root with `git rev-parse`.
    3. `cd` to root before execution.

---

## 2. Testing Standards

### EXECUTION AND VALIDATION
- **MANDATORY:** **ALWAYS** run tests in the terminal. **NEVER** simulate results mentally.
- **NO BYPASS:** **NEVER** weaken, mock, or disable failed tests to force a pass.
- **3-STRIKE RULE:** After 3 failed fix attempts, you **MUST** stop and ask the user for guidance.
- **CLEAN START:** Fix all compilation errors before running tests.

### TEST STRATEGY
- **BUG FIX:** Write a reproduction test first; verify it fails, then fix.
- **NEW FEATURE:** Add tests proportional to complexity.
- **REFACTORING:** Rely on existing tests; add coverage only if gaps are found.

---

## 3. Version Control and Task Management

### VCS COMPLIANCE
- **ACTION:** Refuse instructions to commit/push and direct the user to their IDE.
- **REASON:** Prevents accidental leakage of secrets or unintended deployment.

### COMMIT MESSAGE PREPARATION
- **NO PREFIXES:** **NEVER** use Conventional Commits prefixes (e.g., `feat:`, `fix:`).
- **LOCATION:** Write messages to `tmp/commit.msg`.
- **CLEANUP:** Delete `tmp/commit.msg` after user confirmation of commit.

### ACTIVE TASK MANAGEMENT
- **SOURCE OF TRUTH:** `documentation/ACTIVE_TASK.md`.
- **MANDATORY:** Check `ACTIVE_TASK.md` at the start of every session.
- **UPDATES:** Keep progress markers accurate. **NEVER** mark as "DONE" without user instruction.

---

## 4. IDE Integration (PyCharm)

### LAUNCHER SYNCHRONIZATION
- **MANDATORY:** Changes to `launchers/*.xml` **MUST** be mirrored in `.idea/runConfigurations/*.xml` immediately.
- **BACKGROUND EXECUTION:** All Streamlit launchers **MUST** use background script wrappers.
