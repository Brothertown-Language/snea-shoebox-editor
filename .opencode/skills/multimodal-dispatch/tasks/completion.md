# Task: completion

## Purpose

Ensure the multimodal-dispatch workflow documents its results and produces a status report regardless of outcome. This task is the completion guarantee for multimodal-dispatch — it runs whenever the workflow halts.

## Entry Criteria

The multimodal-dispatch workflow is halting. This includes: successful dispatch and result collection, partial results where some modalities were unavailable, or an error that prevented dispatch.

## Exit Criteria

Dispatch results are documented, a status report is produced, and no orphaned state remains.

## Procedure

### Step 1: Document Results

Compile a status report summarizing all dispatch operations:

```
Multimodal Dispatch Status: <completed | partial | unverified | failed>
Models Used: <list of model names>
Modalities Processed: <list of modalities with status>
Unverified Modalities: <list of modalities that had no model>
```

### Step 2: Clean Up

- Clear any temporary dispatch state
- Ensure the capability snapshot cache is left in a valid state
- If any dispatch operations produced partial results, document what was completed and what was not

### Step 3: Report

Produce the status report in chat output. The completion task is idempotent — invoking it multiple times produces the same result.

Follow the completion-core reference for:
- Push branch (if applicable, idempotent)
- Generate URL (if applicable)
- Report executive summary in chat

## Context Required

- Invoked by: end of multimodal-dispatch workflow
- Related tasks: `probe`, `resolve`, `dispatch`, `dispatch-multi`

Co-authored with AI: <AgentName> (<ModelId>)