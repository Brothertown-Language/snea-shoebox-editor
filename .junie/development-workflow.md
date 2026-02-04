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
**MANDATORY RULE:** **ALWAYS** start the Streamlit application using the provided start script (`./scripts/start_streamlit.sh`). This script uses `nohup` and background execution to ensure the application continues running after the terminal or Junie session exits. There are **NO EXCEPTIONS** to this rule.

```bash
# Run the application locally in the background and ensure it persists
./scripts/start_streamlit.sh
```

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

### Execution
- **MANDATORY RULE:** **ALWAYS** start Streamlit using `./scripts/start_streamlit.sh`. This ensures it runs in the background with `nohup` and survives session exit. There are **NO EXCEPTIONS** or shortcuts.
- **Rule:** NEVER use compound bash commands (e.g., `&&`, `;`, `|`). Execute each command individually.
- **Run all tests:** `uv run python -m unittest discover tests`
- **Rule:** NEVER simulate test execution mentally. **ALWAYS** run the actual tests in the terminal.
- **Rule:** Fix all compilation errors before attempting to run tests.
- **Rule:** Assume any test failures are caused by your recent changes.
- **Rule:** After 3 failed attempts to fix a test, you **MUST** ask the user for guidance.
- **Rule:** NEVER bypass or weaken failed tests by mocking/stubbing to hide issues, deleting/disabling tests, weakening assertions, or using skip flags.
- **Rule (Searching):** **NEVER** search the `.git` folder. **ALWAYS** exclude the `.git` folder from all searching operations.

### Test Strategy by Change Type
- **Bug Fix:** Write a reproduction test first, verify that it fails, and then implement the fix.
- **New Feature:** Add comprehensive tests proportional to the feature's complexity.
- **Refactoring:** Rely on existing tests to ensure no regression; add new tests only if coverage gaps are identified.
- **Documentation/Comments Only:** No tests are required.

## Secrets Management
- **Rule (Zero Tolerance):** **NEVER** commit `.env`, `secrets.toml`, or any file containing credentials or sensitive keys.
- **Rule (Verification):** **ALWAYS** run `git check-ignore <path>` if you are unsure if a file is ignored.
- **Rule (Explicit Add):** **NEVER** use `git add` with explicit paths to files that are meant to be ignored (e.g., `git add .env`).
- **Local Development:** Use `.streamlit/secrets.toml`. This file is ignored by git and must never be committed.
- **Production (Cloud):** Use the Streamlit Community Cloud "Secrets" management interface.
- **Database Connection:** Use `st.connection("postgresql", type="sql")` for connecting to the Aiven instance.

## Version Control

### Commit Messages
- **Rule:** NEVER chain git commands (e.g., `git add && git commit`). Execute them as separate steps.
- **Rule (Safety):** **ALWAYS** run `git status` before `git commit` to verify exactly what is staged.
- **Rule (Exclusion):** If you accidentally stage a secret, **ALWAYS** use `git reset <file>` to unstage it before proceeding.
- **Rule (Prefixes):** **NEVER** use prefixes like `feat:`, `fix:`, `docs:`, or any other Conventional Commits style prefixes in commit messages.
- **Location:** All commit messages must be written to `tmp/commit.msg`.
- **Format:** Use plain, descriptive text.
- **Grouping:** Group all related changes into a single, cohesive commit.
- **Workflow (Requirement):**
    1. Create the commit message using the `create` tool at `tmp/commit.msg`.
    2. Execute the commit command using the terminal.
- **Cleanup:** **ALWAYS** remove `tmp/commit.msg` after the commit is successful.

### Active Task Tracking
- **File:** `documentation/ACTIVE_TASK.md`
- **Requirement:** Update this file every session with the current status of your work.

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
