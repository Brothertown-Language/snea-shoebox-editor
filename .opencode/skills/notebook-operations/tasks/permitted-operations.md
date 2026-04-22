# Task: permitted-operations

## Purpose

Complete reference table for all notebook MCP operations with their tool names and parameters.

## Complete Tool Reference

| Operation | Tool |
|-----------|------|
| Read entire notebook | `the-notebook-mcp_notebook_read` |
| Read cell source | `the-notebook-mcp_notebook_read_cell` |
| Get notebook info | `the-notebook-mcp_notebook_get_info` |
| Get cell count | `the-notebook-mcp_notebook_get_cell_count` |
| Get outline | `the-notebook-mcp_notebook_get_outline` |
| Search notebook | `the-notebook-mcp_notebook_search` |
| Search (case-sensitive) | `the-notebook-mcp_notebook_search` with `case_sensitive=True` |
| Create notebook | `the-notebook-mcp_notebook_create` |
| Delete notebook | `the-notebook-mcp_notebook_delete` |
| Rename notebook | `the-notebook-mcp_notebook_rename` |
| Export notebook | `the-notebook-mcp_notebook_export` |
| Add cell | `the-notebook-mcp_notebook_add_cell` |
| Edit cell source | `the-notebook-mcp_notebook_edit_cell` |
| Delete cell | `the-notebook-mcp_notebook_delete_cell` |
| Move cell | `the-notebook-mcp_notebook_move_cell` |
| Duplicate cell | `the-notebook-mcp_notebook_duplicate_cell` |
| Split cell | `the-notebook-mcp_notebook_split_cell` |
| Merge cells | `the-notebook-mcp_notebook_merge_cells` |
| Change cell type | `the-notebook-mcp_notebook_change_cell_type` |
| Read metadata | `the-notebook-mcp_notebook_read_metadata` |
| Edit metadata | `the-notebook-mcp_notebook_edit_metadata` |
| Read cell metadata | `the-notebook-mcp_notebook_read_cell_metadata` |
| Edit cell metadata | `the-notebook-mcp_notebook_edit_cell_metadata` |
| Clear cell outputs | `the-notebook-mcp_notebook_clear_cell_outputs` |
| Clear all outputs | `the-notebook-mcp_notebook_clear_all_outputs` |
| Validate notebook | `the-notebook-mcp_notebook_validate` |
| Execute cell | `the-notebook-mcp_notebook_execute_cell` ⚠️ |

**⚠️ EXECUTION RESTRICTION:** Notebook execution requires explicit per-session user authorization. Production data execution is ABSOLUTELY FORBIDDEN.

## Required Parameters

Most tools require `notebook_path` as an absolute path:
```python
the-notebook-mcp_notebook_read(notebook_path="/absolute/path/to/notebook.ipynb")
```

Cell operations require `cell_index` (0-based):
```python
the-notebook-mcp_notebook_read_cell(notebook_path="/absolute/path/to/notebook.ipynb", cell_index=0)
```

Search requires `query`:
```python
the-notebook-mcp_notebook_search(notebook_path="/absolute/path/to/notebook.ipynb", query="search_term")
```