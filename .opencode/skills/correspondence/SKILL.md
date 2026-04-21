---
name: correspondence
description: Use when drafting stakeholder emails, status updates, or external communications. Triggers on: email, correspondence, stakeholder email, status update, communication, draft email, reply, notification.
type: discipline-enforcing
license: MIT
compatibility: opencode
---

# Skill: correspondence

Discipline-enforcing skill for drafting email correspondence and stakeholder communications. Enforces multipart/alternative format (text/plain + text/html), stakeholder content rules, audience-aware content levels, and verification-enforcement integration.

## Problem This Skill Solves

Three distinct failures occur when drafting email correspondence without this skill:

1. **No HTML enforcement.** The original email is often multipart/alternative with HTML. The agent writes `Content-Type: text/plain` and uses markdown syntax inside the email body, which renders as raw markdown in email clients.

2. **No stakeholder content rules.** The agent includes internal operations details — runbook file paths, step numbers, internal IP addresses — that are meaningless or confusing to stakeholders.

3. **No format template.** Nothing extends the Summary/Outcome/byline format to email correspondence. The agent guesses at email format and guesses wrong.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `draft` | Draft email correspondence with format template, audience rules, and verification gate | ≈800 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ≈200 |

## Invocation

- `/skill correspondence --task draft` — Draft email correspondence
- `/skill correspondence --task completion` — Invoke when workflow halts at any point
- `/skill correspondence` — Overview only

## Operating Protocol

1. **Verification gate BEFORE drafting.** The agent MUST invoke `verification-enforcement --task verify` before drafting any email correspondence. All claims about external state (domain status, DNS records, service availability, system state) must be verified against live data before inclusion.

2. **Format template REQUIRED.** Every email draft MUST use the multipart/alternative template defined in the `draft` task. No exceptions. The text/plain part uses the Summary/Outcome/byline format. The text/html part renders that same format in proper HTML with structural markup.

3. **Stakeholder content rules REQUIRED.** Content must be filtered through audience-awareness rules before inclusion. Internal ops details are PROHIBITED in external-facing correspondence.

4. **Audience classification FIRST.** Before drafting, the agent MUST classify the audience as internal or external. This classification drives content filtering rules.

5. **Verification gate AFTER drafting.** The agent MUST invoke `verification-enforcement --task revisit` after self-review. Any claims that could not be verified must be marked `⚠️ UNVERIFIED` and escalated to the developer.

6. **Completion guarantee.** If this workflow halts at ANY point — including error, failure, or early termination — invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.

## Enforcement Rules — Email Correspondence Discipline

### Email Format Template (MANDATORY)

Every email produced by this skill MUST use the multipart/alternative format with both text/plain and text/html parts. No email drafts in plain text only. No markdown syntax in email bodies.

**text/plain part:**

```
Summary:

<1-2 sentences describing impact and stakeholder value>

Outcome: <What changed for stakeholders>

---
🤖 <AgentName> (<ModelId>) <status-icon> <status>
```

**text/html part:**

The HTML part renders the same content with proper structural HTML markup:

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

### Stakeholder Content Rules (MANDATORY)

#### Content Classification

| Content Type | Internal Stakeholder | External Stakeholder |
|-------------|---------------------|---------------------|
| Outcome summary | ✅ Include | ✅ Include |
| Root cause (high-level) | ✅ Include | ✅ Include (simplified) |
| Technical details (IPs, paths, commands) | ✅ Include with context | 🚫 PROHIBITED |
| Runbook references ("Step 2-6", file paths) | ✅ Include with context | 🚫 PROHIBITED |
| Internal tool names | ✅ Include | 🚫 PROHIBITED |
| Before/after state (business terms) | ✅ Include | ✅ Include |
| Verification results (business terms) | ✅ Include | ✅ Include |
| Timeline and action items | ✅ Include | ✅ Include |
| Internal system names/identifiers | ⚠️ Include with context | 🚫 PROHIBITED — rephrase generically |
| Error messages and stack traces | ✅ Include | 🚫 PROHIBITED — summarize impact only |

#### Prohibited Content in External-Facing Email

The following content types are ABSOLUTELY PROHIBITED in emails to external stakeholders:

- **Runbook file paths** (e.g., `docs/runbooks/videoconcerthall-dns-correction.md`)
- **Step numbers from internal procedures** (e.g., "repeat Steps 2-6")
- **Internal IP addresses** (e.g., `192.168.1.100`, `10.0.0.5`)
- **Server hostnames** (e.g., `pve-web.internal.example.com`)
- **Internal tool or script names** (e.g., `sync-dns.sh`, `deploy-stack.yml`)
- **Internal project identifiers** (e.g., `PROJECT-4289`)
- **Configuration file paths** (e.g., `/etc/nginx/sites-available/...`)
- **CLI commands intended for internal operations** (e.g., `systemctl restart nginx`)

