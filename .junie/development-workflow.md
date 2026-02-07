<!-- Copyright (c) 2026 Brothertown Language -->

# Development Workflow and Standards

## Setup Commands
Use the following commands for setting up the local development environment.

### Initial Setup
```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install the project in editable mode
uv pip install -e .
```

### Running the Application
**MANDATORY RULE:** **ALWAYS** start the Streamlit application using the provided start script (`./scripts/start_streamlit.sh`) or manually using `nohup`. This script uses `nohup` and background execution to ensure the application continues running after the terminal or Junie session exits. There are **NO EXCEPTIONS** to this rule. 
**LOCAL DEV REQUIREMENT:** For local development, **ALWAYS** use `uv run --extra local` to ensure that `pgserver` and other local dependencies are available.
**COMMAND:** `nohup uv run --extra local streamlit run src/frontend/app.py --server.address 0.0.0.0 --server.port 8501 > tmp/streamlit.log 2>&1 &`

```bash
# Run the application locally in the background and ensure it persists
./scripts/start_streamlit.sh
```

## Project Root and Path Resolution
- **Rule:** When writing scripts that need to find the project root (e.g., for background processes or logging), **ALWAYS** use `git rev-parse --show-toplevel`.
- **MANDATORY Execution Order in Scripts:**
    1. First, `cd` to the script's own directory using `cd "$(dirname "${BASH_SOURCE[0]}")"`.
    2. Then, run `git rev-parse --show-toplevel` to determine the project root.
    3. Finally, `cd` to the resolved project root before executing the main logic.
- **Reason:** This ensures paths are consistently resolved regardless of where the script is invoked from, avoiding "file not found" errors for logs and temporary files.

## NO LOGS OR TEMP FILES IN PROJECT ROOT
- **CRITICAL:** **NEVER** create log files, temporary scripts, or data files in the project root.
- **MANDATORY:** Always use the `tmp/` directory for any transient files.
- **REASON:** Keeping the project root clean is essential for maintainability and prevents accidental commits of junk files.

### Multipage Navigation and `st.switch_page`
When programmatically switching pages in the Streamlit application:
- **Rule:** **ALWAYS** use the file path relative to the main script (e.g., `st.switch_page("pages/view_record.py")`).
- **Rule:** Ensure the target page is registered in `st.navigation` in `src/frontend/app.py` using its file path.
- **Query Parameters:** Use `st.query_params` to pass state between pages when navigating. Example:
  ```python
  st.query_params["id"] = 42
  st.switch_page("pages/view_record.py")
  ```

## Testing Standards

### HTML Export/Preview (Rich Text Clipboard)
- **Requirement:** When copying HTML versions of documentation or data to the clipboard for use in other applications (e.g., for rich text pasting), **ALWAYS** use `xclip` with the explicit `text/html` target.
- **Rule:** Use `pandoc -s` to ensure a standalone HTML document with proper formatting (CSS, head, body).
- **Command:** `pandoc -s -f markdown -t html <file> | xclip -selection clipboard -t text/html`
- **Reason:** Specifying the MIME type ensures the clipboard content is recognized as formatted HTML rather than raw code, and `xclip` provides more reliable rich-text handling across Linux environments than `xsel`.

### Execution
- **MANDATORY RULE:** **ALWAYS** start Streamlit using `./scripts/start_streamlit.sh`. This ensures it runs in the background with `nohup` and survives session exit. There are **NO EXCEPTIONS** or shortcuts.
- **LOCAL DEV REQUIREMENT:** For local development and testing, **ALWAYS** use `uv run --extra local` to ensure that `pgserver` and other local dependencies are available.
- **Rule:** NEVER use compound bash commands (e.g., `&&`, `;`, `|`). Execute each command individually.
- **Run all tests:** `uv run --extra local python -m unittest discover tests`
- **Rule:** NEVER simulate test execution mentally. **ALWAYS** run the actual tests in the terminal.
- **Rule:** Fix all compilation errors before attempting to run tests.
- **Rule:** Assume any test failures are caused by your recent changes.
- **Rule:** After 3 failed attempts to fix a test, you **MUST** ask the user for guidance.
- **Rule:** NEVER bypass or weaken failed tests by mocking/stubbing to hide issues, deleting/disabling tests, weakening assertions, or using skip flags.
- **Rule (Searching):** **NEVER** search the `.git` folder. **ALWAYS** exclude the `.git` folder from all searching operations.
- **Rule (Interactive Commands):** **NEVER** run interactive commands (e.g., `psql`, `python`, `top`). **ALWAYS** use non-interactive flags (e.g., `psql -c "QUERY" < /dev/null`) or execute specific scripts. The `< /dev/null` redirect is mandatory for `psql` and when using `python` with `help()` or similar interactive calls to prevent terminal hangs.

