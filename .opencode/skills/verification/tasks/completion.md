# Task: completion

## Purpose

Ensure the verification workflow documents its results and produces a status report regardless of outcome. This task is the completion guarantee for verification — it runs whenever the workflow halts.

## Entry Criteria

The verification workflow is halting. This includes: all claims verified successfully, partial verification with some unverified claims, or an error that prevented verification.

## Exit Criteria

Verification results are documented, a status report is produced, and no orphaned state remains.

## Procedure

### Step 1: Document Results

Compile a status report summarizing all verification operations:

```
Verification Status: <complete | partial | escalated>
Claims Verified (PASS): <count>
Claims Failed (FAIL): <count>
Claims Unverified: <count>

Failed claims:
- <claim_id>: <reason>

Unverified claims:
- <claim_id>: <modality> — <reason>
```

### Step 2: Clean Up

- Clear any temporary verification state
- Ensure multimodal-dispatch cache is left in valid state
- Document any gaps in modality coverage

### Step 3: Report

Produce the status report in chat output. The completion task is idempotent — invoking it multiple times produces the same result.

Follow the completion-core reference for:
- Push branch (if applicable, idempotent)
- Generate URL (if applicable)
- Report executive summary in chat

### Step 4: FAIL Escalation

If any claims have FAIL status, they MUST be escalated to the developer. FAIL claims are never silently downgraded or omitted from the report. The escalation format is:

```
ESCALATION: <claim_id> — <evidence that contradicts the claim>
```

## Context Required

- Invoked by: end of verification workflow
- Related tasks: `verify`, `verify-single`

Co-authored with AI: <AgentName> (<ModelId>)