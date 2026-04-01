# Environment, Testing & Temporary Files

## Python Environment

- Use `uv sync` for environment setup (creates venv and installs in editable mode). All Python execution via
  `uv run python`. Package ops: add dependencies by editing `pyproject.toml` then running `uv sync` — never `uv add`. `pip` prohibited. No `sys.path` hacks or manual
  path additions.
- **Never use `python3` or `python` directly** — always `uv run python`. Never prefix commands with absolute paths or `cd /absolute/path &&`. See `060-tool-usage.md § Python Interpreter` and `§ Path Rules` for the full zero-tolerance rules.
- Reusable agent scripts live in `ai_bin/` (project root). Invoke with `uv run python ai_bin/<script>`.
- When `pyproject.toml` changes, purge `.venv` and run `uv sync` as a standalone command (never embedded in git hooks,
  commit scripts, or automated pipelines).
- **Database Safety**: Follow production schema protection and test schema isolation in `100-persistence.md`.
  NEVER run test/experimental code against the production schema.

## Isolated Tool Environments

When developing local tools that need their own dependencies (separate from the main project), use isolated tool environments to keep the main project's `pyproject.toml` clean.

### Directory Structure Pattern

```
project/
├── pyproject.toml          # Main project dependencies (kept clean)
├── src/
├── tools/                  # Isolated tool environment
│   ├── pyproject.toml      # Tool-specific dependencies
│   └── my_tool.py
```

The `tools/` directory contains its own `pyproject.toml` with only the dependencies needed by that tool. This keeps heavy or tool-specific dependencies isolated from the main project.

### Invocation Methods

**1. Ephemeral (recommended for one-time use):**
```bash
# Runs in temp venv, cleaned up after execution
uvx --from ./tools my-tool [args]

# Does NOT install globally, does NOT pollute main venv
```

**2. Persistent (for frequently-used tools):**
```bash
# Installs tool globally (available in any directory)
uv tool install ./tools

# Run from anywhere
my-tool [args]

# Uninstall when no longer needed
uv tool uninstall my-tool
```

### Benefits

- **Clean main dependencies**: Main project's `pyproject.toml` stays focused on production dependencies
- **Dependency isolation**: Tool conflicts don't affect the main project
- **No version conflicts**: Tool can use different versions of shared dependencies
- **Faster `uv sync`**: Main project re-sync is faster without tool dependencies
- **Portable**: Tool environment is self-contained and reproducible

### When to Use

Use isolated tool environments when:
- A local tool needs dependencies that are NOT useful for the main project
- You want to try a tool without committing it to `pyproject.toml`
- A tool requires mutually exclusive dependency versions
- You're developing a standalone utility that could be extracted later

Use direct `pyproject.toml` dependencies when:
- The dependency is needed for production code
- The dependency is needed by tests that run against production code
- The dependency is already in the main dependency tree

### Example: Local Analysis Tool

**tools/pyproject.toml:**
```toml
[project]
name = "analysis-tool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pandas>=2.0",
    "matplotlib>=3.7",
    "seaborn>=0.12",
]

[project.scripts]
analyze = "analyze:main"
```

**tools/analyze.py:**
```python
def main():
    import pandas as pd
    import matplotlib.pyplot as plt
    # Tool implementation
```

**Usage:**
```bash
# Ephemeral (no install)
uvx --from ./tools analyze

# Persistent (global install)
uv tool install ./tools
analyze  # Available from any directory
```

This pattern is especially useful for data science tools, analysis scripts, and one-off utilities that would otherwise clutter the main dependency list.

## Node.js Prohibition

**DETESTABLE**: Installing Node.js in a Python-only or Java-only environment is absolutely prohibited. This introduces an unnecessary runtime dependency that pollutes the ecosystem and creates maintenance burden.

### 🚫 NEVER DO
- **NEVER install Node.js globally or locally** on Python-only or Java-only projects.
- **NEVER use NPX** to run packages — NPX requires Node.js runtime.
- **NEVER add Node.js-based tools to project dependencies.**
- **NEVER suggest npm packages as solutions** in Python/Java contexts.
- **NEVER use Node.js-based formatters, linters, or tooling** when native alternatives exist.

### Context
This rule applies universally to:
- **Python projects**: Use `uv`, `pip`, `ruff`, `pytest` — never npm/pnpm/yarn.
- **Java projects**: Use Maven/Gradle, JVM tooling — never npm/pnpm/yarn.
- **Projects with mixed languages**: Isolate Node.js to its designated frontend/service layer.