### Test Strategy by Change Type
- **Bug Fix:** Write a reproduction test first, verify that it fails, and then implement the fix.
- **New Feature:** Add comprehensive tests proportional to the feature's complexity.
- **Refactoring:** Rely on existing tests to ensure no regression; add new tests only if coverage gaps are identified.
- **Documentation/Comments Only:** No tests are required.

## Secrets Management
- **Rule (Zero Tolerance):** **NEVER** commit `.env`, `secrets.toml`, or any file containing credentials or sensitive keys.
- **Rule (Zero Tolerance):** **NEVER** commit the `.streamlit/` folder or any of its contents. This is a critical security violation.
- **Rule (Verification):** **ALWAYS** run `git check-ignore <path>` if you are unsure if a file is ignored.
- **Rule (Explicit Add):** **NEVER** use `git add` with explicit paths to files that are meant to be ignored (e.g., `git add .env`).
- **Local Development:** Use `.streamlit/secrets.toml`. This file is ignored by git and must never be committed.
- **Production (Cloud):** Use the Streamlit Community Cloud "Secrets" management interface.
- **Database Connection:** Use `st.connection("postgresql", type="sql")` for connecting to the Aiven instance.

## Version Control
- **CRITICAL:** **NEVER** execute `git commit` or `git push` commands.
- **ACTION:** If instructed to commit and/or push, you **MUST** refuse and instruct the user to use their IDE interface to perform these actions.
- **REASON:** This ensures that secrets, PII, and other sensitive items are not accidentally committed into the repository history, even if they are listed in `.gitignore`.

### Commit Message Preparation
- **Rule (Exclusion):** If you accidentally stage a secret, **ALWAYS** use `git reset <file>` to unstage it before notifying the user.
- **Rule (Prefixes):** **NEVER** use prefixes like `feat:`, `fix:`, `docs:`, or any other Conventional Commits style prefixes in commit messages.
- **Location:** All commit messages must be written to `tmp/commit.msg`.
- **Format:** Use plain, descriptive text.
- **Grouping:** Group all related changes into a single, cohesive commit description.
- **Workflow (Requirement):**
    1. Create the commit message using the `create` tool at `tmp/commit.msg`.
    2. Instruct the user to commit using their IDE, using the content of `tmp/commit.msg`.
- **Cleanup:** **ALWAYS** remove `tmp/commit.msg` after the user confirms they have committed the changes.

### Active Task and TODO Management
- **Primary Task Tracker:** `documentation/ACTIVE_TASK.md`
- **Requirement:** **ALWAYS** check `documentation/ACTIVE_TASK.md` at the start of every session to understand the current project state and next steps.
- **Requirement:** Update `documentation/ACTIVE_TASK.md` at the end of every session (or during `update_status` calls) with accurate progress markers (`[DONE]`, `[PENDING]`, etc.).
- **NO UNAUTHORIZED COMPLETIONS:** **NEVER** mark any task, roadmap item, or feature as "COMPLETED" or "DONE" in `ACTIVE_TASK.md`, `roadmap.md`, or any other file without explicit user instruction. This is **MANDATORY**.
- **Task-Specific TODOs:** Complex or multi-step tasks may have dedicated files in `documentation/` (e.g., `documentation/TODO_PERSISTENT_LOGIN.md`).
- **Requirement:** If a task-specific TODO file exists and is referenced in `ACTIVE_TASK.md` or the issue description, it MUST be treated as the authoritative source of truth for that specific task's implementation details.
- **Maintenance:** Delete or archive task-specific TODO files once the task is fully completed and verified.

## Deployment

### Production Deployment
- **Trigger:** Automatic deployment occurs on every push to the `main` branch.
- **Process:** Streamlit Community Cloud automatically pulls the latest code and rebuilds.
- **Infrastructure:**
    - **Frontend:** Hosted on Streamlit Community Cloud.
    - **Backend:** Server-side execution within Streamlit Cloud.
    - **Database:** Hosted on Aiven (PostgreSQL).
- **Configuration:** Use the Streamlit Cloud "Secrets" UI for all production environment variables and secrets.

### Configuration Files
- **`.streamlit/secrets.toml`:** Local development secrets (DO NOT COMMIT).
- **`pyproject.toml`:** Main Python package and dependency configuration.
- **`.python-version`:** Specifies the exact Python version (3.12) for both `uv` and Streamlit Cloud.

### Known Deployment Issues
- **Streamlit Cloud Warning:** You may see a warning: "More than one requirements file detected... Available options: uv-sync ..., poetry ...". 
  - **Status:** This is a **false positive** from Streamlit Cloud's heuristic detection. 
  - **Resolution:** Ignore the warning. As long as the logs state `Used: uv-sync with .../uv.lock`, the deployment is using the correct `uv` package manager.
- **Dependency Resolution:** Streamlit Community Cloud ignores `pyproject.toml` in favor of `uv.lock` for environment resolution. Ensure `uv.lock` is committed.
