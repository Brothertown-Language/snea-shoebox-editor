# Srclight Preference Guideline for Python Code Analysis

This guideline defines when to prefer srclight MCP tools vs opencode built-in tools vs `.opencode/tools/guidelines` for search/analysis tasks.

## Critical: Srclight Limitations

**Srclight is a code-only indexer using tree-sitter grammars.**

| What Srclight Indexes | What Srclight Does NOT Index |
| -- | -- |
| Python `.py` files | Markdown `.md` files |
| Python symbols (classes, functions, etc.) | Documentation |
| Python imports/dependencies | Config files |
| Python call graphs | Non-Python files |

**Index verification:**

```
Languages: python (117 files, 1139 symbols)
Config options: --db PATH, --embed TEXT (no include/exclude)
```

## Tool Selection Decision Tree

```
Is the task about Python code?
│
├─ YES → Is it semantic analysis/search?
│         │
│         ├─ YES → Use srclight_* tools
│         │
│         └─ NO (edit, create, format) → Use opencode built-in tools
│              (or pycharm_* for unique capabilities like rename)
│
└─ NO (docs, configs, .md files) → Use opencode built-in tools
                                       (or .opencode/tools/guidelines for .opencode/guidelines/)
```

## Tier 1: Srclight MCP (Python Code Analysis ONLY)

Use srclight tools PREFERENTIALLY for all Python semantic/code analysis tasks:

| Task | Tool | Why |
| -- | -- | -- |
| Find Python symbol by name | `srclight_search_symbols` | Fast FTS + name matching |
| Find Python symbol by meaning | `srclight_semantic_search` | Embedding-based semantic search |
| Find Python symbol by keyword | `srclight_hybrid_search` | Best: FTS + embeddings combined |
| Who calls this function? | `srclight_get_callers` | Built-in call graph |
| What does this call? | `srclight_get_callees` | Built-in dependency graph |
| Refactoring impact | `srclight_get_dependents` | Transitive caller analysis |
| Class hierarchy | `srclight_get_type_hierarchy` | Inheritance tree |
| Git blame for symbol | `srclight_blame_symbol` | Symbol-level history |
| Recent changes | `srclight_recent_changes` | Commit history |
| Code hotspots | `srclight_git_hotspots` | Churn analysis |
| Project overview | `srclight_codebase_map` | Structure + symbol counts |
| Test coverage | `srclight_get_tests_for` | Heuristic test matching |
| Symbol signature | `srclight_get_signature` | Lightweight API lookup |
| Symbols in file | `srclight_symbols_in_file` | File table of contents |

## Tier 2: opencode Built-in Tools (All File Types)

Use opencode built-in tools for basic file operations:

| Task | Tool |
| -- | -- |
| Read file | `read` |
| Write file | `write` |
| Edit file | `edit` |
| Find files | `glob` |
| Search text | `grep` |

## Tier 3: JetBrains MCP (Unique Capabilities Only)

Use JetBrains MCP only for operations with no opencode equivalent:

| Task | Tool |
| -- | -- |
| Semantic rename | `pycharm_rename_refactoring` |
| Code reformat | `pycharm_reformat_file` |
| Build project | `pycharm_build_project` |
| Inspections | `pycharm_get_file_problems` |
| Symbol info | `pycharm_get_symbol_info` |
| Get file problems | `pycharm_get_file_problems` |
| Rename refactoring | `pycharm_rename_refactoring` |

## Tier 4: .opencode/tools/guidelines (Guidelines ONLY)

Use `.opencode/tools/guidelines` commands for searching developer guidelines:

| Task | Command |
| -- | -- |
| Search guidelines | `uv run python .opencode/tools/guidelines search <term>` |
| Read guideline | `uv run python .opencode/tools/guidelines read <filename>` |
| List guidelines | `uv run python .opencode/tools/guidelines read --list` |

## Tool Selection Matrix

| Task | Primary Tool | Alternative |
| -- | -- | -- |
| Find Python symbol by name | `srclight_search_symbols` | `pycharm_get_symbol_info` |
| Find Python symbol by meaning | `srclight_semantic_search` | — |
| Find Python symbol by keyword | `srclight_hybrid_search` | `grep` |
| Who calls this function? | `srclight_get_callers` | Manual search |
| What does this call? | `srclight_get_callees` | Manual search |
| Refactoring impact | `srclight_get_dependents` | Manual search |
| Type hierarchy | `srclight_get_type_hierarchy` | — |
| Git blame for symbol | `srclight_blame_symbol` | `git blame` |
| Recent commits | `srclight_recent_changes` | `git log` |
| Code hotspots | `srclight_git_hotspots` | Manual analysis |
| Project overview | `srclight_codebase_map` | — |
| **Search .md files/guidelines** | `grep` | `.opencode/tools/guidelines search` |
| Find files by glob | `glob` | — |
| Read file content | `read` | — |
| Edit file | `edit` | — |

