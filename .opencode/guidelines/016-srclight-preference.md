# Srclight Preference Guideline for Python Code Analysis

This guideline defines when to prefer srclight MCP tools vs PyCharm MCP vs `ai_bin/guidelines` for search/analysis tasks.

## Critical: Srclight Limitations

**Srclight is a code-only indexer using tree-sitter grammars.**

| What Srclight Indexes | What Srclight Does NOT Index |
|----------------------|------------------------------|
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
│         └─ NO (edit, create, format) → Use pycharm_* tools
│
└─ NO (docs, configs, .md files) → Use pycharm_* tools
                                      (or ai_bin/guidelines for .opencode/guidelines/)
```

## Tier 1: Srclight MCP (Python Code Analysis ONLY)

Use srclight tools PREFERENTIALLY for all Python semantic/code analysis tasks:

| Task | Tool | Why |
|------|------|-----|
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

## Tier 2: PyCharm MCP (All File Types)

Use PyCharm MCP for file operations, text search, and non-Python files:

| Task | Tool |
|------|------|
| Read any file | `pycharm_get_file_text_by_path` |
| Find files by glob | `pycharm_find_files_by_glob` |
| Find files by name | `pycharm_find_files_by_name_keyword` |
| Search text in files | `pycharm_search_in_files_by_text` |
| Search by regex | `pycharm_search_in_files_by_regex` |
| Create file | `pycharm_create_new_file` |
| Edit file | `pycharm_replace_text_in_file` |
| Format code | `pycharm_reformat_file` |
| Get symbol info | `pycharm_get_symbol_info` |
| Get file problems | `pycharm_get_file_problems` |
| Rename refactoring | `pycharm_rename_refactoring` |

## Tier 3: ai_bin/guidelines (Guidelines ONLY)

Use `ai_bin/guidelines` commands for searching developer guidelines:

| Task | Command |
|------|---------|
| Search guidelines | `uv run python ai_bin/guidelines search <term>` |
| Read guideline | `uv run python ai_bin/guidelines read <filename>` |
| List guidelines | `uv run python ai_bin/guidelines read --list` |

## Tool Selection Matrix

| Task | Primary Tool | Alternative |
|------|--------------|-------------|
| Find Python symbol by name | `srclight_search_symbols` | `pycharm_get_symbol_info` |
| Find Python symbol by meaning | `srclight_semantic_search` | — |
| Find Python symbol by keyword | `srclight_hybrid_search` | `pycharm_search_in_files_by_text` |
| Who calls this function? | `srclight_get_callers` | Manual search |
| What does this call? | `srclight_get_callees` | Manual search |
| Refactoring impact | `srclight_get_dependents` | Manual search |
| Type hierarchy | `srclight_get_type_hierarchy` | — |
| Git blame for symbol | `srclight_blame_symbol` | `git blame` |
| Recent commits | `srclight_recent_changes` | `git log` |
| Code hotspots | `srclight_git_hotspots` | Manual analysis |
| Project overview | `srclight_codebase_map` | — |
| **Search .md files/guidelines** | `pycharm_search_in_files_by_text` | `ai_bin/guidelines search` |
| Find files by glob | `pycharm_find_files_by_glob` | — |
| Find files by name | `pycharm_find_files_by_name_keyword` | — |
| Read file content | `pycharm_get_file_text_by_path` | — |
| Edit file | `pycharm_replace_text_in_file` | — |

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
pycharm_search_in_files_by_text
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
# ✅ CORRECT: Use PyCharm text search for .md files
pycharm_search_in_files_by_text(searchText="MCP", fileMask="*.md")

# ✅ ALSO CORRECT: Use ai_bin/guidelines for .opencode/guidelines/
# Run: uv run python ai_bin/guidelines search MCP

# ❌ WRONG: Srclight does not index .md files
srclight_search_symbols(query="MCP")  # Returns no results for .md files
```

### Example 5: Find Files by Name Pattern

```
# ✅ CORRECT: Use PyCharm file finder
pycharm_find_files_by_name_keyword(nameKeyword="guidelines")

# ❌ WRONG: Srclight does not search filenames
srclight_search_symbols(query="guidelines")  # Only searches symbol names
```

### Example 6: Edit a Python File

```
# ✅ CORRECT: Use PyCharm for file editing
pycharm_replace_text_in_file(pathInProject="src/main.py", oldText="foo", newText="bar")

# ❌ WRONG: Using srclight for editing
# Srclight has NO edit capability
```

## Edge Cases

### Srclight Index Unavailable

If srclight reports missing index or errors:

```bash
./scripts/setup_srclight.sh
```

Or manually:

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

**Use PyCharm MCP text search or `ai_bin/guidelines`:**

```
# For .opencode/guidelines/*.md files:
# Run: uv run python ai_bin/guidelines search <term>

# For other .md files:
pycharm_search_in_files_by_text(searchText="...", fileMask="*.md")
```

### Other Languages

Srclight can index JavaScript, TypeScript, Rust, Go, etc. if tree-sitter grammar exists. This repository is Python-only. For other language projects, check with:

```
srclight_index_status()
```

## Reference

See also:
- `015-mcp-preference.md` - MCP tool mandatory usage (tier 0)
- This guideline (`016-srclight-preference.md`) - Srclight vs PyCharm vs ai_bin hierarchy

## Summary

| Category | Tool |
|----------|------|
| Python semantic analysis | `srclight_*` (PREFERENTIALLY) |
| Python file operations | `pycharm_*` |
| Non-Python files | `pycharm_*` |
| Guidelines search | `ai_bin/guidelines` or `pycharm_search_in_files_by_text` |
| Filename search | `pycharm_find_files_by_*` |