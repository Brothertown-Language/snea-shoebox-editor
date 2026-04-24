# Task: overflow-signal

## Purpose

Defines the structured OVERFLOW response protocol. When a sub-agent determines it cannot fit the assigned work within its context window, it MUST return an OVERFLOW signal. The orchestrator receives this and dispatches further sub-agents for the remaining work.

## Entry Criteria

- A sub-agent has returned `status: OVERFLOW`
- The OVERFLOW signal contains valid `remaining_work` and `suggested_splits`

## Exit Criteria

- Remaining work is further decomposed and dispatched, OR
- Depth limit is reached and user is notified

## Procedure

### Step 1: Validate OVERFLOW Signal

Verify the signal contains:

```yaml
status: OVERFLOW
completed_work:
  description: "<what was accomplished>"
  files_changed: ["<path>"]
  summary: "<result of completed portion>"
remaining_work:
  description: "<what still needs doing>"
  scope: "<files, functions, modules affected>"
  spec_references: ["<spec section IDs>"]
suggested_splits:
  - description: "<sub-task 1>"
    scope: "<files/modules>"
  - description: "<sub-task 2>"
    scope: "<files/modules>"
depth: <current depth>
```

If any required field is missing, HALT and report malformed signal.

### Step 2: Check Depth Limit

```
if depth >= DIVIDE_AND_CONQUER_MAX_DEPTH (default 3):
    HALT
    Report to user: "Max decomposition depth reached. Remaining work needs manual splitting."
    Include: remaining_work, suggested_splits
else:
    Proceed to Step 3
```

### Step 3: Record Completed Work

The completed_work portion is valid — record it for the `merge` task. The sub-agent committed and pushed what it finished.

### Step 4: Decompose Remaining Work

Use the sub-agent's `suggested_splits` as input to the `decompose` task. The orchestrator:
1. Reviews `suggested_splits` for spec boundary preservation
2. Adjusts if splits would break a spec requirement
3. Increments depth: `new_depth = current_depth + 1`
4. Creates sub-tasks from the remaining work

### Step 5: Dispatch Further Sub-agents

Dispatch new sub-agents for each decomposed piece of the remaining work per the `dispatch` task. Pass the incremented depth and the completed_work as `prior_context`.

### Step 6: Merge All Results

After all overflow-resolution sub-agents complete, their results are included in the `merge` task alongside the original completed_work.

## Recursive Delegation

Sub-agents CAN signal OVERFLOW at any depth. The protocol recurses:

```
Orchestrator (depth=0)
  → Sub-agent A (depth=1): returns OVERFLOW
    → Orchestrator decomposes remaining, dispatches:
      → Sub-agent A1 (depth=2): returns DONE
      → Sub-agent A2 (depth=2): returns OVERFLOW
        → Depth check: 2 < 3 → decompose further
          → Sub-agent A2a (depth=3): returns DONE
          → Sub-agent A2b (depth=3): returns OVERFLOW
            → Depth check: 3 >= 3 → HALT, report to user
```

## Depth Tracking

Depth is tracked in the Dispatch Context Contract `depth` field:
- Root orchestrator: depth 0
- First sub-agent: depth 1
- Sub-agent spawned from OVERFLOW at depth 1: depth 2
- And so on up to `DIVIDE_AND_CONQUER_MAX_DEPTH`

## Edge Cases

### Malformed OVERFLOW Signal

If `remaining_work` or `suggested_splits` is missing:
1. HALT
2. Report: "Sub-agent returned malformed OVERFLOW signal"
3. Treat as BLOCKED — the remaining work cannot be automatically decomposed

### Sub-agent Returns OVERFLOW with No Completed Work

Valid scenario — the entire sub-task exceeded capacity. The full sub-task becomes `remaining_work` and is decomposed from scratch.

### Depth Limit Variable

`DIVIDE_AND_CONQUER_MAX_DEPTH` defaults to 3. Override by setting the environment variable. Validate that the value is a positive integer; if not, fall back to default.
## Live Verification: Overflow State Claims (MANDATORY)

**Verify overflow detection claims against actual context state per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Context overflow detected" | Verify actual context size | Check token/file count | VERIFICATION-GAP |
| "Decomposition needed" | Verify task scope exceeds single-agent capacity | `srclight_get_dependents(symbol_name="target", transitive=true)` | VERIFICATION-GAP |

**Evidence artifacts:** See enforcement/work-state-verification.md §Evidence Artifacts

## Enforcement References
- Completion checkpoint protocol: see `enforcement/completion-checkpoint.md`
- Result validation: see `enforcement/result-validation.md`
- Overflow signal: see `enforcement/overflow-signal.md`
