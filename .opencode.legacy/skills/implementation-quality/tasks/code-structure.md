# Task: code-structure

Pattern verification for HOW code is organized. Blast radius: MEDIUM. Load once at implementation start, reference continuously.

## Pattern Table

| Requirement | Guideline Reference |
|-------------|-------------------|
| DB operations use Repository classes | `100-persistence.md` - Repository Usage |
| No `session.execute()` in `src/` | `100-persistence.md` - Repository Usage |
| No `session.query()` in `src/` | `100-persistence.md` - Repository Usage |
| No re-exports in `__init__.py` | `080-code-standards.md` - No Re-exports |
| Notebook operations use MCP tools | `061-notebook-rules.md` - Mandatory MCP |
| File edits use PyCharm MCP when available | `015-mcp-preference.md` - Mandatory MCP |
| Single responsibility methods | `080-code-standards.md` - Design Principles |
| No magic strings/numbers | `080-code-standards.md` - No Magic Strings |
| Top-level documentation | `080-code-standards.md` - Top-Level Documentation |
| Type hints mandatory | `080-code-standards.md` - Typing |

## Violation Table

| Violation | Correct Action |
|-----------|---------------|
| `session.execute()` in `src/` | Create/use Repository class, move DB logic there |
| `session.query()` in `src/` | Create/use Repository class, move query there |
| `from X import Y` in `__init__.py` | Use direct import (`from X import Y`) at call site |
| `read`/`edit`/`write` on `.ipynb` | Use `the-notebook-mcp_notebook_*` tools |
| `edit` tool with PyCharm MCP available | Use `pycharm_*` tools |
| Multiple responsibilities in method | Split into single-purpose methods |
| Magic number in code | Extract to named constant |
| Missing function docstring | Add docstring or module-level comment |

## Invocation

```
/skill implementation-quality --task code-structure
```

Load once at implementation start. Reference continuously during:
- Writing new functions
- Creating new classes
- Organizing imports
- Database operations
- Notebook operations

## Continuous Reference

Keep this task loaded when:
- Writing implementation code
- Refactoring existing code
- Adding new database operations
- Working with notebooks

## Cross-References

- `100-persistence.md` - Repository pattern
- `080-code-standards.md` - Code structure requirements
- `061-notebook-rules.md` - Notebook operations
- `015-mcp-preference.md` - MCP tool preference