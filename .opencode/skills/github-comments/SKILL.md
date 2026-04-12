---
name: github-comments
description: Use when posting comments to GitHub Issues or PRs. Triggers on: comment, progress update, issue comment, PR comment, post to GitHub, byline, status indicator.
type: technique
license: MIT
compatibility: opencode
---

# GitHub Comment Protocol

## Overview

Ensures all comments on issues and PRs follow correct format, are posted at the right time, and preserve history by preferring comments over body edits. Progress reports go to chat only — never to issue comments.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `format-comment` | Byline format, status icons, copy editor attribution | ~400 |
| `post-progress` | Chat progress reports (mandatory after every task) | ~350 |
| `post-completion` | Issue closure comments, spec alteration format | ~400 |

## Invocation

- `/skill github-comments --task format-comment` - Format a comment with correct byline
- `/skill github-comments --task post-progress` - Post progress report to chat
- `/skill github-comments --task post-completion` - Post completion/closure comment
- `/skill github-comments` - Overview only

## Operating Protocol

1. **Chat for progress, Issues for state:** Implementation progress → chat only. State changes (PR created, closed, blocked) → issue comment.
2. **Byline always appended:** Every comment and body update ends with `🤖 <AgentName> (<ModelID>) <status>`.
3. **Append never replace:** Issue body attribution is append-only — never overwrite existing bylines.
4. **No dialog prompts:** Never post "awaiting authorization" or "ready when you are" in comments. Use HALT protocol.
5. **Substantive changes get comments:** Non-substantive changes (STATUS, typos, cross-refs) do NOT require comments.
6. **Audit findings are internal:** Spec-auditor findings → act on them, don't post as comments. Post a comment ONLY for substantive revisions.
7. **Respond to user questions:** Always reply via GitHub comment when a user asks a question on an issue.

## Cross-References

- Related skills: `git-workflow` (post comment when PR created), `spec-auditor` (findings are internal guidance)
- Related guidelines: `000-critical-rules.md` (progress reports, ignoring comments), `010-approval-gate.md` (authorization comments)