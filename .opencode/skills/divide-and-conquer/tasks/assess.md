# Task: assess

## Purpose

Pre-flight context-fit assessment. Determine workload sizing for sub-agent dispatch — how many sub-agents and how much context each needs.

**All implementation goes through `assemble-work`.** There is no IMPLEMENT_DIRECTLY path. Assessment informs sizing (single sub-agent vs multiple), not whether to dispatch.

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
| Files affected | Localized to one area | Cross-cutting, touches multiple areas |
| Spec requirements | Simple, single concern | Multiple concerns with dependencies |
| Change complexity | Obvious, pattern-following | Novel, requires design reasoning |
| Context load | All needed context fits comfortably | Agent feels "dense" or risks losing track |
| Dependencies | None or shallow | Deep call chains, type hierarchies |

**Both paths go through `assemble-work`.** Single sub-agent = work-of-1. Multiple sub-agents = work set of N.

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

**There is no IMPLEMENT_DIRECTLY path.** All implementation goes through sub-agent dispatch in `assemble-work`. The assessment only determines sizing:

- `single_sub_agent` → assemble-work dispatches one sub-agent
- `multi_sub_agent` → assemble-work dispatches multiple sub-agents

Even trivial changes (typo fixes, one-line configs) are dispatched through assemble-work as work-of-1. This eliminates forked code paths and ensures consistent execution flow.

## Edge Cases

### Assessment Says Single but Work Grows

If during implementation the scope expands beyond what was assessed:
1. Sub-agent signals OVERFLOW per the overflow-signal contract
2. Orchestrator decomposes further and dispatches additional sub-agents
3. Continues through assemble-work workflow

### Assessment Says Multiple for Simple Work

A conservative assessment (multi-sub-agent for work that could be done by one) is acceptable. The decomposition overhead is small compared to the risk of overflow. Do not second-gauge a multi-sub-agent decision.

Co-authored with AI: <AgentName> (<ModelId>)

## Live Verification: Assessment Claims (MANDATORY)

**Each assessment claim MUST be verified against actual codebase state. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Context overflow risk" | Verify context size requires decomposition | Check actual token/file count of issues | VERIFICATION-GAP |
| "Single sub-agent sufficient" | Verify file scope is limited to cohesive set | `git diff dev --name-only` → count files | CONFLICTING |
| "Multi-sub-agent needed" | Verify task touches multiple independent areas | `srclight_get_dependents(symbol_name="target", transitive=true)` | VERIFICATION-GAP |

**Evidence artifact:** Tool call results confirming assessment accuracy.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Overflow risk unverified | VERIFICATION-GAP | conditional | Check actual context size |
| Assessment contradicted by file scope | CONFLICTING | conditional | Re-assess with actual file list |## Enforcement References
-  Completion checkpoint protocol: see `enforcement/completion-checkpoint.md`
-  Result validation: see `enforcement/result-validation.md`
-  Overflow signal: see `enforcement/overflow-signal.md`
