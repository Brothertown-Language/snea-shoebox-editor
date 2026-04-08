# Task: validate-notebook

## Purpose

Validate Jupyter notebook structure and detect corruption before operations.

## Entry Criteria

- Notebook path provided
- Notebook file exists

## Exit Criteria

- Notebook structure validated
- Corruption detected (if any)
- Backup created (if needed)

## Procedure

### Step 1: Check Notebook Exists

```python
the-notebook-mcp_notebook_get_info(notebook_path="<path>")
```

**If notebook doesn't exist:**
- Report: "Notebook not found: <path>"
- HALT

### Step 2: Validate Structure

**Check for required fields:**
- cells: array of cell objects
- metadata: notebook metadata
- nbformat: format version (must be 4)

### Step 3: Detect Corruption

**Corruption indicators:**
- Missing cells array
- Invalid cell types (not "code" or "markdown")
- Malformed cell structure
- Missing source field in cells

**If corruption detected:**
- DO NOT proceed with operations
- Create backup in `./tmp/notebook-backups/`
- Report corruption details
- HALT

### Step 4: Report Status

```markdown
NOTEBOOK VALIDATION

Path: <path>
Structure: VALID/INVALID
Cells: N cells found
Corruption: NONE/DETECTED [<details>]

Ready for operations: YES/NO
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Missing cells array | Cannot proceed - notebook corrupted |
| Invalid cell types | Report cell index, expected "code" or "markdown" |
| Malformed cells | Report which cells are malformed |
| nbformat mismatch | May still work, log warning |

## Context Required

- notebooks in allowed roots only
- Never use direct file read/write on .ipynb
- Related tasks: `check-corruption`, `backup-notebook`
