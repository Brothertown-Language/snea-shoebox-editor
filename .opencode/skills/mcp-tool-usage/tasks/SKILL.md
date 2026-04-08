# Task: verify-tier0

## Purpose

Verify that PyCharm MCP tools are used for ALL file operations when PyCharm MCP is available.

## Entry Criteria

- File operation needed (read, write, edit, search)
- PyCharm MCP available

## Exit Criteria

- Tier 0 tool used for file operation
- No direct file tools used (read, write, edit, glob, grep)
- No shell file operations (cat, sed, echo)

## Procedure

### Step 1: Check MCP Availability

```python
# Probe PyCharm MCP availability
pycharm_get_project_modules()

# If successful: PyCharm MCP available
# If failed: Fall back to direct tools (with # FALLBACK comment)
```

### Step 2: Select Correct Tier

**Tier 0 - MANDATORY (when MCP available):**
- `pycharm_get_file_text_by_path` - Read files
- `pycharm_replace_text_in_file` - Edit files
- `pycharm_create_new_file` - Create files
- `pycharm_find_files_by_glob` - Find files
- `pycharm_search_in_files_by_text` - Search in files

**Tier 1 - FALLBACK (when MCP unavailable):**
- `read` tool - Read files
- `edit` tool - Edit files
- `write` tool - Write files
- `glob` tool - Find files
- `grep` tool - Search files

### Step 3: Verify Usage

**Check for violations:**
```bash
# Check for direct tool usage when MCP available
grep -r "read\(" . --include="*.py" | grep -v "# FALLBACK"
grep -r "edit\(" . --include="*.py" | grep -v "# FALLBACK"
grep -r "write\(" . --include="*.py" | grep -v "# FALLBACK"
```

### Step 4: Report Violations

**If violation found:**
```markdown
MCP TOOL VIOLATION

File: [file]
Operation: [read/write/edit/glob/grep]
Used: [direct tool]
Should use: [MCP tool]

Resolution: Replace direct tool with MCP tool
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| MCP not responding | Use fallback tools with # FALLBACK comment |
| Direct tool used | Replace with MCP tool |
| Shell command used | Use MCP tool or fallback tool |

## Context Required

- MCP availability checked at session init
- Related tasks: `verify-tier1`, `report-violations`
