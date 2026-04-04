# Engineering Approach Mandate

> **See:** `/skill implementation-quality` for pattern verification tasks and `/skill engineering-approach` for detailed checklists.

## Core Principles

1. **Understand Before Solving** — Read all relevant code before proposing changes. Understand the "why" not just "what". Identify stakeholders and their needs.

2. **Design Before Implementing** — Document the approach in the spec. Consider multiple solutions and tradeoffs. Get approval on approach before coding.

3. **Verify Before Declaring Complete** — Run all tests manually. Check for edge cases. Verify against all success criteria. Update documentation.

4. **Communicate Changes** — Post comments when changes happen (PR created, task completed). DO NOT post comments when creating issues. DO NOT post comments for non-substantive updates (cross-references, origin links, STATUS updates).

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

## Pattern Compliance Verification (Critical)

**⚠️ CRITICAL: All implementation MUST verify pattern compliance against documented guidelines.**

### Pattern Categories

#### File Location Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| Temp files | `./tmp/` directory only | `070-environment.md` |
| Test files | `test/` directory only | `070-environment.md` |
| Migrations | `_Migration` entries in `schema.py` only | `100-persistence.md` |
| Agent scripts | `ai_bin/` directory | `AGENTS.md` |
| Standalone scripts | `scripts/` directory | `070-environment.md` |
| Notebooks | Notebooks directory only | `061-notebook-rules.md` |

| Violation | Correct Action |
|-----------|----------------|
| Standalone migration file | Move to `_Migration` entry in `src/commons/persistence/pg/schema.py` |
| Temp file at project root | Delete, recreate in `./tmp/` |
| Test file in `src/` | Move to `test/` directory |
| Agent script outside `ai_bin/` | Move to `ai_bin/` |

#### Code Structure Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| DB operations | Must use Repository classes | `100-persistence.md` |
| Direct DB access | FORBIDDEN in `src/` | `100-persistence.md` |
| Re-exports in `__init__.py` | FORBIDDEN | `080-code-standards.md` |
| Notebook file operations | Must use `the-notebook-mcp` tools | `061-notebook-rules.md` |
| MCP tool usage | Mandatory when available | `015-mcp-preference.md` |

| Violation | Correct Action |
|-----------|----------------|
| `session.execute()` in `src/` | Create/use Repository class, move DB logic there |
| `session.query()` in `src/` | Create/use Repository class, move query there |
| `from X import Y` in `__init__.py` | Use direct import (`from X import Y`) at call site |
| `read`/`edit`/`write` on `.ipynb` | Use `the-notebook-mcp_notebook_*` tools |
| `edit` tool on project file with PyCharm MCP | Use `pycharm_*` tools |

#### Environment Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| Node.js in Python projects | FORBIDDEN | `070-environment.md` |
| Python execution | `uv run python` only | `070-environment.md` |
| Package management | `uv sync` only, never `uv add` | `070-environment.md` |
| Absolute paths in commands | FORBIDDEN | `060-tool-usage.md` |
| System temp `/tmp/` | FORBIDDEN, use `./tmp/` only | `060-tool-usage.md` |

| Violation | Correct Action |
|-----------|----------------|
| `npm install` in Python project | Use Python-native equivalents (`uv`, `ruff`, `pytest`) |
| `python script.py` | Use `uv run python script.py` |
| `pip install package` | Edit `pyproject.toml`, run `uv sync` |
| `cd /home/user/git/repo && command` | Use workdir or relative paths |
| File path `/tmp/file.txt` | Use `./tmp/file.txt` |

#### Data Patterns

| Pattern | Requirement | Guideline Reference |
|---------|-------------|---------------------|
| Synthetic/fabricated data | FORBIDDEN | `090-data-integrity.md` |
| Defaults for missing required data | FORBIDDEN | `201-errors-missing-data.md` |
| Silent exception swallowing | FORBIDDEN | `200-errors-exception-handling.md` |
| `None` return for required data | FORBIDDEN | `201-errors-missing-data.md` |

| Violation | Correct Action |
|-----------|----------------|
| `data.get("field", "default")` for required field | Raise error if missing |
| `try: ... except: pass` | Log AND re-raise, never swallow |
| `return None` for required data | Raise error instead |
| Fabricated test data in production code | Use real data sources |

### Pre-Implementation Verification

**Before creating ANY file, verify:**

```markdown
## Pre-Implementation Checklist

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
```

### Post-Implementation Verification

**Before marking task complete, verify:**

```markdown
## Post-Implementation Checklist

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
```

### Violation Detection by Spec Auditor

**The `spec-auditor` skill checks for pattern violations:**

When auditing a spec, the auditor verifies:
1. New files respect location patterns
2. No direct DB access in `src/`
3. No re-exports in `__init__.py`
4. Migrations follow schema system patterns
5. Notebook operations use MCP tools

**Violation Report Format:**

```markdown
## Pattern Violations Found

| Category | Violation | Guideline | Remediation |
|----------|-----------|-----------|-------------|
| File Location | Migration file in `src/database/migrations/` | `100-persistence.md` | Move to `_Migration` entry in `schema.py` |
| Code Structure | `session.execute()` in `src/services/` | `100-persistence.md` | Use Repository class in `src/commons/persistence/` |
| Imports | `from X import Y` in `__init__.py` | `080-code-standards.md` | Use direct import at call site |
```

### Integration with Skills

**The `engineering-approach` skill includes pattern verification:**

1. **Pre-work task**: Pattern compliance checklist
2. **Implementation workflow**: Verify files follow patterns
3. **Review-prep task**: Post-implementation pattern verification

**See `engineering-approach` skill for complete workflow.**
