<!-- Copyright (c) 2026 Brothertown Language -->

# SNEA Online Shoebox Editor: Master AI Guidelines (v2.0)

## I. CRITICAL EXECUTION CHECKLIST
These rules are non-negotiable. Every command and tool call MUST pass this checklist.

### 1. The "Zero-Trust" Terminal Gate
- **[ ] NO `cd`**: Never start a command with `cd`. The shell is ALREADY at the project root.
- **[ ] NO ABSOLUTE PATHS**: Strip all `/home/...` prefixes. Use project-relative paths only.
- **[ ] NO COMPOUND COMMANDS**: No `&&`, `;`, or `|`. Split into separate tool calls.
- **[ ] NO SHELL REDIRECTS**: No `>` or `>>` for file editing. Use `create`/`multi_edit` ONLY.
- **[ ] `uv run` PREFIX**: Every Python execution MUST start with `uv run`.
- **[ ] PRIVATE DB**: Every DB-interactive command MUST include `JUNIE_PRIVATE_DB=true`.
- **[ ] NO ONE-LINERS**: No complex `python -c "..."`. Create a script in `tmp/` instead.

### 2. The VCS "Permission Gate"
- **[ ] NO AUTONOMOUS COMMITS**: Never prepare `tmp/commit_task.sh` without explicit instruction.
- **[ ] NOConventional Commits**: Never use `feat:`, `fix:`, etc. in commit messages.
- **[ ] 3-STEP PATH RESOLUTION**: All scripts in `tmp/` or `scripts/` MUST use the boilerplate:
  ```bash
  cd "$(dirname "${BASH_SOURCE[0]}")"
  REPO_ROOT=$(git rev-parse --show-toplevel)
  cd "$REPO_ROOT"
  ```
- **[ ] NO ECHO COMMITS**: Commit scripts MUST execute `git commit` directly, not `echo` it.

---

## II. MODULAR GUIDELINE ARCHITECTURE
You are MANDATED to re-read these specialized modules at the start of every session.

### 1. [AI Behavior & Communication](.junie/ai-behavior.md)
- **Zero-Tolerance for "Vibe Coding"**: No assumptions, no proactive cleanups.
- **Stop and Ask**: Mandatory halt on ambiguity.
- **Natural Counting**: Use 1-based numbering for all plans and lists.

### 2. [Operational Standards](.junie/operational-standards.md)
- **Environment & Safety**: No root access, no home mounts, no logs in root.
- **Technical Execution**: psql flags, no interactive commands, no `.git` grep.

### 3. [Development Workflow](.junie/development-workflow.md)
- **Execution & Testing**: Streamlit backgrounding, terminal-only testing, no test bypass.
- **Progress Tracking**: Mandatory Tri-State Emoji (✅, 🔄, ⏳) for all plans.

### 4. [Project Architecture & Context](.junie/project-architecture.md)
- **Identity & Data**: SNEA linguistic context and MDF standards.

---

## III. MANDATORY INITIALIZATION
1. **RE-READ** all `.junie/*.md` files, including `LONG_TERM_MEMORY.md` and `VIOLATION_LOG.md`.
2. **CHECK** `documentation/ACTIVE_TASK.md` for current context.
3. **ACKNOWLEDGE** by stating "Reviewing AI Guidelines" in your first response.
4. **UPDATE** logs immediately upon any guideline violation or cross-session decision.
