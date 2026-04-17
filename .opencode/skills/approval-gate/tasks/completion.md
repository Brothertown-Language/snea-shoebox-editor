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

Issue URL: <GitBucketHtmlUrl><GitOwner>/<GitRepo>/issues/<number>

🤖 <AgentName> (<ModelId>) <status>
```

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

### Verify Authorization Result Comment Was Actually Posted

```
comments = github_issue_read(method="get_comments", issue_number=N)

Search comments for authorization result (byline pattern):
  - If comment found with authorization result → VERIFIED
  - If comment NOT found → MISSING-ELEMENT (auto-fix: post the comment now)
```

**Evidence artifact:** `github_issue_read(method=get_comments)` response showing whether the authorization result comment exists.

### Verify Label State Matches Actual Authorization State

```
labels = github_issue_read(method="get_labels", issue_number=N)

- If needs-approval label present AND authorization was granted → STRUCTURE-VIOLATION (auto-fix: remove label)
- If needs-approval label absent AND no authorization was found → VERIFICATION-GAP (flag-for-review: label may have been removed prematurely)
```

**Evidence artifact:** Label list from GitHub MCP showing current label state.

### Verify Status Report Matches Actual Workflow Outcome

```
If completion claims "approved" but:
  - No authorization comment found → CONFLICTING (flag-for-review)
  - Authorization comment from bot/agent → CONFLICTING (flag-for-review)
  
If completion claims "blocked" but:
  - Blocker issue is actually closed → VERIFICATION-GAP (flag-for-review: blocker may be resolved)
```

**Evidence artifact:** Comment search results and label state confirming the claimed outcome.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Authorization comment missing from issue | MISSING-ELEMENT | auto-fix | Post the comment immediately |
| Label state inconsistent with auth result | STRUCTURE-VIOLATION | auto-fix | Correct label state |
| Completion outcome contradicts evidence | CONFLICTING | flag-for-review | Report mismatch, developer must judge |
| Format elements missing or misordered | STRUCTURE-VIOLATION | auto-fix | Fix before sending output |