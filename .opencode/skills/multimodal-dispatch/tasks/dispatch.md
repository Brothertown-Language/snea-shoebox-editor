# Task: dispatch

## Purpose

Dispatch a single-modality sub-agent task to the resolved model. This is the core execution task that takes a task prompt, a resolved model, and a content payload, then invokes the appropriate model to process the task.

## Entry Criteria

- A resolved model is available (from `resolve` task), OR a modality hint and content payload are provided for automatic resolution
- A task prompt describing what the sub-agent should accomplish

## Exit Criteria

A `DispatchResult` is returned with status, findings, evidence artifacts, and any unverified modalities.

## Procedure

### Step 1: Resolve Model (if not pre-resolved)

If the model has not been pre-resolved by `resolve`, invoke `resolve` with the provided modality hint and content payload. This ensures the correct model is selected.

If a model was already resolved, proceed with it.

### Step 2: Build Sub-Agent Context

Construct the sub-agent dispatch context:

```
Task Prompt: <task-prompt>
Resolved Model: <model-name>
Modality: <resolved-modality>
Content Payload: <ContentPayload JSON>
```

The sub-agent receives this context and processes the task using the resolved model.

### Step 3: Execute Sub-Agent Dispatch

Dispatch the sub-agent with:
- The task prompt as the primary instruction
- The resolved model as the target for processing
- The content payload for modality-specific processing (e.g., image paths for vision tasks)

**Nested sub-agent architecture (REQ-6):** Sub-agents dispatched by this task may themselves need to route additional sub-tasks. They can invoke `multimodal-dispatch` recursively. The dispatcher prevents circular dispatch by tracking the call chain — it never re-invokes the calling skill.

**Circular dispatch prevention:** Each dispatch carries a `dispatch_chain` list. Before dispatching, check if the calling skill is already in the chain. If so, return an error rather than dispatching circularly.

### Step 4: Collect Results

The sub-agent returns:
- **Findings**: The substantive result of the task (verification result, research findings, etc.)
- **Evidence artifacts**: Tool call references that support the findings
- **Model used**: Which model actually processed the task (for traceability)

### Step 5: Build DispatchResult

Assemble the dispatch result:

```json
{
  "status": "completed | partial | unverified | failed",
  "modality": "<resolved-modality>",
  "model_used": "<model-name>",
  "findings": "<sub-agent output>",
  "evidence_artifacts": ["<tool-call-refs>"],
  "unverified_modalities": [],
  "error": "string | None"
}
```

**Status mapping:**

| Condition | Status |
|-----------|--------|
| All modalities processed successfully | `completed` |
| Some modalities processed, others unverified | `partial` |
| No model available for the modality | `unverified` |
| Sub-agent execution failed | `failed` |

**FAIL is never downgraded to PASS (per 065-verification-honesty.md).** If a verification sub-agent returns FAIL, the dispatch result MUST preserve that FAIL status. It is a critical violation to downgrade FAIL to PASS based on agent judgment.

### Step 6: Return DispatchResult

Return the assembled result. The calling skill (`verification`, `research`, etc.) uses this to build its own result schema.

## DispatchResult Schema

```json
{
  "status": "completed | partial | unverified | failed",
  "modality": "text | vision | embedding | audio | image-gen",
  "model_used": "<model-tag>",
  "findings": "...",
  "evidence_artifacts": [],
  "unverified_modalities": [],
  "error": "string | None"
}
```

## Fallback Behavior

When no model is available for the requested modality:

1. Set `status` to `unverified`
2. Add the modality to `unverified_modalities`
3. Set `findings` to `(unverified: <modality> — <reason for unavailability>)`
4. Set `model_used` to `null`
5. Do NOT block execution — return the unverified result and let the calling skill handle it

This implements REQ-5: unavailable modalities produce `(unverified)` results, never block.

## Context Required

- Depends on: `resolve` (model selection)
- Invoked by: `verification`, `research`, and other skills needing modality-aware sub-agent dispatch
- Followed by: calling skill integrates DispatchResult into its own result schema

Co-authored with AI: <AgentName> (<ModelId>)