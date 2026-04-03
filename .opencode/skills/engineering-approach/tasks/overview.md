# Task: overview

Engineering methodology ensuring proper understanding, design, verification, and scope discipline.

## Core Principles

1. **Understand Before Solving**
   - Read all relevant code before proposing changes
   - Understand the "why" not just "what"
   - Identify stakeholders and their needs

2. **Design Before Implementing**
   - Document the approach in the spec
   - Consider multiple solutions and tradeoffs
   - Get approval on approach before coding

3. **Verify Before Declaring Complete**
   - Run all tests manually
   - Check for edge cases
   - Verify against all success criteria
   - Update documentation

4. **Communicate Changes**
   - Post comments when changes happen (PR created, task completed)
   - DO NOT post comments when creating issues
   - DO NOT post comments for non-substantive updates (cross-references, origin links, STATUS updates)

## Scope Discipline (Critical)

### No Feature Creep

- Implement ONLY what is specified in the approved spec
- No additions, enhancements, or "improvements" beyond scope
- No refactoring unless explicitly requested
- No unrelated fixes discovered during work (file separate issue)

### No Unapproved Work

- Never start implementation without explicit authorization
- "Should I do X?" is a question, not authorization
- Wait for clear "proceed" or "yes" before starting
- If unclear, ask - do not assume

## Anti-Patterns to Avoid

### ❌ FORBIDDEN in Specs

- Vague requirements ("make it better")
- Missing success criteria
- Unstated assumptions
- Ignored edge cases
- No risk assessment
- Skipping design phase
- Proceeding without approval

### ❌ FORBIDDEN in Implementation

- Implementing beyond spec scope
- Adding "helper" functions not requested
- Improving "nearby" code while you're there
- Adding tests for unrequested functionality
- Modifying related files "just to be safe"

## Pre-Implementation Verification

**Before creating ANY file, verify:**

### File Locations
- [ ] New Python file in `src/`? OK if following project structure
- [ ] New test file? Must be in `test/`
- [ ] Migration? Must be `_Migration` entry in `schema.py`
- [ ] Temp/output file? Must be in `./tmp/`
- [ ] Notebook file? Must follow `061-notebook-rules.md`

### Code Structure
- [ ] DB operation? Will use Repository class
- [ ] Import in `__init__.py`? Only docstring, no re-exports
- [ ] Notebook operation? Will use `the-notebook-mcp` tools
- [ ] File edit with PyCharm MCP available? Will use `pycharm_*` tools

### Environment
- [ ] Need Node.js? For Python projects, use Python alternatives
- [ ] Running Python? Will use `uv run python`
- [ ] Adding dependency? Edit `pyproject.toml`, run `uv sync`
- [ ] Using temp directory? Will use `./tmp/`, not `/tmp/`

### Data Handling
- [ ] Missing required field? Will raise error, not use default
- [ ] Exception handling? Will log AND re-raise
- [ ] Returning data? Required fields never return `None`

## Post-Implementation Verification

**Before marking task complete, verify:**

### File Locations Verified
- [ ] Temp files in `./tmp/`
- [ ] Test files in `test/`
- [ ] Migrations in `schema.py`
- [ ] Scripts in `scripts/` or `ai_bin/`

### Code Structure Verified
- [ ] No `session.execute()` or `session.query()` in `src/`
- [ ] No re-exports in `__init__.py`
- [ ] Notebook operations used `the-notebook-mcp` tools
- [ ] File edits used PyCharm MCP when available

### Environment Verified
- [ ] No Node.js installed
- [ ] All Python commands use `uv run`
- [ ] Dependencies added via `pyproject.toml` + `uv sync`
- [ ] No absolute paths in commands
- [ ] Temp files in `./tmp/`, not `/tmp/`

### Data Handling Verified
- [ ] No synthetic/fabricated data
- [ ] Required fields validated, never default
- [ ] Exceptions logged AND re-raised
- [ ] Required data returns concrete types, never `Optional`

## Cross-References

- `000-critical-rules.md` - Critical violation enforcement
- `080-code-standards.md` - Code quality standards
- `130-authority-source.md` - Code as authoritative source