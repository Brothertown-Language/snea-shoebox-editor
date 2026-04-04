# Task: data-integrity

Pattern verification for HOW data is handled. Blast radius: HIGH. Invoke before data operations.

## Pattern Table

| Requirement | Guideline Reference |
|-------------|-------------------|
| No synthetic/fabricated data | `090-data-integrity.md` - Global Absolute Prohibition |
| No defaults for missing required data | `201-errors-missing-data.md` - Missing Data Rules |
| Exceptions logged AND re-raised | `200-errors-exception-handling.md` - Exception Handling |
| Required data returns concrete types | `201-errors-missing-data.md` - Optional vs Required |
| Hardcoded entity IDs forbidden | `090-data-integrity.md` - No Hardcoded Entity IDs |
| Batch operations use pagination | `090-data-integrity.md` - Batch Operations |
| Production data protection | `090-data-integrity.md` - Production Data Protection |

## Violation Table

| Violation | Correct Action |
|-----------|---------------|
| `data.get("field", "default")` for required field | Raise error if missing |
| `try: ... except: pass` | Log AND re-raise, never swallow |
| `return None` for required data | Raise error instead |
| Fabricated test data in production code | Use real data sources |
| Hardcoded PMIDs/IDs in code | Derive dynamically at runtime |
| Large batch without pagination | Use offset/keyset pagination |
| `list(values)` without validation | Validate, raise on missing required |
| Silent defaults for required | Explicit validation with error |

## Invocation

```
/skill implementation-quality --task data-integrity
```

Invoke before:
- Database operations
- Data transformations
- API calls returning data
- Configuration loading
- User input handling

## Pre-Data Operation Checklist

### Required Data
- [ ] Required fields validated (no defaults)
- [ ] Missing required data raises error
- [ ] Concrete return types (not `Optional` for required)

### Exception Handling
- [ ] All `except` blocks re-raise or wrap
- [ ] Exceptions logged with context
- [ ] No bare `except:` or `except Exception: pass`

### Data Sources
- [ ] No synthetic/fabricated data in production
- [ ] No hardcoded entity IDs
- [ ] Test fixtures isolated from production

### Batch Operations
- [ ] Pagination for large datasets
- [ ] Batch size under PostgreSQL limit (`batch_size × N < 65535`)
- [ ] Progress tracking with `tqdm`

## Cross-References

- `090-data-integrity.md` - Data integrity rules
- `201-errors-missing-data.md` - Missing data handling
- `200-errors-exception-handling.md` - Exception handling rules