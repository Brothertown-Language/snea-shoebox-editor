# Task: generate

## Purpose

Generate an operational runbook for a given domain and scenario type. The runbook is a step-by-step "do this, in this order" procedure — not an analysis document. Every command is verified against live documentation. Every value comes from the actual environment.

## Operating Protocol

1. Invoked by: `/skill sre-runbook --task generate`
2. When to use: When an operational runbook is needed for a system, service, or infrastructure domain
3. Exit criteria: Runbook generated with environment-verified instructions at every step, validated against all enforcement rules

## Pre-Conditions

**Domain context AND environment context are MANDATORY.** If any of the following are missing, the agent MUST prompt the user before proceeding:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `domain` | ✅ Yes | System/service name (e.g., "PostgreSQL primary", "Kubernetes ingress") |
| `runbook_type` | ✅ Yes | One of: `one-off-config`, `periodic-procedure`, `troubleshooting`, `incident-response` |
| `severity` | ✅ Yes for troubleshooting/incident-response | One of: `P1` (outage), `P2` (degraded), `P3` (minor). Not required for one-off-config/periodic-procedure. |
| `interface_preference` | ✅ Yes | One of: `gui`, `cli`, `mixed` — determines which instructions go in the runbook |
| `environment_os` | ✅ Yes | OS name and version (e.g., "Proxmox 8.1", "Windows Server 2022", "Ubuntu 24.04") |
| `available_tools` | ✅ Yes | Tools/package managers confirmed installed (e.g., "apt, systemctl, qm", or "PowerShell, DNS Manager") |

If domain OR environment context is missing or insufficient, HALT and prompt the user. Do NOT guess or fabricate context.

If `runbook_type` is not provided, classify it:
- **one-off-config**: The request is to apply a known configuration (DNS records, SSL cert, user provisioning). Default if type is unclear.
- **periodic-procedure**: The request is for a scheduled/recurring task (backup rotation, log rotation, cert renewal).
- **troubleshooting**: The request is to diagnose an unknown problem from symptoms ("site is down", "getting 500s").
- **incident-response**: The request involves an active outage requiring rapid mitigation and postmortem.

When in doubt, default to `one-off-config`.

## Input Parameters

```
domain: <system or service name>
runbook_type: one-off-config | periodic-procedure | troubleshooting | incident-response
severity: P1 | P2 | P3  (required for troubleshooting/incident-response only)
interface_preference: gui | cli | mixed
environment_os: <OS name and version>
available_tools: <comma-separated list of confirmed-available tools>
```

## Type-Aware Format Dispatch

The runbook type determines the output format. The generate task MUST select format before producing any content:

| `runbook_type` | Output Format | YAML Blocks? | Applies Dual-Output Contract? |
|----------------|--------------|-------------|-------------------------------|
| `one-off-config` | Steps-only | No | No |
| `periodic-procedure` | Steps-only | No | No |
| `troubleshooting` | Dual-output | Yes | Yes |
| `incident-response` | Dual-output | Yes | Yes |

### Steps-Only Format (one-off-config and periodic-procedure)

For configuration changes and scheduled procedures, the operator needs "just do the job" instructions. No symptom catalogs, no diagnosis maps, no postmortem templates.

**Steps-only output contract:**

1. **Metadata header** — Plain text header (NOT YAML):
   ```
   Domain: <domain>
   Provider: <provider>
   Date: <date>
   Source: <where this information came from>
   Runbook type: one-off-config | periodic-procedure
   Last verified: Verified against <product> <version> on <date>
   ```

2. **Prerequisites** — Log in, navigate, open elevated session.

3. **Numbered steps with verification** — Each step includes exact field values and a verify command:
   ```
   3. Add A record:
      - Type: A
      - Name: @
      - Value: 192.0.2.1
      - TTL: 3600
      Verify: dig @ns1.directnic.com videoconcerthall.com A +short
   ```

4. **Reference table** — All records/fields consolidated in one place for quick lookup.

5. **Verification script** — One command to check everything:
   ```
   dig @ns1.directnic.com videoconcerthall.com ANY +noall +answer
   ```

