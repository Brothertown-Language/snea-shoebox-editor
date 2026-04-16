# Task: completion

## Purpose

Ensure the verification-enforcement workflow documents its results and produces a status report regardless of outcome. This task is the completion guarantee for verification-enforcement — it runs whenever the workflow halts, whether successfully, with unresolved claims, or on error.

## Entry Criteria

The verification-enforcement workflow is halting. This includes: successful completion of verify and revisit passes, verification failure requiring escalation, or an error that prevents continuation.

## Exit Criteria

Verification results are documented, a status report is produced, and no orphaned state remains.

## Procedure

Document the verification results as a status report. The report lists three categories of claims: verified claims with their evidence sources, unverified claims still carrying `⚠️ UNVERIFIED` markers, and escalated claims that have been reported to the developer. For each claim, the report includes the evidence artifact summary — the claim text, the verification domain, and whether verification succeeded.

If the verification workflow completed successfully with all claims verified, the status report records this and no further action is needed. If unresolved claims remain, the status report records the specific claims, the tools and sources that were consulted, and the reason verification failed for each. This report serves as the escalation document that the developer receives.

The completion task is idempotent — invoking it multiple times produces the same result. It does not re-verify claims, re-dispatch sub-agents, or modify generated content. It only documents the current state and ensures that no verification state is left hanging without a resolution recorded.

The status report is produced in chat output, following the format:

```
Verification Status: <complete|partial|escalated>
Verified: <count> claims
Unverified: <count> claims (see below)
Escalated: <count> claims (see below)

Unverified claims:
- <claim text> — <reason verification failed>

Escalated claims:
- <claim text> — <reason escalated to developer>
```

## Context Required

- Invoked by: end of verification-enforcement workflow
- Related tasks: `verify`, `revisit`, `enforce`