# Task: track

## Purpose

Track an incident or change via GitHub Issue with structured labels and prose narrative. Lightweight incident tracking for two-person teams — no CABs, no SLA databases, no change advisory boards.

## Operating Protocol

1. Invoked by: `/skill sre-runbook --task track`
2. When to use: When tracking an incident, outage, or change through its lifecycle
3. Exit criteria: GitHub Issue created/updated with structured labels and prose narrative

## Pre-Conditions

**A runbook must exist OR the user must provide an incident description.** If neither is available, the agent MUST prompt the user before proceeding.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `incident_type` | ✅ Yes | One of: `incident`, `change`, `degradation` |
| `severity` | ✅ Yes | One of: `P1` (outage), `P2` (degraded), `P3` (minor) |
| `description` | ✅ Yes | Prose description of the incident or change |

If parameters are missing, HALT and prompt the user. Do NOT guess severity or type.

## Input Parameters

```
incident_type: incident | change | degradation
severity: P1 | P2 | P3
description: <prose description of what happened or what changed>
```

## Procedure

### Step 1: Classify the Incident

**WHAT:** Determine incident type and severity from user input and observed evidence.

**WHY:** Classification drives the escalation path, label set, and response urgency. Misclassification leads to wrong response speed or wrong audience.

Classification rubric:

| Incident Type | When to Use | Label |
|---------------|-------------|-------|
| `incident` | Active outage or service disruption | `incident` |
| `change` | Planned or completed infrastructure change | `change` |
| `degradation` | Performance degradation without full outage | `degradation` |

Severity rubric:

| Severity | Definition | Response Target |
|----------|------------|-----------------|
| P1 | Complete outage or data loss risk | Immediate |
| P2 | Degraded performance or partial failure | Within 1 hour |
| P3 | Minor impact, non-blocking | Next business day |

Output:
- `incident_type` label
- `severity` label
- Classification reasoning (WHY this type and severity)

### Step 2: Create GitHub Issue

**WHAT:** Create a GitHub Issue with structured labels and prose narrative body.

**WHY:** GitHub Issues provide the single source of truth for incident tracking. Structured labels enable filtering; prose narrative provides context for humans.

**Follow `issue-operations` skill discipline** — do NOT bypass issue creation validation. Invoke `/skill issue-operations --task pre-creation` before creating the issue.

Issue structure:

```markdown
## Incident Tracking: <title>

**Type:** <incident_type>
**Severity:** P1 | P2 | P3
**Status:** investigating | mitigating | resolved | postmortem

### Timeline

| Time | Event | Reasoning |
|------|-------|-----------|
| <timestamp> | <event description> | <WHY this matters> |

### Classification Reasoning

<Why this incident type and severity were chosen>

### Impact

<What is affected and how>

### Mitigation Steps (if applicable)

<Steps taken or planned, with reasoning for each>

### Verification

<How we confirm the incident is resolved>

### Postmortem Link (if applicable)

<Link to postmortem issue when available>
```

Label set:
- Always: `incident` or `change` or `degradation`
- Always: `P1` or `P2` or `P3`
- Optionally: `escalation` (if escalation threshold reached)

### Step 3: Update Timeline Entries

**WHAT:** As the incident progresses, add timeline entries to the GitHub Issue body.

**WHY:** Timeline entries create the audit trail. Without them, postmortems lack data. Each entry must include reasoning — not just what happened, but why it matters.

**Update workflow:**
1. Read current issue body via `github_issue_read`
2. Add new timeline entry with timestamp, event, and reasoning
3. Update status field if changed
4. Update issue via `github_issue_write`

**Each timeline entry MUST include:**
- Timestamp (or relative marker if exact time unknown)
- Event description (WHAT)
- Reasoning (WHY this event matters or why this action was taken)

### Step 4: Escalation Criteria

**WHAT:** Determine when to escalate based on severity thresholds and time thresholds.

**WHY:** Escalation prevents incidents from lingering without adequate response. Clear criteria remove ambiguity about when and how to escalate.

Escalation thresholds:

| Severity | Escalate If | Action |
|----------|-------------|--------|
| P1 | Not mitigated within 30 minutes | Add `escalation` label, notify on-call lead |
| P2 | Not mitigated within 2 hours | Add `escalation` label, notify on-call |
| P3 | Not resolved within 1 business day | Reassess severity, consider upgrading |

When escalation threshold is reached:
1. Add `escalation` label to the issue
2. Add timeline entry noting escalation and reasoning
3. HALT runbook tracking — escalation requires human decision

### Step 5: Change Tracking (for `change` type only)

**WHAT:** Document what changed, the risk level, and the rollback plan.

**WHY:** Changes without rollback plans are incidents waiting to happen. Every change MUST have a rollback plan documented before execution.

Required fields for change tracking:

```yaml
change:
  what_changed: "<description>"
  risk_level: low | medium | high
  rollback_plan: "<steps to revert the change>"
  reasoning: "<why this change is necessary>"
```

### Step 6: Close with Postmortem

**WHAT:** When the incident is resolved, add postmortem link and close.

**WHY:** Closing without postmortem documentation means the same incident recurs. Every P1 and P2 incident must have a postmortem. P3 incidents may close with a brief retrospective.

**After generating postmortem (via `generate` task or manually):**
1. Add postmortem link to tracking issue
2. Update status to `resolved` or `postmortem`
3. If postmortem action items exist, create follow-up issues
4. Close the tracking issue only after postmortem is complete

**Do NOT close issues before postmortem for P1/P2 incidents.** See `git-workflow --task cleanup` for post-merge closure workflow.

**⚠️ Body-Preservation Safeguard:** When updating timeline entries in Step 3, the update workflow reads the current issue body, adds the new timeline entry, and updates via `github_issue_write(method=update, body=...)`. This MUST verify that the new body preserves all original content. The new body should be LONGER than the original (adding a timeline entry), not shorter. If `len(new_body) < 0.8 * len(original_body)`, HALT — this indicates content erasure. NEVER replace an issue body with a status summary. See `000-critical-rules.md` → "Critical Violation: Issue Body Erasure" for the project-wide rule.

## HALT Conditions

| Condition | Action |
|-----------|--------|
| Missing incident description | HALT, prompt user for context |
| Unable to classify incident type | HALT, present options to user |
| Escalation threshold reached | HALT, add `escalation` label, notify on-call |
| GitHub Issue creation validation fails | HALT, follow `issue-operations` skill guidance |

## Output

A GitHub Issue with:
- Structured labels: `<incident_type>` + `<severity>` + optionally `escalation`
- Prose narrative body following the template above
- Timeline entries with reasoning at every step
- Linked postmortem (for P1/P2 incidents)

## Cross-References

- Related skills: `sre-runbook` (parent skill), `issue-operations` (issue creation discipline), `verification-before-completion` (evidence gates)
- Related tasks: `generate`

## Context Required

- Related guidelines: `010-approval-gate.md` (authorization), `000-critical-rules.md` (issue closure rules)