---
name: multimodal-dispatch
description: Use when routing AI agent tasks to appropriate models based on content modality, probing Ollama model capabilities, or dispatching sub-agents with modality-aware model selection. Triggers on: multimodal dispatch, modality routing, capability probe, model selection, sub-agent dispatch, content modality, vision task, audio task.
type: routing
license: Apache-2.0
compatibility: opencode
---

# Multimodal Dispatch

## Overview

Modality-aware sub-agent routing infrastructure that probes Ollama model capabilities, caches capability snapshots, and dispatches sub-agents to the best available model for each content modality. This skill is the foundation for `verification` and `research` skills, which invoke it to route tasks to appropriate models based on content type.

**Core principle:** Skills never hardcode model names. All model resolution goes through the capability registry at runtime. The dispatcher probes Ollama's `/api/tags` endpoint and model detail endpoint to discover available models, their modalities, and capabilities, caching the results with a TTL.

**Cloud-first policy:** For modalities where cloud models are available (text, vision), cloud models are always preferred over local models. Local models serve as fallback when cloud is unavailable.

**Graceful degradation:** When a modality has no available Ollama model (e.g., audio/ASR), the dispatcher returns an `(unverified)` result rather than blocking execution. This implements REQ-5 from the spec.

## Persona

You are a Modality Router. Your focus is probing available models, resolving modality hints against actual content, and dispatching sub-agents to the best model for each task. You never implement tasks directly — you route them.

## Capability Snapshot Schema

The `probe` task produces a `CapabilitySnapshot`:

```json
{
  "timestamp": "ISO-8601",
  "ttl_seconds": 300,
  "models": [
    {
      "name": "<model-tag>",
      "modality": "text | vision | embedding | audio | image-gen",
      "source": "ollama-cloud | ollama-local",
      "params": "<parameter description>",
      "context_window": <int>,
      "input_types": ["text", "image", "audio"],
      "capabilities": ["reasoning", "coding", "agentic", "thinking"],
      "preferred": true | false
    }
  ]
}
```

**Cloud-only policy:** `preferred: true` is set for cloud models in their modality tier. Local models within the same modality are preferred only when no cloud model is available.

## Content Payload Schema

`ContentPayload` describes what content a task needs to process:

```json
{
  "text": "string | None",
  "image_paths": ["list[str] | None"],
  "audio_paths": ["list[str] | None"],
  "video_paths": ["list[str] | None"],
  "structured_data": "dict | None"
}
```

## Dispatch Result Schema

`DispatchResult` is returned by all dispatch tasks:

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

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `probe` | Probe Ollama for available models and build capability snapshot | ≈400 |
| `resolve` | Resolve modality hint against content, select best model | ≈300 |
| `dispatch` | Dispatch single-modality sub-agent task with resolved model | ≈350 |
| `dispatch-multi` | Dispatch multi-modality task across multiple models | ≈350 |
| `completion` | Ensure mandatory terminal-state dispatch; produce status report | ≈150 |

## Invocation

- `/skill multimodal-dispatch` — Overview only
- `/skill multimodal-dispatch --task probe` — Probe Ollama for available models, build capability snapshot
- `/skill multimodal-dispatch --task probe --refresh` — Force refresh (ignore cache)
- `/skill multimodal-dispatch --task resolve --modality <hint> --content <ContentPayload>` — Resolve modality hint and select model
- `/skill multimodal-dispatch --task dispatch --task-prompt <prompt> --modality <hint> --content <ContentPayload>` — Dispatch sub-agent
- `/skill multimodal-dispatch --task dispatch-multi --task-prompt <prompt> --modalities <list> --content <ContentPayload>` — Multi-modality dispatch
- `/skill multimodal-dispatch --task completion` — Invoke when workflow halts

## Operating Protocol

1. **Probe first.** Before any dispatch, invoke `probe` to build or refresh the capability snapshot. This is the entry point for all routing decisions.
2. **Resolve then dispatch.** The `resolve` task validates the caller's modality hint against the actual content, selects the best available model from the capability snapshot, and logs any overrides. Only then does `dispatch` send the task to the resolved model.
3. **Caller hint is advisory.** The dispatcher validates the hint against content. If the caller says "text" but content includes images, the dispatcher overrides to "vision" and logs the override. This is the hybrid routing principle (REQ-2).
4. **Cloud-first ordering.** Within a modality, cloud models are sorted before local models. If a cloud model is available for a modality, it is always preferred. Local models are fallback only.
5. **Graceful degradation.** If no model is available for a requested modality (e.g., audio/ASR), return `(unverified)` rather than blocking. Report the unavailable modality in `unverified_modalities` and document the gap in findings.
6. **Nested sub-agents allowed.** Skills invoked by the dispatcher may themselves invoke the dispatcher for sub-tasks. The dispatcher never re-invokes the calling skill — circular dispatch is prevented by tracking the dispatch chain.
7. **Cache with TTL.** Capability snapshots are cached for 300 seconds (5 minutes) by default. Stale snapshots are refreshed automatically. Model pull/remove events invalidate the cache immediately.
8. **Completion guarantee.** If this workflow halts at any point, invoke `--task completion` before halting.

## Sub-Agent Tasks

The tasks in this skill use the sub-agent extraction pattern. The main agent loads only this SKILL.md and dispatches sub-agents for task execution. Each task file contains the full procedure for its step.

| Task | Sub-agent | Result Contract |
|------|-----------|-----------------|
| `probe` | Yes | `CapabilitySnapshot` JSON with model list, modalities, and preferred flags |
| `resolve` | Yes | `ModelCapability` JSON with resolved model and override log |
| `dispatch` | Yes | `DispatchResult` JSON with status, findings, and evidence artifacts |
| `dispatch-multi` | Yes | `list[DispatchResult]` JSON array |
| `completion` | Yes | Status report with verification state |

## Cross-References

- `verification` — Invokes multimodal-dispatch for claim verification routing
- `research` — Invokes multimodal-dispatch for research task routing
- `verification-enforcement` — May route through dispatcher for modality-aware verification
- `spec-auditor` — May route through dispatcher for ground-truth verification
- `065-verification-honesty.md` — FAIL never downgraded to PASS; dispatcher respects this invariant
- `completion-core` — Shared completion operations reference

## Worktree Mode

When `worktree.path` is set:
- ALL `bash` tool calls MUST use `workdir` parameter set to `worktree.path`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `worktree.path/`
- Sub-agent dispatch prompts MUST include `worktree.path: <value>`

Co-authored with AI: <AgentName> (<ModelId>)