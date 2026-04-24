# Task: review-prep/report-url

## Purpose

Generate GitHub compare URL from session-init values, report completion to chat in mandatory format, and HALT waiting for explicit "create a PR" instruction.

## Entry Criteria

- Branch is pushed to remote (review-prep/push-and-cleanup completed)
- Dev sync and rebase verified

## Exit Criteria

- Compare URL generated and reported in CHAT ONLY
- Chat output follows mandatory format (summary → outcome → URL → byline)
- Agent HALTs waiting for "create a PR"

## Procedure

### Step 3: Generate Compare URL

**URL Sourcing Rules (MANDATORY — per `000-critical-rules.md`):**

**Pre-Creation URLs (Compare URL before PR exists):** Construct from session-init values with character-match verification:

1. Read `<github.owner>`, `<github.repo>`, `<gitbucket.html_url>` from session init
2. Construct the URL using those exact values
3. **Character-match verification:** Confirm the URL contains the exact `<github.owner>` and `<github.repo>` strings from session init
4. If any mismatch: HALT and report

**If `<gitbucket.html_url>` is empty (not in .env):**
1. REFUSE to generate any URL
2. Report: "Cannot generate URL — `<gitbucket.html_url>` not configured in .env"
3. HALT — do not guess or fabricate a URL

### Step 4: Report Completion (Chat Only)

**⚠️ CRITICAL: URLs go in CHAT ONLY — NEVER to GitHub Issues.**

**Mandatory format:**

```
**Summary:**

<1-2 sentences describing impact and stakeholder value>

**Outcome:** <What changed for stakeholders>

Compare URL: <Constructed from session-init values — character-match verified>

🤖 <AgentName> (<ModelId>) completed
```

**URL Label Context:**

| Context | Label | URL Format |
| -- | -- | -- |
| Pre-PR (after push, before PR creation) | **Compare URL** | `compare/dev...<branch-name>` |
| Post-PR (PR has been created) | **PR URL** | `pull/<PR-number>` |

**Label-format mismatch is a critical violation.** "Compare URL" with `pull/N` format or "PR URL" with `compare/dev...` format is ALWAYS wrong.

### Format Verification (MANDATORY — check before posting)

- [ ] Executive summary present as first element
- [ ] `**Outcome:**` follows summary
- [ ] URL label matches context (pre-PR: "Compare URL" + `compare/dev...`; post-PR: "PR URL" + `pull/N`)
- [ ] URL present as last element before byline
- [ ] AI byline present after URL
- [ ] No URL before summary
- [ ] No byline before URL

**Classification on failure:**

| Failure | Action |
| -- | -- |
| Missing summary | auto-fix — add before proceeding |
| Wrong URL label | auto-fix — change label to match context |
| Missing URL | auto-fix — generate URL before proceeding |
| Missing byline | auto-fix — add before proceeding |
| Wrong ordering | auto-fix — reorder to summary → outcome → URL → byline |

### Step 5: HALT (MANDATORY - NO EXCEPTIONS)

**🚫 CRITICAL VIOLATION: Proceeding past this point without "create a PR" is a CRITICAL GUIDELINE VIOLATION.**

**DO NOT:**
- Squash commits (happens at PR creation)
- Create PR (requires explicit instruction)
- Push again (already pushed)
- Close issues (requires PR merge verification)
- Proceed to any next step

**WAIT for EXPLICIT instruction:** Developer says "create a PR" to proceed.

### Post-Merge Reminder (MANDATORY)

After PR merge confirmation, run `git-workflow --task cleanup` to close issues, clean branches, and verify sub-issue closure.

### PR Body Keyword Discipline

| Keyword | Auto-Closes Issue? | Use When |
| -- | -- | -- |
| `Fixes #N` | YES — auto-closes on merge | Single-issue specs with NO sub-issues |
| `Implements #N` | NO — informational only | Multi-task plans, specs with sub-issues |
| `Related #N` | NO — weak reference | Tangentially related issues |

**When in doubt:** Use `Implements`. It never auto-closes; cleanup task handles closure properly.

## Context Required

- Related tasks: `review-prep/push-and-cleanup`, `pr-creation`
- Related guidelines: `000-critical-rules.md` (URL sourcing, chat output format)