6. **Troubleshooting table** — If X fails, do Y:
   ```
   | Symptom | Likely Cause | Fix |
   |---------|-------------|-----|
   | Record not resolving | TTL not expired | Wait for TTL, then re-verify |
   ```

### Format-Matching Step (MANDATORY BEFORE GENERATION)

Before generating any runbook content:

1. Search the repository for existing runbooks: `glob(pattern="docs/runbooks/**/*.md")`
2. If sibling repos are accessible, search those too
3. If existing runbooks exist, examine their format:
   - Do they use YAML enforcement blocks? → match dual-output format
   - Do they use steps-only numbered format? → match steps-only format
   - Is there a proven format from operator feedback? → match that format
4. If existing runbooks use steps-only format and the runbook_type is `one-off-config` or `periodic-procedure`, use steps-only format
5. If no existing runbooks exist, use the format dictated by `runbook_type`

**The format-matching rule OVERRIDES the type-based default when existing proven formats exist.**

## Procedure

### Pre-Step: Verification Gate (MANDATORY FIRST)

Before collecting environment context or writing any runbook content, invoke `verification-enforcement --task verify`. This gate dispatches section-based sub-agents to collect evidence artifacts for the factual claims the runbook will make — CLI commands, GUI paths, configuration values, and system behavior assertions. Evidence artifacts collected here inform every subsequent step. Claims that cannot be verified at this stage are marked with `⚠️ UNVERIFIED` for resolution in the post-generation revisit pass.

### Step 0: Collect Environment Context (MANDATORY FIRST)

**WHAT:** Determine the operator's interface preference, available tools, OS version, and existing documentation before writing any instructions.

**WHY:** Runbooks generated without environment context prescribe CLI commands for GUI operators, reference tools that aren't installed, and invent paths from training data. Environment context determines WHICH instructions are correct, WHETHER they are still valid, and whether the operator can trust them.

**Check-repo-first:** Before prompting the user for any environment value, check existing documentation in the repository:

```
1. Search for IP addresses, hostlists, system reference tables in docs/ or src/docs/
2. Search for existing runbooks in docs/runbooks/ that reference the same domain
3. If environment values (hostnames, IPs, domains, versions) exist in repo docs, USE THEM — never prompt for values already documented
```

If environment context cannot be determined from the repository, prompt the user:

| Parameter | How to Collect | If Unavailable |
|-----------|---------------|----------------|
| `interface_preference` | Ask: "Do you prefer GUI or CLI for operating [domain]?" | HALT — cannot determine correct instruction path |
| `environment_os` | Ask: "What OS/version is [domain] running on?" | HALT — commands may differ across versions |
| `available_tools` | Ask: "Which tools/managers are installed on [domain]?" | HALT — cannot verify command availability |
| `hostnames/IPs/domains` | Check repo docs first; if absent, ask user | Use values from conversation — NEVER fabricate |

**Evidence anchoring:** Run or request baseline state collection commands:

```
For each relevant system query:
  1. Attempt to run the query directly (if environment is accessible)
  2. If not accessible: ask the user to run the command and supply output
  3. If neither is possible: HALT — do NOT write instructions based on assumed state
  4. Include the baseline output in the runbook under "Current State Baseline"
```

**Version pinning:** Record all version information observed or confirmed:

```yaml
environment:
  os: "<OS name and version>"
  software_versions:
    - name: "<software name>"
      version: "<version observed>"
  verified_at: "<ISO date>"
  interface: gui | cli | mixed
  tools_available:
    - "<tool name>"
```

**Verification gate:** Confirm ALL environment context parameters are collected. If any are missing, HALT and prompt the user. Do NOT proceed with incomplete context.

### Step 1: Document Symptoms

**WHAT:** Catalog all observed symptoms with severity and affected components.

**WHY:** Symptom documentation is the foundation of diagnosis. Without a complete symptom catalog, diagnosis is guesswork.

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

Plus operational observations (what the operator sees, not explanations of why).

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

**Verification gate:** Confirm diagnosis connects to symptoms via evidence. If diagnosis is unconfirmed (low confidence), do NOT proceed to mitigation — escalate instead.

### Step 3: Define Mitigation Steps

**WHAT:** Define specific mitigation actions that target the diagnosed root cause. ONE path per step. Steps only — no explanations, no conditional flows.

