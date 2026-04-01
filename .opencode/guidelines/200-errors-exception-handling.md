# Error Handling: Exception Handling

## Global Absolute Prohibition

**NEVER FUCKING SWALLOW EXCEPTIONS OR OTHERWISE HIDE ERRORS OR MISSING DATA.**

This is a zero-tolerance rule. Violations will be:
- Caught in code review
- Flagged immediately during implementation
- Treated as critical bugs requiring immediate fix

---

## 1. Exception Handling Rules

### 🚫 FORBIDDEN PATTERNS

#### Bare except

```python
# ❌ FORBIDDEN - catches KeyboardInterrupt, SystemExit
try:
    ...
except:
    pass
```

**WHY**: Bare `except:` catches EVERYTHING, including system exit signals and keyboard interrupts. It hides critical control flow.

**CORRECT**: Specify exception types, or use `except Exception:` if truly needed.

---

#### Bare except Exception

```python
# ❌ FORBIDDEN - silently discards all errors
try:
    ...
except Exception:
    pass
```

**WHY**: This pattern is an anti-pattern used to "make code not crash". It's a bug factory - errors are hidden, not handled.

**CORRECT**:
```python
try:
    result = some_operation()
except SomeSpecificError as e:
    logger.error(f"Failed to X: {e}")
    raise  # RE-RAISE - do not swallow
except Exception as e:
    # Catch-all only for logging context, then re-raise
    logger.error(f"Unexpected error in Y: {e}")
    raise RuntimeError(f"Failed during Y: {e}") from e
```

---

#### Pass or continue in except block

```python
# ❌ FORBIDDEN - error is lost
try:
    process_data(data)
except Exception:
    pass  # or continue, or return None
```

**WHY**: The error disappears. Downstream code receives no signal that anything went wrong.

**CORRECT**:
```python
try:
    process_data(data)
except DataValidationError as e:
    raise ValueError(f"Invalid data at record {record_id}: {e}") from e
```

---

#### Log without re-raise

```python
# ❌ FORBIDDEN - log only, no propagation
try:
    ...
except Exception as e:
    logger.error(f"Something went wrong: {e}")
    # Function continues as if nothing happened
```

**WHY**: Logging is NOT error handling. The error is hidden from the caller.

**CORRECT**:
```python
try:
    ...
except Exception as e:
    logger.error(f"Critical failure: {e}")
    raise  # MUST RE-RAISE
```

---

### ✅ REQUIRED PATTERNS

#### Explicit exception types

```python
# ✅ GOOD - specific, re-raises
try:
    file_content = read_file(path)
except FileNotFoundError:
    raise ValueError(f"Configuration file not found: {path}")
except PermissionError as e:
    raise RuntimeError(f"Insufficient permissions for {path}: {e}") from e
```

---

#### Contextual error wrapping

```python
# ✅ GOOD - adds context at each layer
def process_record(record_id: int) -> ProcessedRecord:
    try:
        raw_data = fetch_raw_data(record_id)
        return transform(raw_data)
    except DatabaseError as e:
        raise DataFetchError(f"Failed to fetch record {record_id}: {e}") from e
    except ValidationError as e:
        raise ProcessingError(f"Record {record_id} failed validation: {e}") from e
```

**WHY**: Each layer adds relevant context. The final error message tells you WHERE (process_record), WHAT (fetch vs validation), and WHY (original cause).

---

#### Let it crash (when appropriate)

```python
# ✅ GOOD - don't catch if you can't handle
def calculate_average(values: list[float]) -> float:
    # Let ZeroDivisionError propagate naturally
    # The caller can decide if empty list is acceptable
    return sum(values) / len(values)
```

**WHY**: Not every error needs a try-except. If you can't add context or handle it meaningfully, let it propagate to code that can.

---

*Source: Content migrated from `095-never-hide-problems.md`*