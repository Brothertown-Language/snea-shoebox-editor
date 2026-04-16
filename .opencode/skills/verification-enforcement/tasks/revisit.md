# Task: revisit

## Purpose

Run the post-generation verification pass. After content has been generated and the skill's own quality checks have run, this task scans the output for `⚠️ UNVERIFIED` markers and attempts to resolve them. Any claims that remain unverifiable after this pass are escalated to the developer.

This task is mandatory after every content generation. The output is never shipped as done while unverified claims remain without developer acknowledgment.

## Entry Criteria

Content generation is complete and the skill's self-review or quality-check step has finished. The generated output may contain `⚠️ UNVERIFIED` markers from the `verify` pass.

## Exit Criteria

All `⚠️ UNVERIFIED` markers have been resolved, or remaining unresolvable claims have been escalated to the developer with specific reasons.

## Procedure

The agent scans the generated output for `⚠️ UNVERIFIED` markers. Each marker identifies a claim that could not be verified during the pre-generation `verify` pass. The agent collects these markers and dispatches section-based sub-agents to attempt verification again, using the domain-appropriate tools that match each claim's verification domain.

The revisit pass benefits from the full context of the generated content — the sub-agents can see the claim in its surrounding prose, which may clarify what verification approach is needed. Sometimes the generated text itself reveals that the claim was imprecise and can be rephrased to match what the live source actually says. Other times, the claim is correct but the initial verification attempt used the wrong tool or the wrong query.

Sub-agents in the revisit pass use the same evidence artifact format as the `verify` pass. For each unverified claim, the sub-agent attempts verification and returns either a `Verified: yes` artifact or a `Verified: no` artifact with an expanded reason field explaining what was tried and why it failed.

If claims remain unverifiable after the revisit pass, the agent must not remove the `⚠️ UNVERIFIED` markers and must not ship the content as complete. Instead, it escalates to the developer with a specific report: which claims could not be verified, which tools and sources were consulted, and why verification failed. The developer then has three options: provide the missing evidence, instruct the agent to remove or rephrase the unverifiable claim, or accept the risk and explicitly approve the content with unverified claims.

The revisit pass is the safety net that catches what the initial verify pass missed. It exists because some verifications only become possible after the content exists in full context, and because a second attempt with different tools or queries sometimes succeeds where the first failed.

## Context Required

- Invoked by: content-generating skills after their self-review or quality-check step
- Preceded by: `verify` (pre-generation gate)
- Related tasks: `verify` (pre-generation), `enforce` (orchestrator gate)