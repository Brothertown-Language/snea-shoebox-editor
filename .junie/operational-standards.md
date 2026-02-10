<!-- Copyright (c) 2026 Brothertown Language -->

# Operational Standards: Environment, Tools, and Security

## 1. Commands and Tools

### TECHNICAL EXECUTION RULES
- **MANDATORY RELATIVE PATHS:** **ALWAYS** use project-relative paths (e.g., `src/services/identity_service.py`) in all tool calls, terminal commands, file references, and output. **NEVER** use absolute paths (e.g., `/home/user/git/project/src/...`). The project root is the working directory; all paths must be relative to it.
- **⚠️ NEVER PREFIX COMMANDS WITH `cd`:** The shell is ALREADY at the project root. Do NOT use `cd /path && command` or `cd /path; command`. Just run the command directly. **SELF-CHECK: If your command starts with `cd`, STOP and remove it.** This is a recurring violation (see VIOLATION_LOG.md #3).
- **⚠️ NEVER COPY USER COMMANDS VERBATIM:** When the user provides a shell command in the issue description, treat it as a specification of *what* to run, NOT as a ready-to-execute command. **ALWAYS** translate it to guideline-compliant form: remove `cd /absolute/path`, split `&&` chains into separate tool calls, remove pipes (`|`). Each atomic command must be a separate step. User-provided commands often contain absolute paths and compound operators that violate these standards.
- **MANDATORY psql FLAGS:** Always use `psql -c "QUERY" < /dev/null` or `psql -f script.sql < /dev/null` to prevent terminal hangs.
- **NO INTERACTIVE COMMANDS:** **NEVER** run commands that require user input (e.g., `psql` without flags, `top`, `vim`).
- **NO .git SEARCH:** **ALWAYS** exclude the `.git` directory when searching (e.g., `grep --exclude-dir=.git`).
- **NO `sed -i` OR IN-PLACE SHELL EDITS:** **NEVER** use `sed -i`, `awk -i inplace`, `perl -i`, or any shell command that modifies files in-place. All file modifications MUST use the provided editing tools (`create`, `search_replace`, `multi_edit`). This extends the "NO SHELL REDIRECTS" mandate to cover all forms of shell-based file mutation.
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
### AGGRESSIVE DB CONNECTION REUSE
Database connection pooling is recommended, but idle connections MUST be closed and removed from the pool after a short period (e.g., 5 seconds). If all connections in the pool become idle, the pool is allowed to become empty. This ensures that unused slots are returned to the database as quickly as possible. In SQLAlchemy, this is typically achieved by setting `pool_size=0` and a low `pool_recycle`.

### FATAL DB ERRORS
**FAILED DB OPERATIONS ARE FATAL ERRORS.** DO NOT HIDE OR SWALLOW ERRORS. 
- **NO SILENT RECOVERY:** If a database operation fails, it MUST NOT be caught and ignored. The error MUST propagate to the caller or be logged and re-raised. 
- **NO SWALLOWING IN LOOPS:** Specifically in bulk operations or loops, do NOT use `try/except` blocks that merely log the error and continue to the next iteration if the error is a database exception (e.g., connection failure, integrity violation). The entire operation must halt to prevent inconsistent state or further resource exhaustion.
- **CRITICAL FAILURES:** Database unavailability, connection timeouts, or integrity violations must result in immediate task termination or explicit user-facing failure. 
- **LOGGING:** While errors must be logged, logging is NOT a substitute for raising the exception. 

### DEPENDENCY SECURITY
- **ALWAYS PIN VERSIONS:** Use exact versions in `pyproject.toml` for production.
- **uv.lock IS SOURCE OF TRUTH:** Streamlit Cloud uses `uv.lock`. Ensure it is up-to-date and committed.
- **MINIMAL DEPENDENCIES:** Only add packages when truly necessary. Prefer the standard library.

---

## 4. Code Quality and Safety

### DEPRECATED API AVOIDANCE
- **Deprecated API warnings mean near-future breakage due to bitrot.** Avoid deprecated API usage where easily feasible. When a deprecated call is identified (e.g., via test warnings), replace it with the modern equivalent promptly.
- **Exception:** Sometimes deprecated API usage is required (e.g., no modern replacement exists yet, or the replacement introduces unacceptable complexity). In such cases, document the reason with a code comment.

### PRE-COMMIT CHECKLIST
- [ ] No secrets or PII in code or comments.
- [ ] No sensitive files staged (Verify with `git status`).
- [ ] All new functions have strict type annotations.
- [ ] Copyright headers are present.
- [ ] No debug `print` statements (Use `logging`).
- [ ] No commented-out code.