### ✅ ALLOWED
- **Docker containers that internally use Node.js** — Node.js runs inside container, not on host.
- **Pure Python alternatives** — `githubkit` instead of `@octokit/rest`, `httpx` instead of `axios`.
- **Dedicated frontend repositories** where Node.js IS the correct tool for that codebase.
- **MCP servers via Docker** — Node.js isolated in container only.

### Why This Is Critical
- **Security**: Node.js ecosystem has known supply-chain attack vectors.
- **Dependency bloat**: Adds unnecessary runtime and package manager complexity.
- **Maintenance burden**: Mixed language projects require additional CI/CD configuration.
- **Ecosystem mismatch**: npm packages don't integrate with Python/Java tooling chains.
- **Team friction**: Requires developers to install/maintain Node.js on their machines.

## Production System Protection
- **The AI agent is never permitted to run code against production data.** This is an absolute prohibition with no exceptions — not even for verification, inspection, or read-only queries. Any step that would execute code against production data requires explicit user instruction before execution.
- **DIAGNOSTIC REQUESTS ARE READ-ONLY:** When asked to "check error", "investigate bug", "review logs", or similar diagnostics, the agent MUST:
  1. Look for log files (`.log` files in `./tmp/` or project directories)
  2. Read source code and error messages statically
  3. Analyze code paths without execution
  4. NEVER run the failing script, reproduce the error, or execute against production
- **BUG FIXES ARE CODE-ONLY:** When fixing a bug in production-touching code:
  1. Make the code fix
  2. Use static analysis (lint, typecheck) to verify syntax
  3. STOP — do not run the script against production to verify
  4. Ask user if they want to test/verify (they may provide a test fixture)
- **NEVER run any script, notebook, or command that connects to, reads from, or writes to a production data path**
  (e.g. `pubmed_data_3/db/`, any path outside `./tmp/`) without explicit user authorization in the current session.
- This includes verification steps: do NOT run `pgserver_start.py`, `pgserver_stop.py`, or any script that starts,
  stops, or force-kills a PostgreSQL server process unless the user explicitly says to do so.
- Verification of script correctness must use static analysis (lint, grep, code review) or a dedicated test fixture
  with an isolated `./tmp/` path — never the live production instance.
- **NEVER use production spec files (GitHub Issues) as smoke-test or verification targets.** Spec issues are authoritative tracking artifacts — they are never modified for testing purposes.
- **This applies to `ai_bin/` tool verification too.** When fixing or verifying any tool that mutates plan files,
  always create a throwaway plan copy in `./tmp/` and run the tool against that copy. Never invoke a mutating tool
  against a live plan file as a "test" or "verification" step.
  To create a throwaway copy: `cp plans/SPEC-some-plan.md ./tmp/spec_test.md`, then pass
  `./tmp/spec_test.md` to the tool. Discard after testing. Using `cp` to `./tmp/` for this purpose is the one permitted exception to the
  raw-shell-command prohibition for plan files.
- Violating this rule can crash the production system and corrupt live data.

## Testing

- Use `unittest`. Run from root: `uv run python -m unittest tests/test_filename.py`.
- **NEVER run tests against production data or live data.** Tests must use isolated test fixtures with dedicated test databases (e.g., `PgServerManager` with a test schema). Running tests against production/live data is an absolute prohibition — no exceptions.
- **Never use SQLite for tests.** The project uses PostgreSQL-specific types (JSONB, Vector) that are incompatible with SQLite. All test database fixtures must use a real PostgreSQL instance (via `PgServerManager`).
- No regression tests unless explicitly requested. A regression test is a test added to prevent a previously fixed bug
  from reappearing; this rule does not prohibit new unit tests or reproduction scripts required by the current task.
  Temp test artifacts in `./tmp/` only.
- If `SyntaxWarning: invalid escape sequence` appears in output, stop execution and fix the offending code before
  proceeding.

## Temporary Files

