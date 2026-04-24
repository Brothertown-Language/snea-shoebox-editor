# Task: completion

Idempotent completion subtask for approval-gate. Ensures mandatory steps run regardless of where the workflow halted.

## State Check Phase

1. **Authorization result determined:** Was a yes/no decision reached?
2. **Existing comments:** Check if authorization result comment already posted on issue

## Skill-Specific Completion

1. **Post authorization result comment** (if not already posted):
   - Check issue comments for existing authorization result (byline pattern)
   - If missing: post result comment with authorization status and scope

## Shared Completion Delegation

Reference `.opencode/skills/completion-core/completion-core.md` for reporting:

1. Report executive summary in chat (always runs)
2. Action URL (issue URL) as the URL (ALWAYS last)

## Label State Machine

Before adding or removing labels in completion, consult `141-planning-status-tracking.md §10` for the complete label transition matrix and the GitHub `labels` parameter warning (replaces all labels, not additive).

## Completion Guarantee

**MANDATORY:** Regardless of authorization outcome (approved, rejected, blocked, error), produce a status message containing:
1. Authorization decision (approved/rejected/blocked)
2. Issue number and branch (if applicable)
3. What happens next (workflow forward, HALT, or error)

This is the completion guarantee: NO authorization check ends without a status message.

## Report Phase

Generate executive summary in chat:

```
**Summary:**

<Authorization verification result and scope>

**Outcome:** <What the result means for stakeholders>

Issue URL: <html_url from github_issue_write or github_issue_read API response — NEVER construct from template>

🤖 <AgentName> (<ModelId>) <status>
```

**Post-Creation URL Extraction (MANDATORY — per `000-critical-rules.md` §URL Sourcing):**

The Issue URL MUST be extracted from the API response `html_url` field — NEVER constructed from template variables:

1. If the issue was created in this session: Extract `html_url` from the `github_issue_write` creation response
2. If the issue was read (not created): Extract `html_url` from the `github_issue_read` response
3. **Template construction is FORBIDDEN for post-creation URLs** — do NOT assemble from `<gitbucket.html_url>`, `<github.owner>`, `<github.repo>`, or issue number
4. If `html_url` is not available in the API response: HALT and report

URL is ALWAYS last per `000-critical-rules.md`.

### Format Verification Before Halt (MANDATORY)

**Idempotent — safe to invoke multiple times. This verification runs before EVERY halt, regardless of path.**

**For chat messages (visible output):**

- [ ] Executive summary present as **first** element (before any URL)
- [ ] Outcome line present after summary
- [ ] URL present IF relevant (after outcome, before byline) — required when branch pushed or issue URL exists, **omitted** when no URL exists
- [ ] AI byline present as **LAST** element (after URL, or after outcome when no URL)
- [ ] No URL before executive summary
- [ ] No byline before URL/outcome

**For silent stops (no visible output):**

- [ ] Executive summary already reported in a prior chat message
- [ ] No stale todowrite items remain (all cleared or N/A)

**Evidence requirement:** Each checkpoint verification MUST produce a tool-call artifact confirming the element is present or correctly absent. Verbal assertion without tool-call evidence is insufficient.

**URL applicability:**

| Scenario | URL Required? | Action |
| -- | -- | -- |
| Branch pushed | ✅ Yes | Include compare URL between outcome and byline |
| Issue URL available | ✅ Yes | Include issue URL between outcome and byline |
| No URL available | ❌ No | Omit URL element entirely; byline follows outcome directly |
| PR already created | ✅ Yes | Use PR URL label with `pull/<N>` format |

**Auto-fix on failure:** If any element is missing or misordered, fix the output before sending. Missing elements are MISSING-ELEMENT (auto-fix). Wrong ordering is STRUCTURE-VIOLATION (auto-fix). Elements are auto-fixed before output is sent — NOT reported after the fact.

## Adversarial Verification: Completion Claims

**Before claiming completion, verify that all completion claims are backed by evidence — not asserted without verification.**

### Verification Checklist

- **Authorization result comment posted:** Search issue comments via `github_issue_read(method=get_comments)` for the authorization result (byline pattern). If missing → MISSING-ELEMENT (auto-fix: post now).
- **Label state matches authorization:** Check labels via `github_issue_read(method=get_labels)`. If `needs-approval` present AND authorization granted → STRUCTURE-VIOLATION (auto-fix: remove label). If `needs-approval` absent AND no authorization found → VERIFICATION-GAP (flag-for-review).
- **Status report matches workflow outcome:** If completion claims "approved" but no authorization comment found → CONFLICTING (flag-for-review). If claims "blocked" but blocker issue is closed → VERIFICATION-GAP (flag-for-review).

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
