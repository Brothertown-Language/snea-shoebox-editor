---
name: conflict-resolution
description: Use when resolving git conflicts during rebase, merge, or cherry-pick operations. Triggers on: conflict, merge conflict, rebase conflict, resolve conflict, cherry-pick conflict, conflict resolution, intent conflict, conflict classification.
---

# Skill: conflict-resolution

## Overview

Procedural workflow for classifying and resolving git conflicts with proper intent preservation. Prevents silent erosion of committed work during rebase, merge, cherry-pick, or any git operation that produces conflicts.

## Persona

You are a Conflict Resolution Specialist. Your focus is ensuring no committed work or spec intent is silently lost during git conflict resolution.

## Invocation

- **Automatic**: Invoked by `git-workflow` tasks when conflicts are detected during rebase/merge
- **Manual**: `/skill conflict-resolution` — Overview only
- **Manual**: `/skill conflict-resolution --task classify-and-resolve` — Full classification and resolution procedure
- **Manual**: `/skill conflict-resolution --task completion` — Invoke when workflow halts at any point

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `classify-and-resolve` | Detect, classify, and resolve conflicts by tier | ~550 |
| `completion` | Ensure mandatory terminal-state dispatch occurred; remediate if not; report status | ~200 |

## Conflict Classification Tiers

Before resolving ANY conflict, classify it:

| Tier | Name | Criteria | Agent Action |
|------|------|----------|-------------|
| 1 | **Trivial** | Whitespace, formatting, reordering of unchanged lines | Auto-resolve, silent |
| 2 | **Textual but safe** | Same intent on both sides, just different text | Auto-resolve, note in chat |
| 3 | **Intent conflict** | Different goals, or resolution could alter spec compliance | HALT, flag for developer review |

**Classification rule:** When in doubt, classify UP to the next tier. If unsure whether something is Tier 2 or Tier 3, treat it as Tier 3.

## Notification Format

### Tier 2 (Chat only)

```
**Conflict Resolution (Tier 2 - Textual):**
- File: <path>
- Reason: <why it's textual but safe>
- Resolution: <which side was accepted>
```

### Tier 3 Minor (Chat only)

```
**⚠️ Intent Conflict Detected (Tier 3 - Minor):**
- File: <path>
- Feature branch intent: <what>
- Parent branch intent: <what>
- Resolution: <agent recommendation, awaiting developer confirmation>
```

### Tier 3 Complex (Chat + GitHub Issue)

Chat notification plus persistent GitHub Issue with `conflict-resolution` label for tracking.

## Anti-Patterns

**🚫 NEVER:**
- Resolve ALL conflicts with `git checkout --theirs` or `git checkout --ours`
- Use `git rebase --strategy-option=theirs/ours` as blanket resolution
- Skip reading the conflict content before resolving
- Assume formatting conflicts are always trivial (could hide intent changes)
- Continue rebase after resolving intent conflicts without verifying spec compliance
- Create commits that silently drop committed work

**✅ ALWAYS:**
- Classify every conflict into a tier before resolving
- When in doubt, classify UP (Tier 2 vs Tier 3 → Tier 3)
- Verify spec compliance after resolving all conflicts
- Notify developer for Tier 3 conflicts
- Create GitHub Issue for complex Tier 3 conflicts
- Preserve feature branch intent unless developer says otherwise

## Integration Points

| Skill | When |
|-------|------|
| `git-workflow` `--task review-prep` | Automatically invokes this skill when rebase produces conflicts |
| `git-workflow` `--task implementation` | May invoke if mid-implementation merge produces conflicts |

## Cross-References

- Related skills: `git-workflow` (branch management, rebase operations)
- Related guidelines: `000-critical-rules.md` → "Critical Violation: Blind Conflict Resolution"

**⚠️ COMPLETION GUARANTEE:** If this workflow halts at ANY point — including error, failure, or early termination — you MUST invoke `--task completion` before halting. The completion subtask ensures mandatory steps are never skipped. It is idempotent and safe to invoke multiple times.