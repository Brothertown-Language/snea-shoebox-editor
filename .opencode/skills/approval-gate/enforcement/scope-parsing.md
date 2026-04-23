# Scope Parsing Module

## Verb-Prefix Parsing Table

Authorization phrases carry implicit scope — the pipeline stage the developer expects work to reach. Parse authorization text for scope qualifiers:

| Phrase Pattern | Scope | HALT After | Gap-Fill | PR Strategy |
|----------------|-------|------------|----------|-------------|
| `"approved #N"` (no qualifier) | standard | review-prep | None | individual |
| `"approved #N for spec"` or `"#N approved for spec"` | for_spec | spec_created | None | none |
| `"approved #N for plan"` or `"#N approved for plan"` | for_plan | plan_created | auto-create spec | none |
| `"approved #N for implementation"` or `"#N approved for implementation"` | for_implementation | implementation_complete | auto-create spec+plan, auto-approve | individual |
| `"approved #N for code review"` or `"#N approved for code review"` | for_code_review | code_review_ready | auto-create spec+plan, auto-approve | individual |
| `"approved #N to PR"` or `"#N approved to PR"` | for_pr | pr_created | auto-create spec+plan, auto-approve, auto-PR | stacked |
| `"approved #N pr only"` or `"#N approved for pr only"` | pr_only | pr_created | None | stacked |
| `"approved #N for review"` or `"#N approved for review only"` | review_only | code_review_ready | None | individual |

## Scope Derivation Rules

1. **No qualifier = standard**: `"approved #1200"` → `standard` scope, review-prep halt, no gap-fill
2. **Qualifier present = parse**: Match phrase against table above; ambiguous phrases default to standard
3. **Multiple issues**: `"approved #1200 #1201 #1197 for implementation"` → `for_implementation` scope applies to all listed issues
4. **Phase qualifier**: `"approved: Phase 1 only"` → single-phase authorization for the named phase only, then HALT

## PR Strategy Map

| Scope | PR Strategy |
|-------|-------------|
| standard | individual (one PR per issue) |
| for_spec | none |
| for_plan | none |
| for_implementation | individual |
| for_code_review | individual |
| for_pr | stacked |
| pr_only | stacked |
| review_only | individual |