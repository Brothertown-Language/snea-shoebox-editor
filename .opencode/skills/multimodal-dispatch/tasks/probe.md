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

**Cache TTL enforcement (REQ-3):**

The TTL is enforced strictly. The cache check compares the snapshot's `timestamp` field against the current time:

```
current_time - snapshot.timestamp > ttl_seconds → STALE (refresh required)
current_time - snapshot.timestamp ≤ ttl_seconds → FRESH (return cached)
```

Default TTL is 300 seconds (5 minutes). This can be overridden via the `MULTIMODAL_DISPATCH_TTL` environment variable.

Cache invalidation conditions:
- TTL exceeded (default 300s from `timestamp`)
- `--refresh` flag specified
- Model pull/remove event detected (checked in Step 2)
- Explicit `invalidate_cache()` call

**invalidate_cache() implementation:**

When a model pull or remove event is detected (e.g., `ollama pull`, `ollama rm`), or when the caller explicitly requests cache invalidation:

```bash
rm -f ./tmp/capability-snapshot.json
```

This forces the next `probe` call to rebuild from scratch. The cache file is the single source of truth — deleting it is sufficient for invalidation. No partial or selective invalidation is needed because the entire snapshot is rebuilt on each probe.

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

### Step 3: Apply Cloud-First Ordering (REQ-4, REQ-8)

Sort models within each modality tier using the following ordering rules:

**Cloud-first (REQ-8):** For modalities where cloud models exist (text, vision), cloud models are ALWAYS preferred over local models. Local models within the same modality are used only when no cloud model is available, or as explicit fallback when cloud is unreachable.

**Newer/larger preference (REQ-4):** Within the same source tier (cloud or local), prefer newer and larger models. Sort by:
1. Source tier: `ollama-cloud` before `ollama-local`
2. Parameter count: larger models first (when determinable)
3. Recency: newer model versions first

**Preferred flag assignment:** Set `preferred: true` on the highest-ranked model in each modality. This is exactly one model per modality.

| Modality | Primary (Cloud) | Secondary (Local) | Fallback |
|----------|-----------------|--------------------|----------|
| Text | Cloud text model (preferred) | Local text model | `(unverified)` only |
| Vision | Cloud vision model (preferred) | Local vision model | `(unverified)` only |
| Embedding | — | Local embedding model (preferred) | `(unverified)` only |
| Audio | — | — | `(unverified: ASR deferred)` |
| Image generation | — | Local image-gen model (preferred) | `(unverified)` only |
| TTS | — | Local TTS model (preferred) | `(unverified)` only |

For modalities where no Ollama model exists (audio/ASR, music generation, viseme alignment — PEP 723 deferred per REQ-9), do NOT fabricate entries. These produce `(unverified)` results in dispatch per REQ-5.

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

**Event-driven invalidation:** When the agent observes an `ollama pull` or `ollama rm` command being run (in any context), it MUST call `invalidate_cache()` before the next dispatch. This ensures the capability snapshot reflects the current model state.

**TTL-based invalidation:** Even without explicit events, TTL ensures stale snapshots are never served. A snapshot older than 300 seconds is treated as missing and rebuilt on the next `probe` call.

**No partial invalidation:** The snapshot is an atomic unit. There is no facility for invalidating a single model entry — the entire snapshot is rebuilt.

## Error Handling

- If Ollama is not running (connection refused), return a minimal snapshot with `models: []` and log the unavailability. Dispatch tasks will degrade to `(unverified)` for all modalities.
- If a model detail query fails, skip that model and continue. Log the failure.
- If the entire probe fails, return the last cached snapshot if available, otherwise return empty snapshot.

## Context Required

- Invoked by: `multimodal-dispatch` skill entry point, or any task needing model capabilities
- Followed by: `resolve` (modality routing) or `dispatch` (sub-agent dispatch)
- Related tasks: `resolve`, `dispatch`, `dispatch-multi`

Co-authored with AI: <AgentName> (<ModelId>)