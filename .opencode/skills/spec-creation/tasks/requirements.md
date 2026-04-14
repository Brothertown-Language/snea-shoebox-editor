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

Document constraints and assumptions in any format that clearly communicates:
- **Technical constraints** — platform, language, framework restrictions and their source (investigation findings or user input)
- **Resource constraints** — time, personnel, infrastructure limits and their source
- **Assumptions** — things taken as true without verification, with how to confirm each
- **Dependencies** — external systems, libraries, APIs required and what happens if unavailable
- **Non-requirements** — what is explicitly out of scope and why

### Step 4: Document Non-Requirements

Explicitly list what is NOT in scope:
- Features mentioned but deferred
- Capabilities implied but excluded
- Edge cases that are out of scope

## Content Coverage

Does the requirements analysis cover:
- Explicit requirements from the user?
- Implicit requirements inferred from context?
- Constraints (technical, resource, compatibility)?
- Assumptions (and how to verify them)?
- Non-requirements (what's explicitly out of scope)?

**Any format that covers these concerns is acceptable** — tables, prose lists, bullet points, or structured sections. The agent chooses the format that best communicates the requirements for this specific spec.

## Context Required

- Preceded by: `brainstorming` exploration
- Feeds into: `decompose`, `traceability`, `write`