# Task: research-multi

## Purpose

Research across multiple modalities simultaneously. When a research query requires information from multiple modalities (e.g., "what does this image show and how does it relate to this text"), this task coordinates research across multiple models and aggregates the findings.

## Entry Criteria

- A research query describing what information to discover
- A list of modalities required (e.g., `["text", "vision"]`)
- A content payload with content for each modality
- The `multimodal-dispatch` skill is available for routing

## Exit Criteria

A `ResearchResult` is produced with combined findings from all modalities, source attribution for each, and explicit gap reporting for unavailable modalities.

## Procedure

### Step 1: Resolve Model for Each Modality

For each modality in the requested list:

1. Invoke `multimodal-dispatch --task resolve` with the modality hint and content payload
2. Collect the resolved model for that modality
3. If no model is available, mark the modality as `(unverified)`

### Step 2: Dispatch Per-Modality Research

For each resolved modality, dispatch a research sub-agent:

- **Text modality**: Research query targeting text content and context
- **Vision modality**: Research query targeting image content (what does the image show, what text is in the image, etc.)
- **Other modalities**: Research query targeting the relevant content type

Each sub-agent receives a scoped query focused on its modality, plus the relevant content from the ContentPayload.

### Step 3: Aggregate Findings

Combine findings from all modalities into a unified `ResearchResult`:

- **Findings**: Merge findings from all modalities, noting which modality produced each finding
- **Source attribution**: Include attribution from each model used
- **Modalities used**: List all modalities that produced results
- **Models used**: List all models that were invoked
- **Unverified modalities**: List modalities that had no available model
- **Gaps**: Combine gap descriptions from all unavailable modalities

### Step 4: Determine Overall Status

| Per-Modality Results | Overall Status |
|---------------------|----------------|
| All modalities completed | `completed` |
| Mix of completed and unverified | `partial` |
| All modalities inconclusive | `inconclusive` |
| All modalities failed or no models available | `failed` |

### Step 5: Return ResearchResult

Return the combined `ResearchResult` with all findings, source attributions, and gaps.

## Multi-Modality Example

Researching a document that includes both text and an image:

1. User provides `content = { text: "document text", image_paths: ["figure.png"] }` and `modalities = ["text", "vision"]`
2. `research-multi` resolves text model for text content, vision model for image content
3. Text sub-agent analyzes the document text and produces findings about content
4. Vision sub-agent analyzes the image and produces findings about visual content
5. Findings are combined with source attribution for each modality

## Graceful Degradation (REQ-5)

If a modality has no available model:
- That modality is listed in `unverified_modalities`
- A gap description is added to `gaps`
- Other modalities continue processing
- Overall status is `partial` (if some modalities succeeded) or `failed` (if none succeeded)
- Research is never blocked by an unavailable modality

## Context Required

- Depends on: `multimodal-dispatch` (resolve and dispatch per modality)
- Invoked by: skills needing multi-modality research
- Related tasks: `research` (single-modality version), `completion`

Co-authored with AI: <AgentName> (<ModelId>)