---
name: issue-operations
description: Platform-agnostic issue operations dispatcher. Routes to GitHub MCP or GitBucket API based on GIT_PLATFORM. Triggers on: create issue, new issue, spec creation, submit issue, issue, bug report, comment, progress update, issue comment, PR comment, post to GitHub, byline, status indicator, sub-issue, phase issue, multi-task, create sub issue, link issue, task breakdown, subtask, parent issue, close issue, verify merge.
type: technique
license: MIT
compatibility: opencode
---

# Skill: issue-operations

## Overview

Platform-agnostic Issue Operations dispatcher. Detects `GIT_PLATFORM` from session init and routes all issue tracking operations to the appropriate platform sub-skill. Absorbs and replaces `github-issue-creation`, `github-comments`, and `github-sub-issues`.

## Persona

You are an Issue Operations Dispatcher. Your focus is ensuring all issue operations follow the spec-first workflow with proper validation, labeling, auditor integration, and platform-aware routing.

## Architecture

```
issue-operations/                     # Dispatcher — workflow logic, platform routing
  SKILL.md
  tasks/
    pre-creation.md                   # Validation (absorbed from github-issue-creation)
    single-task-check.md              # Multi-task detection
    creation.md                       # Create with labels/byline
    post-creation.md                  # Auditors, plan trigger
    comment.md                        # Channel routing (absorbed from github-comments)
    close.md                          # Post-merge closure
    link-sub-issue.md                 # Sub-issue hierarchy (absorbed from github-sub-issues)
    verify-merge.md                   # PR merge verification
    capabilities.md                   # Capability probe/discovery
    completion.md                     # Mandatory completion
  platforms/
    github-mcp/
      SKILL.md                        # Capability manifest (dynamic: queries GitHub MCP)
      tools/                          # Thin wrappers around github_* MCP tools
    gitbucket-api/
      SKILL.md                        # Capability manifest (static: probed v4.46.0)
      tools/                          # Existing Python client + tests
      tasks/                          # Existing issue/label/repo/error-recovery tasks
      reference/                      # OpenAPI spec
```

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `pre-creation` | Validate before creating issue (conflicts, superseded, staleness) | ~240 |
| `single-task-check` | Determine if spec needs a plan issue (multi-task) or is single-task | ~160 |
| `creation` | Create issue with proper title, labels, byline via platform routing | ~200 |
| `post-creation` | Invoke auditors, trigger plan creation for multi-task specs | ~180 |
| `comment` | Channel routing — substantive comment gate, format, posting | ~400 |
| `close` | Post-merge closure with parent/child verification | ~250 |
| `link-sub-issue` | Sub-issue linking via platform API or comment-based fallback | ~200 |
| `verify-merge` | Verify PR merge before closing issues | ~200 |
| `capabilities` | Probe platform capabilities (dynamic MCP query or static manifest) | ~150 |
| `completion` | Ensure mandatory completion steps run regardless of workflow outcome | ~200 |

## Invocation

- `/skill issue-operations --task pre-creation` - BEFORE creating issue (validation)
- `/skill issue-operations --task single-task-check` - Check if spec is single-task
- `/skill issue-operations --task creation` - Create issue with enforcement
- `/skill issue-operations --task post-creation` - After creation (auditors, sub-issues)
- `/skill issue-operations --task comment` - Post substantive comment with byline
- `/skill issue-operations --task close` - Close issue after PR merge
- `/skill issue-operations --task link-sub-issue` - Link/create sub-issue to parent
- `/skill issue-operations --task verify-merge` - Verify PR merge status
- `/skill issue-operations --task capabilities` - Probe platform capabilities
- `/skill issue-operations --task completion` - Invoke when workflow halts at any point
- `/skill issue-operations` - Overview only

**COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps (labels, auditors, sub-issues, status report) are never skipped. It is idempotent and safe to invoke multiple times.

## Platform Routing

### Detection

The dispatcher detects `GIT_PLATFORM` from session init output:

| `GIT_PLATFORM` | Platform Sub-Skill |
|----------------|-------------------|
| `github` | `platforms/github-mcp/` |
| `gitbucket` | `platforms/gitbucket-api/` |
| (unset) | `platforms/github-mcp/` (default) |

### Target Parameter

```yaml
target:
  owner:     # overridden for submodules
  repo:        # overridden for submodules
  platform:   # rarely overridden (defaults to session GIT_PLATFORM)
```

### Capability Resolution (Hybrid)

1. If platform MCP tools present with `capabilities()` → use dynamic capabilities
2. If no MCP or no capabilities endpoint → fall back to static manifest in platform SKILL.md
3. If neither available → conservative defaults (basic CRUD only)

