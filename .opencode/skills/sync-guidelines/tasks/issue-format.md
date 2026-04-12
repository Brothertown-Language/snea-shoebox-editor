# Task: issue-format

## Purpose

Structured template for sync issue content with classification analysis and file contents.

## Template

```markdown
# [SYNC] {direction}: {count} files from {source_repo}

**Source:** {source_owner}/{source_repo}
**Commit:** [{short_sha}](commit_url)
**Direction:** Push | Pull
**Sync Method:** Issue-based (intelligent inspection, no patterns)

## Classification Analysis

### File: {filepath}

**Content Read:** Yes (full file analyzed)

**Analysis:**
- {finding_1}
- {finding_2}
- {finding_3}

**Project-Specific Content Found:**
- {specific content or "None"}

**Classification:** ✅ Core / 🚫 Project-Specific / ⚠️ Uncertain

---

{Repeat for each file}

## Files to Sync (Core Only)

| File | Classification | Key Reason |
|------|---------------|------------|
| {path} | Core | {reason} |

## Files Not Synced

| File | Classification | Key Reason |
|------|---------------|------------|
| {path} | Project-Specific | {reason} |

## File Contents

### {filename}

```{language}
{full file content}
```

## Verification

- Source commit: [{sha[:8]}](url)
- All files read and analyzed: Yes
- Pattern-based classification used: No

---
*Created by sync-guidelines skill*
*Classification via intelligent content inspection*
```

## Key Requirements

- Every file MUST be read and analyzed (no pattern-based classification)
- Classification reasoning MUST be documented in issue
- Project-specific content MUST be identified explicitly
- File contents MUST be included for human review
- Verification section MUST confirm intelligent inspection was used

## Context Required

- Related skills: `sync-guidelines` (parent skill)
- Related tasks: `sync-push`, `sync-pull`