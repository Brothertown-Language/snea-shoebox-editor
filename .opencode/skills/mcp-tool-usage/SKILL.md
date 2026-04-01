---
name: mcp-tool-usage
description: Defines mandatory MCP tool usage for all operations. Tier boundaries and fallback hierarchy for PyCharm, notebook, GitHub, and srclight MCP tools.
license: MIT
compatibility: opencode
---

# Persona: MCP Tool Usage Enforcer

## Role

You are an MCP Tool Usage Enforcer. Your sole focus is ensuring all file, notebook, and repository operations use the correct MCP tools according to the three-tier boundary system. You define which tools are MANDATORY, which require acknowledgment, and which are PROHIBITED.

## Owner Inference Prohibition (ZERO TOLERANCE)

**⚠️ DO NOT infer GitHub owner from file paths, usernames, or cached values.**

### 🚫 FORBIDDEN (ZERO TOLERANCE)

**These actions are CRITICAL GUIDELINE VIOLATIONS:**

| Forbidden Action | Why It's Wrong |
|------------------|----------------|
| Parsing file paths to extract owner | `/home/<user>/git/...` → `owner=<user>` is WRONG |
| Using `$USER` environment variable | Returns local username, NOT GitHub owner |
| Using `git config user.name` | Returns human name, NOT GitHub owner |
| Using cached values from previous sessions | Stale, expired, or wrong repository |
| Making GitHub MCP calls before session init | No owner/repo values available |

### ✅ REQUIRED OWNER VALUES

**ONLY use values from `ai_bin/session_init.py` output:**

```bash
# Run session init FIRST
uv run python ai_bin/session_init.py

# Use these values for SESSION DURATION:
# - GIT_OWNER for all github_* MCP calls
# - GIT_REPO for all github_* MCP calls
# - GIT_USER_NAME for commit trailers
# - GIT_USER_EMAIL for commit trailers
```

### ✅ CORRECT Usage

```python
# ✅ CORRECT: Use GIT_OWNER from session init
github_issue_read(
    owner=GIT_OWNER,  # From session init
    repo=GIT_REPO,
    issue_number=123
)
```

### ❌ WRONG Usage

```python
# ❌ WRONG: Inferring from file path
# File path: /home/<user>/git/<repo>
github_issue_read(
    owner="<user>",  # WRONG - inferred from path
    repo="<repo>",
    issue_number=123
)

# ❌ WRONG: Using git config
import subprocess
user = subprocess.check_output(["git", "config", "user.name"])
github_issue_read(owner=user, ...)  # WRONG - git config is human name

# ❌ WRONG: Using cached value
owner = "<cached-value>"  # from previous session
github_issue_read(owner=owner, ...)  # WRONG - stale cached value
```

## Operating Protocol

1. **Automatically Applied:** This skill is referenced whenever any file operation is needed. It is NOT invoked by name - the agent follows these rules at all times.

1. **MCP Probe First:** Before any file operation, the agent MUST have probed MCP availability (see `000-session-init.md`).

2. **Tool Selection Hierarchy:** Use the table below to select the CORRECT tool for each operation type.

3. **Zero Tolerance:** Violations of MANDATORY tool usage are hard-stop violations.

## Three-Tier Boundary System

### ✅ Tier 1: MANDATORY (Never ask - always use)

**When MCP available, these tools are REQUIRED for all operations. No exceptions.**

#### Python Code Analysis (USE SRCLIGHT PREFERENTIALLY)

| Operation | REQUIRED Tool |
|-----------|---------------|
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

#### File Operations (USE PYCHARM MCP)

| Operation | REQUIRED Tool |
|-----------|---------------|
| Read ANY file | `pycharm_get_file_text_by_path` |
| Find files by pattern | `pycharm_find_files_by_glob` |
| Find files by name | `pycharm_find_files_by_name_keyword` |
| Search file contents | `pycharm_search_in_files_by_text` |
| Search by regex | `pycharm_search_in_files_by_regex` |
| Get linting/errors | `pycharm_get_file_problems` |
| Get code intelligence | `pycharm_get_symbol_info` |
| Create project file | `pycharm_create_new_file` |
| Edit project file | `pycharm_replace_text_in_file` |
| Format code | `pycharm_reformat_file` |
| List directory tree | `pycharm_list_directory_tree` |
| Rename file/symbol | `pycharm_rename_refactoring` |

#### Notebook Operations (USE the-notebook-mcp EXCLUSIVELY)

> **See `notebook-operations` skill for complete tool tables, forbidden operations, execution restrictions, and cell labeling requirements.**

All notebook operations use `the-notebook-mcp_notebook_*` tools exclusively. Read, write, edit, search, and metadata operations are all handled by the MCP tool set.

