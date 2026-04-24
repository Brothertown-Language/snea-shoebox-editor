# Task: research

## Purpose

Discover information using modality-aware dispatch. This task takes a research query, dispatches it to the appropriate model via `multimodal-dispatch`, and produces findings with source attribution and gap reporting.

## Entry Criteria

- A research query describing what information to discover
- A modality hint (or "auto" for automatic detection)
- A content payload describing available evidence
- The `multimodal-dispatch` skill is available for routing

## Exit Criteria

A `ResearchResult` is produced with findings, source attribution, and explicit gap reporting.

## Procedure

### Step 1: Detect Modality

Inspect the content payload and query to determine the appropriate modality:

- **Text-only query** with only `text` content → modality `text`
- **Query about images** with `image_paths` → modality `vision`
- **Query about audio** with `audio_paths` → modality `audio` (likely UNVERIFIED)
- **Multi-modality query** → use `research-multi` task instead

If the caller provided a modality hint, use it as a starting point. The `multimodal-dispatch --task resolve` task validates the hint against content.

### Step 2: Dispatch via multimodal-dispatch

Invoke `multimodal-dispatch --task dispatch` with:
- `task-prompt`: "Research this query: <query_text>. Provide findings with source attribution."
- `modality`: The resolved modality
- `content`: The content payload

### Step 3: Collect Findings with Source Attribution

From the `DispatchResult`, extract findings and build source attribution:

```json
{
  "source_type": "model_output",
  "source_ref": "<model-tag>",
  "confidence": "high | medium | low"
}
```

**Confidence levels:**
- `high`: Finding verified against a live source (tool call, documentation lookup)
- `medium`: Finding from model output with no direct live verification
- `low`: Finding is inconclusive or based on unverifiable information

Source attribution is mandatory for every finding. A finding without source attribution is an unverified claim, not a verified finding.

### Step 4: Identify Gaps

- List modalities that were unavailable (reported in `unverified_modalities`)
- List knowledge areas where the model could not produce definitive findings (reported in `gaps`)
- Format gap descriptions explicitly: "No Ollama model available for <modality>; <reason>"

Example gap: `"No Ollama model available for audio; ASR deferred to PEP 723 phase"`

### Step 5: Build ResearchResult

Assemble the complete result:

```json
{
  "status": "completed | partial | inconclusive | failed",
  "findings": "<research findings>",
  "source_attribution": [
    {
      "source_type": "model_output",
      "source_ref": "<model-tag>",
      "confidence": "high"
    }
  ],
  "modalities_used": ["text"],
  "models_used": ["<model-tag>"],
  "unverified_modalities": [],
  "gaps": []
}
```

**Status determination:**

| Condition | Status |
|-----------|--------|
| All requested modalities produced findings | `completed` |
| Some modalities produced findings, others unverified | `partial` |
| Research performed but findings not definitive | `inconclusive` |
| No model available or error occurred | `failed` |

### Step 6: Return Result

Return the `ResearchResult`. The calling skill uses this to build its own findings.

## Unverified Modalities (REQ-5)

When a modality has no available model:

1. Add the modality to `unverified_modalities`
2. Add a gap description to `gaps`: `(unverified: <modality> — <reason>)`
3. Set `status` to `partial` if other modalities succeeded, or `inconclusive` if no modalities succeeded
4. Do NOT block execution — the research continues with available modalities

This implements REQ-5: unavailable modalities produce `(unverified)` results, never block.

## Context Required

- Depends on: `multimodal-dispatch` (model selection and dispatch)
- Invoked by: skills needing modality-aware research (spec-creation, correspondence, etc.)
- Related tasks: `research-multi`, `completion`

Co-authored with AI: <AgentName> (<ModelId>)