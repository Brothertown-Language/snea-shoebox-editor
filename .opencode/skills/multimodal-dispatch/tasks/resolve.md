# Task: resolve

## Purpose

Resolve a caller's modality hint against the actual content payload, validate the hint, select the best available model from the capability snapshot, and log any overrides. This task implements the hybrid routing principle (REQ-2): the caller provides a hint, the dispatcher validates it, and if the hint contradicts the content, the dispatcher overrides and logs.

## Entry Criteria

- A capability snapshot exists (from `probe` task)
- A modality hint is provided by the caller
- A content payload is provided

## Exit Criteria

A resolved `ModelCapability` is selected, any hint overrides are logged, and the result is ready for `dispatch`.

## Procedure

### Step 1: Load Capability Snapshot

Load the cached capability snapshot from `./tmp/capability-snapshot.json`. If the snapshot is stale (older than TTL) or missing, invoke `probe` first to refresh it.

### Step 2: Analyze Content Payload

Inspect the `ContentPayload` to determine the actual modalities present:

| Content Field | Implied Modality |
|---------------|-------------------|
| `text` present | `text` (always included) |
| `image_paths` non-empty | `vision` (required in addition to text) |
| `audio_paths` non-empty | `audio` (ASR/transcription) |
| `video_paths` non-empty | `vision` (frame extraction) |
| `structured_data` present | `text` (serialized) |

### Step 3: Validate Modality Hint

Compare the caller's modality hint against the content-derived modalities:

- If hint matches content → use hint as-is
- If hint contradicts content (e.g., hint="text" but content has images) → **override hint** to match content, log the override
- If hint is "auto" or not provided → infer from content entirely

Override logging format:

```
MODALITY_OVERRIDE: caller_hint=<hint> content_derived=<actual> resolved=<final> reason=<why>
```

This log entry is included in the `DispatchResult.findings` field for traceability.

### Step 4: Select Best Model

From the capability snapshot, select the model for each resolved modality:

1. Filter models by modality match
2. Sort by source tier (cloud first, local second)
3. Within tier, prefer newer/larger models
4. Select the top-ranked model (which has `preferred: true`)

For the primary resolved modality, use the `preferred: true` model from the snapshot.

If no model is available for a resolved modality:
- Mark the modality as `(unverified)` in the result
- Log the unavailability: `UNVERIFIED_MODALITY: <modality> — no Ollama model available; <reason>`

### Step 5: Return Resolved Model

Return the resolved model information:

```json
{
  "resolved_modality": "<final-modality>",
  "model": {
    "name": "<model-tag>",
    "modality": "<modality>",
    "source": "<source-tier>",
    "preferred": true
  },
  "override_log": [
    {
      "caller_hint": "<original-hint>",
      "content_derived": "<actual>",
      "resolved": "<final>",
      "reason": "<why>"
    }
  ],
  "unverified_modalities": [],
  "cache_hit": true
}
```

## Cloud-First Preference (REQ-8 / REQ-4)

For text and vision modalities, cloud models are always preferred when available:

| Modality | Primary (Cloud) | Secondary (Local) | Fallback |
|----------|-----------------|--------------------|----------|
| Text (reasoning/coding) | Cloud text model | Local text model | `(unverified)` |
| Vision (OCR/image) | Cloud vision model | Local vision model | `(unverified)` |
| Embedding | — | Local embedding model | `(unverified)` |
| Audio | — | — | `(unverified: ASR deferred to PEP 723 phase)` |
| Image generation | — | Local image-gen model | `(unverified)` |

The `preferred: true` flag in the capability snapshot already reflects this ordering. `resolve` simply selects the preferred model.

## Error Handling

- No capability snapshot available → invoke `probe` first
- No model for resolved modality → return `(unverified)` for that modality
- Multiple models for same modality → select `preferred: true` model

## Context Required

- Depends on: `probe` (capability snapshot)
- Invoked by: callers needing model resolution
- Output consumed by: `dispatch`, `dispatch-multi`

Co-authored with AI: <AgentName> (<ModelId>)