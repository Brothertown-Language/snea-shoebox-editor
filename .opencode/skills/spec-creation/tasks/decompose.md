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
- **Interface Requirements:** What the unit must accept, return, and guarantee (function names, responsibilities, input/output contracts)
- **Data Boundaries:** What data exists, what constraints it satisfies, what invariants hold (table names, constraint tables, ownership boundaries)
- **Boundary conditions:** What crosses the unit boundary, in what format

**Why first:** Interface definitions constrain implementation correctly. Code written against undefined interfaces tends to couple to implementation details.

**Boundary discipline:**

| ✅ Spec-Level (WHAT) | ❌ Plan-Level (HOW) |
|-----------------------|----------------------|
| "validate_user() accepts user_id, returns bool" | `def validate_user(user_id: int) -> bool: ...` |
| "users table has unique email constraint" | `CREATE TABLE users (email TEXT UNIQUE)` |
| "processing must complete within 2s" | "use batch processing with chunk size 100" |
| "layer must not depend on presentation" | "use dependency injection pattern" |

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

## Content Coverage

Does the decomposition define clear units with:
- A single purpose for each unit?
- Defined interfaces (what goes in, what comes out)?
- Known invariants that must hold?
- Failure modes (how it fails, what happens)?

**Any format that communicates these concerns clearly is acceptable** — structured per-unit sections, tables, prose descriptions, or diagrams. The agent chooses the format that best serves the spec's complexity.

## Context Required

- Preceded by: `requirements`
- Feeds into: `traceability`, `risk`, `write`