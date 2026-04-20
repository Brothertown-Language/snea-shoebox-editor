# Incremental Build Discipline

## Mandate

All implementation MUST follow the incremental build discipline: top-down decomposition → bottom-up design → per-item TDD cycle.

This discipline applies to ALL scopes — GREENFIELD, NEW_FEATURE, FIX, and ENHANCEMENT — without exception. The difference between scopes is what the top-down analysis starts from, not whether the discipline applies.

**AUTHORITY:** This guideline is the single source of truth for the incremental build discipline. Cross-references from `000-critical-rules.md`, `010-approval-gate.md`, and skill files point here.

## Scope Classification

| Scope | Top-Down Starts From | Input Artifact |
|-------|---------------------|---------------|
| GREENFIELD | Project spec (no existing code) | New project specification |
| NEW_FEATURE | Existing code + feature request | Feature spec with acceptance criteria |
| FIX | Existing code + bug report | Bug report with root cause analysis |
| ENHANCEMENT | Existing code + change request | Enhancement spec with change scope |

All scopes follow: top-down decomposition → bottom-up design → per-item TDD. The discipline is the same; the starting material differs.

## Top-Down Decomposition Rules

Before implementation begins, the plan MUST include:

1. **Item enumeration** — Every implementation unit listed as a discrete item with a name, scope, and deliverable
2. **Dependency ordering** — Items ordered so that each item's dependencies are satisfied by preceding items
3. **Acceptance criteria per item** — Each item has testable acceptance criteria that can be verified independently
4. **Concern boundaries** — Items that cross architectural concerns are flagged with explicit transition notes

Top-down decomposition is performed during brainstorming (`brainstorming --task explore`) and verified at the approval gate (`approval-gate --task verify-authorization` Step 4.5).

## Bottom-Up Design Rules

Within each item, the plan MUST specify:

1. **Classes/modules** — What code components will be created or modified
2. **Interfaces** — Function signatures, API contracts, data formats
3. **Test contracts** — What the enforcement test or verification will check before implementation

Bottom-up design is performed during plan creation (`writing-plans --task create`) and included in the plan template.

## Per-Item TDD Cycle

Each implementation item MUST follow:

| Phase | Action | Guideline Change |
|-------|--------|-----------------|
| **RED** | Add enforcement test scenario that verifies the change (expect failure — change doesn't exist yet) | Test scenario committed alongside the `.md` change it tests |
| **GREEN** | Make the `.md` file change that makes the test pass | The actual guideline, skill, or AGENTS.md modification |
| **REFACTOR** | Clean up cross-references, verify consistency with other files | Ensure no broken references between files |
| **COMMIT** | Both the test addition and the `.md` change committed together as one working slice | Commit message references the item number |

**Enforcement test runner:**
```
bash .opencode/tests/with-test-home opencode-cli run '<scenario>'
```

**Full suite verification:**
```
bash .opencode/tests/test-enforcement.sh
bash .opencode/tests/with-test-home --clean-all
```

## Anti-Patterns (Critical Violations)

These patterns are critical violations per `000-critical-rules.md`:

- **Monolithic implementation** — Implementing multiple items in a single branch/commit without decomposition
- **Code-first** — Writing code before writing the enforcement test for that change
- **No decomposition** — Skipping item enumeration and dependency ordering
- **Batching items** — Combining items that should be separate into one implementation pass
- **Merging without tests** — Submitting changes where the enforcement test for that change doesn't pass

These anti-patterns are also documented as the "Monolithic Implementation" critical violation in `000-critical-rules.md`.

## Cross-References

- `000-critical-rules.md` → "Monolithic Implementation" critical violation section (authoritative enforcement)
- `010-approval-gate.md` → Step 4.5 item decomposition verification (gate enforcement)
- `brainstorming/SKILL.md` → `top-down-analysis` task (decomposition generation)
- `writing-plans/SKILL.md` → Per-item bottom-up design sections (design generation)
- `executing-plans/SKILL.md` → Per-item TDD cycle reference (execution enforcement)
- `divide-and-conquer/SKILL.md` → TDD phase in dispatch context (dispatch enforcement)

**Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)**