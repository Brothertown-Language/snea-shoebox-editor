# Task: swap-reorder

## Purpose

Composed workflows for swapping and reordering notebook cells. These are not single MCP calls — they compose multiple `move_cell` invocations.

## Swap Two Cells

To swap cells at indices `i` and `j` (where `i < j`):

1. Move cell `i` to position `j`: `the-notebook-mcp_notebook_move_cell(notebook_path=..., from_index=i, to_index=j)`
2. Move cell `j` (now at `j-1` after step 1) to position `i`: `the-notebook-mcp_notebook_move_cell(notebook_path=..., from_index=j-1, to_index=i)`

**Example:** Swap cells at index 2 and index 5:
```
Step 1: move_cell(from_index=2, to_index=5)   → cell at 2 moves to 5, cells 3-5 shift left
Step 2: move_cell(from_index=4, to_index=2)   → the former cell 5 (now at 4) moves to 2
```

## Reorder Multiple Cells

Reordering is a sequence of `move_cell` operations. Process from the target layout backward to avoid index shifts:

1. Define the desired target order (e.g., `[3, 1, 0, 2]` means original cell 3 goes first, then 1, 0, 2).
2. Starting from the last position, move each cell to its target location.

**Example:** Reorder cells `[A, B, C, D]` to `[C, A, D, B]`:
```
Step 1: move_cell(from_index=2, to_index=0)   → [C, A, B, D]
Step 2: move_cell(from_index=3, to_index=1)   → [C, D, A, B]  (adjust indices after step 1 shifts)
```

## Verification

Always use `the-notebook-mcp_notebook_get_outline` before AND after any swap/reorder operation to verify the cell order is correct:

```python
# Before
the-notebook-mcp_notebook_get_outline(notebook_path="/path/to/notebook.ipynb")

# Perform swap/reorder operations

# After
the-notebook-mcp_notebook_get_outline(notebook_path="/path/to/notebook.ipynb")
```

## Common Pitfalls

- **Index shift after move:** After moving a cell, all indices after the source position shift. Account for this in subsequent moves.
- **Not verifying:** Always verify cell order after operations using `get_outline`.
- **Using absolute paths:** Notebook paths must be absolute paths.