- All temp scripts/data/artifacts in `./tmp/` ONLY. NO OTHER FOLDERS PERMITTED. **Never use `/tmp/` (system temp) or any other folder.** This includes any diagnostic or exploratory Python scripts — files named `temp_*.py`, `test_*.py` (outside `test/`), or similar one-off scripts must be placed in `./tmp/`, never at the project root.
- **NO BOGUS PATHS**: Using relative paths that exit the current directory (e.g., `../tmp/`) in scripts or notebooks is **absolutely forbidden**. This creates brittle, non-portable code. All file system operations MUST use paths derived from `project_root` or `base_dir` (e.g., `project_root / 'tmp' / 'index.html'`) as provided by the project's standard utilities (e.g., `notebook_utils.py`).
- **Mandatory for CLI text updates:** Use `./tmp/` to store input files for `ai_bin` text update tools to avoid shell escaping and newline issues.
- Project root must stay clean — no root-level temp files.
- **`.output.txt` files must be placed in `./tmp/` (e.g., `./tmp/.output.txt`), never at the project root (`.output.txt` is a violation).**
- **Mandatory pre-submit root cleanliness check:** Before calling `submit`, confirm the project root is clean:
  (1) Never create `.output.txt`, `temp_*.py`, or any other temp/diagnostic file at the project root — always use `./tmp/` at time of creation.
  (2) Run `uv run python ai_bin/file-exists .output.txt` — if it exists, move it to `./tmp/.output.txt` immediately (`mv .output.txt ./tmp/.output.txt`).
  (3) Check for any `temp_*.py` files at the project root (`ls temp_*.py 2>/dev/null`) — if any exist, move them to `./tmp/` before submitting.

### ⚠️ MANDATORY: Temp Files Cleanup After Task Completion

**Temp files MUST be cleaned up after every task — no exceptions.**

### ✅ ALWAYS DO — After Task Completion

1. **Remove temp scripts** — `rm ./tmp/temp_*.py` or `rm ./tmp/test_*.py`
2. **Remove temp data files** — `rm ./tmp/*.json ./tmp/*.csv ./tmp/*.html` (task-specific artifacts)
3. **Preserve persistent temp files** — Files intentionally kept for caching or future runs:
   - `./tmp/*.db` (SQLite databases)
   - `./tmp/*.log` (log files)
   - `./tmp/.*` (hidden files like `.output.txt`)
4. **Verify cleanup** — `ls ./tmp/` should only show intentional persistent files

### 🚫 NEVER DO

- **NEVER leave temp files "for later cleanup"** — cleanup is mandatory, not optional
- **NEVER leave diagnostic scripts in `./tmp/` after task ends** — delete immediately after use
- **NEVER defer cleanup** — it happens in the same session as task completion
- **NEVER delete persistent temp files** (`.db`, `.log`, hidden files) without explicit instruction

### Cleanup Commands

```bash
# Remove temporary scripts (safe for task artifacts)
rm ./tmp/temp_*.py ./tmp/test_*.py 2>/dev/null

# Remove temporary data files (safe for task artifacts)
rm ./tmp/*.json ./tmp/*.csv ./tmp/*.html 2>/dev/null

# List remaining files (should only show persistent ones)
ls ./tmp/
```

## Local LLM Agent (Ollama)

- **Location:** `local-agent-setup/uv-ollama/`
- **Start command:** run `bash local-agent-setup/uv-ollama/start-ollama-uv.sh` from the project root.
- **What it does:** installs `uv` locally (if absent), checks for a global Ollama binary (falls back to local download if not found), starts the Ollama server in the background, pulls `qwen2.5-coder:32b-instruct-q4_0`, and prints the API URL when ready.
- **API URL:** `http://127.0.0.1:11434`
- **PyCharm connection:** use the printed URL to configure the local AI assistant endpoint in PyCharm Settings.
- **Recommendation:** install Ollama globally (`curl -fsSL https://ollama.com/install.sh | sh`) before running the script — the global binary is preferred over the local download.

## PyCharm IDE

- No usability-conflicting shortcuts are enabled (e.g., double-Shift / Search Everywhere is disabled). Do not suggest
  shortcuts or navigation paths that depend on these features being active.
- For IDE settings, direct the user via **Settings** menus only — never via keyboard shortcuts that may be disabled.
- The **New UI is not in use** and must never be suggested. It is inaccessible and adversarial to the user's workflow.
  Always assume Classic UI.

## Markdown Formatting

- Use triple backtick fenced code blocks for all examples. No backslash escapes or HTML entities for backticks within
  fenced blocks.
- **Forbidden operation (Step-0205 hard rule)**: Do **not** execute any notebook that touches production data. This includes `the-notebook-mcp_notebook_execute_cell`, `pycharm_runNotebookCell`, or any execution method.
- **Global forbidden execution on production-touching workflows**: Never run full notebook/script execution commands for any notebook or script that touches production data. If verification is required, use non-executing inspection/read-only checks via `the-notebook-mcp` tools and production-safe alternatives only.