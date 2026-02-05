---
author: Human
contributor: AI
status: active
date: 2026-02-03
---
<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Online Shoebox Editor - AI Guidelines

## CRITICAL RULES - READ FIRST

### ALWAYS use `uv run` for Python commands
- **CORRECT:** `uv run python script.py`
- **CORRECT:** `uv run python -m unittest discover tests`
- **WRONG:** `python script.py` or `python3 script.py`
- This applies to ALL Python execution: scripts, tests, modules, REPL, everything.

### NEVER mount volumes or create files in user home directory
- Docker volumes must ONLY be mounted in project directory or /tmp
- **WRONG:** Mounting volumes to ~/.cache, ~/.local, or any path in /home/username
- **REASON:** This breaks user's local environment and permissions
- If you need temporary storage, use /tmp or project's tmp/ directory

### Docker containers and mounted volumes MUST NEVER use root
- **ALWAYS** run containers with user matching host user (e.g., `--user $(id -u):$(id -g)`)
- **NEVER** run containers as root - this creates permission issues
- **ANY file access via mounted volumes MUST be done as unprivileged user, NEVER as root**
- Use `setfacl` or similar to ensure dev (non-root) can access/edit/remove all files
- Dev must be able to access, edit, or remove mounted volumes at will
- Example: `docker run --user $(id -u):$(id -g) -v $(pwd)/tmp:/tmp ...`

### DO NOT USE PREFIXES IN COMMIT MESSAGES
- **NEVER** use prefixes like `feat:`, `fix:`, `docs:`, or any other Conventional Commits style prefixes in commit messages.
- **ALWAYS** use plain, descriptive text for commit messages.
- **CORRECT:** `git commit -m "Add new feature for record validation"`
- **WRONG:** `git commit -m "feat: add record validation"`

### DO NOT USE SHELL REDIRECTS - THEY ARE DANGEROUS
- **ALWAYS** use the designated tools (like `create`, `search_replace`, `multi_edit`) to modify files.
- **NEVER** use shell redirects (`>`, `>>`) in terminal commands to create or append to files.
- **REASON:** Shell redirects bypass tool-specific validations and can lead to data loss or corruption.

### NEVER USE COMPOUND BASH COMMANDS
- **NEVER** use `&&`, `;`, or `|` to chain multiple commands in a single bash tool call.
- **ALWAYS** execute each command as a separate, discrete step.
- **WRONG:** `git add . && git commit -m "msg" && git push`
- **CORRECT:** Call `bash` for `git add`, then call `bash` for `git commit`, then call `bash` for `git push`.
- **REASON:** Chained commands are harder to debug, bypass status checks between steps, and violate the principle of atomic operations.

### NEVER grep the `.git` folder
- **ALWAYS** exclude the `.git` directory when using `grep` or similar search tools.
- **CORRECT:** `grep -r --exclude-dir=.git "search_term" .`
- **WRONG:** `grep -ri "search_term" .`
- **REASON:** The `.git` folder contains binary files and metadata that produce erroneous search results.

### GUIDELINE UPDATES
- When told to remember to update the AI guidelines, **do nothing else**.
- "Remember" means ONLY updating the guidelines; it does NOT mean making code changes, edits, or deletions.
- Focus exclusively on identifying the necessary updates and applying them to the `.junie/` documentation.

### Frontend Architecture: Streamlit (Community Cloud)
- **Production:** Streamlit Community Cloud (connected to private GitHub repo)
- **Local Dev:** **MANDATORY** use of `nohup` for background execution (e.g., `./scripts/start_streamlit.sh`)
- **Hosting:** Streamlit Community Cloud for frontend, Aiven for PostgreSQL database
- **Secrets:** Use `.streamlit/secrets.toml` locally and "Secrets" UI in Streamlit Cloud

---

## Detailed Guidelines
The AI guidelines have been organized into the following specialized modules for better clarity and maintenance.

### 1. [AI Role and Behavior](.junie/ai-behavior.md)
- Professional role and Technical Lead responsibilities.
- Communication style and requirements.
- **Uncompressed** documentation format standards (Explicit vs. SPR).

### 2. [Code Standards and Organization](.junie/code-standards.md)
- Copyright headers, naming conventions, and code style.
- Single Responsibility Principle for methods.
- Strict type annotations and memory tracking.

### 3. [Development Workflow](.junie/development-workflow.md)
- Setup, execution, and deployment commands.
- Testing standards and execution rules.
- Secrets management and version control (Commit Messages).

### 4. [Project Context and Architecture](.junie/project-context.md)
- Project identity, ethics, and tech stack.
- Architecture details and data layer (MDF).
- Linguistic context and SNEA language details.

### 5. Security and Quality References
Detailed security and quality standards are maintained in these specific files:
- **[Security: Secrets](.junie/security-secrets.md)**
- **[Security: Dependencies](.junie/security-dependencies.md)**
- **[Security: Logging](.junie/security-logging.md)**
- **[Security: Configuration](.junie/security-configuration.md)**
- **[Code Quality](.junie/code-quality.md)**
