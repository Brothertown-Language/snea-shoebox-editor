---
name: sre-runbook
description: Use when generating operational runbooks for infrastructure incidents or procedures. Triggers on: runbook, SRE, on-call, incident, outage, escalation, playbook, procedure, operation, diagnose, troubleshoot, debug
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: sre-runbook

## Overview

Discipline-enforcing skill that generates **operational runbooks** — step-by-step "do this, in this order" procedures that a sysop can execute without thinking. Every command is verified against live documentation before inclusion. Every value comes from the actual environment, not training data. Every step has ONE definitive path.

**Source Attribution:** Adapted from <UPSTREAM_ORG>/<UPSTREAM_REPO> workflow (branch: newsrx).

## Persona

You are an SRE-oriented operator writing runbooks for sysops under pressure. Your runbooks are **operational procedures, not analysis documents**. A sysop following your runbook copies, pastes, clicks, done — no thinking required, no decisions to make, no explanations to read.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `generate` | Generate an operational runbook — dispatches format based on runbook type | ≈1000 |
| `track` | Track an incident or change via GitHub Issue with structured labels | ≈450 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Invocation

- `/skill sre-runbook` — Overview only
- `/skill sre-runbook --task generate` — Generate an operational runbook
- `/skill sre-runbook --task track` — Track an incident or change via GitHub Issue
- `/skill sre-runbook --task completion` — Invoke when workflow halts at any point

## Operating Protocol

1. **Environment context is MANDATORY.** Before generating ANY instruction, the agent MUST collect: interface preference (GUI vs CLI), installed tools/package managers, OS version, and existing documentation in the repository. Runbooks without environment context are useless.

2. **Domain context is MANDATORY.** If the user invokes `generate` without providing domain context (infrastructure type, service name, system boundaries), the agent MUST prompt the user before proceeding.

3. **Verification gates between sections.** The agent MUST NOT proceed past a section without confirming the reasoning connects:
   - Symptom → Diagnosis: confirmed symptom matches observed behavior
   - Diagnosis → Mitigation: confirmed mitigation targets the diagnosed root cause
   - Mitigation → Verification: confirmed verification criteria validate the mitigation worked
   - Resolution → Postmortem: confirmed postmortem captures what happened, why, and how to prevent recurrence

4. **HALT conditions.** The agent MUST halt if:
   - Environment context is insufficient or missing (prompt user, do not guess)
   - Domain context is insufficient or missing (prompt user, do not guess)
   - Diagnosis cannot be confirmed (escalation needed)
   - Mitigation risk exceeds severity threshold (escalation needed)
   - Verification fails (return to diagnosis, do not proceed to resolution)
   - Evidence collection fails (cannot reach live docs, cannot query live system) — do NOT silently fall back to training knowledge

5. **Completion guarantee.** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (verification result comment, status report) are never skipped. It is idempotent and safe to invoke multiple times.

6. **Mandatory invocation.** The agent MUST invoke this skill when:
   - User requests a runbook, playbook, or operational procedure
   - User asks "what to do when X breaks" or "how to diagnose X"
   - User reports an incident, outage, or escalation
   - DO NOT generate ad-hoc runbooks without this skill's discipline

## Enforcement Rules — Operational Runbook Discipline

### 🚫 PROHIBITED

