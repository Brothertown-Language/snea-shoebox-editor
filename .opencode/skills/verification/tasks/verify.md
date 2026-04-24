# Task: verify

## Purpose

Verify multiple claims against evidence using modality-aware dispatch. This task takes a list of claims and a content payload, dispatches each claim to the appropriate model via `multimodal-dispatch`, and collects ClaimResult for each claim.

## Entry Criteria

- A list of claims to verify (each claim has an ID, text, and optional modality hint)
- A content payload describing the evidence to verify against
- The `multimodal-dispatch` skill is available for routing

## Exit Criteria

A `VerificationResult` is produced containing a `ClaimResult` for each claim, with PASS/FAIL/UNVERIFIED status and evidence artifacts.

## Procedure

### Step 1: Classify Claims by Modality

For each claim, determine the required modality:

- **Text claim**: Claims about code, configuration, documentation, or text content → modality `text`
- **Vision claim**: Claims about images, screenshots, diagrams, or visual content → modality `vision`
- **Audio claim**: Claims about audio content → modality `audio` (likely UNVERIFIED in this phase)
- **Mixed claim**: Claims involving multiple modalities → route via `dispatch-multi`

The classification uses the content payload: if `image_paths` is non-empty, at least some claims need `vision` modality. If `text` is the only content field, all claims need `text` modality.

### Step 2: Dispatch Each Claim

For each claim, invoke `multimodal-dispatch --task dispatch` with:
- `task-prompt`: "Verify this claim against the provided evidence: <claim_text>"
- `modality`: The resolved modality for this claim
- `content`: The content payload

For multi-modality claims, use `multimodal-dispatch --task dispatch-multi` instead.

### Step 3: Collect ClaimResults

For each dispatch result, construct a `ClaimResult`:

```json
{
  "claim_id": "<id>",
  "status": "<PASS | FAIL | UNVERIFIED>",
  "evidence": "<summary of verification>",
  "evidence_artifacts": ["<tool_call_ref>", ...],
  "model_used": "<model_tag>",
  "modality": "<resolved_modality>"
}
```

**Status determination from `DispatchResult.status`:**

| DispatchResult.status | ClaimResult.status |
|----------------------|-------------------|
| `completed` | `PASS` or `FAIL` based on evidence |
| `partial` | `PASS` for verified parts, `UNVERIFIED` for unavailable parts |
| `unverified` | `UNVERIFIED` — no model available for modality |
| `failed` | `FAIL` — verification failed due to error |

The key distinction: `completed` dispatch means the model processed the claim successfully, but the claim itself may still fail verification. The dispatch `status` refers to whether the model operation completed, not whether the claim passes verification. A claim that the model processed but found to be false gets `FAIL`, not `PASS`.

**FAIL is never downgraded to PASS (per 065-verification-honesty.md).** If the verifying model determines a claim is false, the `ClaimResult.status` is FAIL. No amount of "close enough" or "functionally equivalent" reasoning can change FAIL to PASS.

### Step 4: Assemble VerificationResult

Combine all `ClaimResult` entries into a `VerificationResult`:

```json
{
  "total_claims": <count>,
  "passed": <count>,
  "failed": <count>,
  "unverified": <count>,
  "claims": [<ClaimResult>, ...]
}
```

### Step 5: Return Result

Return the `VerificationResult`. The calling skill or orchestrator uses this to report verification status.

## UNVERIFIED Handling

When a claim requires a modality that has no available model (e.g., audio/ASR, which is deferred per REQ-9), the ClaimResult is:

```json
{
  "claim_id": "C3",
  "status": "UNVERIFIED",
  "evidence": "(unverified: audio — ASR deferred to PEP 723 phase)",
  "evidence_artifacts": [],
  "model_used": null,
  "modality": "audio"
}
```

UNVERIFIED claims do not block execution. They are reported as gaps for the developer to address.

## Context Required

- Depends on: `multimodal-dispatch` (model selection and dispatch)
- Invoked by: `verification-enforcement`, `spec-auditor`, and other skills needing modality-aware verification
- Related tasks: `verify-single`, `completion`

Co-authored with AI: <AgentName> (<ModelId>)