**WHY:** Runbooks are operational procedures. A sysop under pressure needs "do this" instructions, not decision trees.

**Single-path enforcement:** For each mitigation action, include exactly ONE method:

- If `interface_preference` is `gui`: provide GUI steps only (click this, navigate there)
- If `interface_preference` is `cli`: provide CLI commands only
- If `interface_preference` is `mixed`: provide the operator's preferred interface; CLI only when no GUI equivalent exists
- NEVER present "or via CLI" alternatives alongside GUI steps
- NEVER present "or via GUI" alternatives alongside CLI steps

**Prerequisites-first:** If any command requires elevated privileges:

```
## Prerequisites

1. Open elevated PowerShell (right-click → Run as Administrator)

## Mitigation Steps

1. Set-MaxCacheTtl ...
```

NOT:

```
1. Set-MaxCacheTtl ...  (requires admin)
```

**Minimum-necessary:** Include ONLY the settings/parameters that directly solve the diagnosed problem. Do NOT include:
- Related-but-irrelevant settings from the same subsystem
- "Recommended" values for parameters not causing the issue
- Additional parameters "just in case"

**Set-and-restore pattern:** Structure commands as exactly two blocks:

```
## Apply Fix

1. <command to set the specific value>

## Restore Defaults (if needed)

1. <command to restore the original value>
```

NOT:

```
## Check Current Value

1. <command to query>  ← REMOVED — if we're going to overwrite, pre-checking is unnecessary
2. <command to set>
3. <command to verify>
4. <command to reset if needed>
```

Output — AI-parseable enforcement block:

```yaml
mitigation:
  - step: "<mitigation action>"
    targets_root_cause: "<reference to diagnosis entry>"
    risk_level: low | medium | high
    rollback: "<restore-defaults command>"
    interface: gui | cli
```

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

**Verification gate:** Confirm each criterion maps to a symptom. If verification fails, return to Step 2 (re-diagnose) — do NOT proceed to postmortem.

### Step 5: Postmortem Template

**WHAT:** Generate a postmortem template capturing what happened, why, and how to prevent recurrence.