Each platform sub-skill decides internally whether to query MCP or read static manifest. The dispatcher never sees this decision.

### Fallback Patterns

| Operation | GitBucket Status | Fallback |
|----------|----------------|----------|
| Create issue | WORKS | — |
| List/get issues | WORKS | — |
| Update issue (PATCH) | BROKEN | Add comment with change content |
| Close issue | BROKEN | Add comment "Closing: reason" |
| Revise spec | BROKEN | Add comment with full revised body |
| Add/update/delete comment | WORKS | — |
| Sub-issues | BROKEN | Comment-based linking on parent issue |
| Search issues/PRs | BROKEN | Iterative listing + client-side filter |
| Create/list/get PRs | WORKS | — |
| Merge PR | WORKS | — |

## Operating Protocol

1. **Mandatory invocation (no decision point):** The agent MUST invoke this skill when:
   - Agent is about to create an issue
   - Agent is about to post a comment to an issue/PR
   - Agent is about to close an issue
   - Agent is about to link sub-issues
   - DO NOT use direct `github_issue_write` / `github_add_issue_comment` / `github_sub_issue_write` calls
   - ALWAYS route through this skill for validation and platform routing

2. **Workflow sequence (issue creation):**
   - Phase 1: `pre-creation` → Validate spec, check for conflicts/superseded
   - Phase 2: `single-task-check` → Determine if spec needs a plan issue
   - Phase 3: `creation` → Create issue with labels and byline (routed to platform)
   - Phase 4: `post-creation` → Invoke auditors, trigger plan creation via writing-plans if multi-task

3. **Comment workflow:**
   - `comment` task → Substantiveness gate → Format with byline → Post via platform

4. **Sub-issue workflow:**
   - `link-sub-issue` task → Platform with sub-issue API → formal link; Platform without → comment-based fallback

## Substantive Comment Gate

**A comment is substantive if and only if it conveys information a stakeholder needs to understand what changed or why.**

| Comment Type | Substantive? | Action |
|-------------|-------------|--------|
| "Approval Tracking: Approvals tracked via comments" | No | ELIMINATE |
| "Created by" standalone comment | No | MOVE to issue body footer |
| "Ready for approval workflow" instructions | No | ELIMINATE |
| "Created sub-issue for phase: X" | No | ELIMINATE |
| Hierarchy tree report | No | ELIMINATE |
| "Starting execution" | No | ELIMINATE |
| Step evidence per step | No | ELIMINATE |
| Verification result | No | ELIMINATE |
| Raw auditor report | No | ELIMINATE |
| Substantive spec change explanation | Yes | KEEP |
| Closing summary (explains what changed) | Yes (conditional) | KEEP if substantive |
| Production data violation documentation | Yes | KEEP |
| Squash violation report | Yes | KEEP |
| Response to user question on issue | Yes | KEEP |

## Issue Tracking Required — Platform Routing

**When issue tracking tools are NOT available, the agent MUST refuse planning work entirely.**

### NO FALLBACK TO LOCAL FILES

- **PROHIBITED**: Using `plans/SPEC-*.md` files as fallback when issue tracking is unavailable
- **PROHIBITED**: Creating local plan files when issue tracking is unavailable
- **PROHIBITED**: Proceeding with implementation without issue tracking

### REQUIRED ACTION

If issue tracking tools are unavailable:
1. STOP immediately
2. Report: "Issue tracking tools unavailable. Cannot create or track specs without issue tracking."
3. Wait for issue tracking to be restored before proceeding

## Sub-Issue Fallback Detail

When platform lacks `sub_issue_write` API:
1. Post structured comment on parent issue listing sub-issue numbers
2. Dispatcher records which method was used (formal link vs comment) for later closure operations
3. Sub-issue closure queries parent comments to find children

## Search Fallback Detail

When platform lacks search API:
1. List PRs/issues with `direction=desc&sort=created&per_page=30`
2. Scan each item body for reference pattern (`Fixes #N`, `#N`)
3. Stop on first match — most recent PRs are most likely to be relevant
4. Paginate only if no match found on first page

## PATCH Fallback Detail

When platform PATCH endpoint is broken (returns 404):
- All mutations on existing issues are comments
- Title change → comment "Title updated: New Title"
- Body change → comment with full revised body
- State change → comment "Closing: reason" / "Reopening: reason"

## Interdependencies

| Skill | Purpose | Integration Point |
|-------|---------|-------------------|
| `spec-auditor` | Orchestrate spec quality audit | Run BEFORE approval |
| `approval-gate` | Enforce authorization | Run AFTER issue created |
| `writing-plans` | Plan issue creation | Invoke for multi-task specs after creation |

## When to Invoke

