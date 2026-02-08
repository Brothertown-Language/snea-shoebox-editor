<!-- Copyright (c) 2026 Brothertown Language -->

# Operational Standards: Environment, Tools, and Security

## 1. Commands and Tools

### TECHNICAL EXECUTION RULES
- **MANDATORY psql FLAGS:** Always use `psql -c "QUERY" < /dev/null` or `psql -f script.sql < /dev/null` to prevent terminal hangs.
- **NO INTERACTIVE COMMANDS:** **NEVER** run commands that require user input (e.g., `psql` without flags, `top`, `vim`).
- **NO .git SEARCH:** **ALWAYS** exclude the `.git` directory when searching (e.g., `grep --exclude-dir=.git`).
- **CLEAN ROOT POLICY:** **NEVER** create log files, temporary scripts, or data files in the project root. All transient files MUST go to `tmp/`.

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
