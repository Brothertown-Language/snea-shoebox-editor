# Task: selection-guide

## Purpose

Tool selection decision trees for choosing the correct tool when multiple options exist.

## For Python Code Operations

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

## For File Operations

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

| File Extension | Linter | Formatter |
|----------------|--------|-----------|
| `.py` | `ruff check` | `ruff format` |
| `.md` | `pymarkdownlnt scan` | `mdformat` |

**CRITICAL:** Never run `ruff` on `.md` files. Never run `pymarkdownlnt` on `.py` files.