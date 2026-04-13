# Task: assess

## Purpose

Pre-flight context-fit assessment. Determine workload sizing for sub-agent dispatch — how many sub-agents and how much context each needs.

**All implementation goes through `assemble-batch`.** There is no IMPLEMENT_DIRECTLY path. Assessment informs sizing (single sub-agent vs multiple), not whether to dispatch.

## Entry Criteria

- A task is about to begin
- The agent has NOT yet started implementation

## Exit Criteria

- Assessment outcome is documented: workload sizing (single sub-agent or multi-sub-agent)
- Assessment reasoning is captured for traceability

## Procedure

### Step 1: Evaluate Context Fitness

The agent holistically evaluates context sizing for sub-agent dispatch. Consider:

- **Scope of work**: How many spec requirements must be satisfied?
- **Number of files**: How many source files need modification or creation?
- **Complexity of changes**: Are the changes localized or cross-cutting? Do they involve deep call chains, type hierarchies, or multi-module coordination?
- **Context dependencies**: Does the work require holding large API surfaces, complex data structures, or extensive cross-references in mind simultaneously?
- **Spec density**: Is the spec concise or does it contain extensive detail, edge cases, and multi-phase requirements?

**No hardcoded thresholds.** A 5-file change may fit in a single sub-agent if all edits are obvious and independent. A 2-file change may need multiple sub-agents if the logic is deeply interleaved.

### Step 2: Determine Workload Sizing

| Signal | Single Sub-Agent | Multiple Sub-Agents |
| -- | -- | -- |
| Files affected | 1-2, localized | 3+, cross-cutting |
| Spec requirements | 1-2, simple | 3+, with dependencies |
| Change complexity | Obvious, pattern-following | Novel, requires design reasoning |
| Context load | All needed context fits comfortably | Agent feels "dense" or risks losing track |
| Dependencies | None or shallow | Deep call chains, type hierarchies |

**Both paths go through `assemble-batch`.** Single sub-agent = batch of one. Multiple sub-agents = batch of N.

### Step 3: Document Assessment

Produce a structured assessment:

```yaml
assessment:
  task: "<task description>"
  sizing: single_sub_agent | multi_sub_agent
  reasoning: "<1-3 sentences explaining the sizing>"
  files_estimated: <N>
  spec_requirements: <N>
  complexity: trivial | moderate | complex
  depth: 0
```

### No Direct Implementation Exception

**There is no IMPLEMENT_DIRECTLY path.** All implementation goes through sub-agent dispatch in `assemble-batch`. The assessment only determines sizing:

- `single_sub_agent` → assemble-batch dispatches one sub-agent
- `multi_sub_agent` → assemble-batch dispatches multiple sub-agents

Even trivial changes (typo fixes, one-line configs) are dispatched through assemble-batch as a batch of one. This eliminates forked code paths and ensures consistent execution flow.

## Edge Cases

### Assessment Says Single but Work Grows

If during implementation the scope expands beyond what was assessed:
1. Sub-agent signals OVERFLOW per the overflow-signal contract
2. Orchestrator decomposes further and dispatches additional sub-agents
3. Continues through assemble-batch workflow

### Assessment Says Multiple for Simple Work

A conservative assessment (multi-sub-agent for work that could be done by one) is acceptable. The decomposition overhead is small compared to the risk of overflow. Do not second-gauge a multi-sub-agent decision.

Co-authored with AI: <AI-Name> (<model-id>)