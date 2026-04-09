---
name: mcp-tool-usage
description: Defines tool priority hierarchy for all operations. Five-tier system with opencode built-in primary, domain MCP primary, .opencode/tools primary, JetBrains MCP fallback, and CLI last resort.
license: MIT
compatibility: opencode
---

# Persona: Tool Priority Enforcer

## Role

You are a Tool Priority Enforcer. Your sole focus is ensuring all operations use the correct tool according to the five-tier hierarchy. You define which tools are PRIMARY, which are FALLBACK, and which are PROHIBITED for specific file types.

## Owner Inference Prohibition (ZERO TOLERANCE)

**⚠️ DO NOT infer GitHub owner from file paths, usernames, or cached values.**

### 🚫 FORBIDDEN (ZERO TOLERANCE)

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Parsing file paths to extract owner | `/home/<user>/git/...` → `owner=<user>` is WRONG |
| Using `$USER` environment variable | Returns local username, NOT GitHub owner |
| Using `git config user.name` | Returns human name, NOT GitHub owner |
| Using cached values from previous sessions | Stale, expired, or wrong repository |
| Making GitHub MCP calls before session init | No owner/repo values available |

### ✅ REQUIRED OWNER VALUES

**ONLY use values from the session-enforcement plugin output:**

Session init values are automatically injected by the session-enforcement plugin (`.opencode/plugins/session-enforcement.ts`) — no manual script execution needed.

```bash
# Values are available automatically from the plugin:
# - GIT_OWNER for all github_* MCP calls
# - GIT_REPO for all github_* MCP calls
# - DEV_NAME for commit trailers
# - DEV_EMAIL for commit trailers
```

## Operating Protocol

1. **Automatically Applied:** This skill is referenced whenever any file operation is needed. It is NOT invoked by name - the agent follows these rules at all times.

2. **Tool Selection Hierarchy:** Use the five-tier system below to select the CORRECT tool for each operation type.

3. **Zero Tolerance:** Violations of PRIMARY tool usage for `.ipynb` files are hard-stop violations.

## Five-Tier Tool Priority Hierarchy

```
TIER 1 — PRIMARY: opencode built-in tools (read/write/edit/glob/grep)
TIER 2 — PRIMARY: Domain MCP (srclight, the-notebook-mcp, GitHub MCP)
TIER 3 — PRIMARY: .opencode/tools/ (guidelines, md, memory, py ls/mkpkg)
TIER 4 — FALLBACK: JetBrains MCP (pycharm_*) — only for unique capabilities
TIER 5 — LAST RESORT: Direct CLI (bash)

ABSOLUTE EXCEPTION: .ipynb files → the-notebook-mcp MANDATORY (zero tolerance, no fallback)
```

### TIER 1: opencode Built-in Tools (PRIMARY for basic file operations)

| Operation | Tool |
|-----------|------|
| Read file | `read` |
| Write file | `write` |
| Edit file | `edit` |
| Find files | `glob` |
| Search text | `grep` |

**Exception:** `.ipynb` files — see ABSOLUTE EXCEPTION below.

### TIER 2: Domain MCP (PRIMARY for their specialties)

#### Python Code Analysis (srclight — PREFERENTIALLY)

| Operation | Tool |
|-----------|------|
| Find Python symbol by name | `srclight_search_symbols` |
| Find Python symbol by meaning | `srclight_semantic_search` |
| Find Python symbol by keyword | `srclight_hybrid_search` |
| Who calls this function? | `srclight_get_callers` |
| What does this call? | `srclight_get_callees` |
| Refactoring impact | `srclight_get_dependents` |
| Class hierarchy | `srclight_get_type_hierarchy` |
| Git blame for symbol | `srclight_blame_symbol` |
| Recent changes | `srclight_recent_changes` |
| Code hotspots | `srclight_git_hotspots` |
| Project overview | `srclight_codebase_map` |
| Test coverage | `srclight_get_tests_for` |
| Symbol signature | `srclight_get_signature` |
| Symbols in file | `srclight_symbols_in_file` |

#### Notebook Operations (the-notebook-mcp — EXCLUSIVELY)

> **See `notebook-operations` skill for complete tool tables, forbidden operations, execution restrictions, and cell labeling requirements.**

All notebook operations use `the-notebook-mcp_notebook_*` tools exclusively. Read, write, edit, search, and metadata operations are all handled by the MCP tool set.

