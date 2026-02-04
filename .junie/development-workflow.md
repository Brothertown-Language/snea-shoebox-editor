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
```bash
# Run the frontend locally
uv run streamlit run src/frontend/app.py
```

## Testing Standards

### Execution
- **Run all tests:** `uv run python -m unittest discover tests`
- **Rule:** NEVER simulate test execution mentally. **ALWAYS** run the actual tests in the terminal.
- **Rule:** Fix all compilation errors before attempting to run tests.
- **Rule:** Assume any test failures are caused by your recent changes.
- **Rule:** After 3 failed attempts to fix a test, you **MUST** ask the user for guidance.
- **Rule:** NEVER bypass or weaken failed tests by mocking/stubbing to hide issues, deleting/disabling tests, weakening assertions, or using skip flags.

### Test Strategy by Change Type
- **Bug Fix:** Write a reproduction test first, verify that it fails, and then implement the fix.
- **New Feature:** Add comprehensive tests proportional to the feature's complexity.
- **Refactoring:** Rely on existing tests to ensure no regression; add new tests only if coverage gaps are identified.
- **Documentation/Comments Only:** No tests are required.

## Secrets Management
- **Local Development:** Use `.streamlit/secrets.toml`. This file is ignored by git and must never be committed.
- **Production (Cloud):** Use the Streamlit Community Cloud "Secrets" management interface.
- **Database Connection:** Use `st.connection("postgresql", type="sql")` for connecting to the Supabase instance.

## Version Control

### Commit Messages
- **Location:** All commit messages must be written to `tmp/commit.msg`.
- **Format:** Use plain, descriptive text.
- **Constraint:** **DO NOT** use Conventional Commits prefixes (e.g., `feat:`, `fix:`).
- **Grouping:** Group all related changes into a single, cohesive commit.
- **Workflow (Recommended):**
    1. Create the commit message in `tmp/commit.msg.tmp`.
    2. Move it to `tmp/commit.msg` just before committing.
- **Cleanup:** **ALWAYS** remove `tmp/commit.msg` (or the `.tmp` version) after the commit is successful.

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
    - **Database:** Hosted on Supabase (PostgreSQL).
- **Configuration:** Use the Streamlit Cloud "Secrets" UI for all production environment variables and secrets.

### Configuration Files
- **`.streamlit/secrets.toml`:** Local development secrets (DO NOT COMMIT).
- **`pyproject.toml`:** Main Python package and dependency configuration.
