# Task: verify

## Purpose

Run the pre-generation verification gate. Before a content-generating skill produces any output, this task collects evidence artifacts for every factual claim the agent intends to make. The agent declares its intended claims, dispatches sub-agents to verify each content section against live sources, and assembles the results. Claims that cannot be verified are marked for later resolution.

## Entry Criteria

A content-generating skill is about to produce output. The agent has identified what content it will generate and what claims that content will make.

## Exit Criteria

Evidence artifacts have been collected for all claims, or unverifiable claims have been marked with `⚠️ UNVERIFIED` for the revisit pass to resolve.

## Procedure

The orchestrator begins by identifying the content sections that the generating skill intends to produce. These sections correspond to the natural divisions of the output — for a spec, this might be objectives, constraints, success criteria, and affected files; for a runbook, this might be environment context, diagnosis, mitigation steps, and verification criteria. The orchestrator does not need to know the exact content yet — it needs to know the claims that will be made, broadly categorized.

For each content section, the orchestrator dispatches one sub-agent with a focused mission: verify all factual claims that will appear in this section against live sources and return evidence artifacts. The sub-agent receives the section context, the claim types expected, and the verification domains that apply. Each sub-agent uses domain-appropriate tools: `srclight_get_signature` for API claims, `read` for config and source code claims, `srclight_get_symbol` for code behavior claims, bash commands for CLI tool verification, and web fetches for external documentation claims.

Each sub-agent classifies every claim it encounters into the appropriate verification domain, selects the evidence tool, collects the evidence, and returns a structured evidence artifact for each claim. Claims that the sub-agent cannot verify against any live source are marked with `⚠️ UNVERIFIED` and the specific reason verification failed is recorded.

The evidence artifact format is:

```
Claim: <what the content asserts>
Domain: <verification domain — API, config, code behavior, docs, CLI>
Source: <tool call or document that provided the evidence>
Verified: <yes|no>
Marker: <if no, ⚠️ UNVERIFIED>
Reason: <if no, why verification failed>
```

The orchestrator assembles the evidence artifacts from all sub-agents. If every claim has a `Verified: yes` artifact, the generation proceeds with full confidence. If some claims are marked `⚠️ UNVERIFIED`, the generation proceeds — but the unverified claims must be marked with `⚠️ UNVERIFIED` in the generated content so the revisit pass can find and attempt to resolve them.

No claim appears in generated content without an evidence artifact. If the agent has no tool call to support a claim, it must not assert the claim as verified. This is the core principle: no tool call means no claim, and no evidence means no assertion.

## Context Required

- Invoked by: content-generating skills as their first substantive step
- Followed by: the content generation steps of the invoking skill
- Related tasks: `revisit` (post-generation resolution), `enforce` (orchestrator gate)