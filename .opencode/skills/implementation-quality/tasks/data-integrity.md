# Task: data-integrity

Pattern verification for HOW data is handled. Blast radius: HIGH. Invoke before data operations.

## Data Integrity Rules (Zero-Tolerance)

| Pattern | Rule |
|---------|------|
| No synthetic/fabricated data | FORBIDDEN - data must be from real sources |
| No defaults for missing required data | FORBIDDEN - raise error if required field missing |
| Exceptions logged AND re-raised | FORBIDDEN - never swallow exceptions |
| Required data returns concrete types | FORBIDDEN - never return None for required data |
| Hardcoded entity IDs forbidden | FORBIDDEN - derive dynamically at runtime |
| Batch operations use pagination | REQUIRED - for datasets >1000 rows |
| Production data protection | FORBIDDEN - never run against production without explicit auth |

## Error Handling Rules (Zero-Tolerance)

| Pattern | Rule |
|---------|------|
| Bare `except:` | FORBIDDEN - catches system signals |
| `except Exception: pass` | FORBIDDEN - swallows all errors |
| Log without re-raise | FORBIDDEN - must re-raise after logging |
| Return None for required data | FORBIDDEN - raise error instead |

## Complete Data Integrity Rules

**Global Absolute Prohibition:**

- **NO SYNTHETIC/IMAGINARY/FABRICATED DATA — PERIOD, NO EXCEPTIONS**: Real, verifiable data from real sources only
- **FAIL-FAST**: Raise contextual errors immediately, never swallow exceptions
- **NO FALSE DATA**: Never use proxy/fallback/synthetic data
- **NO DEFAULT DATA**: Never assign defaults to fill missing DB fields
- **NO INVALID DEFAULTS**: Never default parameters that drive deterministic logic
- **HARD FAIL ON MISSING REQUIRED DATA**: Raise immediately for missing required fields
- **VERIFY BEFORE RECOMMEND**: Never recommend backfills/schema changes based on assumptions
- **NO UNAUTHORIZED FORMAT CHANGES**: Strictly prohibited without explicit, documented authorization
- **MANDATORY AUDIT LOGGING**: Any proposed format change must include automated audit report
- **Cross-References are MANDATORY**: Any reference data used for validation MUST have source of record documented

## Complete Error Handling Rules

| Pattern | Enforcement |
|---------|-------------|
| Bare `except:` | Zero tolerance - catches system signals, hides critical flow |
| `except Exception: pass` | Zero tolerance - bug factory, errors hidden not handled |
| Pass/continue in except block | Zero tolerance - error lost, no signal to caller |
| Log without re-raise | Zero tolerance - logging is not error handling |
| Explicit exception types | Required - specify what you catch |
| Contextual error wrapping | Required - add context at each layer |
| Let it crash (when appropriate) | Allowed - if you can't add context, propagate |
| Return None for required data | Forbidden - raise ValueError instead |

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

- `090-data-integrity.md` - Complete data integrity rules