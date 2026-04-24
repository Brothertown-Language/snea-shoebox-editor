# Task: dispatch-multi

## Purpose

Dispatch a task across multiple modalities simultaneously. When a single task requires processing in multiple modalities (e.g., verifying an OCR'd document requires both vision to read the original image and text to check the transcription), this task coordinates dispatches to multiple models and aggregates the results.

## Entry Criteria

- A list of modalities is required (e.g., `["text", "vision"]`)
- A content payload with content for each modality
- A task prompt describing the overall objective

## Exit Criteria

A `list[DispatchResult]` is returned with one entry per modality. Partial results are returned for modalities where models are available; `(unverified)` results for modalities where no model exists.

## Procedure

### Step 1: Resolve Model for Each Modality

For each modality in the requested list:

1. Invoke `resolve` with the modality hint and the content payload
2. Collect the resolved model for that modality
3. If no model is available, mark the modality as `(unverified)`

### Step 2: Dispatch Per-Modality Sub-Agents

For each resolved modality, dispatch a sub-agent using `dispatch`:

- **Text modality**: Sub-agent processes text content, uses text model
- **Vision modality**: Sub-agent processes image content, uses vision model
- **Other modalities**: Sub-agent processes modality-specific content, uses appropriate model

Each sub-agent receives:
- A scoped task prompt derived from the overall objective, focused on its modality
- The resolved model for its modality
- The relevant content from the ContentPayload

### Step 3: Aggregate Results

Collect all `DispatchResult` entries and aggregate into a combined result:

```json
[
  {
    "status": "completed",
    "modality": "vision",
    "model_used": "<vision-model>",
    "findings": "<vision-findings>",
    "evidence_artifacts": ["<vision-evidence>"],
    "unverified_modalities": [],
    "error": null
  },
  {
    "status": "completed",
    "modality": "text",
    "model_used": "<text-model>",
    "findings": "<text-findings>",
    "evidence_artifacts": ["<text-evidence>"],
    "unverified_modalities": [],
    "error": null
  }
]
```

### Step 4: Determine Overall Status

The overall status is determined by the worst-case per-modality status:

| Per-Modality Status | Overall Status |
|--------------------|----------------|
| All `completed` | `completed` |
| Mix of `completed` and `partial` | `partial` |
| Any `unverified` | `partial` (if others completed) or `unverified` (if all unverified) |
| Any `failed` | `failed` (if critical) or `partial` (if non-critical) |

**FAIL is never downgraded to PASS.** If any per-modality result is FAIL, the overall result MUST preserve that failure. The calling skill decides how to handle multi-modality failures.

### Step 5: Return Results

Return the `list[DispatchResult]`. The calling skill is responsible for integrating the multi-modality results into its own result schema (e.g., `ResearchResult` for the `research` skill, or a combined verification result for the `verification` skill).

## Multi-Modality Example

Verifying that an OCR transcription matches an original document:

1. User provides `content = { text: "transcribed text", image_paths: ["document.png"] }` and `modalities = ["vision", "text"]`
2. `dispatch-multi` resolves vision model for the image, text model for the transcription
3. Vision sub-agent reads the original image and reports what it sees
4. Text sub-agent analyzes the transcription for accuracy
5. Both results are returned; the calling skill compares vision findings against text findings

## Graceful Degradation (REQ-5)

If a modality has no available model:
- That modality's entry in the result list has `status: "unverified"`
- `findings` is `(unverified: <modality> — <reason>)`
- `model_used` is `null`
- Other modalities continue processing
- Execution is never blocked by an unavailable modality

## Context Required

- Depends on: `resolve` (per-modality model selection), `dispatch` (per-modality execution)
- Invoked by: `verification`, `research`, and other skills needing multi-modality processing
- Related tasks: `dispatch` (single-modality version)

Co-authored with AI: <AgentName> (<ModelId>)