# Task: risk

## Purpose

Analyze risk, blast radius, failure propagation, and operational requirements (logging, metrics, alerts, deployment).

## Entry Criteria

- Requirements extraction completed
- (Recommended) Decomposition completed for interface-level risk analysis

## Exit Criteria

- Risk assessment with severity and probability
- Blast radius analysis for high-risk components
- Operational requirements documented
- Mitigation strategies identified

## Procedure

### Step 1: Risk Assessment

For each component/change, assess:
- What risks exist (technical, integration, data, security)
- Severity of each risk (low/medium/high/critical)
- Probability of each risk occurring
- Mitigation strategy for each risk

### Step 2: Blast Radius Analysis

For high-risk components (severity HIGH or CRITICAL):
- If this component fails, what breaks?
- How far does the failure propagate?
- What is the rollback strategy?

### Step 3: Failure Propagation Map

Identify cascading failures:
- Component A fails → Components B, C affected
- Component B fails → Components D, E affected
- Where are the circuit breakers?

### Step 4: Operational Requirements

Document operational needs:
- **Logging:** What to log, at what level, structured or unstructured
- **Metrics:** What to measure, aggregation strategy
- **Alerts:** When to alert, threshold configuration
- **Deployment:** Rollout strategy, blue/green, canary, feature flags
- **Data migration:** Schema changes, data transformation, rollback

## Content Coverage

Does the risk assessment cover:
- Severity and probability for each risk?
- Blast radius for high-risk components (what breaks, how far it spreads, rollback strategy)?
- Failure propagation paths?
- Operational requirements (logging, metrics, alerts, deployment)?

**Any format that communicates these concerns effectively is acceptable.** Formal risk tables with severity/probability matrices work well for complex specs. Prose descriptions work well for simple specs with few risks. The agent chooses the format that best serves the spec.

## Context Required

- Preceded by: `requirements`, optionally `decompose`
- Feeds into: `write`
- Note: Creation-time operational requirements are enforced here. `spec-auditor` verifies completeness as a second pass.