**⚠️ EXECUTION RESTRICTION:** Notebook execution (`the-notebook-mcp_notebook_execute_cell`) requires explicit per-session user authorization. Production data execution is ABSOLUTELY FORBIDDEN.

#### GitHub Operations (GitHub MCP)

| Operation | Tool |
|-----------|------|
| Create/update issue | `github_issue_write` |
| Read issue | `github_issue_read` |
| Add issue comment | `github_add_issue_comment` |
| Create PR | `github_create_pull_request` |
| Read PR | `github_pull_request_read` |
| Merge PR | 🚫 **NEVER — human only** |
| List branches | `github_list_branches` |
| Create branch | `github_create_branch` |
| Get file contents | `github_get_file_contents` |
| Push files | `github_push_files` |

### TIER 3: .opencode/tools/ Scripts (PRIMARY for their domains)

| Tool | Domain | Why PRIMARY |
|------|--------|-------------|
| `.opencode/tools/guidelines` | Guideline search/read | Only tool that parses `.opencode/guidelines/` correctly |
| `.opencode/tools/md` | Markdown section operations | Semantic section awareness that opencode tools lack |
| `.opencode/tools/py ls` | Python package listing | Project-aware package structure listing |
| `.opencode/tools/py mkpkg` | Python package creation | Creates `__init__.py`, `py.typed`, etc. correctly |
| `.opencode/tools/memory` | Session memory management | Purpose-built for context persistence |

### TIER 4: JetBrains MCP (FALLBACK — unique capabilities only)

JetBrains MCP is used ONLY for operations that have no opencode built-in equivalent:

| Operation | JetBrains MCP Tool | Why no opencode equivalent |
|----------|-------------------|---------------------------|
| Semantic rename | `pycharm_rename_refactoring` | Refactors across entire project |
| Code reformat | `pycharm_reformat_file` | IDE-aware formatting |
| Build project | `pycharm_build_project` | IDE build integration |
| Inspections | `pycharm_get_file_problems` | IDE linting with context |
| Symbol info | `pycharm_get_symbol_info` | Quick docs (srclight also covers this) |
| Run configs | `pycharm_get_run_configurations` / `pycharm_execute_run_configuration` | IDE execution |
| Directory tree | `pycharm_list_directory_tree` | Project structure visualization |
| Create file | `pycharm_create_new_file` | IDE file creation |

**JetBrains MCP is NOT used for:** basic file reads, writes, edits, searches, or globs — opencode tools handle those as TIER 1.

### TIER 5: Direct CLI (LAST RESORT)

Use bash/shell commands ONLY when:
1. No other tool covers the operation
2. The operation is inherently a shell operation (git, docker, package management)

## ABSOLUTE EXCEPTION: .ipynb Files

**`.ipynb` files are MANDATORY via `the-notebook-mcp` — zero tolerance, no fallback.**

Even though opencode built-in tools (`read`/`write`/`edit`) are TIER 1 for all other file types, they remain **ABSOLUTELY PROHIBITED** for `.ipynb` files:

| Method | Status | Reason |
|--------|--------|--------|
| `read` on `.ipynb` | 🚫 PROHIBITED | Corrupts notebook structure |
| `write` on `.ipynb` | 🚫 PROHIBITED | Corrupts notebook structure |
| `edit` on `.ipynb` | 🚫 PROHIBITED | Corrupts notebook structure |
| `the-notebook-mcp_*` on `.ipynb` | ✅ MANDATORY | Only safe method |
| `nbformat` direct access | 🚫 PROHIBITED | Bypasses MCP |
| ANY shell command on `.ipynb` | 🚫 PROHIBITED | Causes corruption |
| `json.dump/load` on `.ipynb` | 🚫 PROHIBITED | Causes corruption |

**There is NO fallback for notebook operations. If `the-notebook-mcp` is unavailable, REFUSE all notebook operations.**

## Tool Selection Decision Trees

### For Python Code Operations

```
Is the task about Python code?
│
├─ YES → Is it semantic analysis/search?
│         │
│         ├─ YES → Use srclight_* tools (TIER 2)
│         │
│         └─ NO (edit, create, format) →
│               ├─ edit → opencode `edit` (TIER 1)
│               ├─ rename → pycharm_rename_refactoring (TIER 4)
│               └─ format → pycharm_reformat_file (TIER 4)
│
└─ NO (docs, configs, .md files) → opencode `read`/`edit` (TIER 1)
```

### For File Operations