**WHY:** Postmortems close the feedback loop. Without postmortems, the same incident recurs.

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
```

## Live Verification Requirements (MANDATORY)

**Every command, GUI path, button label, menu structure, and API call in the runbook MUST be verified against a live source before inclusion.**

### Verification Sources (in priority order)

| Source | How | When Required |
|--------|-----|---------------|
| Live system query | Run the command directly or ask user to supply output | ALL CLI commands |
| `--help` output | Run `<command> --help` and verify flags/syntax exist | ALL CLI commands |
| `man` page | Run `man <command>` and verify parameters | When `--help` unavailable |
| Official vendor documentation | Fetch from vendor docs URL | ALL GUI paths, API calls, settings |
| Existing runbooks in repo | Check `docs/runbooks/` for verified commands | As reference/cross-check |

### Verification Procedure

For each CLI command in the runbook:

```
1. Run `<command> --help` or `man <command>`
2. Verify every flag and parameter exists in the help output
3. If a flag/parameter does NOT appear in help output → EXCLUDE it, do NOT annotate "(unverified)"
4. Record the verification source in the runbook metadata
```

For each GUI path in the runbook:

```
1. Verify the path against official vendor documentation
2. If no vendor documentation confirms the path → EXCLUDE it
3. NEVER invent GUI paths, button labels, or menu structures from training data
4. If only a CLI exists for a setting, state that explicitly: "No GUI available — CLI only"
```

### Evidence Collection Failure Handling

**If the agent cannot verify a command or path against a live source:**

1. Do NOT include the unverified command/path in the runbook
2. Do NOT annotate it as "(unverified)" — unverified information is excluded
3. HALT and inform the user: "I cannot verify [command/path] against live documentation. Please run `[command] --help` and supply the output, or confirm the correct syntax."
4. Do NOT silently fall back to training knowledge — this is the worst-case scenario that produces confident-sounding wrong instructions

## HALT Conditions

| Condition | Action |
|-----------|--------|
| Environment context missing or insufficient | HALT, prompt user for context |
| Domain context missing or insufficient | HALT, prompt user for context |
| Runbook type unclear and cannot be classified | Default to one-off-config (steps-only) |
| Diagnosis unconfirmed (low confidence) — troubleshooting/incident-response only | HALT, escalate — do NOT mitigate |
| Mitigation risk exceeds severity threshold — troubleshooting/incident-response only | HALT, escalate before proceeding |
| Verification fails — troubleshooting/incident-response only | Return to Step 2, do NOT proceed to postmortem |
| Escalation needed | HALT, create GitHub Issue with `escalation` label |
| Evidence collection fails (cannot verify command against live source) | HALT, prompt user for confirmation or output — do NOT fall back to training knowledge |
| Live documentation unavailable | HALT, inform user — do NOT generate instructions from training data |

## Output Contract

The output contract depends on the runbook type:

### Steps-Only Output (one-off-config and periodic-procedure)

File naming convention: `docs/runbooks/<domain>-<scenario>.md`

The generated runbook is saved as a Markdown file with:

1. **Metadata header** — plain text (domain, provider, date, source, runbook type, last verified)
2. **Prerequisites** — log in, navigate, open elevated session
3. **Numbered steps with verification** — each step has exact field values and a verify command after each step
4. **Reference table** — all records/fields in one place for quick lookup
5. **Verification script** — one command to check everything at once
6. **Troubleshooting table** — if X fails, do Y

**No YAML enforcement blocks.** No symptom catalog. No diagnosis map. No postmortem template. The operator needs to "just do the job."

### Dual-Output (troubleshooting and incident-response)

File naming convention: `docs/runbooks/<domain>-<scenario_type>.md`

The generated runbook is saved as a Markdown file with:

1. **Environment header** — verified environment context block:
   ```yaml
   environment:
     os: "<os and version>"
     interface: gui | cli | mixed
     tools: ["<confirmed tool list>"]
     verified_at: "<ISO date>"
     last_verified: "Verified against <product> <version> on <date>"
   ```

2. **Current state baseline** — evidence anchoring with actual outputs
3. **AI-parseable yaml+symbolic enforcement blocks** (structured data for automation)
4. **Operational procedures** — numbered steps with copy-paste commands
5. **Restore defaults** — rollback commands
6. **Verification commands** — confirm fix applied
7. **Postmortem template** (incident-response only) — timeline and action items

File naming convention: `docs/runbooks/<domain>-<scenario_type>.md`

## Self-Review Step (MANDATORY — Before Presenting)

After generating the runbook, the agent MUST validate the output against ALL enforcement rules. One-shot correctness is the target.

### Validation Checklist

1. ✅ Runbook type classified (one-off-config, periodic-procedure, troubleshooting, incident-response)?
2. ✅ Format-matching rule applied (existing runbooks in repo checked for format)?
3. ✅ For one-off-config/periodic-procedure: steps-only format with NO YAML blocks?
4. ✅ For troubleshooting/incident-response: dual-output format with YAML enforcement blocks?
5. ✅ Environment context collected and documented?
6. ✅ Single path per operation (no "or via CLI" alternatives)?
7. ✅ Only confirmed-available tools referenced?
8. ✅ Real values from environment (zero generic placeholders)?
9. ✅ Prerequisites (elevation) before privileged commands?
10. ✅ Steps only — no explanations, no conditional flows?
11. ✅ Minimum-necessary settings only?
12. ✅ Set-and-restore pattern (two command blocks)?
13. ✅ No content re-added after removal?
14. ✅ Every CLI command verified against `--help`/`man`/live docs?
15. ✅ Every GUI path verified against vendor docs?
16. ✅ Evidence anchoring with baseline outputs?
17. ✅ Version/environment pinning included?
18. ✅ "Last verified" timestamp included?
19. ✅ Existing repo documentation checked for hostnames/IPs/domains?
20. ✅ No training-knowledge commands presented as verified?
21. ✅ Evidence collection failure handled (HALT, not fallback)?
22. ✅ Verification-failure gate passed for EVERY section with operational steps? (If ALL sources failed for any section, was the section blocked and user prompted?)
23. ✅ DNS record types validated against RFC constraints and provider capabilities? (If DNS runbook: no CNAME at apex, no unsupported record types)
24. ✅ VERIFICATION-GAP annotations explicit (provider name, claims unconfirmed, sources attempted)?
25. ✅ For steps-only: reference table and troubleshooting table included?
26. ✅ For steps-only: each step has exact field values and verify command?
27. ✅ For steps-only: metadata header is plain text, NOT YAML?
28. ✅ Communication scope correct? Status communications include full narrative context (cause, attribution, what was wrong, what was corrected, before/after for each affected component, current state, references) — NOT steps-only format applied outside operational procedures?
29. ✅ AI byline present on all agent-generated communications (email replies, notifications, stakeholder updates)?
30. ✅ Byline present in BOTH plain-text and HTML sections of dual-format communications?
31. ✅ Byline not removed on subsequent edits of agent-generated communications?
32. ✅ Byline semantics correct? "on behalf of <dev.name>" or "copy editor for <dev.name>" when user provided direct message/instructions; bare `<AgentName> (<ModelId>)` when agent authored the communication?

If ANY check fails, fix the runbook before presenting. The user should never need to correct the same issue twice.

### Post-Self-Review: Verification Revisit (MANDATORY)

After the self-review step, invoke `verification-enforcement --task revisit`. This pass scans the generated runbook for any remaining `⚠️ UNVERIFIED` markers and attempts to resolve them using domain-appropriate tools. Claims that cannot be resolved are escalated to the developer. The runbook must not ship as complete while unverified claims remain without developer acknowledgment.

### Verification-Failure Gate: Runbook-Section Blocking (MANDATORY)

**🚫 CRITICAL: Before presenting any section containing operational steps, verify that at least ONE live source confirmed the claims in that section. If ALL sources failed, the section MUST be blocked.**

For each section with operational steps:

```
1. Count verification attempts and results for that section's claims
2. If AT LEAST ONE source confirmed → proceed (note source in evidence block)
3. If ALL sources failed or were unreachable:
   a. Replace the section's operational steps with a VERIFICATION-GAP block:
      "VERIFICATION-GAP: <provider> documentation unreachable — <claims> unconfirmed.
       Please confirm: (a) <first unverified claim>, (b) <second unverified claim>"
   b. Do NOT present the unverified instructions as operational steps
   c. Record the gap in the runbook metadata:
      verification_gaps:
        - section: "<section name>"
          provider: "<provider>"
          claims_unconfirmed: ["<claim 1>", "<claim 2>"]
          sources_attempted:
            - source: "<URL or tool>"
              result: "<error>"
          user_action_required: true
