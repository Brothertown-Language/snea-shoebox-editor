# Task: validate

## Purpose

Check an existing plan for placeholders and completeness.

## Validation Checks

01. **Placeholder detection** — Zero TBD/TODO tolerance
02. **Completeness** — Plan addresses the stated problem
03. **Actionability** — Steps are concrete, not abstract goals
04. **Testability** — Success criteria include executable verification commands with exact expected values (not just "measurable" — each SC must specify a command that produces a deterministic pass/fail result)
05. **TDD structure** — Each task has failing test → implement → passing test steps
06. **File structure** — All files are listed with responsibilities
07. **Self-review evidence** — Agent has performed spec coverage, placeholder, and type consistency checks
08. **Spec reference** — Plan body contains a spec reference (search for `Spec: #N` pattern)
09. **Sub-issue parent** — If plan has sub-issues, they link to the plan (not the spec)
10. **Plan label** — Plan issue has `plan` label

## No-Placeholders Rule

Every step must contain actual content. These are **plan failures**:

| Pattern | Why Prohibited |
| -- | -- |
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
| -- | -- | -- |
| Spec (GitHub Issue) | YES, during iterative development | TBD, TODO, \[needs investigation\], \[placeholder\] |
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

## Live Verification: Validation Evidence (MANDATORY)

**Each validation check MUST be verified via tool call, not just asserted. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
| -- | -- | -- | -- |
| "No placeholders present" | Search for placeholder patterns in plan body | \`grep(pattern="TBD | TODO |
| "Spec reference exists in plan" | Search for `Spec: #N` pattern | `grep(pattern="Spec: #")` on plan body | MISSING-ELEMENT |
| "Sub-issues link to plan (not spec)" | Verify sub-issue parent | `github_issue_read(method="get_sub_issues", issue_number=plan_number)` | STRUCTURE-VIOLATION |
| "Plan has `plan` label" | Verify label on plan issue | `github_issue_read(method="get", issue_number=plan_number)` → check labels | MISSING-ELEMENT |
| "Steps are actionable" | Verify each step has concrete action | Manual parse — flag abstract goals | VERIFICATION-GAP |

**Evidence artifact:** Tool call results for automated checks; manual review log for actionable-step verification.

### Finding Classification

| Finding | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Placeholders found | VERIFICATION-GAP | conditional | Remove placeholders or mark plan invalid |
| Missing spec reference | MISSING-ELEMENT | auto-fix | Add spec reference to plan body |
| Sub-issues under wrong parent | STRUCTURE-VIOLATION | auto-fix | Re-link under plan |
| Missing `plan` label | MISSING-ELEMENT | auto-fix | Add label immediately |
| Abstract goals found | VERIFICATION-GAP | flag-for-review | Flag for plan author to rewrite |
