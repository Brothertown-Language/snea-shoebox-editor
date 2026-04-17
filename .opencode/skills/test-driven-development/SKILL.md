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

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `red` | Write failing test for new behavior | ~200 |
| `green` | Write minimal implementation to pass test | ~150 |
| `refactor` | Clean up while keeping tests green | ~200 |

## Invocation

- `/skill test-driven-development` — Overview only
- `/skill test-driven-development --task red` — Write failing test
- `/skill test-driven-development --task green` — Write minimal implementation
- `/skill test-driven-development --task refactor` — Refactor with tests green

## Operating Protocol

1. **Contextual invocation:** This skill is invoked when user explicitly requests TDD approach, spec has clear testable behavior, or development involves new functions/classes with well-defined contracts. NOT mandatory — use when TDD adds value.
2. **Red-Green-Refactor cycle:** RED: Write a test that fails (defines expected behavior). GREEN: Write minimal code to make test pass (satisfy contract). REFACTOR: Clean up code while keeping tests green.
3. **Exit conditions:** TDD cycle is COMPLETE when test was written before implementation, implementation passes the test, code is refactored and clean, and all existing tests still pass.

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

## Test Standards

- Use `pytest` for all tests
- Run from root: `uv run pytest test/test_filename.py`
- Use `PgServerManager` for database tests (never SQLite)
- Use `./tmp/` for test artifacts

## Integration with Existing Workflow

### Dispatch Order

```
executing-plans (step with TDD approach) → TDD red → TDD green → TDD refactor → verification-before-completion
```

TDD is invoked contextually — not mandatory for all development.

## Cross-References

- Related skills: `systematic-debugging` (testing bug fixes), `verification-before-completion` (evidence)
- Related guidelines: `070-environment.md` (testing standards), `080-code-standards.md` (code quality)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `github.platform` environment variable