# Task: structure

## Purpose

Check that a document has clear progress tracking, creation context, and consistent structure. For specs, this means verifying that content is findable, trackable, and organized. For non-spec document types, structure checks are adapted to be less strict.

**Note for non-spec document types:** STATUS/phase/step markers and approval tracking are relaxed differently per type:
- **Plan:** Has phases but no approval tracking — check phases, skip approval markers
- **Process Flow:** Has sequential steps but no STATUS headers — check step numbering and I/O contracts, skip STATUS/phase checks
- **Runbook/SOP:** Has sequential steps and possibly a prerequisites section — check step numbering and section presence, skip STATUS/phase checks
- **Checklist:** Has checkbox items — check checkbox format, skip STATUS/phase/step checks
- **Reference Doc:** No structural format required — skip this subtask entirely (baseline uses fresh-start only)

## Checks

This subtask verifies content quality and completeness, not structural conformity to a specific template.

| Check | Problem Class | Description | Classification |
|-------|---------------|-------------|----------------|
| Trackability | CONTENT-COVERAGE | Is there a way to track progress? (Any format: STATUS phase.step, simple status note, inline progress markers) | flag-for-review |
| Creation context | CONTENT-COVERAGE | Is there creation context (date, author, or STATUS marker)? | flag-for-review |
| Consistent structure | CONTENT-COVERAGE | Does the spec use consistent structure throughout? (Sections, phases, or steps are organized logically, not randomly scattered) | flag-for-review |
| Concern-named phases | MISSING-ELEMENT | Do phase names describe specific concerns, not generic activities? ("Database Schema Setup", not "Implementation") | flag-for-review |

**Advisory guidelines (not mandatory):**
- STATUS with prose-driven format (e.g., `STATUS: in progress — Authorization Gate, Step 1`) is recommended for multi-phase specs — it references concern names rather than numeric phase indices, making progress tracking self-explanatory and resilient to phase renumbering
- STATUS with `phase.step` format (e.g., `STATUS: 1.2`) is backward-compatible but no longer recommended
- CREATED date is recommended but not mandatory
- Phase/step numbering is recommended for multi-phase specs, optional for simple specs
- Status markers (`☐`/`↻`/`☑`/`☒`) are recommended but any clear progress indicator works

## Procedure

1. Read the spec issue via GitHub MCP
2. Check that progress is trackable (any clear method)
3. Check that creation context exists (date, author, or status marker)
4. Check that structure is consistent (not randomly organized)
5. Check that phase names describe specific concerns (if phases exist)

## Report Format

```
Subtask: structure
Finding: [CONTENT-COVERAGE|MISSING-ELEMENT] - [summary]
Location: [section of spec]
Context: [why content quality matters for this spec]
Classification: flag-for-review
Fix Action: flagged for review — [reason]
Severity: [HIGH|MEDIUM|LOW]
```

## Why Flag-for-Review (Not Auto-Fix)

Structure choices are context-dependent:
- A simple bug fix doesn't need `STATUS: 1.2` — `in progress` or `complete` is sufficient
- A spec with phases named "Setup" and "Verification" might be fine for a small change
- The agent has full context about the spec's complexity; the auditor doesn't

All structure findings are reported for agent review. The agent decides whether to apply changes.

Co-authored with AI: <AgentName> (<ModelId>)