When a stakeholder email MUST reference technical details, rephrase them in stakeholder-relevant terms. Instead of "repeat Steps 2-6 of the runbook," say "the standard DNS correction procedure was applied." Instead of "parking IP 10.0.0.5," say "the registrar's parking page."

### Audience-Awareness Rules (MANDATORY)

Before drafting, the agent MUST classify the correspondence audience:

| Audience | Classification | Content Level |
|----------|---------------|---------------|
| External client or customer | External | Outcome-only: what happened, what was fixed, current state |
| External vendor or partner | External | Outcome-only: relevant facts about the interaction only |
| Internal team members | Internal | Full context: technical details, commands, internal references |
| Internal stakeholders (execs, managers) | Internal-Executive | Business-level context: outcomes, timelines, decisions needed |
| Mixed (internal + external on same thread) | Conservative | Apply external rules — assume the most restrictive audience |

**Conservative default rule:** When the audience is mixed or unclear, apply external-stakeholder rules. It is always safer to under-share than to leak internal details.

### AI Byline Rule (MANDATORY)

The AI byline is MANDATORY in ALL correspondence produced by this skill. It MUST appear in both text/plain and text/html parts.

| Agent's Role | Byline Format | Example |
|---------------|---------------|---------|
| Agent authored the correspondence | `🤖 <AgentName> (<ModelId>) <status>` | `🤖 OpenCode (ollama-cloud/glm-5.1) ✅ completed` |
| Agent drafted on behalf of user who provided direct instructions | `🤖 <AgentName> on behalf of <dev.name>` | `🤖 OpenCode on behalf of Michael Conrad` |
| Agent edited/formatting-only on user's direct content | `🤖 <AgentName>, copy editor for <dev.name>` | `🤖 OpenCode, copy editor for C.W. Henderson` |

The byline MUST NOT be removed on subsequent edits.

<<<<<<< HEAD
### Matching Original Format (MANDATORY)

When replying to an existing email thread:

1. **Detect original format.** Read the original email's Content-Type header. If it is `multipart/alternative` or `text/html`, the reply MUST be multipart/alternative with both text/plain and text/html parts.
2. **Match original structure.** If the original email uses HTML formatting, the reply MUST also use HTML formatting. Never downgrade an HTML thread to plain text.
3. **Preserve thread context.** Include relevant context from the original email (quoted or summarized) in the reply.

<<<<<<< HEAD
=======
=======
### Content-Type Propagation (MANDATORY)

When generating a reply to existing communication, the output format MUST match the source communication's content type. This is a **verification step**, not a formatting preference — the agent MUST inspect the content type of the source before drafting the reply.

**General rule:** If the source is HTML multipart, the reply is HTML multipart. If the source is plain text, the reply is plain text. If the source is structured data (JSON, YAML), the reply follows that schema. The agent must not default to markdown when the source uses a different format, because markdown renders as raw text in non-markdown contexts.

**Email-specific rule:** Read the `Content-Type` header of the source `.eml` file before drafting any reply:

| Source Content-Type | Required Reply Format | Verification Step |
|---------------------|-----------------------|-------------------|
| `multipart/alternative` or `text/html` | Multipart/alternative with text/plain + text/html parts | `read` the `.eml` file, grep for `Content-Type:` header |
| `text/plain` (no HTML part) | Plain text only (no markdown syntax) | `read` the `.eml` file, grep for `Content-Type:` header |
| Markdown-formatted email (rare) | Markdown is acceptable only if the source uses it | Verify source contains markdown formatting |

**Never use markdown syntax inside an email body unless the source email uses markdown.** Markdown renders as raw text (`**bold**` appears as literal `**bold**` text, `---` appears as a literal horizontal rule characters) in all standard email clients. This is not an email-client rendering issue — it is a content-type mismatch.

**Protocol:**

1. **Inspect BEFORE drafting.** Read the original communication's content type before writing any reply content. This inspection is mandatory, not optional.
2. **Match the format.** Produce output in the same content type as the source. HTML source → HTML reply. Plain text source → plain text reply. JSON source → JSON reply.
3. **Never downgrade.** If the source uses HTML, the reply MUST include HTML. Never downgrade an HTML thread to plain text with markdown syntax.
4. **Preserve thread context.** Include relevant context from the original communication (quoted or summarized) in the reply.

>>>>>>> spec/1098-fix
### Attribution Verification (MANDATORY)

When correspondence attributes an action to a person (e.g., "completed by Person X", "Person X renewed the domain"), the attribution MUST be verified against source evidence before inclusion. This is a specialized application of the verification-enforcement attribution domain to correspondence.

**Attribution evidence sources:**

