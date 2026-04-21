# Task: draft

## Purpose

Draft email correspondence following the multipart/alternative format template, stakeholder content rules, audience-awareness rules, and verification-enforcement integration.

## Entry Criteria

- Correspondence context provided (reply-to thread, new email, status update, notification)
- Audience classification determined (internal, external, internal-executive, or mixed)
- Original email format detected (if reply-to thread)

## Exit Criteria

- Email draft produced in multipart/alternative format (text/plain + text/html)
- Content filtered by audience classification
- Verification gates passed (verify before, revisit after)
- Self-review checklist completed
- AI byline present in both parts

## Procedure

### Step 1: Audience Classification

Determine the correspondence audience before drafting ANY content:

| Question | Answer | Classification | Content Level |
|----------|--------|---------------|---------------|
| Is the recipient an external client, customer, or vendor? | Yes | External | Outcome-only |
| Is the recipient an internal team member? | Yes | Internal | Full context |
| Is the recipient an internal executive or manager? | Yes | Internal-Executive | Business-level |
| Is the audience mixed (internal + external)? | Yes | Conservative | Apply external rules |
| Is the audience unclear? | — | Conservative | Apply external rules |

**Output:** Classification and rationale recorded.

### Step 2: Pre-Draft Verification Gate

Invoke `verification-enforcement --task verify` before drafting.

For email correspondence, the verification domains are:

| Claim Type | Verification Action | Tool Call |
|-----------|-------------------|-----------|
| Domain status (active, expired, renewed) | Verify against WHOIS or registrar status | `bash` to run WHOIS query or `webfetch` to check registrar |
| DNS record state (correct, incorrect, changed) | Verify against live DNS query | `bash` to run `dig` or `nslookup` |
| Service availability (up, down, degraded) | Verify against live service check | `bash` to run health check or `webfetch` |
| Dates and timelines | Verify against live data | `bash` to run date queries |
| Quoted content from original email | Verify original email content matches | `read` original email file |
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
| Person-action attribution (who did what) | Verify against email headers, commit authors, PR/issue creators, or explicit source statements | `read` email headers, `srclight_blame_symbol`, `github_pull_request_read`, `github_issue_read` |
>>>>>>> spec/1097-fix
=======
| Person-action attribution (who did what) | Verify against email headers, commit authors, PR/issue creators, or explicit source statements | `read` email headers, `srclight_blame_symbol`, `github_pull_request_read`, `github_issue_read` |
>>>>>>> spec/1098-fix
=======
| Person-action attribution (who did what) | Verify against email headers, commit authors, PR/issue creators, or explicit source statements | `read` email headers, `srclight_blame_symbol`, `github_pull_request_read`, `github_issue_read` |
>>>>>>> spec/1099-fix

**Evidence artifacts must be collected before drafting proceeds.**

### Step 3: Content Filtering

Apply stakeholder content rules based on audience classification:

#### For External Stakeholders

🚫 PROHIBITED content in external-facing email:
- Runbook file paths (e.g., `docs/runbooks/...`)
- Step numbers from internal procedures (e.g., "repeat Steps 2-6")
- Internal IP addresses (e.g., `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`)
- Server hostnames (e.g., `pve-web.internal.example.com`)
- Internal tool or script names
- Internal project identifiers
- Configuration file paths
- CLI commands for internal operations

✅ REQUIRED rephrasing for external stakeholders:
- "the standard DNS correction procedure was applied" instead of "repeat Steps 2-6 of the runbook"
- "the registrar's parking page" instead of "parking IP 10.0.0.5"
- "our infrastructure team corrected the DNS records" instead of "sysadmin ran sync-dns.sh"

#### For Internal Stakeholders

✅ Full context is appropriate:
- Technical details, commands, internal references
- Before/after state with specifics
- Verification results with command output
- Runbook references with file paths

#### For Internal-Executive Stakeholders

✅ Business-level context:
- Outcomes and impact in business terms
- Timeline and decisions needed
- Risk assessment summaries
- Escalation decisions

⚠️ AVOID:
- Deep technical details that require context the executive doesn't have
- Command-line output (summarize instead)
- Detailed step-by-step procedures (link to runbook instead)

### Step 4: Format Template Application

#### Detect Original Email Format

If replying to an existing email thread:

1. Read the original email's Content-Type header
2. If `multipart/alternative` or `text/html` → Reply MUST be multipart/alternative
3. If `text/plain` only → Reply MAY be text/plain only (but multipart is still preferred)

#### Multipart/Alternative Template

Every email draft MUST include both parts:

**text/plain part:**
```
Summary:

<1-2 sentences describing impact and stakeholder value>

Outcome: <What changed for stakeholders>

---
🤖 <AgentName> (<ModelId>) <status-icon> <status>
```