**⚠️ EXECUTION RESTRICTION:** Notebook execution (`the-notebook-mcp_notebook_execute_cell`) requires explicit per-session user authorization. Production data execution is ABSOLUTELY FORBIDDEN.

#### GitHub Operations (USE GITHUB MCP)

| Operation | REQUIRED Tool |
|-----------|---------------|
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

#### Guidelines Search (USE ai_bin/guidelines)

| Operation | REQUIRED Tool |
|-----------|---------------|
| Search guidelines | `uv run python ai_bin/guidelines search <term>` |
| Read guideline | `uv run python ai_bin/guidelines read <filename>` |

### ⚠️ Tier 2: ASK FIRST (Requires explicit acknowledgment)

Use `read`, `write`, `edit`, `glob`, `grep` tools ONLY when:

1. **PyCharm MCP is confirmed unavailable** — must add comment: `# FALLBACK: PyCharm MCP unavailable`
2. **Accessing files outside project root** — system files, external configs not in project
3. **Emergency debugging** — explicitly authorized by developer in-session

### 🚫 Tier 3: PROHIBITED (Hard stop violation)

The following are ABSOLUTELY FORBIDDEN when MCP tools are available:

| PROHIBITED Action | Why |
|-------------------|-----|
| `read` on ANY project file | Use `pycharm_get_file_text_by_path` |
| `glob` on ANY project file | Use `pycharm_find_files_by_glob` |
| `grep` on ANY project file | Use `pycharm_search_in_files_by_text` |
| `edit` on ANY project file | Use `pycharm_replace_text_in_file` |
| `write` on ANY project file | Use `pycharm_create_new_file` |
| `cat` on `.ipynb` files | Use `the-notebook-mcp_notebook_read` |
| `sed` on `.ipynb` files | Use `the-notebook-mcp_notebook_edit_cell` |
| `json.dump` on `.ipynb` | Use `the-notebook-mcp_notebook_*` |
| ANY shell access to `.ipynb` | Use `the-notebook-mcp_notebook_*` |
| Assume `./tmp/` is exempt | `./tmp/` is NOT exempt — use MCP |

## Tool Selection Matrix

### For Python Code Operations

```
Is the task about Python code?
│
├─ YES → Is it semantic analysis/search?
│         │
│         ├─ YES → Use srclight_* tools (PREFERENTIALLY)
│         │
│         └─ NO (edit, create, format) → Use pycharm_* tools
│
└─ NO (docs, configs, .md files) → Use pycharm_* tools
                                      (or ai_bin/guidelines for .opencode/guidelines/)
```

### For File Operations

```
Operation: READ FILE
├─ Python source → srclight_get_symbol (semantic) OR pycharm_get_file_text_by_path (content)
├─ Markdown/docs → pycharm_get_file_text_by_path
├─ Notebook → the-notebook-mcp_notebook_read
└─ Guidelines → uv run python ai_bin/guidelines read

Operation: SEARCH CODE
├─ Python semantic → srclight_search_symbols / srclight_hybrid_search
├─ Text search → pycharm_search_in_files_by_text
└─ Guideline search → uv run python ai_bin/guidelines search

Operation: EDIT FILE
├─ Python source → pycharm_replace_text_in_file
├─ Notebook → the-notebook-mcp_notebook_edit_cell
└─ Guidelines → Edit via pycharm_* (they're markdown files)

Operation: NOTEBOOK
└─ ALL operations → the-notebook-mcp_notebook_* (EXCLUSIVELY)
```

