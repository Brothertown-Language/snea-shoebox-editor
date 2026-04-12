# Task: green

## Purpose

Write minimal implementation code to make the failing test pass. No more, no less.

## Operating Protocol

1. Invoked by: `/skill test-driven-development --task green`
2. When to use: After `--task red` has confirmed a failing test
3. Exit criteria: Implementation written, test PASSES

## Principles

1. **Write minimal code:** Only enough to make the test pass
2. **No premature optimization:** Get it working first
3. **No scope creep:** Don't add features not tested
4. **Don't predict future tests:** Today's test only

## Workflow

```python
# src/module.py

from datetime import date

def parse_date(date_string: str) -> date:
    """Parse ISO format date string to date object."""
    try:
        return date.fromisoformat(date_string)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}")
```

## Verification

```bash
# Test must PASS after implementation
uv run pytest test/test_module.py::test_parse_date_iso_format -v
# Expected: PASSED
```

## Context Required

- Related skills: `test-driven-development` (parent skill)
- Related tasks: `red`, `refactor`