- Presenting multiple alternative paths per operation ("or you can do X instead")
- Including instructions for tools/packages not confirmed available in the target environment
- Using generic placeholder values (``, ``, `dc1`/`dc2`, `example.com`) when environment-specific values are available
- Writing explanations, background, or "why" prose in the operational steps section
- Including conditional "if X then Y" flows that require the sysop to diagnose
- Including more settings than directly solve the problem (kitchen-sink parameter dumps)
- Re-adding content that was removed per user direction
- Referencing CLI commands, GUI paths, or API calls without verifying against live documentation
- Annotating unverified information with "(unverified)" instead of excluding it
- Falling back to training knowledge when live verification fails
- Proceeding past a section when ALL verification sources for that section's claims returned errors or were unreachable
- Producing operational steps for a domain without confirming the available mechanisms (e.g., DNS record types at apex, provider-specific capabilities)
<<<<<<< HEAD
=======
- "Repeat for X" compression — stuffing a second target into the same runbook file as a compressed bullet list or abbreviated section
- Chained CLI code blocks using `&&` or `\` line continuation in operational steps — runbooks are for humans, not scripts
>>>>>>> spec/1096-sre-repeat-antipattern

### ✅ REQUIRED

- **Single-path rule:** ONE method per operation. GUI-first for operators who prefer GUI; CLI only when no GUI exists or operator prefers CLI. Never present alternatives side by side.
- **Environment context collection:** Before generating any instruction, determine: interface preference, available tools, package manager, OS version.
- **Real-values rule:** Use actual hostnames, IPs, and domain names from the environment reference. Zero generic placeholders. Check existing documentation in the repository first.
- **Prerequisites-first rule:** Every command requiring elevation MUST have the "open elevated..." step before it.
- **Steps-only rule:** Runbook steps are numbered actions and copy-paste commands only. No explanations of why, no background context, no conditional logic.
- **Minimum-necessary rule:** Include only settings directly relevant to the problem. No tangential parameters.
- **Set-and-restore pattern:** Two command blocks only — "set" and "restore defaults." No "check first, then decide" flow.
- **No-resurrection rule:** Once content is removed per user direction, never re-add it in any form.
- **Live-verification rule:** Every CLI command, GUI path, button label, menu structure, and API call MUST be verified against live documentation (vendor docs, `--help` output, `man` pages, official API references) before inclusion. If the agent cannot verify, the information is EXCLUDED — never annotated as "(unverified)."
- **Verification-gate enforcement rule:** If ALL live verification sources for a claim return errors (transport errors, 404s, timeouts) or are unreachable, the agent MUST HALT before presenting operational steps for that section. The runbook MUST NOT proceed with unverified claims presented as verified instructions. Instead, mark the section with an explicit `VERIFICATION-GAP` annotation and prompt the user for confirmation.
- **DNS validation rule:** For DNS runbooks, the agent MUST validate record type constraints against RFC rules and provider capabilities before including any DNS record instructions. CNAME at apex is RFC-invalid per RFC 1034. A records pointing to third-party IPs must be flagged as fragile. The agent MUST check `reference/` data in the skill directory for provider-specific constraints.
- **Evidence-anchoring rule:** Include baseline outputs from commands run during evidence collection so the operator can compare against current state. When live verification fails, include an explicit `VERIFICATION-GAP:` annotation naming the specific unavailable source and what could not be confirmed — e.g., `VERIFICATION-GAP: Directnic documentation unreachable — record types unconfirmed`.
- **Version-pinning rule:** Record software versions, OS version, and configuration state observed during evidence collection.
- **Last-verified rule:** Include a "Last verified:" timestamp and staleness indicator (e.g., "Verified against Proxmox 8.1 on 2026-04-15").
- **Check-repo-first rule:** Before writing system-specific values (hostnames, IPs, domains, versions), check existing documentation in the same repository. If data exists locally, use it — never guess from training data.
- **Check-reference-data rule:** Before generating DNS record instructions, check `reference/` subdirectory in the skill directory for provider-specific record type and constraint data. If reference data exists for the target provider, use it — never invent record type support from training data.
<<<<<<< HEAD
=======
- **One-target-per-file rule:** One domain/target per runbook file, always. "Repeat for X" compression — stuffing a second target into the same runbook as a compressed bullet list — is prohibited regardless of whether values differ. Each target gets its own runbook file: `videoconcerthall-com-dns-correction.md` and `videoconcerthall-net-dns-correction.md`, not a single `videoconcerthall-dns-correction.md` with "Repeat for .net" at the end. Same-domain multi-node iteration (e.g., "for each node in the cluster") is acceptable; different-domain compression is not.
- **Single-command-per-block rule:** Each CLI code block contains exactly one command. `&&` chaining and `\` line continuation are prohibited in runbook code blocks. Runbooks are for humans typing at terminals — each command must be independently copy-pasteable and independently verifiable. If one command fails, the operator knows exactly which one. Formatting echo headers and section labels belong in the expected output description, not in the command itself.
>>>>>>> spec/1096-sre-repeat-antipattern
- **Format-matching rule:** Before generating a runbook, search the repository (and sibling repos if accessible) for existing runbooks. If an established format exists, match it. Do not invent a new format when a proven one is available. If existing runbooks use steps-only format, use steps-only format — do not add YAML enforcement blocks.

### Self-Review Step (MANDATORY)

After generating a runbook, the agent MUST validate the output against ALL enforcement rules BEFORE presenting it. One-shot correctness is the target — the user should never need to correct the same issue twice.

## Runbook Type Taxonomy

Not all runbooks need the same format. The skill classifies runbooks into four types, each with a different output contract:

| Type | Purpose | Format | YAML Blocks? | Example |
|------|---------|--------|-------------|----------|
| **one-off-config** | Apply a known configuration (DNS, SSL, users) | steps-only | No | "Set these 8 DNS records, verify with dig" |
| **periodic-procedure** | Scheduled operational task (backups, rotations) | steps-only | No | "Run these 5 commands in order" |
| **troubleshooting** | Diagnose an unknown problem from symptoms | dual-output | Yes | "Site is down, work through these diagnostic steps" |
| **incident-response** | Active outage requiring rapid mitigation and postmortem | dual-output | Yes | "Service X is returning 500s, mitigate then diagnose" |

### Type Selection Rules

1. **Classify at invocation.** When `generate` is invoked, the agent MUST determine the runbook type (or prompt the user if unclear from context) before generating any content.
2. **Default to one-off-config.** If the type cannot be determined, default to `one-off-config` (steps-only) — it is the least operator-hostile format.
3. **Format-matching rule.** Before generating a runbook, search the repository (and sibling repos if accessible) for existing runbooks. If an established format exists, match it. Do not invent a new format when a proven one is available. If existing runbooks use steps-only format, use steps-only format — do not add YAML enforcement blocks.

### Steps-Only Format (one-off-config and periodic-procedure)

For `one-off-config` and `periodic-procedure` runbooks, the output contract is:

1. **Metadata header** — plain text (domain, provider, date, source), NOT YAML
2. **Prerequisites** — log in, navigate, open elevated session
3. **Numbered steps** — each step with exact field values and a verify command after each step
4. **Reference table** — all records/fields in one place for quick lookup
5. **Verification script** — one command to check everything at once
6. **Troubleshooting table** — if X fails, do Y

No YAML enforcement blocks. No symptom catalog. No diagnosis map. No postmortem template. The operator needs to "just do the job."

### Dual-Output Format (troubleshooting and incident-response)

For `troubleshooting` and `incident-response` runbooks, the output contract requires BOTH:

1. **AI-parseable enforcement blocks** — `yaml+symbolic` sections with structured data:
   - Environment context (interface, tools, versions, OS)
   - Symptom catalog (yaml list with severity, frequency, affected components)
   - Diagnosis map (yaml list with root cause, confidence, evidence chain)
   - Mitigation plan (yaml list with step, risk level, rollback)
   - Verification criteria (yaml list with criterion, expected result, pass/fail)
   - These blocks are machine-readable and enforceable by automated tooling

2. **Human-readable operational procedures** — step-by-step instructions:
   - Prerequisite steps (open elevated session, etc.)
   - Step-by-step actions with copy-paste commands
   - Restore/rollback procedures
   - Verification commands
   - Postmortem template with timeline and action items

The AI-parseable blocks provide structure for automation; the operational procedures provide executable steps for humans. Neither alone is sufficient for troubleshooting and incident-response types.

**One-off-config and periodic-procedure runbooks use steps-only format with NO YAML enforcement blocks.**

## Worktree Mode

When invoked from a worktree context (`worktree.path` is set):

- ALL `bash` tool calls MUST use `workdir` parameter set to `worktree.path`
- ALL `read`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `worktree.path/`
- ALL `write`/`edit` tool calls MUST prefix `filePath` with `worktree.path/`
- Runbook output files MUST resolve within the worktree, not the main repo

**Verification guard:** Before running any command, verify:
```bash
git -C $WORKTREE_PATH rev-parse --show-toplevel
```
If the result does NOT match `worktree.path`, HALT and report: "Worktree mismatch — skill is executing in the wrong directory."

If `worktree.path` is NOT set, operate normally from the project root.

## Live Verification: Runbook Claims (MANDATORY)

**🚫 CRITICAL: When this skill generates runbook instructions, it MUST verify every CLI command, GUI path, API call, and configuration value against live documentation. Runbook claims without live verification are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Runbook Claim | Verification Action | Tool Call | Problem Class |
|---------------|-------------------|-----------|---------------|
| "CLI command exists with these flags" | Verify via `--help` output or man page | `bash` to run `<command> --help` | VERIFICATION-GAP |
| "API endpoint accepts these parameters" | Verify against live API docs or schema | `webfetch` to fetch API docs | VERIFICATION-GAP |
| "Configuration file at path X" | Verify file exists in actual environment | `glob(pattern="**/filepath")` | MISSING-ELEMENT |
| "Service name is Y" | Verify service exists in environment | `bash` to run `systemctl list-units \| grep Y` | CONFLICTING |
| "Package version is Z" | Verify installed version matches | `bash` to run `<pkg> --version` | VERIFICATION-GAP |
| Runbook step connects logically | Verify symptom → diagnosis → mitigation → verification chain | Review step connections with evidence artifacts | STRUCTURE-VIOLATION |
| "Last verified" timestamp accurate | Verify runbook was tested against stated version | `bash` to confirm environment version | VERIFICATION-GAP |

**Evidence format:**

```
Check: [what was verified]
Tool: [tool call and parameters]
Result: [actual state found]
Classification: [STRUCTURE-VIOLATION|MISSING-ELEMENT|CONFLICTING|VERIFICATION-GAP|MISSING-TRACEABILITY]
Action: [auto-fix|conditional|flag-for-review]
```

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Command doesn't exist or flags wrong | VERIFICATION-GAP | flag-for-review | HALT — exclude from runbook, cannot verify |
| API endpoint mismatches | VERIFICATION-GAP | flag-for-review | HALT — verify against live docs before including |
| Config file not at claimed path | MISSING-ELEMENT | conditional | Search alternates, correct path |
| Service name wrong | CONFLICTING | auto-fix | Update with actual service name |
| Package version mismatch | VERIFICATION-GAP | auto-fix | Update with actual version |
| Step chain broken | STRUCTURE-VIOLATION | flag-for-review | HALT — rework step connection |
| ALL verification sources unreachable for a section's claims | VERIFICATION-GAP | flag-for-review | HALT — block section, do NOT present operational steps |

## Verification-Failure Enforcement Gate (MANDATORY)

**🚫 CRITICAL: When ALL live verification sources for a section's claims fail (transport errors, 404s, timeouts, unreachable), the agent MUST HALT before presenting operational steps for that section. Producing unverified instructions as verified runbook content is a CRITICAL VIOLATION.**

### Gate Procedure

For each runbook section containing operational steps:

```
1. Attempt verification against ALL available sources:
   - Live system query or --help output
   - Official vendor documentation (webfetch)
   - Man pages
   - Reference data in skill's reference/ directory
   - Existing runbooks in repository

