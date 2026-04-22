# Task: enforce

## Purpose

Verify that sub-agent output includes evidence artifacts before the orchestrator accepts it. This task is the orchestrator-level gate that catches sub-agents who returned content without evidence — the hallmark of a sub-agent that generated content from memory rather than live verification.

## Entry Criteria

An orchestrator skill (such as `divide-and-conquer`) has dispatched sub-agents for content generation and needs to validate their output before incorporating it.

## Exit Criteria

All sub-agent outputs have been checked for evidence artifacts. Outputs without evidence have been rejected, re-dispatched, or escalated.

## Procedure

The orchestrator receives output from each sub-agent. For every sub-agent that returned content containing factual claims, the orchestrator checks that evidence artifacts accompany the claims. Evidence artifacts follow the format defined in the `verify` task: `Claim`, `Domain`, `Source`, `Verified`, and optionally `Marker` and `Reason`.

A sub-agent that returns content with factual claims but no evidence artifacts has not completed verification. The orchestrator must reject this output and either re-dispatch the sub-agent with explicit instructions to collect evidence, or escalate if re-dispatch is not feasible.

The check is straightforward: for each factual claim in the sub-agent's output, does an evidence artifact exist? If the claim appears in the output unadorned by either an evidence artifact or a `⚠️ UNVERIFIED` marker, the sub-agent has produced content without verification — the very pattern that verification-enforcement exists to prevent.

Sub-agents that return fully verified output (all claims have `Verified: yes` artifacts) are accepted immediately. Sub-agents that return output with some `⚠️ UNVERIFIED` markers are accepted provisionally — the markers will be resolved by the `revisit` task during the post-generation pass. Sub-agents that return output with factual claims and no artifacts at all are rejected.

The enforce task runs at the orchestrator level, not at the content-generator level. Content-generating skills use `verify` and `revisit`. Skills that orchestrate content generation across multiple sub-agents use `enforce` to validate the sub-agent outputs before assembly.

## Context Required

- Invoked by: orchestrator skills (divide-and-conquer, work execution)
- Related tasks: `verify` (pre-generation gate), `revisit` (post-generation pass)