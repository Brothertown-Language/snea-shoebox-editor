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

For each component/change:
| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|

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

## Output Format

```
## Risk Assessment

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|

### Blast Radius: <high-risk component>
- Failure impact: <what breaks>
- Propagation: <how far it spreads>
- Rollback: <recovery strategy>

## Operational Requirements
- Logging: <requirements>
- Metrics: <requirements>
- Alerts: <requirements>
- Deployment: <requirements>
- Data migration: <requirements>
```

## Context Required

- Preceded by: `requirements`, optionally `decompose`
- Feeds into: `write`
- Note: Creation-time operational requirements are enforced here. `spec-auditor` verifies completeness as a second pass.