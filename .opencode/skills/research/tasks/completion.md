# Task: completion

## Purpose

Ensure the research workflow documents its results and produces a status report regardless of outcome. This task is the completion guarantee for research — it runs whenever the workflow halts.

## Entry Criteria

The research workflow is halting. This includes: successful discovery with findings, partial results where some modalities were unavailable, inconclusive research, or an error.

## Exit Criteria

Research results are documented, a status report is produced, and no orphaned state remains.

## Procedure

### Step 1: Document Results

Compile a status report summarizing all research operations:

```
Research Status: <completed | partial | inconclusive | failed>
Findings: <summary of key findings>
Modalities Used: <list of modalities that produced results>
Models Used: <list of models invoked>
Unverified Modalities: <list of modalities with no available model>
Gaps: <list of knowledge gaps>
```

### Step 2: Clean Up

- Clear any temporary research state
- Ensure multimodal-dispatch cache is left in valid state
- Document any gaps in modality coverage

### Step 3: Report

Produce the status report in chat output. The completion task is idempotent — invoking it multiple times produces the same result.

Follow the completion-core reference for:
- Push branch (if applicable, idempotent)
- Generate URL (if applicable)
- Report executive summary in chat

## Context Required

- Invoked by: end of research workflow
- Related tasks: `research`, `research-multi`

Co-authored with AI: <AgentName> (<ModelId>)