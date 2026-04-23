# Incremental Build Discipline

## Mandate

All implementation MUST follow the incremental build discipline: top-down decomposition → bottom-up design → per-item TDD cycle.

This discipline applies to ALL scopes — GREENFIELD, NEW_FEATURE, FIX, and ENHANCEMENT — without exception. The difference between scopes is what the top-down analysis starts from, not whether the discipline applies.

**AUTHORITY:** This guideline is the single source of truth for the incremental build discipline. Cross-references from `000-critical-rules.md`, `010-approval-gate.md`, and skill files point here.

## Scope Classification

| Scope | Top-Down Starts From | Input Artifact |
| -- | -- | -- |
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
| -- | -- | -- |
| **RED** | Add enforcement test scenario that verifies the change (expect failure — change doesn't exist yet). For each spec SC that applies to this item, the enforcement test assertion for that SC MUST be in RED state (exists and fails) before the item's implementation commit. | Test scenario committed alongside the `.md` change it tests; SC-specific test assertions with `# SC-N:` comments |
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

## Enforcement Mechanism

The RED phase is enforced at multiple checkpoints to prevent GREEN-without-RED violations. Each enforcement point requires tool-call evidence that the test was verified to fail before implementation proceeds.

**Checkpoint 0 — Spec Creation RED Gate:** Before a spec is approved, enforcement test assertions for each spec success criterion MUST exist and be in RED state (failing) in `test-enforcement.sh`. This is enforced by `spec-creation/tasks/write.md` Step 0.5 and `issue-review/tasks/analyze-and-spec.md` Step 4.1. The approval gate verifies this at Step 4.6 — enforcement test assertions for spec SCs must have been written before the spec was approved, not just before implementation.

**Checkpoint 1 — executing-plans/tasks/start.md Step 5.5:** Before dispatching to divide-and-conquer, the agent MUST verify that RED test artifacts exist for each item. If no RED test artifact exists, the agent MUST HALT and require the RED phase to be completed.

**Checkpoint 2 — writing-plans/tasks/create.md Step 2:** Plans MUST include a RED verification step that produces tool-call evidence of test failure. The plan template requires a step between writing the test and implementing the change where the agent runs the test and captures the failure output as evidence.

**Checkpoint 3 — Git log order verification:** The test file commit must precede the implementation commit for each task. `git log` order is checked during review-prep to confirm that the RED phase commit came before the GREEN phase commit.

**Checkpoint 4 — Approval gate Step 4.6:** The approval gate verifies that each enforcement test assertion was written before the implementation commit for its corresponding item. This prevents retroactive test creation that was never in RED state.

**HALT requirement:** If no RED test artifact exists at any checkpoint, the agent MUST HALT and require the RED phase. Proceeding without RED evidence is a critical violation per `000-critical-rules.md` → "Monolithic Implementation" section.

## SC-Specific TDD Mandate

The per-item TDD cycle's RED phase MUST include SC-specific test assertions, not just general enforcement assertions. For each spec SC that applies to a given item, the enforcement test assertion for that SC must be in RED state (exists and fails) before the item's implementation commit.

SC test assertions MUST be in RED state (exist and fail) before the item's implementation commit. If an SC test assertion is written after implementation (GREEN-without-RED), the test never verified that the SC was actually unmet before implementation — it only verified that the implementation makes the test pass, which is circular.

## Cross-References

- `000-critical-rules.md` → "Monolithic Implementation" critical violation section (authoritative enforcement)
- `000-critical-rules.md` → "Enforcement Mechanism" section (RED phase verification requirements)
- `010-approval-gate.md` → Step 4.5 item decomposition verification (gate enforcement)
- `brainstorming/SKILL.md` → `top-down-analysis` task (decomposition generation)
- `writing-plans/SKILL.md` → Per-item bottom-up design sections (design generation)
- `executing-plans/SKILL.md` → Per-item TDD cycle reference (execution enforcement)
- `divide-and-conquer/SKILL.md` → TDD phase in dispatch context (dispatch enforcement)

**Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)**
