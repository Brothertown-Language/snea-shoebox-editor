# Task: refactor

## Purpose

Clean up implementation code while keeping all tests passing. Refactoring changes structure, not behavior.

## Operating Protocol

1. Invoked by: `/skill test-driven-development --task refactor`
2. When to use: After `--task green` has confirmed passing tests
3. Exit criteria: Code refactored, all tests still pass, no behavior changes

## Principles

1. **Tests stay green:** All tests pass during refactoring
2. **Small steps:** One refactoring at a time
3. **Run tests after each step:** Ensure nothing breaks
4. **No behavior changes:** Refactoring changes structure, not behavior

## Workflow

1. Identify code smells (duplication, long methods, unclear names)
2. Make one small refactoring
3. Run tests
4. If tests pass → commit refactoring
5. If tests fail → revert and try different approach

## Verification

```bash
# All tests must pass after refactoring
uv run pytest test/ -v
```

## When to Use TDD

| Situation | Use TDD? | Reason |
|-----------|----------|--------|
| New function/class with clear contract | ✅ Yes | Tests define expected behavior |
| Bug fix with clear reproduction | ✅ Yes | Test reproduces bug, fix resolves it |
| Complex algorithm | ✅ Yes | Tests verify edge cases |
| Exploration/prototyping | ❌ No | Behavior not yet defined |
| UI layout changes | ❌ No | Hard to test visually |
| Config/data changes | ❌ No | No code logic to test |

## Context Required

- Related skills: `test-driven-development` (parent skill)
- Related tasks: `red`, `green`