```

### DNS Record Validation Gate (MANDATORY for DNS runbooks)

Before writing ANY DNS record instructions, validate:

```
1. Check reference/ directory for provider-specific DNS constraint data
   - If reference data exists AND confirms the proposed record type → proceed
   - If reference data exists AND contradicts the proposed record type → adjust the record type
   - If no reference data exists → HALT and request provider DNS details from user

2. Apply RFC-level DNS constraints (hard rules, non-negotiable):
   a. CNAME at zone apex → FORBIDDEN (RFC 1034). Use ALIAS/ANAME or A record.
   b. CNAME with other records at same name → FORBIDDEN (RFC 1034). CNAME must be the only record type at a name.

3. Flag provider-level fragility (soft warnings, proceed with annotation):
   a. A record to third-party IP → flag as FRAGILE with explanation
   b. Provider defects reported by user → include as KNOWN-DEFECT annotation
```

If DNS validation fails (RFC-level constraint violated), HALT and correct the record type before proceeding. If provider capabilities are unconfirmed, HALT and prompt user.

### Prose-Structure Check Note

Non-operational sections of the generated runbook — the environment header, symptom descriptions, diagnosis reasoning, and postmortem narrative — should remain prose. These sections communicate context and reasoning; rigid enumeration or tabular structure in them reduces readability. Operational steps (numbered commands, mitigation actions, verification commands) are naturally structured and exempt from the prose check. When a section mixes operational commands with surrounding reasoning, the reasoning stays prose while the commands stay structured.

## Context Required

- Related skills: `sre-runbook` (parent skill), `systematic-debugging` (root cause discipline), `verification-before-completion` (evidence gates)
- Related tasks: `track`