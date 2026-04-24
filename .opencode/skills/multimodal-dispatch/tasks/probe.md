# Task: probe

## Purpose

Query the Ollama API for available models and their capabilities, building a `CapabilitySnapshot` that other tasks use for routing decisions. This task is the entry point for all dispatch operations — without a capability snapshot, no routing can occur.

## Entry Criteria

The dispatcher needs current model capability information. No prior snapshot is required (this task creates one).

## Exit Criteria

A `CapabilitySnapshot` JSON is produced containing all available models with their modalities, capabilities, source tier, and preferred flags. Stale or missing snapshots are replaced.

## Procedure

### Step 1: Check Cache

Check if a cached capability snapshot exists and is within TTL (default: 300 seconds). If a valid cache entry exists and `--refresh` was not specified, return the cached snapshot immediately.

Cache location: `./tmp/capability-snapshot.json`

Cache invalidation conditions:
- TTL exceeded (default 300s from `timestamp`)
- `--refresh` flag specified
- Model pull/remove event detected (checked in Step 2)

### Step 2: Probe Ollama API

Query Ollama for available models:

```bash
curl -s http://localhost:11434/api/tags
```

Parse the response to extract model names. For each model, query its detail endpoint:

```bash
curl -s http://localhost:11434/api/show -d '{"name":"<model-tag>"}'
```

Extract capability information from each model's detail response:
- **Modality**: Determine from model family and capabilities (e.g., models with vision capabilities are modality `vision`; text-only models are `text`; embedding models are `embedding`)
- **Source tier**: Determine from model tag suffix (e.g., `:cloud` → `ollama-cloud`, `:latest` or no tier suffix → `ollama-local`)
- **Context window**: Extract from model parameters if available, otherwise use known defaults
- **Capabilities**: Infer from model family (e.g., reasoning, coding, agentic, thinking)
- **Input types**: Determine from modality (text models accept `["text"]`, vision models accept `["text", "image"]`)

### Step 3: Apply Cloud-First Ordering

Sort models within each modality tier:
1. Cloud models first (`ollama-cloud` source)
2. Local models second (`ollama-local` source)
3. Within each tier, prefer newer/larger models

Set `preferred: true` on the highest-ranked model in each modality. This is the model that `resolve` will select by default for that modality.

For modalities where only local models exist (e.g., embedding, TTS, image generation), the local model is `preferred: true`.

For modalities where no Ollama model exists (e.g., audio/ASR, music, viseme), do NOT fabricate entries. These modalities produce `(unverified)` results in dispatch, per REQ-5.

### Step 4: Build CapabilitySnapshot

Assemble the snapshot:

```json
{
  "timestamp": "<ISO-8601>",
  "ttl_seconds": 300,
  "models": [
    {
      "name": "<model-tag>",
      "modality": "<text|vision|embedding|audio|image-gen>",
      "source": "<ollama-cloud|ollama-local>",
      "params": "<parameter description>",
      "context_window": <int>,
      "input_types": ["<input-type>", ...],
      "capabilities": ["<capability>", ...],
      "preferred": <true|false>
    }
  ]
}
```

### Step 5: Cache and Return

Write the snapshot to `./tmp/capability-snapshot.json` and return it.

## Cache Invalidation

On model pull/remove events detected through Ollama API changes, invoke `invalidate_cache()`:

```bash
rm -f ./tmp/capability-snapshot.json
```

The next `probe` call will rebuild from scratch.

## Error Handling

- If Ollama is not running (connection refused), return a minimal snapshot with `models: []` and log the unavailability. Dispatch tasks will degrade to `(unverified)` for all modalities.
- If a model detail query fails, skip that model and continue. Log the failure.
- If the entire probe fails, return the last cached snapshot if available, otherwise return empty snapshot.

## Context Required

- Invoked by: `multimodal-dispatch` skill entry point, or any task needing model capabilities
- Followed by: `resolve` (modality routing) or `dispatch` (sub-agent dispatch)
- Related tasks: `resolve`, `dispatch`, `dispatch-multi`

Co-authored with AI: <AgentName> (<ModelId>)