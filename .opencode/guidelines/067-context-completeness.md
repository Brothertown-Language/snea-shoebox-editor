# Context Completeness — Read All Comments Before Acting

## Zero Tolerance Rule

**🚫 CRITICAL VIOLATION: Acting on a GitHub/GitBucket resource without reading ALL comments first.**

The body or description alone is NEVER sufficient context. Comments may contain critical information: authorizations, direction changes, clarifications, blockers, or bug reports.

## Core Principle

**Before reviewing, auditing, or taking any action on a GitHub/GitBucket resource (issue, PR, discussion), the agent MUST read ALL comments on that resource. The body/description alone is NEVER sufficient context.**

## Why This Matters

| What Gets Missed | Consequence |
| -- | -- |
| Authorization in a comment | Implementing without approval or missing approval |
| Direction change in a comment | Implementing the wrong approach |
| Clarification in a comment | Building on stale or incorrect understanding |
| Bug report in a comment | Ignoring known issues |
| PR review feedback | Repeating mistakes reviewers already flagged |
| Scope change in a comment | Implementing beyond or outside changed scope |

## Scope of Resources

| Resource | What to Read |
| -- | -- |
| Issues | Issue body + ALL issue comments |
| Pull Requests | PR description + ALL PR comments + ALL review comments |
| Discussions | Discussion body + ALL discussion comments |

## When This Applies

| Action | Must Read Comments First? |
| -- | -- |
| Reviewing/auditing a spec | ✅ YES — always |
| Acting on an issue (implement, revise) | ✅ YES — always |
| Checking authorization | ✅ YES — authorization lives in comments |
| Responding to a question | ✅ YES — may already be answered |
| Creating sub-issues for a parent | ✅ YES — comments may define phases |
| Post-implementation reporting | ✅ YES — new comments may have arrived |
| Simply reading an issue for info | ❌ NO — but MUST read before any subsequent action |

## Evidence Requirement

When the agent reads comments before acting, it MUST show evidence:

- **Reference specific comments**: "Saw comment by @user on 2026-04-09 approving Phase 2" not just "I read the comments"
- **Count or summarize**: "Read 5 comments — 2 approvals, 1 clarification, 2 progress updates"
- **Highlight relevant ones**: Call out comments that change or clarify the spec content

### What COUNTS as Evidence

✅ **Evidence Shown:**

- Calling `github_issue_read` with `method=get_comments` and referencing the results
- Citing specific comment content: "Comment #3 by @dev adds constraint X"
- Summarizing: "3 comments total — 1 approval, 1 scope change, 1 progress update"
- Quoting relevant comment text inline

❌ **NOT Evidence:**

- "I read the comments" without showing what was found
- Acting on an issue without any comment reference in the response
- Assuming comments haven't changed since last read
- "The comments don't affect this" without showing what comments exist

## Staleness Rule

Comments may have been added **since the agent last read the resource**. The agent MUST re-read comments if:

- The agent is about to take a significant action (implementation, approval check, PR creation, issue closure, spec revision)
- The agent previously relied on memory instead of re-reading (see `065-verification-honesty.md`)
- Any time has passed since the last read — comments are live, async data

### Significant Actions Requiring Re-Read

The staleness rule is NOT about time estimation. It is about **action significance**. Before any of these actions, re-read comments even if read moments ago:

1. Starting implementation
2. Checking authorization status
3. Creating or updating a PR
4. Closing an issue
5. Revising a spec
6. Creating sub-issues

## Single Exchange Window

If comments were read in the **immediately preceding exchange** (the last assistant turn in the same conversation), the agent MAY reference those results without re-reading. Any earlier reference requires re-checking for new comments.

This is consistent with the Single Exchange Window defined in `065-verification-honesty.md`.

## Relationship to Other Critical Rules

This guideline complements (does not replace):

- **"Ignoring Issue Comments" (`000-critical-rules.md`)**: That rule requires *responding* to user comments; this requires *reading* them before acting
- **"Verification Honesty" (`065-verification-honesty.md`)**: That rule requires actual verification instead of memory; reading comments IS verification work
- **"Bug Discovery Does NOT Authorize" (`000-critical-rules.md`)**: Authorization often lives in comments; missing comments = missing authorization

## 🚫 FORBIDDEN

- Acting on an issue after reading only the issue body
- Reviewing a PR without reading review comments
- Checking authorization without reading recent comments
- Assuming "no new comments" without actually checking
- Caching comment state from a previous session
- Skipping comment reads because "I checked earlier"

## ✅ REQUIRED

- Read ALL comments before ANY action on a resource
- Show evidence of having read comments (count, summarize, or cite)
- Re-read before significant actions even if recently read
- Use `github_issue_read` with `method=get_comments` (or equivalent) to fetch comments
- Treat comment reading as mandatory verification work (per `065-verification-honesty.md`)

## Related Guidelines

- `065-verification-honesty.md` — Never rely on memory when instructed to check
- `000-critical-rules.md` — Zero tolerance violations including "Ignoring Issue Comments"
- `075-docs-verification.md` — Mandatory live documentation verification
- `130-authority-source.md` — Code as authoritative source