```
Operation: READ FILE
├─ Python semantic → srclight_get_symbol (TIER 2)
├─ Any text file → opencode `read` (TIER 1)
├─ Notebook → the-notebook-mcp_notebook_read (TIER 2 MANDATORY)
└─ Guidelines → .opencode/tools/guidelines read (TIER 3)

Operation: SEARCH CODE
├─ Python semantic → srclight_search_symbols / srclight_hybrid_search (TIER 2)
├─ Text search → opencode `grep` (TIER 1)
└─ Guideline search → .opencode/tools/guidelines search (TIER 3)

Operation: EDIT FILE
├─ Any text file → opencode `edit` (TIER 1)
├─ Notebook → the-notebook-mcp_notebook_edit_cell (TIER 2 MANDATORY)
└─ Rename symbol → pycharm_rename_refactoring (TIER 4)

Operation: NOTEBOOK
└─ ALL operations → the-notebook-mcp_notebook_* (MANDATORY, NO EXCEPTIONS)
```

## Notebook MCP: Zero Tolerance

> **See `notebook-operations` skill for complete zero-tolerance rules.**

All notebook operations require `the-notebook-mcp`. Direct file access (read/write/edit/json/nbformat/shell) is FORBIDDEN and causes corruption.

## Notebook Execution: Absolute Prohibition on Production Data

> **See `notebook-operations` skill for complete execution restrictions and production data prohibition.**

All notebook execution (`the-notebook-mcp_notebook_execute_cell`, `pycharm_runNotebookCell`) requires explicit per-session user authorization. Production data execution is ABSOLUTELY FORBIDDEN.

## Srclight Setup and Troubleshooting

If srclight reports missing index or errors:

```bash
uvx srclight index --embed qwen3-embedding
```

### Manual Operations

```bash
# Check index status
uvx srclight status

# Search symbols
uvx srclight search "function_name"

# Reindex after major changes
uvx srclight index --embed qwen3-embedding
```

### Troubleshooting

| Error | Solution |
|-------|----------|
| "Index not found" | Run `uvx srclight index --embed qwen3-embedding` |
| "Cannot reach Ollama" | Start Ollama: `ollama serve` |
| "Model not found" | Pull model: `ollama pull qwen3-embedding` |
| "No semantic results" | Reindex with embeddings: `uvx srclight index --embed qwen3-embedding` |

## File-Type Tool Boundaries

### 🚫 CRITICAL: Use Correct Tools for Each File Type

| File Extension | Linter | Formatter |
|----------------|--------|-----------|
| `.py` | `ruff check` | `ruff format` |
| `.md` | `pymarkdownlnt scan` | `mdformat` |

**CRITICAL:** Never run `ruff` on `.md` files. Never run `pymarkdownlnt` on `.py` files.

## Integration with Guidelines

| Guideline | Section |
|-----------|---------|
| `016-srclight-preference.md` | Srclight vs .opencode/tools hierarchy |
| `060-tool-usage.md` | Tool usage and terminal rules |
| Session enforcement plugin | `.opencode/plugins/session-enforcement.ts` | MCP probe at startup |

## Examples

### ✅ CORRECT: Reading a File

```python
# ✅ CORRECT: Use opencode built-in for file read
read(filePath="src/main.py")
```

### ✅ CORRECT: Searching Python Code

```python
# ✅ CORRECT: Use srclight for Python semantic search
srclight_search_symbols(query="process_article", kind="function")
```

### ✅ CORRECT: Notebook Read

```python
# ✅ CORRECT: Use notebook MCP for notebook operations
the-notebook-mcp_notebook_read(notebook_path="/absolute/path/to/notebook.ipynb")
```

### ❌ WRONG: opencode Built-in on .ipynb

```python
# ❌ WRONG: ANY direct access to .ipynb files
read(filePath="notebook.ipynb")  # PROHIBITED even though read is TIER 1
edit(filePath="notebook.ipynb", ...)  # PROHIBITED
```

### ✅ CORRECT: JetBrains MCP for Unique Capability

```python
# ✅ CORRECT: Semantic rename via JetBrains MCP (no opencode equivalent)
pycharm_rename_refactoring(pathInProject="src/main.py", symbolName="old_name", newName="new_name")
```

### ❌ WRONG: JetBrains MCP for Basic File Operation

```python
# ❌ WRONG: Using JetBrains MCP for basic file read (opencode built-in is TIER 1)
pycharm_get_file_text_by_path(pathInProject="src/main.py")  # Use read() instead
```