| Trigger | Task |
|---------|------|
| Creating new `[SPEC]` issue | `pre-creation` → `single-task-check` → `creation` → `post-creation` |
| Creating new `[Task]` issue | `creation` (skip validation) |
| Posting comment | `comment` |
| Closing issue post-merge | `close` |
| Linking sub-issues | `link-sub-issue` |
| Verifying PR merge | `verify-merge` |
| Agent about to call `github_issue_write` directly | STOP → invoke this skill instead |

## Critical Rules

### NEVER DO

- Create issues via direct `github_issue_write` calls (bypasses validation)
- Skip `needs-approval` label for new specs
- Create sub-issues for single-task specs
- Skip auditor invocation for multi-task specs
- Create issues with conflicting/overlapping objectives
- Create sub-issues directly under spec (sub-issues go under plan)
- Post non-substantive comments to issues

### ALWAYS DO

- Invoke `pre-creation` task before creating issue
- Apply `needs-approval` label to new specs
- Add creation byline in issue body footer
- Invoke auditors before approval
- Check for superseding/conflicting issues
- For multi-task specs, invoke `writing-plans` for plan creation
- Route all operations through platform sub-skills
- Use `./tmp/` for temporary files (never `/tmp/`)

## Task Dependencies

```
pre-creation → single-task-check → creation → post-creation
                                            ↓
                                     (if multi-task)
                                            ↓
                                      writing-plans skill
                                            ↓
                                      plan issue (with sub-issues under plan)
```

## Enforcement

**This skill is MANDATORY for all issue operations.**

Direct `github_issue_write` / `github_add_issue_comment` / `github_sub_issue_write` calls bypassing this skill are a CRITICAL GUIDELINE VIOLATION.

When creating a new issue:
1. STOP before calling platform API directly
2. Invoke `/skill issue-operations --task pre-creation`
3. Follow validation results (HALT if conflicts)
4. Invoke `/skill issue-operations --task creation`
5. Invoke `/skill issue-operations --task post-creation`

## Submodule Provenance Issues

Submodule provenance issues are created as part of the `git-workflow` provenance task, not through this skill's standard flow. See `git-workflow/tasks/provenance.md` for the complete implementation.

### Provenance Issue Creation Pathway

When the `git-workflow` provenance task creates an issue in a submodule repository:

| Aspect | Standard | Provenance |
| -- | -- | -- |
| Invocation | Via this skill | Via `git-workflow --task provenance` |
| Target repo | Parent repo | Submodule repo |
| Labels | `needs-approval` | None (provenance tracking is informational) |
| Title format | `[SPEC]`, `[SPEC-FIX]`, etc. | `Sync from <parent-repo>/<parent-branch>: ...` or `Release ...` |
| Body | Spec content | Provenance metadata (parent refs, tier info) |
| Byline | Required | Required |

### Key Differences

- **No pre-creation validation:** Provenance issues are created automatically during git workflow
- **No plan creation:** Provenance issues are standalone tracking records
- **No auditor invocation:** Provenance issues are informational records
- **Three-tier fallback:** Provenance gracefully falls back through tiers without HALT

### Cross-Reference

For the provenance issue body format and tier-specific details, see `git-workflow/tasks/provenance.md`.

## Sub-Agent Tasks

### Execution Mode Table

| Task | Words | Mode |
|------|-------|------|
| `pre-creation` | ~240 | inline |
| `single-task-check` | ~160 | inline |
| `creation` | ~200 | inline |
| `post-creation` | ~180 | inline |
| `comment` | ~400 | inline |
| `close` | ~250 | inline |
| `link-sub-issue` | ~200 | inline |
| `verify-merge` | ~200 | inline |
| `capabilities` | ~150 | inline |
| `completion` | ~200 | inline |

All tasks are under 1,000 words — inline execution. No sub-agent dispatch needed.

## Live Verification: Issue Operations Evidence (MANDATORY)

**Each factual claim about platform state, issue state, and issue relationships MUST be verified via tool call before acting. Assertions without tool-call artifacts are VERIFICATION-GAP findings per `065-verification-honesty.md`.**

| Claim | Verification Action | Tool Call | Problem Class |
|-------|-------------------|-----------|---------------|
| "Issue #N exists" | Verify via platform API | `github_issue_read(method="get", issue_number=N)` | MISSING-ELEMENT |
| "PR #N is merged" | Verify merge status | `github_pull_request_read(method="get", pullNumber=N)` → check `merged` field | VERIFICATION-GAP |
| "Platform supports sub-issues" | Probe capabilities | `issue-operations --task capabilities` | CONFLICTING |
| "Issue has `needs-approval` label" | Verify label presence | `github_issue_read(method="get_labels", issue_number=N)` | VERIFICATION-GAP |
| "All sub-issues closed" | Verify each sub-issue state | `github_issue_read(method="get_sub_issues", issue_number=N)` → check each closed | VERIFICATION-GAP |
| "No conflicting spec exists" | Search for overlapping issues | `github_search_issues(query="label:spec <keyword>")` | CONFLICTING |
| "Session init has GIT_OWNER/GIT_REPO" | Verify session values | Check session init output | MISSING-ELEMENT |

