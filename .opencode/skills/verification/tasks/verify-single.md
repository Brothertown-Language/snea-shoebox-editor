# Task: verify-single

## Purpose

Verify a single claim against evidence using modality-aware dispatch. This is the single-claim version of the `verify` task, designed for targeted verification of individual claims.

## Entry Criteria

- A single claim to verify (with text and optional modality hint)
- A content payload describing the evidence to verify against
- The `multimodal-dispatch` skill is available for routing

## Exit Criteria

A `ClaimResult` is produced with PASS/FAIL/UNVERIFIED status, evidence, and the model used.

## Procedure

### Step 1: Detect Content Modality

Inspect the content payload to determine the appropriate modality:

| Content Field | Modality |
|---------------|----------|
| `text` only | `text` |
| `image_paths` non-empty | `vision` |
| `audio_paths` non-empty | `audio` (likely UNVERIFIED) |
| Mixed content | Use `dispatch-multi` |

If the caller provided a modality hint, use it as a starting point. The `multimodal-dispatch --task resolve` task validates the hint against content and overrides if contradicted.

### Step 2: Dispatch via multimodal-dispatch

Invoke `multimodal-dispatch --task dispatch` with:
- `task-prompt`: "Verify this claim against the provided evidence: <claim_text>. Return PASS if the evidence supports the claim, FAIL if the evidence contradicts the claim, or UNVERIFIED if you cannot determine the answer."
- `modality`: The detected or hinted modality
- `content`: The content payload

### Step 3: Construct ClaimResult

From the `DispatchResult`, build a `ClaimResult`:

```json
{
  "claim_id": "C1",
  "status": "<PASS | FAIL | UNVERIFIED>",
  "evidence": "<summary>",
  "evidence_artifacts": ["<tool_call_ref>", ...],
  "model_used": "<model_tag>",
  "modality": "<resolved_modality>"
}
```

**Status determination:**

The model's response determines the claim status:
- If the model confirms the claim with evidence → PASS
- If the model contradicts the claim with evidence → FAIL
- If the model cannot determine → UNVERIFIED
- If no model is available for the modality → UNVERIFIED with gap description

**FAIL is never downgraded to PASS.** This invariant is absolute. A claim that fails verification stays FAIL regardless of how "close" it is to passing.

### Step 4: Return ClaimResult

Return the single `ClaimResult`. The calling skill uses this to build its own result.

## Error Handling

- If `multimodal-dispatch` returns `unverified` status → `ClaimResult.status = UNVERIFIED`
- If `multimodal-dispatch` returns `failed` status → `ClaimResult.status = FAIL` with error details in evidence
- If the content payload is empty → `ClaimResult.status = UNVERIFIED` with "no content provided for verification"

## Context Required

- Depends on: `multimodal-dispatch` (model selection and dispatch)
- Invoked by: `verify` task (for individual claims), or directly by skills needing single-claim verification
- Related tasks: `verify`, `completion`

Co-authored with AI: <AgentName> (<ModelId>)