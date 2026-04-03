---
name: github-sub-issues
description: Multi-task spec sub-issue creation and management workflow. Defines single-task exemption, auto-create workflow, database ID requirement, and phase-level structure for GitHub Issue sub-issues.
license: MIT
compatibility: opencode
---

# GitHub Sub-Issues Workflow

Ensures multi-task specs have proper sub-issue structure before implementation begins.

## When to Use

- Before implementing multi-task spec (MANDATORY)
- When creating parent issue with phases (AUTO-CREATE)
- When verifying sub-issue linkage

## Available Tasks

| Task | Description |
|------|-------------|
| `overview` | Complete sub-issue workflow with auto-create |

## Single-Task vs Multi-Task Exemption

### Single-Task Exemption

**Single-task issues do NOT require sub-issues.**

A spec is "single-task" if:
- Exactly ONE implementation task/phase
- No task decomposition needed
- Entire spec implementable in one unit of work
- No independent concerns requiring separate tracking

**Example - Single-task (NO sub-issue required):**
```
SPEC #100: Fix typo in README
- One task: Fix the typo
- No decomposition needed
```

**Example - Multi-task (SUB-ISSUES REQUIRED):**
```
SPEC #101: Add user authentication
- Concern 1: Database schema (independent deployment unit)
- Concern 2: API endpoints (independent testing unit)
- Concern 3: UI components (independent risk profile)
```

## Sub-Issue Verification Gate

### MANDATORY Check Before Implementation

1. Call `github_issue_read method=get_sub_issues` on parent issue
1. **If empty AND multi-task:**
   - AUTO-CREATE sub-issues (see workflow)
   - DO NOT BLOCK for manual creation
1. **If sub-issues exist:**
   - Verify phase being implemented is among them
   - Proceed with implementation

### FORBIDDEN

- Implementing phase that exists only as text in parent issue body
- Proceeding when `get_sub_issues` returns empty (for multi-task specs) without creating sub-issues
- Assuming markdown checkboxes = task tracking
- Creating step-level sub-issues (create PHASE-level only)

## Auto-Create Workflow

**When AI agent determines spec has multiple independent concerns:**

1. For each PHASE in spec:
   - Create issue: `github_issue_write method=create` with title `[Task: #N] <phase-description>`
   - Get database ID from response
   - Link: `github_sub_issue_write method=add`

2. Post comment: "Created X sub-issues for phase tracking"

3. Proceed with implementation

## Quick Start

Use `/skill github-sub-issues --task overview` for complete workflow.