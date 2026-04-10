---
name: test-driven-development
description: Use when writing tests before implementation, or when adopting a test-first development approach. Triggers on: TDD, test first, red green refactor, write test, test-driven, unit test, regression.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: test-driven-development

## Overview

Test-driven development (TDD) workflow that enforces writing tests before implementation code. Tests define the contract, implementation satisfies the contract, and refactoring maintains quality. This is an optional quality gate skill invoked contextually when the development approach benefits from TDD.

**Source Attribution:** This skill is adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are a Test-First Developer. Your focus is defining expected behavior through tests before writing implementation.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `red` | Write failing test for new behavior | ~600 |
| `green` | Write minimal implementation to pass test | ~500 |
| `refactor` | Clean up while keeping tests green | ~400 |

## Invocation

- `/skill test-driven-development` - Overview only
- `/skill test-driven-development --task red` - Write failing test
- `/skill test-driven-development --task green` - Write minimal implementation
- `/skill test-driven-development --task refactor` - Refactor with tests green

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when:
   - User explicitly requests TDD approach
   - Spec has clear testable behavior
   - Development involves new functions/classes with well-defined contracts
   - NOT mandatory — use when TDD adds value

2. **Red-Green-Refactor cycle:**
   - RED: Write a test that fails (defines expected behavior)
   - GREEN: Write minimal code to make test pass (satisfy contract)
   - REFACTOR: Clean up code while keeping tests green

3. **Exit conditions:** TDD cycle is COMPLETE when:
   - Test was written before implementation
   - Implementation passes the test
   - Code is refactored and clean
   - All existing tests still pass

## Red Phase: Write Failing Test

### Principles

1. **Test defines the contract:** What should the function/class do?
2. **Test must fail:** If test passes without implementation, test is wrong
3. **One assertion per test concept:** Test one behavior per test method
4. **Use meaningful test names:** `test_functionName_expectedBehavior_whenCondition`

### Workflow

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

### Test Location

Tests go in `test/` directory following project convention:

```
test/
├── test_module.py          # Unit tests for src/module.py
├── test_integration.py     # Integration tests
└── conftest.py             # Shared fixtures
```

### Verification

```bash
# Test must FAIL before implementation
uv run pytest test/test_module.py::test_parse_date_iso_format -v
# Expected: FAILED (or ERROR if function doesn't exist yet)
```

## Green Phase: Write Minimal Implementation

### Principles

1. **Write minimal code:** Only enough to make the test pass
2. **No premature optimization:** Get it working first
3. **No scope creep:** Don't add features not tested
4. **Don't predict future tests:** Today's test only

### Workflow

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

### Verification

```bash
# Test must PASS after implementation
uv run pytest test/test_module.py::test_parse_date_iso_format -v
# Expected: PASSED
```

## Refactor Phase: Clean Up

### Principles

1. **Tests stay green:** All tests pass during refactoring
2. **Small steps:** One refactoring at a time
3. **Run tests after each step:** Ensure nothing breaks
4. **No behavior changes:** Refactoring changes structure, not behavior

### Workflow

1. Identify code smells (duplication, long methods, unclear names)
2. Make one small refactoring
3. Run tests
4. If tests pass → commit refactoring
5. If tests fail → revert and try different approach

### Verification

```bash
# All tests must pass after refactoring
uv run pytest test/ -v
```

## Integration with Existing Workflow

### Dispatch Order

TDD is invoked contextually — not mandatory for all development.

```
executing-plans (step with TDD approach) → TDD red → TDD green → TDD refactor → verification-before-completion
```

### When to Use TDD

| Situation | Use TDD? | Reason |
|-----------|----------|--------|
| New function/class with clear contract | ✅ Yes | Tests define expected behavior |
| Bug fix with clear reproduction | ✅ Yes | Test reproduces bug, fix resolves it |
| Complex algorithm | ✅ Yes | Tests verify edge cases |
| Exploration/prototyping | ❌ No | Behavior not yet defined |
| UI layout changes | ❌ No | Hard to test visually |
| Config/data changes | ❌ No | No code logic to test |

### Test Standards

- Use `pytest` for all tests
- Run from root: `uv run pytest test/test_filename.py`
- Use `PgServerManager` for database tests (never SQLite)
- Use `./tmp/` for test artifacts

## Enforcement Mechanism

This is an **optional** quality gate skill. It is not automatically enforced.

### What Skills SHOULD Check

1. **When TDD is selected:**
   - Was test written before implementation?
   - Does test fail without implementation?
   - Does implementation pass the test?
   - Are all tests still green after refactoring?

2. **TDD violations:**
   - Implementation before test → RECOMMEND starting with test
   - Test always passes → Test doesn't validate anything
   - Refactoring breaks tests → Revert and refactor differently

## Cross-References

- Related skills: `systematic-debugging` (testing bug fixes), `verification-before-completion` (evidence)
- Related guidelines: `070-environment.md` (testing standards), `080-code-standards.md` (code quality)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow enforces test-driven development to ensure correctness and prevent regression.

**Key adaptations for OpenCode:**
- Integrated with existing test framework (`pytest`)
- PostgreSQL test fixtures via `PgServerManager`
- Dispatch table integration for contextual invocation
- Optional quality gate (not mandatory)