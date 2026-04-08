# Task: structure

## Purpose

Check that a spec follows the required structural format for STATUS headers, phase/step numbering, and status markers.

## Checks

| Check | Problem Class | Description |
|-------|---------------|-------------|
| STATUS header | STRUCTURE-VIOLATION | Is `STATUS: phase.step` present? |
| CREATED date | MISSING-ELEMENT | Is `CREATED: YYYY-MM-DD` present? |
| Phase numbering | STRUCTURE-VIOLATION | Are phases numbered 1, 2, 3...? |
| Step numbering | STRUCTURE-VIOLATION | Are steps numbered within each phase? |
| Status markers | STRUCTURE-VIOLATION | Are `☐`/`↻`/`☑`/`☒` used correctly? |
| Phase names | MISSING-ELEMENT | Do phase names describe specific concerns, not generic activities? |

## Procedure

1. Read the spec issue via GitHub MCP
2. Check for STATUS header at the top
3. Check for CREATED date
4. Check that phases are numbered sequentially
5. Check that steps are numbered within each phase
6. Check that status markers are present on each step
7. Verify phase names describe specific concerns (not "Implementation", "Testing", "Build")

## Phase Name Quality

| Pattern | Status | Reason |
|---------|--------|--------|
| Single-word activity | BOILERPLATE-TITLE flag | No concern boundary specified |
| "Testing" alone | BOILERPLATE-TITLE flag | Generic activity |
| "Testing Infrastructure" | ACCEPTABLE | Specific concern |
| "Database Schema Setup" | GOOD | Specific concern |
| "Implementation" | BOILERPLATE-TITLE flag | Generic activity |

**Note:** This subtask flags BOILERPLATE-TITLE as a finding, but does NOT auto-rename phases. The agent decides whether to rename.

## Report Format

```
Subtask: structure
Finding: [STRUCTURE-VIOLATION|MISSING-ELEMENT] - [summary]
Location: [section of spec]
Context: [why structure matters for this spec]
Recommendation: [suggested fix]
Severity: [HIGH|MEDIUM|LOW]
```

Co-authored with AI: OpenCode (ollama-cloud/glm-5)