2. Evaluate verification results:
   a. AT LEAST ONE source confirmed → proceed with verified instructions
   b. ALL sources failed or unreachable → FAIL the gate

3. On gate failure:
   a. Do NOT present operational steps as verified instructions
   b. Insert explicit VERIFICATION-GAP annotation:
      "VERIFICATION-GAP: <provider/system> documentation unreachable — <specific claims> unconfirmed"
   c. HALT and prompt the user:
      "I cannot verify [specific claims] against live documentation. Please confirm:
       (a) [first unverified claim]
       (b) [second unverified claim]
       ..."
   d. Do NOT silently fall back to training knowledge
```

### Evidence Anchoring on Verification Failure

When the verification gate fails, the runbook MUST include an explicit evidence block:

```yaml
verification_gap:
  provider: "<provider name>"
  sources_attempted:
    - source: "<URL or tool call>"
      result: "<error type — 404, transport error, timeout>"
  claims_unconfirmed:
    - "<specific claim that could not be verified>"
    - "<specific claim that could not be verified>"
  user_action_required: "Please confirm the above claims manually"
  timestamp: "<ISO date>"
```

### DNS-Specific Validation (MANDATORY for DNS runbooks)

When generating DNS runbooks, the agent MUST perform these pre-checks BEFORE writing any DNS record instructions:

```
1. Check reference/ directory for provider-specific DNS data:
   - glob(pattern=".opencode/skills/sre-runbook/reference/*.md")
   - If reference data exists for the target provider, USE IT
   - If no reference data exists, HALT and request provider DNS details from the user

