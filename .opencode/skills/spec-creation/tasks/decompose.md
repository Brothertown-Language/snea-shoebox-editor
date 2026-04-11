# Task: decompose

## Purpose

Break the problem into discrete units with defined interfaces, inputs, outputs, invariants, and failure modes. Define APIs, data contracts, and schemas before implementation.

## Entry Criteria

- Requirements extraction completed (or explicitly skipped for trivial specs)

## Exit Criteria

- Problem decomposed into discrete units
- Interfaces defined for each unit (APIs, data contracts, schemas)
- Invariants and failure modes documented

## Procedure

### Step 1: Identify Discrete Units

Break the problem into logical units where each unit:
- Has a single clear purpose
- Has well-defined inputs and outputs
- Can be understood independently
- Can be tested independently

### Step 2: Define Interfaces First (Interface-First Thinking)

For each unit, define:
- **API contracts:** Function signatures, endpoints, request/response schemas
- **Data contracts:** Data types, validation rules, serialization format
- **Boundary conditions:** What crosses the unit boundary, in what format

**Why first:** Interface definitions constrain implementation correctly. Code written against undefined interfaces tends to couple to implementation details.

### Step 3: Document Invariants

For each unit:
- What must always be true (preconditions, postconditions)
- What must never happen (safety invariants)
- What the unit guarantees to callers

### Step 4: Identify Failure Modes

For each unit:
- How can it fail? (input errors, dependency failures, resource exhaustion)
- What happens when it fails? (error propagation, fallback behavior, recovery)
- How is failure detected? (logging, metrics, alerts)

## Output Format

```
## Problem Decomposition

### Unit: <name>
- Purpose: <one-sentence description>
- Interface: <API contract, data schema>
- Inputs: <what comes in>
- Outputs: <what goes out>
- Invariants: <what must always be true>
- Failure modes: <how it fails, what happens>
```

## Context Required

- Preceded by: `requirements`
- Feeds into: `traceability`, `risk`, `write`