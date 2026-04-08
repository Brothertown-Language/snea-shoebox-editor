# Task: verify-size-limits

## Purpose

Check code artifacts for size limit compliance before commit or PR creation.

## Entry Criteria

- Code changes prepared for commit
- Files modified or created
- User requests size verification

## Exit Criteria

- All new/modified functions checked (≤40 lines)
- All new/modified notebook cells checked (≤50 lines)
- All new files checked (≤300 lines)
- Grandfathered files identified and excluded
- Violations reported with recommendations

## Procedure

### Step 1: Identify Changed Files

```bash
git status --porcelain
git diff --name-only
```

### Step 2: Classify Files

**New files:** MUST be checked
**Modified files:** Check modified functions/cells only
**Grandfathered files:** Identify and exclude from checks

**Grandfather detection:**
```bash
# File existed before this skill's introduction
git log --oneline --follow -- <file> | wc -l
# If > 1, file is grandfathered
```

### Step 3: Check Function Sizes

**Using ai_bin/py structure:**
```bash
uv run python ai_bin/py structure --stats <file>
```

**Output includes:**
```
function_name: 35 lines
another_function: 45 lines  # ← EXCEEDS 40-line limit
```

**For each function > 40 lines:**
1. Flag as violation
2. Note current size vs limit
3. Recommend decomposition

### Step 4: Check Notebook Cell Sizes

**Using notebook-mcp tools:**
```bash
the-notebook-mcp_notebook_get_outline notebook_path="<path>"
the-notebook-mcp_notebook_read_cell notebook_path="<path>" cell_index=N
```

**For each cell:**
1. Count source lines
2. If > 50 lines, flag as violation
3. Recommend splitting

### Step 5: Check File Sizes

**Using wc:**
```bash
wc -l <file>
grep -c '.' <file>  # Exclude blank lines
```

**For NEW files only:**
- If > 300 lines, flag as violation
- Recommend package structure split

### Step 6: Generate Violation Report

**Format:**
```
SIZE VIOLATIONS DETECTED

File: src/module.py
Function: process_data
Current: 45 lines
Limit: 40 lines
Recommendation: Decompose into process_data() + validate_data() + transform_data()

Notebook: notebooks/analysis.ipynb
Cell 5: Data processing
Current: 65 lines
Limit: 50 lines
Recommendation: Split into 3 focused cells

New File: src/large_module.py
Current: 350 lines
Limit: 300 lines
Recommendation: Split into package/ with submodules
```

### Step 7: Halt on Violations

**If ANY violations found:**
1. STOP - do not proceed with commit
2. Post violation report to user
3. Wait for fixes before continuing

**If NO violations found:**
1. Report: "Size limits verified ✓"
2. Proceed with commit workflow

## Size Limits Reference

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| Functions | 40 lines | Body only (no docstrings, imports, blanks) |
| Notebook Cells | 50 lines | All lines in cell source |
| Files (NEW only) | 300 lines | Total (excluding blanks, module docstring) |

## Grandfather Policy

**Existing files are EXEMPT:**
- Files that existed before this skill
- Modified grandfathered files: check NEW code only
- No retroactive errors on existing code

**New files must comply:**
- New files created by agent
- Newly added files via git add

## Common Issues

| Issue | Resolution |
|-------|------------|
| "Function is 35 lines but flagged" | Check if counting docstrings - should exclude |
| "File was just created but grandfathered?" | File moved/renamed - check git history |
| "Cell has 48 lines but marked ok" | Correct - under 50 limit |
| "Should I decompose all grandfathered files?" | No - only during natural refactoring |

## Context Required

- Related skills: git-workflow (commit preparation)
- Grandfather policy: Files > 1 commit old are exempt
- New files require full compliance check
