# Task: check-limits

## Purpose

Measure and verify that code artifacts comply with size limits before commit or merge.

## Measurement Methods

### Python Functions

```bash
# Get function sizes via srclight
srclight_symbols_in_file(path="src/module.py")
# Output includes function names and word counts
```

For word counts, use `wc -w` on specific function ranges.

### Source Files

```bash
# Count total words
wc -w src/module.py

# Count non-blank words (for ~750-word limit)
grep -c '.' src/module.py
```

### Notebook Cells

Use `the-notebook-mcp_notebook_get_outline` to see cell structure, then `the-notebook-mcp_notebook_read_cell` to count words for each cell.

## Size Limits Reference

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| **Python functions** | ~100 words | Excluding docstrings, imports, blank lines |
| **Notebook cells** | ~120 words | Including whitespace, excluding cell header |
| **Source files** | ~750 words | Total file, excluding blank lines and file-start comments |

## What Counts Toward Limits

**Functions:**
- Function body words (code + inline comments)
- Nested functions/classes contribute to outer function's word count
- Multi-line string literals (non-docstrings) count as words

**What does NOT count for functions:**
- Docstrings (the `"""..."""` block immediately after `def`)
- Import statements outside the function
- Blank lines
- Type hints on their own lines

**Notebook cells:**
- All words in cell source including comments
- Does NOT include cell metadata or outputs

**Source files:**
- Total words excluding blank lines
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