# Task: decompose

## Purpose

Split a DECOMPOSE-assessed task into sub-tasks suitable for sub-agent dispatch. Each sub-task receives a scoped description, boundaries, and dispatch context. Preserve spec boundaries — never split within a single spec requirement.

## Entry Criteria

- Assessment outcome is DECOMPOSE
- The spec and its requirements are understood

## Exit Criteria

- Sub-tasks are defined with descriptions, scope, and boundaries
- Sub-tasks are ordered by dependency
- Each sub-task is small enough for a single sub-agent context

## Procedure

### Step 1: Identify Decomposition Axes

Split along natural boundaries:
- **Spec requirement boundaries** — each requirement (or group of tightly coupled requirements) becomes one sub-task
- **Module boundaries** — changes to distinct modules or layers
- **File boundaries** — groups of closely related files

**Never split within a single spec requirement.** A requirement that touches 3 files is ONE sub-task, not three.

### Step 2: Define Each Sub-task

For each sub-task:

```yaml
sub_task:
  id: "<sequential ID, e.g., D1, D2>"
  description: "<what to implement, with enough detail for a sub-agent>"
  scope: "<files, modules, functions affected>"
  boundaries: "<what is OUT of scope — explicit to prevent scope creep>"
  spec_references: ["<spec section IDs this sub-task covers>"]
  depends_on: ["<sub-task IDs this depends on, or empty>"]
  depth: <current depth + 1>
  prior_context: "<intent from sub-agents that must complete before this one>"
```

### Step 3: Order by Dependency

- Sub-tasks with no dependencies run first
- Dependent sub-tasks run after their dependencies complete
- Independent sub-tasks can be dispatched in sequence (never in parallel — one branch per issue, sequential to avoid merge conflicts)

### Step 4: Verify Decomposition Fitness

Check each sub-task:
1. Is it small enough for a sub-agent to hold all needed context?
2. Does it preserve spec boundaries (no split within a single requirement)?
3. Are boundaries explicit (preventing scope creep)?
4. Are dependencies correctly identified?

If any sub-task still seems too large, decompose it further (increment depth).

### Step 5: Record Decomposition

Document the decomposition plan:

```yaml
decomposition:
  parent_task: "<original task description>"
  depth: <current depth>
  sub_tasks:
    - id: D1
      description: "..."
      scope: "..."
      depends_on: []
    - id: D2
      description: "..."
      scope: "..."
      depends_on: [D1]
```

## Edge Cases

### A Single Spec Requirement is Too Large

If one spec requirement is too large for a single sub-agent:
1. Do NOT split the requirement
2. Dispatch it as-is with the OVERFLOW protocol
3. The sub-agent may return OVERFLOW; handle per `overflow-signal` task

### Circular Dependencies

If decomposition reveals circular dependencies between sub-tasks:
1. Merge the circular sub-tasks into one
2. Re-assess if the merged sub-task is still within context capacity
3. If not, dispatch and handle OVERFLOW

### Depth Limit Reached

If decomposition depth exceeds `DIVIDE_AND_CONQUER_MAX_DEPTH` (default 3):
1. HALT
2. Report the situation to the user
3. Suggest the work may need to be broken into separate issues/phases
## Live Verification: Decomposition Claims (MANDATORY)

**Verify decomposition claims against actual codebase state per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Tasks are independent" | Verify no code dependency between tasks | `srclight_get_dependents(symbol_name="target")` | CONFLICTING |
| "File scope per task verified" | Verify file references exist | `glob(pattern="**/filepath")` | MISSING-TRACEABILITY |
| "Dependency order correct" | Verify must-precede claims | `srclight_get_callers(symbol_name="target")` | VERIFICATION-GAP |

**Evidence artifact:** Tool call results confirming decomposition accuracy.
## Enforcement References
-  Completion checkpoint protocol: see `enforcement/completion-checkpoint.md`
-  Result validation: see `enforcement/result-validation.md`
-  Overflow signal: see `enforcement/overflow-signal.md`