## Embeddings and Semantic Search

Semantic search requires embedding coverage. Check before using:

```
srclight_embedding_status  # Returns: symbol count, coverage %, model name
```

For this repository: 100% coverage with `qwen3-embedding` model.

## Fallback Chain

When srclight fails or returns no results:

```
srclight_search_symbols
    ↓ (no results)
srclight_hybrid_search
    ↓ (no results)
grep
```

## Examples

### Example 1: Find a Python Function by Name

```
# ✅ CORRECT: Use srclight for Python symbol search
srclight_search_symbols(query="process_article", kind="function")

# ❌ WRONG: Using PyCharm text search for Python symbols
pycharm_search_in_files_by_text(searchText="process_article")
```

### Example 2: Find Who Calls a Function

```
# ✅ CORRECT: Use srclight call graph
srclight_get_callers(symbol_name="process_article", project="<project-name>")

# ❌ WRONG: Manual text search for call sites
pycharm_search_in_files_by_text(searchText="process_article(")
```

### Example 3: Find Code by Semantic Meaning

```
# ✅ CORRECT: Use srclight semantic search
srclight_semantic_search(query="code that handles article parsing", kind="function")

# ❌ WRONG: Text search cannot find semantic matches
pycharm_search_in_files_by_text(searchText="article parsing")
```

### Example 4: Search Guidelines/Documentation

```
# ✅ CORRECT: Use grep for .md files
grep(pattern="MCP", glob="**/*.md")

# ✅ ALSO CORRECT: Use .opencode/tools/guidelines for .opencode/guidelines/
# Run: uv run python .opencode/tools/guidelines search MCP

# ❌ WRONG: Srclight does not index .md files
srclight_search_symbols(query="MCP")  # Returns no results for .md files
```

### Example 5: Find Files by Name Pattern

```
# ✅ CORRECT: Use glob to find files
glob(pattern="**/test_*.py")

# ❌ WRONG: Srclight does not search filenames
srclight_search_symbols(query="guidelines")  # Only searches symbol names
```

### Example 6: Edit a Python File

```
# ✅ CORRECT: Use opencode built-in edit for simple edits
edit(filePath="src/main.py", oldString="foo", newString="bar")

# ✅ ALSO CORRECT: Use JetBrains MCP rename for symbol refactoring
pycharm_rename_refactoring(pathInProject="src/main.py", symbolName="foo", newName="bar")

# ❌ WRONG: Using srclight for editing
# Srclight has NO edit capability
```

### Worktree Path Resolution

When `WORKTREE_PATH` is set (working in a git worktree), all file operation tools must prefix paths with the worktree path. See `060-tool-usage.md` for the complete tool-by-tool table.

```
# ✅ CORRECT: In worktree context, prefix with WORKTREE_PATH
edit(filePath=f"{WORKTREE_PATH}/src/main.py", oldString="foo", newString="bar")

# ❌ WRONG: Relative path in worktree context resolves to main repo
edit(filePath="src/main.py", oldString="foo", newString="bar")
```

## Edge Cases

### Srclight Index Unavailable

If srclight reports missing index or errors:

```bash
uvx srclight index --embed qwen3-embedding
```

### Finding Files by Name

**Always use PyCharm MCP for filename searches:**

```
pycharm_find_files_by_name_keyword(nameKeyword="test_")
pycharm_find_files_by_glob(globPattern="**/test_*.py")
```

Srclight does not support filename search.

### Guidelines and .md Files

**Use `.opencode/tools/guidelines` or opencode `grep`:**

```
# For .opencode/guidelines/*.md files:
# Run: uv run python .opencode/tools/guidelines search <term>

# For other .md files:
grep(pattern="<term>", glob="**/*.md")
```

### Finding Files by Name

**Use opencode `glob` to find files:**

```
glob(pattern="**/test_*.py")
```

## Summary

| Category | Tool |
| -- | -- |
| Python semantic analysis | `srclight_*` (PREFERENTIALLY) |
| Basic file operations | opencode `read`/`write`/`edit`/`glob`/`grep` (PRIMARY) |
| Notebook operations | `the-notebook-mcp_*` (MANDATORY for .ipynb) |
| Guidelines search | `.opencode/tools/guidelines` or `grep` |
| Filename search | `glob` |
| Semantic rename | `pycharm_rename_refactoring` (FALLBACK) |
| Code reformat | `pycharm_reformat_file` (FALLBACK) |
| Build/inspections | `pycharm_build_project`/`pycharm_get_file_problems` (FALLBACK) |
