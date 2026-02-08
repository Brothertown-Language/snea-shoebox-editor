<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Online Shoebox Editor: Master AI Guidelines

## I. CRITICAL OPERATIONAL MANDATES
These rules are non-negotiable and supersede all other instructions. Failure to follow these rules is considered a critical operational error.

### 1. Execution and Tooling
- **ALWAYS use `uv run`**: Every Python command (scripts, tests, modules) MUST be prefixed with `uv run`. 
  - *Correct:* `uv run python script.py`
  - *Incorrect:* `python script.py`
- **NO SHELL REDIRECTS**: Never use `>` or `>>` to modify files. Use the provided tools (`create`, `search_replace`, `multi_edit`).
- **NO COMPOUND COMMANDS**: Execute every command as a separate step. Never use `&&`, `;`, or `|` to chain operations.
- **NEVER grep `.git`**: Always exclude the `.git` directory when searching code.
- **RELATIVE PATHS ONLY**: All terminal commands MUST use paths relative to the project root. NEVER use absolute paths (e.g., `/home/user/git/project/...`) or `cd /absolute/path && command`. The shell is always at the project root—use it directly (e.g., `cat README.md`, NOT `cd /home/muksihs/git/snea-shoebox-editor && cat README.md`). This applies to ALL commands without exception.

### 2. Environment and Safety
- **NO ROOT ACCESS**: Never run containers as root. Always use `--user $(id -u):$(id -g)`.
- **NO HOME DIRECTORY MOUNTS**: Docker volumes and file creations must stay within the project directory or `/tmp`.
- **NO LOGS IN ROOT**: Keep the project root clean. All logs and transient files MUST go into `tmp/`.
- **MANDATORY PRIVATE DATABASE**: All operations (scripts, tests, database interactions) MUST use the private Junie database (`JUNIE_PRIVATE_DB=true`) unless specifically and clearly instructed otherwise by the user. NO EXCEPTIONS.

### 3. Version Control and Security
- **NEVER COMMIT OR PUSH**: Do not execute `git commit` or `git push`.
- **COMMIT SCRIPT METHOD**: Committing changes to source code MUST be done by creating a shell script in `tmp/` (e.g., `tmp/commit_task.sh`) along with a message file (e.g., `tmp/commit.msg`) **ONLY when directly instructed to prepare for a commit**. The commit script **MUST** include the mandatory 3-step path resolution boilerplate (see `development-workflow.md` §1: `cd "$(dirname "${BASH_SOURCE[0]}")"`, then `REPO_ROOT=$(git rev-parse --show-toplevel)`, then `cd "$REPO_ROOT"`). Instruct the user to review and run this script via their IDE.
  - *Exception*: You MAY directly update your own guideline files in `.junie/` and memory files (e.g., `documentation/ACTIVE_TASK.md`) if necessary.
- **ZERO TOLERANCE FOR SECRETS**: Never commit credentials, `.env` files, or the `.streamlit/` folder. Use `git check-ignore` to verify safety.
- **NEVER COMMIT TEMPORARY FILES**: It is strictly forbidden to commit files from the `tmp/` directory or any other transient files (e.g., `refactoring_plan.md`, `commit.msg`, `commit_task.sh`). Always verify staging with `git status` and ensure `.gitignore` is respected.
- **NO Conventional Commits**: Do not use prefixes like `feat:` or `fix:` in commit messages prepared for the user.

---

## II. MODULAR GUIDELINE ARCHITECTURE
To maintain precision and avoid "vibe coding," these guidelines are divided into specialized modules. You are MANDATED to re-read these files at the start of every session.

### 1. [AI Behavior and Communication](.junie/ai-behavior.md)
- **Zero-Tolerance for "Vibe Coding"**: No assumptions, no "proactive cleanups," no unauthorized refactoring.
- **Deep Inspection Mandatory**: NEVER rely on memory for verification. Always inspect the actual source code to confirm the current state.
- **No Roadmap Driving**: You are the executor. Never implement future phases without explicit instruction.
- **Communication Standards**: No apologies, no sycophancy, technical focus only.
- **Stop and Ask**: If a task is ambiguous, you must halt and seek clarification.

### 2. [Operational Standards](.junie/operational-standards.md)
- Detailed CLI rules, Docker configurations, and security protocols.
- Secrets management and dependency pinning (`uv.lock`).

### 3. [Development Workflow](.junie/development-workflow.md)
- **Background Execution**: Streamlit MUST be run with `nohup` or the provided scripts.
- **Testing Standards**: Manual verification is prohibited; always run tests in the terminal.
- **PyCharm Integration**: Mandatory synchronization between `launchers/` and IDE configurations.

### 4. [Project Architecture and Context](.junie/project-architecture.md)
- **Identity**: Linguistic context for SNEA languages and ethical standards.
- **Data Layer**: MDF (Multi-Dictionary Formatter) standards and database schema requirements.

---

## III. MANDATORY SESSION INITIALIZATION
1. **RE-READ** all files in the `.junie/` directory, including the `LONG_TERM_MEMORY.md` and `VIOLATION_LOG.md`.
2. **CHECK** `documentation/ACTIVE_TASK.md` for the current status.
3. **ACKNOWLEDGE** compliance by stating "Reviewing AI Guidelines" in your first response.
4. **VALIDATE** all external links and assumptions against the actual source code.
5. **UPDATE** `LONG_TERM_MEMORY.md` and `VIOLATION_LOG.md` whenever a new cross-session decision is made or a violation is identified.
