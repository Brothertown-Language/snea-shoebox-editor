# Task: requirements

## Purpose

Extract explicit, implicit, constraint, and non-requirements from investigation results. Build a constraints & assumptions ledger.

## Entry Criteria

- Brainstorming exploration completed
- Investigation results available

## Exit Criteria

- All requirement types identified and categorized
- Constraints & assumptions documented
- Non-requirements explicitly listed (what is NOT in scope)

## Procedure

### Step 1: Extract Explicit Requirements

From investigation results, extract all directly stated requirements:
- What the user explicitly asked for
- What the spec or issue description states
- What success criteria are defined

### Step 2: Identify Implicit Requirements

Requirements implied but not stated:
- Performance expectations (response time, throughput)
- Security requirements (auth, encryption, access control)
- Compatibility requirements (browsers, platforms, versions)
- Usability requirements (accessibility, error messages)

### Step 3: Build Constraints & Assumptions Ledger

| Category | Items | Source |
|----------|-------|--------|
| Technical constraints | Platform, language, framework restrictions | Investigation |
| Resource constraints | Time, personnel, infrastructure limits | User input |
| Assumptions | Things taken as true without verification | Inference |
| Dependencies | External systems, libraries, APIs required | Investigation |
| Non-requirements | What is explicitly NOT in scope | User input + scoping |

### Step 4: Document Non-Requirements

Explicitly list what is NOT in scope:
- Features mentioned but deferred
- Capabilities implied but excluded
- Edge cases that are out of scope

## Output Format

```
## Requirements Extraction

### Explicit Requirements
1. [R1] <requirement>
2. [R2] <requirement>

### Implicit Requirements
1. [IR1] <requirement> (inferred from: <source>)

### Constraints
- <constraint> (source: <investigation or user>)

### Assumptions
- <assumption> (verification: <how to confirm>)

### Non-Requirements (Out of Scope)
- <exclusion> (reason: <why>)
```

## Context Required

- Preceded by: `brainstorming` exploration
- Feeds into: `decompose`, `traceability`, `write`