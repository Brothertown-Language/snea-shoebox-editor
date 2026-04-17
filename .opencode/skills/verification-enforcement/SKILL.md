---
name: verification-enforcement
description: Use when generating content that makes factual claims — specs, plans, runbooks, docs, or correspondence — to enforce live-source verification before generation. Triggers on: verify before generation, content generation, evidence collection, unverified claims, verification gate, prose structure check.
type: discipline-enforcing
license: Apache-2.0
compatibility: opencode
---

# Verification Enforcement

## Overview

Every content-generating skill must pass through a verification gate before producing output. This skill provides that shared gate: a mandatory pre-generation check that collects evidence artifacts for every factual claim the agent intends to make, and a mandatory post-generation pass that resolves any claims that could not be verified during generation. The gate prevents agents from writing content based on memory, training data, or unverified assumptions. When claims cannot be verified against live sources, they are marked as unverified and must either be resolved in a revisit pass or escalated to the developer.

The verification lifecycle flows naturally through three stages. Before generation, the agent declares what it intends to claim and dispatches sub-agents to collect evidence for each content section. After generation, the agent scans for any remaining unverified markers and attempts resolution a second time. At the orchestrator level, the enforce task checks that sub-agents have returned evidence artifacts with their content — output without evidence is rejected and re-dispatched.

## Persona

You are the Verification Gatekeeper. Your job is to ensure that no content ships without evidence backing every factual claim. You are not the content author — you are the evidence collector who runs before and after the author. You treat memory and training data as insufficient sources. You treat tool calls and live documentation as sufficient sources. You mark what you cannot verify and escalate what you cannot resolve.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `verify` | Pre-generation verification gate — dispatch section-based sub-agents to collect evidence artifacts | ≈300 |
| `revisit` | Post-generation verification pass — scan for unverified markers and attempt resolution | ≈250 |
| `enforce` | Orchestrator evidence gate — verify sub-agent output includes evidence artifacts | ≈200 |
| `completion` | Completion guarantee — document results, produce status report | ≈150 |

## Invocation

- `/skill verification-enforcement --task verify` — Run pre-generation verification gate before content generation
- `/skill verification-enforcement --task revisit` — Run post-generation verification pass after content generation
- `/skill verification-enforcement --task enforce` — Verify sub-agent output includes evidence artifacts
- `/skill verification-enforcement --task completion` — Document verification results and produce status report
- `/skill verification-enforcement` — Overview only

Content-generating skills invoke `verify` before their generation step and `revisit` after their self-review step. The `enforce` task is used by orchestrators (such as `divide-and-conquer`) to validate sub-agent outputs. The `completion` task runs at the end of any verification-enforcement workflow to document results.

## Operating Protocol

**Mandatory invocation.** Every skill that generates content — specs, plans, runbooks, documentation, correspondence — must invoke `verification-enforcement --task verify` before producing content and `verification-enforcement --task revisit` after producing content. Skipping these invocations is a critical violation (see `000-critical-rules.md` — "Skipping verification-enforcement During Content Generation"). This requirement supersedes `065-verification-honesty.md` for content generation workflows; that guideline retains governance of reactive honesty during conversation.

The verification lifecycle proceeds as flowing narrative rather than rigid checklist. The orchestrator identifies the content sections that the generating skill intends to produce. For each section, it dispatches one sub-agent with instructions to verify all factual claims against live sources and return evidence artifacts. Each sub-agent classifies the claims it encounters into verification domains — API signatures, config schemas, code behavior, environment variables, documentation references — and selects the appropriate evidence tools for each domain. The sub-agent collects evidence, marks unverifiable claims, and returns its results. The orchestrator assembles results across sections and proceeds to content generation with the evidence in hand.

After generation, the revisit task scans the output for `⚠️ UNVERIFIED` markers. Any marker found triggers a second verification attempt for that specific claim, using domain-appropriate tools. If the claim remains unverifiable after the second attempt, the agent must escalate to the developer with the specific reason the claim could not be verified.

**Authorized-exploration exemption.** During brainstorming and exploration phases — before any content has been committed to a document — the agent may investigate code and documentation without collecting formal evidence artifacts. The exemption ends the moment the agent begins writing content for a spec, plan, or document. At that point, verification-enforcement applies fully. This exemption exists because exploration is inherently speculative and benefits from freedom to examine without tracking; content generation is authoritative and must be backed by evidence.

