# Task: cell-labels

## Purpose

Cell labeling convention and metadata handling for notebook cells.

## Why Labels Are Recommended

1. **Prevents index confusion:** Cell indices shift when cells are added/deleted. Labels are stable references.
2. **Self-documenting:** Labels describe cell purpose (e.g., `email-report`, `validation-summary`).
3. **Enables label-based edits:** Future tooling may support label-based cell operations.

## Label Naming Convention

- **Format:** lowercase, hyphen-separated (e.g., `load-data`, `email-report`, `ir-compilation`)
- **Length:** 2-30 characters
- **Descriptive:** Should indicate the cell's purpose
- **Unique:** Each label must be unique within a notebook

## How to Add Labels

Use `the-notebook-mcp_notebook_edit_cell_metadata`:

```python
the-notebook-mcp_notebook_edit_cell_metadata(
    notebook_path="/absolute/path/to/notebook.ipynb",
    cell_index=5,
    metadata_updates={"label": "email-report"}
)
```

## Label Examples

| Cell Purpose | Label |
|-------------|-------|
| Load CSV data | `load-data` |
| Clean missing values | `clean-data` |
| Generate summary statistics | `summary-stats` |
| Create visualization | `plot-results` |
| Compile report | `compile-report` |
| Send email | `email-report` |
| Validate schema | `validate-schema` |

## Forbidden Actions

- Direct JSON manipulation like `metadata: {"label": "name"}` in raw notebook files
- Using `json.dump` or `nbformat` to modify metadata
- Using `edit` tool on `.ipynb` files

All metadata changes MUST go through `the-notebook-mcp_notebook_edit_cell_metadata`.