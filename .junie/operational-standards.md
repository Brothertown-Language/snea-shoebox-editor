<!-- Copyright (c) 2026 Brothertown Language -->

# Operational Standards: Environment, Tools, and Security

## 1. Commands and Tools

### TECHNICAL EXECUTION RULES
- **MANDATORY RELATIVE PATHS:** **ALWAYS** use project-relative paths (e.g., `src/services/identity_service.py`) in all tool calls, terminal commands, file references, and output. **NEVER** use absolute paths (e.g., `/home/user/git/project/src/...`). The project root is the working directory; all paths must be relative to it.
- **MANDATORY psql FLAGS:** Always use `psql -c "QUERY" < /dev/null` or `psql -f script.sql < /dev/null` to prevent terminal hangs.
- **NO INTERACTIVE COMMANDS:** **NEVER** run commands that require user input (e.g., `psql` without flags, `top`, `vim`).
- **NO .git SEARCH:** **ALWAYS** exclude the `.git` directory when searching (e.g., `grep --exclude-dir=.git`).
- **CLEAN ROOT POLICY:** **NEVER** create log files, temporary scripts, or data files in the project root. All transient files MUST go to `tmp/`.
- **JUNIE PRIVATE DB:** Junie tests and destructive tasks **MUST** use a private `pgserver` instance.
    - Set `JUNIE_PRIVATE_DB=true` in the environment to activate.
    - Path: `tmp/junie_db`.
    - **NEVER** perform destructive tests or updates on the local developer DB (`tmp/local_db`).
    - **CLONING:** To clone the dev DB to Junie's private DB, use:
      `uv run python scripts/clone_db.py` (ensure the script exists and targets `tmp/junie_db`).

---

## 2. Docker and Environment

### HOST USER ALIGNMENT
- **USER MATCHING:** **ALWAYS** match host user in Docker: `--user $(id -u):$(id -g)`.
- **PERMISSIONS:** Ensure the host user (dev) can access/edit/remove all files in mounted volumes.

### VOLUME MOUNTING
- **NEVER** mount volumes to the user's home directory (e.g., `~/.cache`).
- **ALWAYS** mount to the project directory or `/tmp`.

---

## 3. Security and Secrets

### SECURITY HARDENING
- **HARDCODING PROHIBITED:** **NEVER** hardcode secrets in source code. Use environment variables or Streamlit secrets.
- **MANDATORY CHECK:** Use `git check-ignore <path>` to verify if a file is excluded from VCS before creation.
- **PROHIBITION ON COMMITTING `tmp/`**: **NEVER** include files from the `tmp/` directory in a git commit. The `tmp/` directory is strictly for transient logs, database instances, and coordination files that must never enter the repository history.

### DEPENDENCY SECURITY
- **ALWAYS PIN VERSIONS:** Use exact versions in `pyproject.toml` for production.
- **uv.lock IS SOURCE OF TRUTH:** Streamlit Cloud uses `uv.lock`. Ensure it is up-to-date and committed.
- **MINIMAL DEPENDENCIES:** Only add packages when truly necessary. Prefer the standard library.

---

## 4. Code Quality and Safety

### PRE-COMMIT CHECKLIST
- [ ] No secrets or PII in code or comments.
- [ ] No sensitive files staged (Verify with `git status`).
- [ ] All new functions have strict type annotations.
- [ ] Copyright headers are present.
- [ ] No debug `print` statements (Use `logging`).
- [ ] No commented-out code.
