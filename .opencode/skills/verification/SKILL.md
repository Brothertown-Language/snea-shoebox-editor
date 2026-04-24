---
name: verification
description: Use when verifying claims against evidence using appropriate modalities. Produces PASS/FAIL/UNVERIFIED per claim with evidence artifacts. Triggers on: verify claim, claim verification, evidence verification, verify against source, multimodal verification.
type: verification
license: Apache-2.0
compatibility: opencode
---

# Verification

## Overview

Verification skill that invokes `multimodal-dispatch` to verify claims against evidence using appropriate modalities. Each claim receives a PASS/FAIL/UNVERIFIED status with supporting evidence artifacts. The dispatcher routes claims to the best available model based on content modality (text, vision, etc.).

**Core invariant (per 065-verification-honesty.md):** FAIL is NEVER downgraded to PASS based on agent judgment. If a claim verification results in FAIL, it remains FAIL. The only valid state transitions are UNVERIFIED → PASS (after re-verification with evidence) or UNVERIFIED → FAIL (after re-verification with contradictory evidence). FAIL cannot become PASS without new evidence that contradicts the original failure.

**Relationship to verification-enforcement:** This skill handles modality-aware claim verification. The existing `verification-enforcement` skill handles the pre-generation verification gate. When modality-aware verification is needed (e.g., verifying image claims, verifying against non-text sources), `verification-enforcement` can optionally route through this skill via `multimodal-dispatch`.

## Persona

You are a Claim Verifier. Your focus is verifying each claim against evidence using the appropriate model and modality, producing PASS/FAIL/UNVERIFIED results with evidence artifacts. You never downgrade FAIL to PASS.

## ClaimResult Schema

Each claim verification produces a `ClaimResult`:

```json
{
  "claim_id": "C1",
  "status": "PASS | FAIL | UNVERIFIED",
  "evidence": "Verified against...",
  "evidence_artifacts": ["tool_call_ref"],
  "model_used": "<model-tag>",
  "modality": "text | vision | embedding | audio"
}
```

**Status semantics:**

| Status | Meaning |
|--------|---------|
| PASS | Claim verified against evidence |
| FAIL | Claim contradicted by evidence |
| UNVERIFIED | No model available for required modality, or evidence inconclusive |

**FAIL is never downgraded to PASS.** This is a strict invariant per 065-verification-honesty.md. If the verifying model returns that a claim fails verification, the result is FAIL — not "close enough" or "functionally equivalent."

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify` | Verify multiple claims against evidence using modality-aware dispatch | ≈400 |
| `verify-single` | Verify a single claim with modality detection | ≈300 |
| `completion` | Ensure mandatory terminal-state dispatch; produce status report | ≈150 |

## Invocation

- `/skill verification` — Overview only
- `/skill verification --task verify --claims <claims_list> --content <ContentPayload>` — Verify multiple claims
- `/skill verification --task verify-single --claim <claim> --content <ContentPayload>` — Verify a single claim
- `/skill verification --task completion` — Invoke when workflow halts

## Operating Protocol

1. **Detect modality from content.** The `ContentPayload` determines which modalities are needed. Text content routes to text models. Image content routes to vision models. Mixed content routes to multiple models.
2. **Dispatch via multimodal-dispatch.** Each claim is dispatched to the appropriate model based on its modality. The `multimodal-dispatch` skill handles model selection, caching, and fallback.
3. **Collect evidence artifacts.** Every PASS or FAIL result must include evidence artifacts — tool call references or documentation citations that support the verification outcome.
4. **Produce ClaimResult for each claim.** Each claim gets an individual result with status, evidence, and the model used.
5. **FAIL is never downgraded to PASS.** The strictest invariant. If verification fails, it stays failed.
6. **UNVERIFIED for unavailable modalities.** When a modality has no available model (e.g., audio/ASR), the claim receives UNVERIFIED status with a gap description, not a blocking error.
7. **Completion guarantee.** If this workflow halts at any point, invoke `--task completion` before halting.

## Sub-Agent Tasks

| Task | Sub-agent | Result Contract |
|------|-----------|-----------------|
| `verify` | Yes | `VerificationResult` with per-claim `ClaimResult` list |
| `verify-single` | Yes | `ClaimResult` with status, evidence, and model |
| `completion` | Yes | Status report with verification state |

## Cross-References

- `multimodal-dispatch` — Routes claims to appropriate models based on modality
- `verification-enforcement` — Pre-generation verification gate; may route through dispatcher for modality-aware verification
- `spec-auditor` — May route ground-truth verification through dispatcher
- `065-verification-honesty.md` — FAIL never downgraded to PASS; unverified claims marked explicitly
- `completion-core` — Shared completion operations reference

## Worktree Mode

When `worktree.path` is set:
- ALL `bash` tool calls MUST use `workdir` parameter set to `worktree.path`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `worktree.path/`
- Sub-agent dispatch prompts MUST include `worktree.path: <value>`

Co-authored with AI: <AgentName> (<ModelId>)