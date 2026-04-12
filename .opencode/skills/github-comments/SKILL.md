---
name: github-comments
description: Use when posting comments to GitHub Issues or PRs. Triggers on: comment, progress update, issue comment, PR comment, post to GitHub, byline, status indicator.
type: technique
license: MIT
compatibility: opencode
---

# GitHub Comment Protocol

## Overview

Ensures all comments on issues and PRs are substantive and stakeholder-meaningful. Progress reports go to chat only — never to issue comments. Comments exist for stakeholders; only content that helps stakeholders understand what changed or why deserves a comment.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `format-comment` | Byline format, status icons, copy editor attribution | ~400 |
| `post-completion` | Issue completion comments (substantive only), spec alteration format | ~400 |

## Invocation

- `/skill github-comments --task format-comment` - Format a comment with correct byline
- `/skill github-comments --task post-completion` - Post completion/closure comment (substantive only)
- `/skill github-comments` - Overview only

## Operating Protocol

1. **Substantive only:** Post issue comments ONLY when they convey stakeholder-meaningful information (what changed, why, or response to questions).
2. **No workflow comments:** Never post instructional, tracking, status, or lifecycle comments (e.g., "Starting execution", "Approval Tracking", "Created sub-issue for phase: X").
3. **Approval via labels:** Approval state is tracked via `needs-approval` label — never via comments.
4. **Byline always appended:** Every comment and issue body ends with `🤖 <AgentName> (<ModelID>) <status>`.
5. **Audit findings are internal:** Auditor reports are guidance for the agent. Post a comment ONLY if a spec requires substantive revision that stakeholders need to understand.
6. **Respond to user questions:** Always reply via GitHub comment when a user asks a question on an issue.

## Substantive Comment Gate

**A comment is substantive if and only if it conveys information a stakeholder needs to understand what changed or why.**

| Comment Type | Substantive? | Action |
|-------------|-------------|--------|
| "Approval Tracking: Approvals tracked via comments" | No | **ELIMINATE** |
| "Created by" standalone comment | No | **MOVE to issue body footer** |
| "Ready for approval workflow" instructions | No | **ELIMINATE** |
| "Created sub-issue for phase: X" | No | **ELIMINATE** |
| Hierarchy tree report | No | **ELIMINATE** |
| "Starting execution" | No | **ELIMINATE** |
| Step evidence per step | No | **ELIMINATE** |
| Verification result | No | **ELIMINATE** |
| Raw auditor report | No | **ELIMINATE** |
| Substantive spec change explanation | **Yes** | **KEEP** |
| Closing summary (explains what changed) | **Yes** (conditional) | **KEEP if substantive** |
| Production data violation documentation | **Yes** | **KEEP** |
| Squash violation report | **Yes** | **KEEP** |
| Response to user question on issue | **Yes** | **KEEP** |

## Cross-References

- Related skills: `git-workflow` (post comment when PR created), `spec-auditor` (findings are internal guidance)
- Related guidelines: `000-critical-rules.md` (progress reports, ignoring comments), `010-approval-gate.md` (authorization via labels)