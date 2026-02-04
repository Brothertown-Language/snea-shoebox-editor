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

## Project Overview

### Identity
- **Purpose:** Collaborative editing of Southern New England Algonquian (SNEA) language records
- **Format:** MDF (Multi-Dictionary Formatter) - Shoebox/Toolbox standard
- **Languages:** Natick, Mohegan-Pequot, Narragansett, and related SNEA languages
- **Repository:** Private, restricted access
- **Ethics:** Respect Nation sovereignty; use "Nation" not "Tribal"; mark AI contributions

### Technology Stack
- **Language:** 100% Python
- **Frontend:** Streamlit
- **Backend:** Streamlit (Server-side execution)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** GitHub OAuth (via `streamlit-oauth`)
- **Package Manager:** uv (NOT pip, NOT poetry)
- **Deployment:** Streamlit Community Cloud (Auto-deploy on git push)

## Development Environment

### Setup Commands
```bash
# Initial setup
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .

# Run tests
uv run python -m unittest discover tests

# Run frontend locally
uv run streamlit run src/frontend/app.py
```

### Secrets Management
- **Local:** `.streamlit/secrets.toml` (ignored by git)
- **Cloud:** Streamlit Cloud "Secrets" management interface
- **Database:** Use `st.connection("postgresql", type="sql")` for Supabase connection

## Architecture Details

### Application Structure
- **Frontend/Backend:** Unified Streamlit application in `src/frontend/app.py`
- **Database:** Supabase PostgreSQL instance
- **Authentication:** GitHub OAuth integration for authorized users

### Data Layer
- **Format:** MDF (Multi-Dictionary Formatter)
- **Storage:** PostgreSQL (Supabase)
- **Hierarchy:** \lx (lexeme) -> \ps (part of speech) -> \ge (gloss)
- **Validation:** Advisory visual feedback on MDF compliance; linguists decide whether to enforce
- **Parser:** src/shared/mdf_parser.py
- **Validator:** src/shared/mdf_validator.py

## Testing Standards

### Unit Tests
- Framework: unittest (Python standard library)
- Location: tests/ directory
- Run command: `uv run python -m unittest discover tests`
- Coverage: Backend logic, MDF parsing, validation

### Test Strategy by Change Type
- **Bug fix:** Write reproduction test first, verify it fails, then fix
- **New feature:** Add tests proportional to complexity
- **Refactoring:** Rely on existing tests, add only if gaps exist
- **Documentation only:** No tests needed

### Test Execution Rules
- NEVER simulate tests mentally - always run them
- Fix compilation errors before running tests
- Assume test failures are caused by your changes
- After 3 failed fix attempts, ask user for guidance
- NEVER bypass failed tests by:
  - Mocking/stubbing to hide issues
  - Deleting or @Ignore/@Disabled annotations
  - Weakening assertions
  - Using skip flags (-DskipTests, etc.)

## Version Control

### Commit Messages
- Location: tmp/commit.msg (mandatory)
- Format: Plain descriptive text
- **DO NOT** use Conventional Commits prefixes (feat:, fix:, docs:, etc.)
- Group related changes into single commit
- **RECOMMENDED WORKFLOW:** Create commit message in `tmp/commit.msg.tmp` and then move it to `tmp/commit.msg` before each commit. This avoids worrying about deleting it beforehand or afterwards.
- If not using the recommended workflow, **ALWAYS** remove `tmp/commit.msg` if it exists before creating it from scratch.
- **ALWAYS** remove `tmp/commit.msg` after committing if it wasn't moved from `.tmp`.

### Active Task Tracking
- File: documentation/ACTIVE_TASK.md
- Update every session with current work status

## Code Standards

### Copyright Headers
Required for all .py and .md files (except data files):
```python
# Copyright (c) 2026 Brothertown Language
```
```markdown
<!-- Copyright (c) 2026 Brothertown Language -->
```
- If editing existing file with header, DO NOT modify the header
- If creating new file, add appropriate header

### Code Style
- Follow existing codebase patterns exactly
- Match indentation, naming, import order
- Mirror comment frequency and language
- Keep changes consistent with surrounding code

### File Naming
- Follow project conventions for casing and separators
- Maintain continuous numbering for sequential files
- Preserve exact numbering format

### Method Design and Code Organization
- **ALWAYS break code into discrete methods** - Each method should do one thing and do it well
- **NEVER create multi-function methods** - Methods must have single, clear responsibility
- **NEVER use "any" type** - All types must be explicit and specific
- Keep methods focused and cohesive
- Prefer composition over complex multi-purpose functions

### Type Annotations
- **ALWAYS use strict typing** - All function parameters, return values, and variables must have explicit type annotations
- Use specific types, never `Any` unless absolutely unavoidable
- Leverage Python's typing module (List, Dict, Optional, Union, etc.)
- Type hints are mandatory, not optional

