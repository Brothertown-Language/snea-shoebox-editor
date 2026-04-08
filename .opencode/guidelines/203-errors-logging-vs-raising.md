# Error Handling: Logging vs Raising

## 3. Logging vs Raising

### Rule: Log AND Raise, Not Log OR Raise

```python
# ❌ WRONG - log only
try:
    risky_operation()
except Exception as e:
    logger.error(f"Failed: {e}")
    # Swallowed - error is lost

# ❌ WRONG - raise only (misses log record)
try:
    risky_operation()
except Exception as e:
    raise  # No log trail

# ✅ CORRECT - log AND raise
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise  # Preserve traceback
```

---

## 4. Agent Behavior Requirements

Agents MUST:

1. **Never write code that swallows exceptions** - no `except: pass`, no `except Exception: continue`, no silent returns
2. **Never hide missing data** - no defaults, no placeholders, no synthetic data for required fields
3. **Always add context** - wrap exceptions with relevant information at each layer
4. **Use domain-specific exceptions when appropriate** - create API/module-specific exception classes (e.g., `MeshValidationError`, `PubMedAPIError`) to clarify WHERE and WHAT failed
5. **Validate early** - check required parameters at function entry
6. **Use type hints** - `Optional` for optional data, non-optional for required data
7. **Document failure modes** - if a function can fail, document HOW it fails in docstring

---

## 5. Code Review Checklist

When reviewing code, check:

- [ ] No bare `except:` blocks
- [ ] No `except Exception: pass` or `except: pass`
- [ ] All `except` blocks either re-raise or raise a new exception
- [ ] Required parameters validated at function entry
- [ ] No defaults applied to missing required data
- [ ] No placeholder/fabricated data used to fill gaps
- [ ] Type hints use `Optional` explicitly for nullable data
- [ ] Error messages include relevant context (ids, names, paths)
- [ ] Logging is paired with re-raising, not standalone
- [ ] Domain-specific exception classes used for API/module boundaries
- [ ] Exception hierarchies used for complex modules (BaseError, APIError, ValidationError, etc.)

---

## 6. Cross-References

- **090-data-integrity.md** - Data quality and validation rules
- **070-environment.md** - Production data protection
- **080-code-standards.md** - Code quality standards
- **000-session-init.md** - Agent initialization and boundaries

This guideline is foundational. When in doubt: **raise, don't return.**

---

*Source: Content migrated from `095-never-hide-problems.md`*