**Evidence artifact:** Tool call results for each claim before the operation proceeds.

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| Issue not found | MISSING-ELEMENT | flag-for-review | HALT — cannot operate on missing issue |
| PR not merged | VERIFICATION-GAP | flag-for-review | HALT — do not close issue |
| Platform lacks capability | CONFLICTING | auto-fix | Use fallback pattern from SKILL.md |
| Label missing | VERIFICATION-GAP | auto-fix | Add missing label |
| Sub-issues still open | VERIFICATION-GAP | flag-for-review | Do not close parent |
| Conflicting spec found | CONFLICTING | flag-for-review | HALT — report conflict |
| Session values missing | MISSING-ELEMENT | flag-for-review | HALT — cannot construct API calls |

## Cross-Reference Verification (MANDATORY)

**🚫 CRITICAL: Each cross-reference must be verified against actual skill content. Assertions without verification are VERIFICATION-GAP findings.**

| Reference | Verification | Finding Class |
| -- | -- | -- |
| `spec-auditor` in Cross-References | File exists at `.opencode/skills/spec-auditor/SKILL.md` | MISSING-TRACEABILITY if missing |
| `approval-gate` in Cross-References | File exists at `.opencode/skills/approval-gate/SKILL.md` | MISSING-TRACEABILITY if missing |
| `writing-plans` in Cross-References | File exists at `.opencode/skills/writing-plans/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` in Cross-References | File exists at `.opencode/skills/git-workflow/SKILL.md` | MISSING-TRACEABILITY if missing |
| `spec-auditor` ground-truth subtask | File exists at `.opencode/skills/spec-auditor/tasks/ground-truth.md` | MISSING-TRACEABILITY if missing |
| `065-verification-honesty.md` metadata extension | Guideline contains "Metadata Verification Extension" section | CONFLICTING if missing |
| Task table entry `pre-creation` | File exists at `.opencode/skills/issue-operations/tasks/pre-creation.md` | MISSING-TRACEABILITY if missing |
| Task table entry `creation` | File exists at `.opencode/skills/issue-operations/tasks/creation.md` | MISSING-TRACEABILITY if missing |
| Task table entry `close` | File exists at `.opencode/skills/issue-operations/tasks/close.md` | MISSING-TRACEABILITY if missing |
| Task table entry `verify-merge` | File exists at `.opencode/skills/issue-operations/tasks/verify-merge.md` | MISSING-TRACEABILITY if missing |
| Task table entry `link-sub-issue` | File exists at `.opencode/skills/issue-operations/tasks/link-sub-issue.md` | MISSING-TRACEABILITY if missing |
| Task table entry `comment` | File exists at `.opencode/skills/issue-operations/tasks/comment.md` | MISSING-TRACEABILITY if missing |
| Platform sub-skills | Files exist at `platforms/github-mcp/SKILL.md` and `platforms/gitbucket-api/SKILL.md` | MISSING-TRACEABILITY if missing |
| `git-workflow` provenance task | Task exists at `.opencode/skills/git-workflow/tasks/provenance.md` | MISSING-TRACEABILITY if missing |

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
| Platform sub-skill missing | MISSING-TRACEABILITY | flag-for-review | Platform support may have changed |

**Adversarial cross-reference:** The `spec-auditor --task ground-truth` subtask (Phase 1 of spec #827) performs adversarial verification of metadata claims including sub-issue state, label accuracy, and authorization currency — all of which are core concerns for issue operations. When this skill encounters a label or sub-issue state claim that may be stale or inaccurate, invoke `spec-auditor --task ground-truth` to verify. See `065-verification-honesty.md` → "Metadata Verification Extension" for the extended principle.

## Cross-References

- Related skills: `spec-auditor`, `approval-gate`, `writing-plans`, `git-workflow`, `spec-auditor` (ground-truth adversarial verification)
- Related guidelines: `010-approval-gate.md`, `000-critical-rules.md`, `065-verification-honesty.md` (metadata verification extension)
- Authorization classification: See `010-approval-gate.md` Action Authorization Classification
- Platform sub-skills: `platforms/github-mcp/SKILL.md`, `platforms/gitbucket-api/SKILL.md`