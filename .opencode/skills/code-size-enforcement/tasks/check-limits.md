# Task: check-limits

## Purpose

Measure and verify that code artifacts comply with size limits before commit or merge.

## Measurement Methods

### Python Functions

```bash
# Get function sizes via srclight
srclight_symbols_in_file(path="src/module.py")
# Output includes function names and line ranges
```

For line counts, use `wc -l` on specific function ranges.

### Source Files

```bash
# Count total lines
wc -l src/module.py

# Count non-blank lines (for 300-line limit)
grep -c '.' src/module.py
```

### Notebook Cells

Use `the-notebook-mcp_notebook_get_outline` to see cell structure, then `the-notebook-mcp_notebook_read_cell` to count lines for each cell.

## Size Limits Reference

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| **Python functions** | 40 lines | Excluding docstrings, imports, blank lines |
| **Notebook cells** | 50 lines | Including whitespace, excluding cell header |
| **Source files** | 300 lines | Total file, excluding blank lines and file-start comments |

## What Counts Toward Limits

**Functions:**
- Function body lines (code + inline comments)
- Nested functions/classes contribute to outer function's line count
- Multi-line string literals (non-docstrings) count as lines

**What does NOT count for functions:**
- Docstrings (the `"""..."""` block immediately after `def`)
- Import statements outside the function
- Blank lines
- Type hints on their own lines

**Notebook cells:**
- All lines in cell source including comments and whitespace
- Does NOT include cell metadata or outputs

**Source files:**
- Total lines excluding blank lines
- Excluding module-level docstrings
- Excluding file-start comments (copyright, license)

## Grandfather Policy

Files that existed BEFORE this skill was introduced are grandfathered:

| Scenario | Enforcement |
|----------|-------------|
| **New file created** | MUST comply with all limits |
| **Modified grandfathered file** | Only modified code checked |
| **Renamed file** | Retains grandfather status |
| **File moved to new location** | Retains grandfather status |
| **Deleted and recreated** | Treated as NEW file |

## Check Procedure

1. Identify all new and modified files in the changeset
2. Skip grandfathered files (only check modified portions)
3. For each file: measure function sizes, cell sizes, file sizes
4. Flag any violations
5. If violations found: invoke `/skill code-size-enforcement --task decompose` for guidance