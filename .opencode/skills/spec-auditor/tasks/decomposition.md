# Task: decomposition

## Purpose

Detect when a spec should be split into multiple independent specs with dependency notes. A spec that tries to do too much in one change is harder to review, harder to implement correctly, and harder to verify.

This subtask applies the decomposition heuristic: a spec is flagged for decomposition when it meets **2 or more** of 5 criteria. Findings are classified as **conditional** (not auto-fix), meaning the auditor identifies concerns and suggests decomposition but does not auto-apply any split.

## Heuristic Criteria

A spec meets the decomposition threshold when **2 or more** of the following criteria are satisfied:

| # | Criterion | Threshold | Signal |
|---|-----------|-----------|--------|
| 1 | Independent concerns | >1 concern that can be removed without breaking the others | "X and Y and Z" phrasing rather than "X with Y consequences" |
| 2 | Phases | >3 phases | Each phase is a candidate for its own spec |
| 3 | Non-overlapping file sets | >2 disjoint file sets across phases | Phase 1 touches files A-D, Phase 2 touches E-H, Phase 3 touches I-L |
| 4 | File count | >15 files affected | Spec is trying to do too much in one change |
| 5 | Word count | >2000 words in body | Hard to review for fidelity during plan auditing |

**Scoring:** Count how many criteria the spec satisfies. If count >= 2, flag for decomposition.

**Negative case:** Specs with 1 concern, <=3 phases, <=15 files, and <=2000 words should NOT be flagged.

## Procedure

1. **Count independent concerns:**
   - Read the document via the appropriate source (GitHub MCP for issues, `read` for files, `webfetch` for URLs)
   - Identify distinct concerns: a concern is a coherent area of change that can be understood, implemented, and verified independently
   - "X and Y and Z" phrasing (coordinating conjunctions linking distinct topics) signals independent concerns
   - "X with Y consequences" phrasing (subordinate relationship) signals a single concern with ramifications
   - If >1 independent concern found, Criterion 1 is met

2. **Count phases:**
   - Count distinct phases or step groups in the document
   - If >3 phases, Criterion 2 is met

3. **Analyze file sets for overlap:**
   - Extract all file references from the document body
   - Group files by the phase that touches them
   - Compute overlap: count how many file groups share zero files with each other
   - If >2 disjoint file sets (groups with zero overlap), Criterion 3 is met

4. **Count affected files:**
   - Count unique file paths mentioned in the document
   - If >15 unique files, Criterion 4 is met

5. **Count words:**
   - Count words in the document body (excluding metadata headers like STATUS, CREATED, etc.)
   - If >2000 words, Criterion 5 is met

6. **Evaluate decomposition threshold:**
   - If criteria met >= 2, generate a DECOMPOSITION-CANDIDATE finding
   - If criteria met < 2, no finding — spec is appropriately scoped

## Concern Analysis

When the decomposition threshold is met, analyze the spec's concerns:

1. **List identified concerns** — name each distinct concern and its associated phases
2. **Map file sets per concern** — which files does each concern touch
3. **Identify dependencies between concerns** — which concern depends on which, and what is the nature of the dependency (data dependency, API dependency, deployment dependency)
4. **Suggest decomposition** — propose how to split the spec into N independent specs, with dependency notes explaining the sequencing

The decomposition suggestion should be concrete enough that a developer can act on it, but does not prescribe a specific split — the developer decides whether to accept the suggestion.

## Report Format

```
Subtask: decomposition
Finding: DECOMPOSITION-CANDIDATE - [N] of 5 criteria met: [list criteria met]. Consider splitting into [M] specs with dependency notes.
Location: [document scope — "entire document" or specific sections]
Context: [why decomposition matters for this spec — e.g., "5 independent concerns across 8 phases touching 23 files; review fidelity risk is high"]
Classification: conditional
Fix Action: conditional — decomposition suggested: [concern 1], [concern 2], ... with dependencies: [dependency notes]. Developer decision required.
Severity: [HIGH|MEDIUM|LOW]
Criteria Met:
  - [Criterion name]: [value] (threshold: [threshold value])
  - ...
Identified Concerns:
  - [Concern 1]: [phases], [file set]
  - [Concern 2]: [phases], [file set]
  - ...
Suggested Decomposition:
  - Spec A: [concern 1] — [dependency: none / depends on Spec B]
  - Spec B: [concern 2] — [dependency: depends on Spec A for ...]
  - ...
```

**For specs that do NOT meet the threshold, no finding is generated.** Do not report "0/5 criteria met — no decomposition needed."

## Auto-Fix Classification

| Problem Class | Classification | Fix Action |
|---------------|---------------|------------|
| DECOMPOSITION-CANDIDATE | conditional | Suggest decomposition with concern identification and dependency notes; developer decides whether to split |

**This finding is NEVER auto-fixed.** Splitting a spec requires understanding domain context, project priorities, and team preferences that the auditor cannot judge. The auditor identifies the signal and suggests a decomposition; the developer decides.

## When to Run

- Multi-phase specs (conditional subtask for Spec type)
- Complex feature specs with many files
- Any spec where the auditor detects "X and Y and Z" phrasing in the problem statement

## When to Skip

- Single-task specs (no phases to split)
- Simple bug fixes
- Specs that clearly address one concern with minimal file impact

## Cross-Reference

- `concerns` subtask — Analyzes phase structure and concern separation; decomposition identifies when the spec itself should be split
- `content-quality` subtask — SCOPE-CREEP-RISK finding is related but distinct: scope creep identifies out-of-scope changes, decomposition identifies appropriate scope that is too large for a single spec
- `010-approval-gate.md` — Multi-task plan authorization; decomposition suggests creating multiple specs that would each follow the spec → plan → implementation flow

Co-authored with AI: <AgentName> (<ModelId>)