# Task: validate

## Purpose

Check an existing plan for placeholders and completeness.

## Validation Checks

1. **Placeholder detection** — Zero TBD/TODO tolerance
2. **Completeness** — Plan addresses the stated problem
3. **Actionability** — Steps are concrete, not abstract goals
4. **Testability** — Success criteria are measurable
5. **TDD structure** — Each task has failing test → implement → passing test steps
6. **File structure** — All files are listed with responsibilities
7. **Self-review evidence** — Agent has performed spec coverage, placeholder, and type consistency checks

## No-Placeholders Rule

Every step must contain actual content. These are **plan failures**:

| Pattern | Why Prohibited |
|---------|----------------|
| `TBD` | Incomplete plan |
| `TODO` | Incomplete plan |
| `[to be determined]` | Incomplete plan |
| `[needs investigation]` | Investigation should be in spec |
| `[placeholder]` | Incomplete plan |
| `[requires research]` | Research should be in spec |
| `implement later` | Plan not actionable |
| `fill in details` | Details must be specified |
| `Add appropriate error handling` | Must specify actual code |
| `Add validation` / `Handle edge cases` | Must specify actual code |
| `Write tests for the above` | Must include actual test code |
| `Similar to Task N` | Must repeat the code — engineer may read tasks out of order |
| Steps describing what to do without showing how | Code blocks required for code steps |
| References to types/functions not defined in any task | All referenced symbols must be defined |

## Specs vs Plans

| Artifact | Placeholders Allowed? | Examples |
|----------|----------------------|----------|
| Spec (GitHub Issue) | YES, during iterative development | TBD, TODO, [needs investigation], [placeholder] |
| Plan (for implementation) | NO — zero tolerance | None allowed before implementation begins |

## Validation Logic

```python
INVALID_PATTERNS = [
    "TBD", "TODO", "tbd", "todo",
    "[to be determined]", "[needs investigation]",
    "[placeholder]", "[requires research]",
    "implement later", "fill in details",
]

def validate_plan(plan_content: str) -> bool:
    for pattern in INVALID_PATTERNS:
        if pattern in plan_content:
            return False
    return True
```

Does NOT enforce a specific section order. A plan without "Risks" is valid if risks are addressed elsewhere or are not relevant.