### Memory and Long-Term Tracking
- **Use memory files appropriately** - Store long-term information in .junie/ directory
- **Structure for quick retrieval** - Organize memory files for easy, accurate information lookup
- Use clear hierarchies and consistent formatting
- Update memory files when instructed to "remember" something
- When instructed to "remember", update guidelines appropriately and make no other changes

## Security and Code Quality

### Overview
Detailed security and code quality guidelines are maintained in separate files for easier reference and maintenance. **Review these files before committing code or handling sensitive data.**

### Security Guidelines
- **[security-secrets.md](.junie/security-secrets.md)** - Secrets management, .env files, pre-commit verification
  - Never commit sensitive files (.env, keys, tokens)
  - Pre-commit content verification for sensitive patterns
  - Environment variables and Cloudflare secrets usage
- **[security-dependencies.md](.junie/security-dependencies.md)** - Dependency and supply chain security
  - Version pinning and package verification
  - Third-party code review and license compliance
  - Regular updates and vulnerability scanning
- **[security-logging.md](.junie/security-logging.md)** - Safe logging and error handling
  - Never log sensitive data (tokens, passwords, PII)
  - Sanitize user input before logging
  - Generic error messages for users, detailed logs for developers
- **[security-configuration.md](.junie/security-configuration.md)** - Configuration management
  - pyproject.toml, .streamlit/secrets.toml handling
  - Supabase connection strings and secrets rotation
  - Environment-specific configuration

### Code Quality Guidelines
- **[code-quality.md](.junie/code-quality.md)** - Pre-commit checklist and quality standards
  - Pre-commit verification checklist
  - Code quality standards (no commented code, no debug prints, tracked TODOs)
  - Input validation and sanitization
  - Database safety and API security

## Deployment

### Production Deployment
- Trigger: Push to main branch
- Process: Streamlit Community Cloud automatically pulls and builds from git
- Frontend: Hosted on Streamlit Cloud
- Backend: Streamlit server-side execution
- Configuration: Streamlit Cloud "Secrets" UI
- Note: Database hosted on Supabase (PostgreSQL)

### Configuration Files
- `.streamlit/secrets.toml`: Local development secrets
- pyproject.toml: Python package and dependency config

## AI Role and Behavior

### Your Role
- Technical Lead / Full-Stack Developer / Not a Linguist
- Provide concise, technical, professional responses
- Focus on "SO WHAT" - actionable information only
- No unsolicited assistance or suggestions
- Defer to Human Lead on decisions

### Communication Style
- Succinct and direct
- Technical accuracy over verbosity
- Answer what was asked, nothing more
- If unclear, ask specific clarifying questions

## Linguistic Context

### MDF Format
- Standard: Shoebox/Toolbox MDF tags
- Common tags: \lx (lexeme), \ps (part of speech), \ge (gloss), \dt (date)
- Typical hierarchy: lexeme -> part of speech -> gloss (linguist decides actual structure)
- Validation: Advisory visual hints only; linguists decide whether to follow conventions

### SNEA Languages
- Southern New England Algonquian language family
- Includes: Natick, Mohegan-Pequot, Narragansett, and related languages
- Historical and contemporary documentation
- Cultural sensitivity required in all work

## Documentation Format Guidelines

### When to Use SPR (Sparse Priming Representation)
SPR format is ONLY appropriate for:
- **Domain knowledge references** - Factual information that doesn't require behavioral compliance
  - Examples: MDF tag definitions, linguistic grammar rules, technical specifications
  - Files: `mdf-guidelines-spr.md`, `algonquian-grammar-spr.md`
- **Quick reference materials** - Compressed lookups for established facts
- **Meta-documentation** - Documentation about SPR format itself

### When to Use Explicit Format (NOT SPR)
Explicit, clear, direct format is REQUIRED for:
- **Operational instructions** - How the AI should behave, what actions to take
  - Examples: Development workflows, testing procedures, deployment steps
  - Files: `guidelines.md`, `ui-development-spr.md` (now rewritten)
- **Critical rules** - Requirements that must be followed without interpretation
  - Examples: "ALWAYS use uv run", "NEVER mount volumes in home directory"
- **Step-by-step procedures** - Sequential instructions with concrete examples
- **Architecture decisions** - System design choices that affect behavior

### Rationale
The repeated compliance issues (uv run, Docker volumes, stlite architecture) demonstrated that:
1. **SPR compression loses critical nuance** for behavioral instructions
2. **Ambiguity in operational guidelines** leads to systematic violations
3. **Explicit examples prevent misinterpretation** of requirements
4. **Domain facts** (MDF tags, grammar) benefit from compression as quick references

### Format Requirements
When writing explicit operational documentation:
- Use **CRITICAL RULES** or **ALWAYS/NEVER** headers for non-negotiable requirements
- Provide **concrete examples** with correct/incorrect comparisons
- Include **explicit commands** with full syntax
- Add **rationale** when rules seem arbitrary
- Use **bold** for emphasis on key requirements