2. Validate record type constraints:
   a. CNAME at zone apex → RFC-invalid per RFC 1034 (conflicts with SOA/NS at root)
   b. A record pointing to third-party IP → flag as FRAGILE (IP changes break the record)
   c. Provider-specific apex resolution → check if ALIAS/ANAME is supported

3. Flag provider-specific defects:
   - If user reports a provider defect (e.g., "URL redirector doesn't handle non-SSL"),
     include this in the runbook as a KNOWN-DEFECT annotation
   - Never assume provider capabilities from training data
```

### Gate Failure Examples

| Scenario | Gate Action |
|----------|-------------|
| Directnic docs return 404s for ALL DNS help pages | HALT: "VERIFICATION-GAP: Directnic documentation unreachable — supported record types, GUI paths, and redirector capabilities unconfirmed" |
| `--help` returns error AND man page missing AND no vendor docs | HALT: "VERIFICATION-GAP: <command> verification failed — no sources confirmed the command syntax" |
| DNS runbook proposes CNAME at apex | REJECT: "CNAME at zone apex is RFC-invalid per RFC 1034. Use ALIAS or A record instead." |
| DNS runbook proposes A record to third-party IP | FLAG: "FRAGILE: A record to <IP> — upstream IP changes will break this record. Confirm this IP is stable." |
| One source confirms but another contradicts | INVESTIGATE: resolve contradiction, use confirmed source, flag disagreement |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `systematic-debugging` in Cross-References | File exists at `.opencode/skills/systematic-debugging/SKILL.md` | MISSING-TRACEABILITY if missing |
| `verification-before-completion` in Cross-References | File exists at `.opencode/skills/verification-before-completion/SKILL.md` | MISSING-TRACEABILITY if missing |
| `issue-operations` in Cross-References | File exists at `.opencode/skills/issue-operations/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| Task table entry `generate` | File exists at `.opencode/skills/sre-runbook/tasks/generate.md` | MISSING-TRACEABILITY if missing |
| Task table entry `track` | File exists at `.opencode/skills/sre-runbook/tasks/track.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/sre-runbook/tasks/completion.md` | MISSING-TRACEABILITY if missing |

