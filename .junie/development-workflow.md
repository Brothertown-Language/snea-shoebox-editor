<!-- Copyright (c) 2026 Brothertown Language -->
<!-- 🚨 SUPREME DIRECTIVE: NO EDITS WITHOUT EXPLICIT APPROVAL ("Go", "Proceed", "Approved") 🚨 -->

# Development Workflow: Execution, Testing, and VCS

## 1. MANDATORY PLAN APPROVAL
- **ZERO-TOLERANCE:** All technical execution is secondary to the Authorization Gate. Never modify ANY file without an approved plan. See `.junie/guidelines.md`.

## 2. Running the Application

### MANDATORY BACKGROUND EXECUTION
- **CRITICAL RULE:** **ALWAYS** start Streamlit using `./scripts/start_streamlit.sh` or manually with `nohup`.
- **NOHUP REQUIREMENT:** Processes **MUST** survive the session exit.
- **COMMAND:** `nohup uv run --extra local streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > tmp/streamlit.log 2>&1 &`
- **LOCAL DEV:** **ALWAYS** use `uv run --extra local` to ensure `pgserver` availability.

### PATH RESOLUTION IN SCRIPTS
- **MANDATORY:** **ALL** shell scripts created or modified MUST use the following one-liner boilerplate for path resolution to ensure reliability across all execution environments (terminal, IDE, background tasks).
- **MANDATORY ONE-LINER (NO EXCEPTIONS):**
    `cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"`

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

## 3. Version Control and Task Management (v7.0 PROTOCOL)
### VCS COMPLIANCE: DECLARATIVE COMMIT PROTOCOL
- **STRICT PROHIBITION ON DIRECT GIT**: You are strictly forbidden from running `git add` or `git commit` directly in the terminal.
- **COMMIT DIRECTIVE MANDATE**: Commits are ONLY permitted when explicitly instructed by the User via a "Commit Directive" (e.g., "Prepare a commit"). 
    - **NO PLANNING:** You are forbidden from including commit preparation steps in any task plan unless the User has already issued a Commit Directive.
    - **NO ASSUMPTION:** Autonomous preparation or planning of commits is a critical guideline violation.
- **STEP 0: SECURITY INSPECTION**: Before creating ANY commit artifacts, you MUST run `bash scripts/pre_commit_check.sh` to verify that no ignored files, secrets, or unintended changes are being prepared for staging.
  - **MANDATORY FILE LIST**: You MUST create `tmp/commit_files.txt` containing the project-relative paths of all files to be committed (one per line). The check script will automatically read from this file.
  - **REVIEW UNTRACKED**: You MUST also review the "OTHER uncommitted changes" section of the script output to identify any untracked files that should be included in `tmp/commit_files.txt`.
  - **UNTRACKED FILE EXCEPTION**: If untracked files are detected, and you are absolutely convinced they should not be tracked, you MUST notify the user, explain your reasoning, and STOP. Do not proceed with creating commit artifacts until the user acknowledges.
- **STEP 1: CREATE MESSAGES**: Create `tmp/commit_<N>.msg` files for each semantic group.
- **STEP 2: GENERATE VALIDATED SCRIPT**: Create `tmp/commit.sh`.
  - **MANDATORY PATH RESOLUTION**: The script MUST include the mandatory `cd/git rev` shell fragment as the first command after `set -e`.
  - **FRAGMENT**: `cd "$(dirname "${BASH_SOURCE[0]}")" && REPO_ROOT=$(git rev-parse --show-toplevel) && cd "$REPO_ROOT"`
  - **NO FORCE**: The `-f` flag is strictly PROHIBITED.
  - **ATOMIC COMMITS**: Use separate `git add` + `git commit` blocks per semantic group.
- **PROHIBITION ON EXECUTION**: AI is forbidden from running the commit script. User ONLY.
- **REVIEW ALL UNCOMMITTED FILES**: Before manifest creation, run `git status` to identify modified and untracked files.
- **GROUP BY PURPOSE**: AI Guideline updates MUST always be in a separate commit from application code.
- **MESSAGE FORMAT**: No Conventional Commits prefixes. Summary sentence + blank line + high-level focused overview.
- **REASON**: Direct `git add` risks committing secrets or ignored files. Using a script ensures explicit path staging and review. Violation is a critical breach of trust.


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
