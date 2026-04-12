# Task: red

## Purpose

Write a failing test that defines the expected behavior before any implementation code exists.

## Operating Protocol

1. Invoked by: `/skill test-driven-development --task red`
2. When to use: When starting TDD cycle — writing the first test for new behavior
3. Exit criteria: Test written and confirmed FAILING (or ERROR if function doesn't exist yet)

## Principles

1. **Test defines the contract:** What should the function/class do?
2. **Test must fail:** If test passes without implementation, test is wrong
3. **One assertion per test concept:** Test one behavior per test method
4. **Use meaningful test names:** `test_functionName_expectedBehavior_whenCondition`

## Workflow

```python
# test/test_module.py

def test_parse_date_iso_format():
    """parse_date should return date object for ISO format strings."""
    result = parse_date("2026-04-07")
    assert result == date(2026, 4, 7)

def test_parse_date_invalid_input_raises():
    """parse_date should raise ValueError for invalid date strings."""
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date("not-a-date")
```

## Test Location

Tests go in `test/` directory following project convention:

```
test/
├── test_module.py          # Unit tests for src/module.py
├── test_integration.py     # Integration tests
└── conftest.py             # Shared fixtures
```

## Verification

```bash
# Test must FAIL before implementation
uv run pytest test/test_module.py::test_parse_date_iso_format -v
# Expected: FAILED (or ERROR if function doesn't exist yet)
```

## Context Required

- Related skills: `test-driven-development` (parent skill)
- Related tasks: `green`, `refactor`