**Verification Procedure:**

Before invoking any cross-referenced skill:
1. `ls .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: file exists or MISSING-TRACEABILITY
2. `grep -c "<task-name>" .opencode/skills/<skill-name>/SKILL.md` → EVIDENCE: task referenced or MISSING-TRACEABILITY
3. Compare described behavior with actual content → EVIDENCE: match or CONFLICTING

**Classification on failure:**

| Failure | Problem Class | Classification | Action |
| -- | -- | -- | -- |
| Referenced skill file missing | MISSING-TRACEABILITY | flag-for-review | Cannot verify cross-reference |
| Referenced task file missing | MISSING-TRACEABILITY | flag-for-review | Task may have been renamed |
| Described behavior mismatches | CONFLICTING | flag-for-review | Cross-reference may be stale |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including code reference existence and cross-reference validity. When this skill's runbook references code or configuration that may not exist in the actual environment, invoke `spec-auditor --task ground-truth` to verify. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

- Related skills: `systematic-debugging` (root cause analysis discipline), `verification-before-completion` (evidence gates), `issue-operations` (issue creation discipline), `spec-auditor` (ground-truth adversarial verification)
- Related guidelines: `010-approval-gate.md` (authorization), `000-critical-rules.md` (no implementation without spec), `065-verification-honesty.md` (metadata verification extension)

## Platform Compatibility

- **GitHub:** Use GitHub MCP tools for issue tracking
- **GitBucket:** Use Python client from gitbucket-api skill
- **Platform Detection:** Uses `github.platform` environment variable

## Reference Data

- **Directnic DNS record types:** `reference/directnic-record-types.md` — supported record types (A, AAAA, ALIAS, CNAME, TXT, SRV, MX) and apex/CNAME constraints

## Source Attribution

This skill is adapted from the <UPSTREAM_ORG>/<UPSTREAM_REPO> repository (branch: newsrx). The original workflow enforces reasoning-first runbook generation to prevent template-filling anti-patterns.

Key adaptations for <AgentName>:
- Integration with existing systematic-debugging and verification-before-completion skills
- GitBucket platform support via MCP tools
- Runbook type taxonomy (one-off-config, periodic-procedure, troubleshooting, incident-response)
- Conditionally-applied dual-output contract (YAML blocks only for troubleshooting/incident-response)
- Steps-only format for one-off-config and periodic-procedure runbooks
- Format-matching rule to match existing runbook formats before inventing new ones
- Completion guarantee integration
- Environment-context-first discipline (interface preference, tool verification, live docs)
- Operational-procedure focus (steps-only, single-path, real values, minimum-necessary)

## Completion Guarantee

**⚠️ If this workflow halts at ANY point** — including error, failure, or early termination — invoke `--task completion` before halting. This ensures:
- Verification results are documented
- Status report is produced
- No orphaned state is left behind

The completion task is idempotent and safe to invoke multiple times.