| Source Type | Evidence Tool | What It Proves |
|-------------|--------------|----------------|
| Email From/Sender header | `read` on email file or source | Who sent the email |
| GitHub commit author | `srclight_blame_symbol` or `github_list_commits` | Who committed the change |
| PR creator | `github_pull_request_read(method=get)` | Who created the PR |
| Issue comment author | `github_issue_read(method=get_comments)` | Who wrote the comment |
| Explicit statement in source material | `read` or `grep` on source document | Who was named as performing the action |

**Attribution rule:** If the source does not explicitly state who performed an action, the agent MUST NOT attribute — either omit the person's name entirely or write "completed per [reference]" without naming an individual. Inferring "who did what" from role proximity (e.g., "the tech person must have done the tech work") is prohibited.

<<<<<<< HEAD
>>>>>>> spec/1097-fix
=======
>>>>>>> spec/1098-fix
### Verification-Enforcement Integration (MANDATORY)

The verification-enforcement skill applies to email correspondence the same way it applies to specs, plans, and runbooks:

1. **Before drafting:** Invoke `verification-enforcement --task verify` to collect evidence artifacts for any claims about external state (domain status, DNS records, service availability).
2. **After drafting and self-review:** Invoke `verification-enforcement --task revisit` to scan for `⚠️ UNVERIFIED` markers and attempt resolution.
3. **Escalate unresolved claims.** If any claims cannot be verified after the revisit pass, the agent MUST escalate to the developer with the specific reason.

### Self-Review Checklist (MANDATORY)

After drafting email correspondence, the agent MUST validate against ALL of the following before presenting the draft:

- [ ] Both text/plain and text/html parts are present
- [ ] HTML part uses proper structural markup (no markdown syntax in email body)
<<<<<<< HEAD
=======
- [ ] Content-type propagation verified: source Content-Type header inspected before drafting, reply format matches source format
- [ ] No markdown syntax in email body unless source email uses markdown
>>>>>>> spec/1098-fix
- [ ] Summary section is 1-2 sentences maximum
- [ ] Outcome section states what changed for stakeholders
- [ ] AI byline appears in both text/plain and text/html parts
- [ ] Content is filtered by audience classification (internal vs. external)
- [ ] No internal ops details appear in external-facing correspondence
- [ ] No runbook paths, step numbers, internal IPs, or internal tool names in external content
<<<<<<< HEAD
<<<<<<< HEAD
=======
- [ ] All person-action attributions verified against source evidence (no role-proximity inference)
>>>>>>> spec/1097-fix
=======
- [ ] All person-action attributions verified against source evidence (no role-proximity inference)
>>>>>>> spec/1098-fix
- [ ] Verification-enforcement verify task was invoked before drafting
- [ ] Verification-enforcement revisit task was invoked after self-review
- [ ] All `⚠️ UNVERIFIED` markers resolved or escalated

## Worktree Mode

When invoked from a worktree context (`worktree.path` is set):

- ALL `bash` tool calls MUST use `workdir` parameter set to `worktree.path`
- ALL `read`/`write`/`edit`/`glob`/`grep` tool calls MUST prefix `filePath`/`path` with `worktree.path/`
- Email drafts saved to files MUST resolve within the worktree, not the main repo

**Verification guard:** Before running any command, verify:
```bash
git -C $WORKTREE_PATH rev-parse --show-toplevel
```
If the result does NOT match `worktree.path`, HALT and report: "Worktree mismatch — skill is executing in the wrong directory."

If `worktree.path` is NOT set, operate normally from the project root.

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `verification-enforcement` in Cross-References | File exists at `.opencode/skills/verification-enforcement/SKILL.md` | MISSING-TRACEABILITY if missing |
| `issue-operations` in Cross-References | File exists at `.opencode/skills/issue-operations/SKILL.md` | MISSING-TRACEABILITY if missing |
| `sre-runbook` in Cross-References | File exists at `.opencode/skills/sre-runbook/SKILL.md` | MISSING-TRACEABILITY if missing |
| Task table entry `draft` | File exists at `.opencode/skills/correspondence/tasks/draft.md` | MISSING-TRACEABILITY if missing |
| Task table entry `completion` | File exists at `.opencode/skills/correspondence/tasks/completion.md` | MISSING-TRACEABILITY if missing |

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

## Cross-References

- Related skills: `verification-enforcement` (pre/post generation verification gates), `issue-operations` (comment format and byline rules), `sre-runbook` (status communication scope, byline rule, format-matching rule)
- Related guidelines: `000-critical-rules.md` (mandatory format for chat/comments, AI co-authored attribution), `010-approval-gate.md` (authorization before implementation), `065-verification-honesty.md` (verification before claims)

## Source Attribution

Co-authored with AI: OpenCode (ollama-cloud/glm-5.1)

## Completion Guarantee

**⚠️ If this workflow halts at ANY point** — including error, failure, or early termination — invoke `--task completion` before halting. This ensures:
- Email draft verification results are documented
- Status report is produced
- No orphaned state is left behind

The completion task is idempotent and safe to invoke multiple times.