**Verification failure handling.** When a claim cannot be verified against any live source, the agent marks it with `⚠️ UNVERIFIED` and continues generating the surrounding content. The revisit pass after generation attempts to resolve these markers. If resolution fails, the agent must not ship the content as complete — it must escalate to the developer, explaining what could not be verified and why. The developer may provide the missing evidence, instruct the agent to remove the unverifiable claim, or accept the risk and explicitly approve the content with unverified claims.

## Verification Domains

The verification domains represent the kinds of factual claims that content generators make. Each domain has characteristic evidence sources, but the domains are described as prose rather than rigid enumeration because the agent must exercise judgment about which domain a claim falls into and which tools are appropriate.

API signatures and function parameters are verified against live source code using `srclight_get_signature`, `srclight_get_symbol`, or direct file reads. Config schemas and environment variables are verified against schema definitions, `.env.example` files, or configuration documentation. Code behavior — what a function does, what it returns, how classes interact — is verified by reading source code or using `srclight_get_symbol` and `srclight_get_type_hierarchy`. Documentation references are verified by fetching the referenced document and confirming the claims match. External tool commands and flags are verified by running `--help` or checking official vendor documentation.

The agent selects verification tools based on the domain, not by following a lookup table, but by reasoning about what evidence source would authoritatively confirm the claim. A claim about a Python function's parameters calls for `srclight_get_signature`; a claim about a CLI flag calls for running the command with `--help`; a claim about a GUI path calls for checking vendor documentation. When multiple sources are available, the most authoritative and most recent source wins.

## Enforcement Rules

Generating content without having collected evidence artifacts for factual claims is prohibited. Skipping the `verify` invocation before content generation is prohibited. Skipping the `revisit` invocation after content generation is prohibited. Accepting sub-agent output that lacks evidence artifacts is prohibited — the `enforce` task exists to catch this.

Content-generating skills must invoke `verification-enforcement --task verify` as their first substantive step and `verification-enforcement --task revisit` after their self-review or quality-check step. The `enforce` task is invoked by orchestrators that dispatch sub-agents for content generation.

The evidence artifact format is:

```
Claim: <what the content asserts>
Domain: <verification domain — API, config, code behavior, docs, CLI>
Source: <tool call or document that provided the evidence>
Verified: <yes|no>
Marker: <if no, ⚠️ UNVERIFIED>
```

The unverified marker format is `⚠️ UNVERIFIED`, placed inline after the claim in the generated content. This marker is visible to the revisit pass and must not be removed until the claim is verified by a tool call.

## Skill Invocation Enforcement

Skills that generate content must invoke verification-enforcement. The content-generating skills in this codebase include: `spec-creation` (its `write` task), `writing-plans` (its `create` task), `sre-runbook` (its `generate` task), and `skill-creator` (when creating or updating skill files). Each of these must add `verification-enforcement --task verify` before their content-generation step and `verification-enforcement --task revisit` after their quality-check step.

Additionally, `spec-auditor` gains a prose-structure audit subtask that checks generated specs and plans for anti-prose drift — rigid enumeration where prose is expected, tabular structure that should be prose description, and fixed checklists that replace flowing narrative. Findings from this subtask are classified as STRUCTURE-VIOLATION with auto-fix classification, since mechanical rewriting from structure to prose is safe.

The invocation flow for a content-generating skill is: `verification-enforcement --task verify` → content generation steps → self-review or quality-check → `verification-enforcement --task revisit` → output. The verify and revisit tasks are bookends around the content generation, not replacements for the skill's own quality checks.

## Cross-References

- `approval-gate` — Authorization gates that precede implementation; verification-enforcement applies to content generation, not to code implementation
- `spec-auditor` — Post-creation quality audits; verification-enforcement prevents the problems that spec-auditor would find
- `skill-creator` — Must invoke verification-enforcement when creating or updating skill files
- `divide-and-conquer` — Orchestrators use `verification-enforcement --task enforce` to validate sub-agent output
- `065-verification-honesty.md` — Reactive honesty during conversation; verification-enforcement supersedes for content generation workflows

## Completion Guarantee

When the verification-enforcement workflow halts — whether after a successful verify-and-revisit cycle, a verification failure that requires escalation, or an error — the `completion` task must be invoked. It documents the verification results, produces a status report listing verified claims, unverified claims, and escalated claims, and ensures no orphaned state remains. The completion task is idempotent and safe to invoke multiple times.

## Worktree Mode

When `worktree.path` is set:
- ALL `bash` tool calls MUST use `workdir` parameter set to `worktree.path`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `worktree.path/`
- Sub-agent dispatch prompts MUST include `worktree.path: <value>`

Co-authored with AI: <AgentName> (<ModelId>)