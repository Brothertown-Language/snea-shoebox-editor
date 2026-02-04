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

### DO NOT USE SHELL REDIRECTS - THEY ARE DANGEROUS
- **ALWAYS** use the designated tools (like `create`, `search_replace`, `multi_edit`) to modify files.
- **NEVER** use shell redirects (`>`, `>>`) in terminal commands to create or append to files.
- **REASON:** Shell redirects bypass tool-specific validations and can lead to data loss or corruption.

### Frontend Architecture: Streamlit (Community Cloud)
- **Production:** Streamlit Community Cloud (connected to private GitHub repo)
- **Local Dev:** Regular Streamlit server (`uv run streamlit run src/frontend/app.py`)
- **Hosting:** Streamlit Community Cloud for frontend, Supabase for PostgreSQL database
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