**text/html part:**
```html
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
  <h3 style="margin-bottom: 8px;">Summary</h3>
  <p><1-2 sentences describing impact and stakeholder value></p>

  <h3 style="margin-bottom: 8px;">Outcome</h3>
  <p><What changed for stakeholders></p>

  <hr style="border: none; border-top: 1px solid #ccc; margin: 16px 0;">
  <p style="font-size: 0.85em; color: #666;">
    🤖 &lt;AgentName&gt; (&lt;ModelId&gt;) &lt;status-icon&gt; &lt;status&gt;
  </p>
</div>
```

#### Byline Format

| Agent's Role | Byline Format | Example |
|---------------|---------------|---------|
| Agent authored | `🤖 <AgentName> (<ModelId>) <status>` | `🤖 OpenCode (ollama-cloud/glm-5.1) ✅ completed` |
| Agent drafted on behalf of user | `🤖 <AgentName> on behalf of <dev.name>` | `🤖 OpenCode on behalf of Michael Conrad` |
| Agent edited user's content | `🤖 <AgentName>, copy editor for <dev.name>` | `🤖 OpenCode, copy editor for C.W. Henderson` |

The byline MUST appear in BOTH text/plain and text/html parts. It MUST NOT be removed on subsequent edits.

### Step 5: Self-Review Checklist

After drafting, validate against ALL of the following:

- [ ] Both text/plain and text/html parts are present (or text/plain only when original was text/plain)
- [ ] HTML part uses proper structural markup (no markdown syntax like `**bold**` or `---` in email body)
- [ ] Summary section is 1-2 sentences maximum
- [ ] Outcome section states what changed for stakeholders
- [ ] AI byline appears in both text/plain and text/html parts
- [ ] Content is filtered by audience classification (internal vs. external)
- [ ] No internal ops details in external-facing correspondence
- [ ] No runbook paths, step numbers, internal IPs, or internal tool names in external content
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
- [ ] All person-action attributions verified against source evidence (no role-proximity inference)
>>>>>>> spec/1097-fix
=======
- [ ] All person-action attributions verified against source evidence (no role-proximity inference)
>>>>>>> spec/1098-fix
=======
- [ ] All person-action attributions verified against source evidence (no role-proximity inference)
>>>>>>> spec/1099-fix
- [ ] Original email format matched (multipart reply to multipart, etc.)
- [ ] Email thread context preserved (quoted or summarized)

### Step 6: Post-Draft Verification Gate

Invoke `verification-enforcement --task revisit` after self-review.

- Scan the draft for `⚠️ UNVERIFIED` markers
- Attempt resolution for each marker using appropriate verification tools
- If any markers remain unresolved after revisit:
  - Escalate to developer with specific reason the claim could not be verified
  - Include the unresolved marker in the draft for developer review

### Step 7: Present Draft

Present the completed email draft to the calling context with:

1. Audience classification and rationale
2. Content filtering decisions (what was included/excluded and why)
3. Verification results (verified claims, unresolved markers)
4. The complete multipart/alternative email

## Common Issues

| Issue | Resolution |
|-------|------------|
| Original email is HTML-only | Reply MUST be multipart/alternative with both parts |
| Original email is plain text | Reply MAY be text/plain only, but multipart is still preferred |
| Mixed internal/external audience | Apply conservative (external) content rules |
| Unsure about content sensitivity | Default to external rules — under-sharing is safer than leaking |
| Verifying domain status fails | Mark as `⚠️ UNVERIFIED`, escalate to developer |
| Verifying DNS state fails | Mark as `⚠️ UNVERIFIED`, escalate to developer |
| Agent drafted on behalf of user | Use "on behalf of" byline format |
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
| Attribution uncertain (who did what) | Omit the person's name or write "completed per [reference]" without naming an individual — never infer from role proximity |
| Source contradicts assumed attribution | Use the source evidence, not the assumption — correct the attribution or omit it |
>>>>>>> spec/1097-fix
=======
| Attribution uncertain (who did what) | Omit the person's name or write "completed per [reference]" without naming an individual — never infer from role proximity |
| Source contradicts assumed attribution | Use the source evidence, not the assumption — correct the attribution or omit it |
>>>>>>> spec/1098-fix
=======
| Attribution uncertain (who did what) | Omit the person's name or write "completed per [reference]" without naming an individual — never infer from role proximity |
| Source contradicts assumed attribution | Use the source evidence, not the assumption — correct the attribution or omit it |
>>>>>>> spec/1099-fix

## Context Required

- Session values: `github.owner`, `github.repo`, `dev.name`, `dev.email`
- Original email content (if reply-to thread)
- Audience context (who is receiving the email)
- Related skills: `verification-enforcement` (verify and revisit tasks)
- Original email file path (if reading from file system)