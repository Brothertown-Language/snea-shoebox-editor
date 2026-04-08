# No Backward Compatibility During Refactoring

## Rule

When refactoring internal code (non-public API):
- Do NOT create backward compatibility aliases
- Do NOT add deprecation warnings
- Fix ALL callers immediately
- Clean breaks are less confusing and less wasteful

## Rationale

Backward compatibility is ONLY for public APIs with external consumers. Internal code has no external consumers - only the current codebase. Creating backward compatibility aliases:

1. **Increases maintenance burden** - aliases must be maintained alongside new names
2. **Creates confusion** - developers see both old and new names, unclear which to use
3. **Delays the inevitable** - aliases accumulate until finally removed
4. **Litters the codebase** - deprecation warnings, `# TODO: remove` comments, stale imports

## When to Apply

### Apply this rule when:
- Renaming internal modules, classes, functions, or variables
- Changing internal function signatures
- Moving code between internal modules
- Refactoring internal data structures

### Do NOT apply when:
- Changing public API (anything users import)
- Modifying library interfaces consumed externally
- Changing database schemas that external tools might use
- Updating configuration file formats that users might have customized

## Examples

### Bad: Backward Compatibility Alias

```python
# query_ir.py
CompiledQuery = FieldQuery | CompoundFieldQuery

# deprecated aliases - DO NOT DO THIS
PgQuery = CompiledQuery  # Deprecated: use CompiledQuery

def render_tsquery(expr: QueryExpr) -> str:
    ...

# deprecated - DO NOT DO THIS
def render_pg_tsquery(expr: QueryExpr) -> str:
    """Deprecated: use render_tsquery"""
    return render_tsquery(expr)
```

### Good: Clean Break

```python
# query_ir.py
CompiledQuery = FieldQuery | CompoundFieldQuery

def render_tsquery(expr: QueryExpr) -> str:
    ...

# Then update ALL callers immediately:
# - query_compiler.py
# - edismax_query.py
# - test files
# - notebook imports
```

## Enforcement

1. **Pre-commit hooks** should reject deprecated alias patterns
2. **Code review** should flag any backward compatibility shims
3. **Tests** must use new names only - no test coverage for deprecated aliases

## Related Guidelines

- 080-code-standards.md - General code quality
- 090-data-integrity.md - Schema migration policies (different concern)
