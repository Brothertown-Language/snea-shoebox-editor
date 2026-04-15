# Task: generate

## Purpose

Generate an operational runbook for a given domain and scenario type. Enforces reasoning at every step — each action must explain WHY it is the right action for the observed symptoms and diagnosed root cause.

## Operating Protocol

1. Invoked by: `/skill sre-runbook --task generate`
2. When to use: When an operational runbook is needed for a system, service, or infrastructure domain
3. Exit criteria: Runbook generated with reasoning at every step, verified against dual-output contract

## Pre-Conditions

**Domain context is MANDATORY.** If any of the following are missing, the agent MUST prompt the user before proceeding:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain` | ✅ Yes | System/service name (e.g., "PostgreSQL primary", "Kubernetes ingress") |
| `scenario_type` | ✅ Yes | One of: `incident`, `procedure`, `degradation`, `failover` |
| `severity` | ✅ Yes | One of: `P1` (outage), `P2` (degraded), `P3` (minor) |

If domain context is missing or insufficient, HALT and prompt the user. Do NOT guess or fabricate domain context.

## Input Parameters

```
domain: <system or service name>
scenario_type: incident | procedure | degradation | failover
severity: P1 | P2 | P3
```

## Procedure

### Step 1: Document Symptoms

**WHAT:** Catalog all observed symptoms with severity and affected components.

**WHY:** Symptom documentation is the foundation of diagnosis. Without a complete symptom catalog, diagnosis is guesswork. Each symptom must be classified by severity and component so that diagnosis can trace symptoms to root causes.

Output — AI-parseable enforcement block:

```yaml
symptoms:
  - description: "<observed behavior>"
    severity: P1 | P2 | P3
    affected_components:
      - "<component name>"
    frequency: always | intermittent | one-time
    observed_at: "<timestamp or condition>"
```

Plus human-readable narrative explaining context and background.

**Verification gate:** Confirm each symptom matches observed behavior. If symptoms are ambiguous, HALT and prompt for clarification.

### Step 2: Diagnose Root Cause

**WHAT:** Trace symptoms to root cause through causal reasoning chains.

**WHY:** Diagnosis without reasoning is pattern-matching, not engineering. Each diagnosis step must explain why this root cause is the most likely explanation for the observed symptoms, citing evidence (logs, metrics, state).

Output — AI-parseable enforcement block:

```yaml
diagnosis:
  - root_cause: "<identified root cause>"
    confidence: high | medium | low
    severity: P1 | P2 | P3
    evidence_chain:
      - symptom: "<symptom from Step 1>"
        evidence: "<log output, metric, state observation>"
        reasoning: "<why this evidence supports this root cause>"
    affected_components:
      - "<component name>"
    escalation_threshold: "<time or condition that triggers escalation>"
```

Plus human-readable narrative with decision tree explaining reasoning.

**Verification gate:** Confirm diagnosis connects to symptoms via evidence. If diagnosis is unconfirmed (low confidence), do NOT proceed to mitigation — escalate instead.

### Step 3: Define Mitigation Steps

**WHAT:** Define specific mitigation actions that target the diagnosed root cause.

**WHY:** Mitigation steps must address the diagnosed root cause, not just suppress symptoms. Each step must explain why this action resolves the root cause, and what risk it carries.

Output — AI-parseable enforcement block:

```yaml
mitigation:
  - step: "<mitigation action>"
    targets_root_cause: "<reference to diagnosis entry>"
    risk_level: low | medium | high
    rollback: "<rollback procedure if mitigation fails>"
    reasoning: "<why this action addresses the root cause>"
```

Plus human-readable narrative with decision trees for conditional mitigation paths.

**Verification gate:** Confirm each mitigation step targets a diagnosed root cause. If mitigation does not address the root cause, return to Step 2.

### Step 4: Define Verification Criteria

**WHAT:** Define specific, measurable criteria that confirm the mitigation resolved the symptoms.

**WHY:** Verification must confirm symptoms are resolved, not just that something changed. Each criterion must map to a specific symptom from Step 1 and confirm it is no longer present.

Output — AI-parseable enforcement block:

```yaml
verification:
  - criterion: "<what to verify>"
    expected_result: "<expected outcome>"
    maps_to_symptom: "<reference to symptom from Step 1>"
    pass_condition: "<exact condition for pass>"
    fail_action: "<what to do if verification fails>"
```

Plus human-readable narrative explaining verification methodology.

**Verification gate:** Confirm each criterion maps to a symptom. If verification fails, return to Step 2 (re-diagnose) — do NOT proceed to postmortem.

### Step 5: Postmortem Template

**WHAT:** Generate a postmortem template capturing what happened, why, and how to prevent recurrence.

**WHY:** Postmortems close the feedback loop. Without postmortems, the same incident recurs. The template must capture causal reasoning, not just timelines.

Output — AI-parseable enforcement block:

```yaml
postmortem:
  incident_title: "<title>"
  severity: P1 | P2 | P3
  duration: "<time from detection to resolution>"
  root_cause_category: "<configuration | dependency | capacity | code | security>"
  contributing_factors:
    - "<factor with reasoning>"
  action_items:
    - action: "<preventive action>"
      owner: "<role or team>"
      reasoning: "<why this prevents recurrence>"
```

Plus human-readable narrative with timeline template and action item tracking.

## HALT Conditions

| Condition | Action |
|-----------|--------|
| Domain context missing or insufficient | HALT, prompt user for context |
| Diagnosis unconfirmed (low confidence) | HALT, escalate — do NOT mitigate |
| Mitigation risk exceeds severity threshold | HALT, escalate before proceeding |
| Verification fails | Return to Step 2, do NOT proceed to postmortem |
| Escalation needed | HALT, create GitHub Issue with `escalation` label |

## Output Contract

The generated runbook is saved as a Markdown file in `docs/runbooks/` with both:
1. AI-parseable yaml+symbolic enforcement blocks (structured data for automation)
2. Human-readable narrative prose (context and reasoning for humans)

File naming convention: `docs/runbooks/<domain>-<scenario_type>.md`

## Self-Review Step (MANDATORY)

After generating the runbook, the agent MUST review its own output for template-fill patterns. Check:
1. Does every step include WHY reasoning? If not, add it.
2. Does every diagnosis connect to symptoms via evidence? If not, add evidence chains.
3. Does every mitigation target a diagnosed root cause? If not, add reasoning.
4. Does every verification criterion map to a specific symptom? If not, add mappings.
5. Does the postmortem template include action items with reasoning? If not, add reasoning.

If any step lacks reasoning, the runbook is incomplete. Add reasoning before presenting.

## Context Required

- Related skills: `sre-runbook` (parent skill), `systematic-debugging` (root cause discipline), `verification-before-completion` (evidence gates)
- Related tasks: `track`