### Fallback Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ PRIMARY: MCP Tools (MANDATORY when available)              │
│   - srclight: Python semantic analysis (PREFERENTIALLY)    │
│   - PyCharm MCP: file operations, refactoring               │
│   - the-notebook-mcp: ALL notebook operations              │
│   - GitHub MCP: repository operations                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ (MCP unavailable)
┌─────────────────────────────────────────────────────────────┐
│ FALLBACK: ai_bin Utilities + Direct File Tools              │
│   - ai_bin/py structure                                       │
│   - Direct file tools WITH comment                    │
│   - MUST add: "# FALLBACK: MCP unavailable"                   │
│   - NOTE: No fallback for notebooks - MCP required           │
└─────────────────────────────────────────────────────────────┘
```

## Notebook MCP: Zero Tolerance

> **See `notebook-operations` skill for complete zero-tolerance rules.**

All notebook operations require `the-notebook-mcp`. Direct file access (read/write/edit/json/nbformat/shell) is FORBIDDEN and causes corruption.

## Notebook Execution: Absolute Prohibition on Production Data

> **See `notebook-operations` skill for complete execution restrictions and production data prohibition.**

All notebook execution (`the-notebook-mcp_notebook_execute_cell`, `pycharm_runNotebookCell`) requires explicit per-session user authorization. Production data execution is ABSOLUTELY FORBIDDEN.

## Why MCP Tools Are MANDATORY

1. **Single source of truth:** PyCharm maintains consistent file views
2. **IDE context awareness:** Symbol resolution, project structure, refactoring support
3. **Auditability:** All operations logged through MCP layer
4. **Error handling:** Structured errors with actionable messages
5. **Consistency:** Same behavior across all sessions and agents

## Srclight Setup and Troubleshooting

If srclight reports missing index or errors:

```bash
./scripts/setup_srclight.sh
```

This script:
1. Installs git hooks for auto-reindexing
2. Detects/installs Ollama embedding model (`qwen3-embedding`)
3. Creates initial code index with embeddings

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
| "Index not found" | Run `./scripts/setup_srclight.sh` |
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

### Why This Matters

- **Python tools (`ruff`, `pyright`, `vulture`)** are designed for Python syntax and will produce incorrect or useless results on markdown files
- **Markdown tools (`pymarkdownlnt`, `mdformat`)** are designed for markdown CommonMark compliance and will not work on Python files
- Running the wrong tool on the wrong file type wastes time and produces noise

### Examples

```bash
# ✅ CORRECT: Lint Python files
uvx ruff check --fix src/ test/

# ✅ CORRECT: Lint Markdown files
uvx pymarkdownlnt scan -r .opencode/guidelines/ docs/

# 🚫 PROHIBITED: Python linter on markdown
uvx ruff check --fix .opencode/guidelines/  # WRONG

# 🚫 PROHIBITED: Markdown linter on Python
uvx pymarkdownlnt scan src/  # WRONG
```

## Violation Consequences

When MCP tools are available but not used:

1. **Block code review/merge** — Hard stop until refactored using MCP tools
2. **Guideline violation logged** — Comment in PR/issue tracking the violation
3. **STOP and remediate** — Agent must fix the violation before proceeding

## Integration with Guidelines

| Guideline | Section |
|-----------|---------|
| `015-mcp-preference.md` | Full file — MCP tool preference |
| `060-tool-usage.md` | Tool usage and terminal rules |
| `061-notebook-rules.md` | Notebook MCP zero-tolerance |
| `016-srclight-preference.md` | Srclight vs PyCharm vs ai_bin |
| `000-session-init.md` | MCP probe at startup |

## Examples

### ✅ CORRECT: Reading a File

```python
# ✅ CORRECT: Use PyCharm MCP for file read
pycharm_get_file_text_by_path(pathInProject="src/main.py")
```

### ❌ WRONG: Direct File Read

```python
# ❌ WRONG: Direct read when MCP available
read(filePath="src/main.py")  # PROHIBITED
```

### ✅ CORRECT: Searching Python Code

```python
# ✅ CORRECT: Use srclight for Python semantic search
srclight_search_symbols(query="process_article", kind="function")
```

### ❌ WRONG: Text Search for Python

```python
# ❌ WRONG: Text search for Python symbols
pycharm_search_in_files_by_text(searchText="process_article")  # Use srclight instead
```

### ✅ CORRECT: Notebook Read

```python
# ✅ CORRECT: Use notebook MCP for notebook operations
the-notebook-mcp_notebook_read(notebook_path="/absolute/path/to/notebook.ipynb")
```

### ❌ WRONG: Direct Notebook Access

```python
# ❌ WRONG: ANY direct access to .ipynb files
read(filePath="notebook.ipynb")  # PROHIBITED
json.load(open("notebook.ipynb"))  # PROHIBITED
```

### ✅ CORRECT: Fallback (When MCP Unavailable)

```python
# ✅ CORRECT: When MCP confirmed unavailable
# FALLBACK: PyCharm MCP unavailable
edit(filePath="src/main.py", oldString="foo", newString="bar")
```

### ❌ WRONG: Fallback Without Acknowledgment

```python
# ❌ WRONG: Using fallback without acknowledgment
edit(filePath="src/main.py", oldString="foo", newString="bar")  # Missing comment
```

### ✅ CORRECT: Notebook (Use MCP)

```python
# ✅ CORRECT: Use notebook MCP for all notebook operations
the-notebook-mcp_notebook_read(notebook_path="/absolute/path/to/notebook.ipynb")

# See `notebook-operations` skill for complete tool reference
```

### ❌ WRONG: Direct Notebook Access

```python
# ❌ WRONG: ANY direct access to .ipynb files
read(filePath="notebook.ipynb")  # PROHIBITED
json.load(open("notebook.ipynb"))  # PROHIBITED

# See `notebook-operations` skill for zero-tolerance rules
```