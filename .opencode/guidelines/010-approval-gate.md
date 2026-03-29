# Approval Gate

> **See `.opencode/skills/approval-gate/SKILL.md` for complete procedural workflow including:**
> - Spec + authorization requirements
> - Sub-issue verification gate
> - Single-task exemption
> - Re-evaluation checklist
> - Bug report response

## Tier 0: Zero Tolerance Rules

**These rules are inviolable. Violation is a protocol breach.**

### Mandatory Requirements

| Requirement | Rule |
|-------------|------|
| **Spec before code** | NO code/guideline changes WITHOUT approved spec |
| **Authorization required** | NO implementation WITHOUT explicit `"approved"` or `"go"` |
| **Branch first** | Create feature branch BEFORE any file modification |
| **Human-only merge** | Agents MUST NEVER merge PRs |
| **MCP tools** | Use PyCharm/GitHub MCP for file operations when available |
| **Silent halt** | HALT after completion, after PR creation — no prompts |
| **PR timing** | PRs require explicit `"create a PR"` instruction |
| **Issue closure** | Close issues ONLY after PR merge confirmed |

### Authorization Scope

- **Issue-bound**: Authorization applies ONLY to the specific issue where it was given
- **Session-bound**: New session = new authorization required (no carryover from previous sessions)
- **Single-use**: Authorization for current phase/task only within that issue
- **External input invalidates**: Bug reports require re-authorization
- **Revision ≠ implementation**: Spec updates don't authorize code changes

**🚫 CRITICAL: Old authorizations do NOT apply:**
- "Approved #332" in previous session → NOT VALID for new session
- Previous session authorization → NOT VALID for new issue/spec
- Authorization is ZERO-BASED — every task needs NEW authorization

### Revision Revokes Approval (MANDATORY)

**Any modification to a spec or task document MUST immediately revoke approval.**

When a spec is modified:
1. **Status transitions to pending**: `STATUS: X.Y` → `STATUS: X.Y (REVISED - NEEDS APPROVAL)`
2. **Label applied**: Add `needs-approval` label to the issue
3. **Agent MUST HALT**: Do NOT proceed with implementation
4. **Fresh authorization required**: New explicit approval needed before implementation

**Note**: When using `revise` command, the agent MAY post comments explaining changes but MUST NOT proceed with implementation. `revise` commands allow only documentation updates, never code changes.

**This applies to:**
- Any modification to the spec body (requirements, steps, criteria)
- Any modification to task steps or acceptance criteria
- Typo fixes in spec content (use GitHub comments for clarifications instead)
- Minor clarifications that affect interpretation

**Exempt from approval revocation:**
- STATUS marker updates (`☐ → ☑`, `1.1 → 1.2`)
- Progress comments added to issue
- Bug report additions (separate from spec content changes)

### Sub-Issue Verification (Multi-task Specs)

**Before implementing multi-task specs:**

1. Call `github_issue_read(method="get_sub_issues", issue_number=N)`
2. If empty AND multi-task → AUTO-CREATE phase-level sub-issues
3. Single-task specs are exempt from sub-issues

### Bug Report Response

When bug report requires code changes:

1. Add `needs-approval` label
2. Post additional spec comment
3. HALT immediately
4. Wait for explicit `go` or `approved`

## What This Guideline Does NOT Cover

**The skill handles procedural workflow:**

- Spec + approval requirements details
- Re-evaluation checklist
- Pre-implementation verification steps
- Single-task exemption logic
- Authorization scope rules
- Workflow decision tree

**See the skill for complete implementation details.**

## Related Guidelines

| Guideline | Purpose |
|-----------|---------|
| `000-critical-rules.md` | Critical violations and auditor enforcement |
| `020-go-prohibitions.md` | GO command restrictions |
| `120-github-issue-first.md` | Issue-first strategy and sub-issues |
| `124-github-archive-workflow.md` | Issue closure timing |
| `github-sub-issues/SKILL.md` | Sub-issue creation workflow |
| `pr-creation-workflow/SKILL.md` | PR creation timing |