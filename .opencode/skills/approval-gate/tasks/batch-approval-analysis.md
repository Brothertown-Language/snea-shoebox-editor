# Task: batch-approval-analysis

## Purpose

Analyze interdependencies when multiple issues are approved simultaneously, determine execution order, identify parallelization opportunities, and produce an execution plan for sub-agent dispatch.

## Entry Criteria

- Multiple issues approved at the same time (e.g., `Approved: #660, #662, #621`)
- Each issue has been verified by `verify-authorization`
- User has explicitly authorized implementation

## Exit Criteria

- Each approved issue classified by dependency category
- Dependency graph produced with execution order
- Parallel-safe groups identified
- Execution plan presented to developer in chat
- Non-actionable issues identified and excluded from implementation

## Procedure

### Step 1: Read All Approved Issues

For each approved issue, read the full issue body and comments:

```python
for issue_number in approved_issues:
    issue = github_issue_read(method="get", issue_number=issue_number)
    comments = github_issue_read(method="get_comments", issue_number=issue_number)
    # Store issue data for analysis
```

### Step 2: Classify Each Issue

Determine each issue's category:

| Category | Criteria | Action |
|----------|----------|--------|
| **Must-precede** | Issue A modifies files that Issue B also needs to edit | Execute A before B |
| **Independent** | Issue A and B touch completely different files | Can run in parallel |
| **Conflict-risk** | Issue A and B both modify overlapping files | Serialize or coordinate |
| **Meta/Non-code** | Issue describes behavior/rule with NO code changes | Exclude from implementation |

**Classification heuristics:**

1. **File overlap analysis**: Scan each issue's body for file path references, directory references, or component names that map to files in the repo.
2. **Skill overlap**: Issues using the same skills that mutate shared state (e.g., both update `000-critical-rules.md`) are conflict-risk.
3. **Logical ordering**: When Issue A's output becomes Issue B's input (e.g., A creates a skill that B references), A must precede B.
4. **Scope analysis**: `.opencode/`-only changes vs `src/` changes vs doc-only changes.

### Step 3: Build Dependency Graph

Create a directed graph where:
- Nodes = approved issues
- Edges = "must-precede" relationships
- Groups = sets of issues with no inter-dependencies (parallel-safe)

```markdown
## Dependency Analysis

### Execution Order

**Serial (must be done in order):**
1. #A — must precede #B (shared file: `path/to/file.md`)
2. #B — depends on #A output

**Parallel-safe Group 1:**
- #C (touches `.opencode/skills/X/`)
- #D (touches `src/module_y.py`)

**Parallel-safe Group 2:**
- #E (touches `docs/`)

### Excluded (Non-actionable)
- #F — meta/behavioral issue, no code changes required
```

### Step 4: Determine Execution Strategy

| Strategy | When | How |
|----------|------|-----|
| **Sequential** | Must-precede chain exists | Execute in dependency order |
| **Parallel** | Independent issues | Dispatch via `subagent-driven-development` |
| **Hybrid** | Mix of both | Serial for must-precede, parallel for independent groups |
| **Exclude** | Meta/non-code issues | Report exclusion with reason |

### Step 5: Present Execution Plan to Developer

**MANDATORY: The dependency analysis MUST be visible in chat (not hidden in agent reasoning).**

Format:

```markdown
## Batch Approval — Dependency Analysis

**Approved Issues:** #660, #662, #621, #614, #630

### Classification

| Issue | Category | Files | Dependencies |
|-------|----------|-------|-------------|
| #660 | Meta/Non-code | N/A | None (no code changes) |
| #662 | Independent | `.opencode/skills/` | None |
| #621 | Conflict-risk | `.opencode/guidelines/000-*.md` | Conflicts with #630 |
| #614 | Independent | `src/` | None |
| #630 | Must-precede #621 | `.opencode/guidelines/` | Must complete before #621 |

### Execution Plan

**Phase 1 (Serial):**
1. #630 — must precede #621

**Phase 2 (Parallel-safe):**
- #662 (`.opencode/skills/`)
- #614 (`src/`)

**Phase 3 (After #630):**
- #621 (`.opencode/guidelines/`)

**Excluded:**
- #660 — meta/behavioral issue, no code changes required

Proceeding with execution plan.
```

### Step 6: Execute

After presenting the plan, execute according to the dependency order:

1. **Sequential issues**: Execute one at a time in dependency order
2. **Parallel-safe groups**: Use `subagent-driven-development` skill
3. **Report completion**: After ALL issues complete, report ONCE and HALT ONCE

## Single-Issue Shortcut

**When only ONE issue is approved:** Skip dependency analysis entirely. Proceed directly to standard `verify-authorization` → implementation workflow.

This task is ONLY invoked when TWO OR MORE issues are approved together.

## Classification Detail

### Must-Precede Detection

An issue A must precede issue B when:
- A creates or modifies a file that B references or imports
- A defines a function/class/variable that B uses
- A restructures a directory that B assumes the old layout for
- A adds a dependency that B requires to build

### Conflict-Risk Detection

Two issues are conflict-risk when:
- Both modify the same file (detected via file path mentions)
- Both add content to the same section of a shared document
- Both rename/move the same files
- Both use skills that modify the same state file (e.g., `000-critical-rules.md`)

### Independent Detection

Two issues are independent when:
- They touch completely different file trees
- They use different skills with no overlapping state
- They add new files rather than modifying existing ones
- They can be merged in any order without conflicts

### Meta/Non-Code Detection

An issue is meta/non-code when:
- The body describes behavioral rules without file modifications
- The issue tracks observability or enforcement without requiring code changes
- The "implementation" is just acknowledging a pattern, not writing code
- All success criteria are satisfied by existence of documentation or rules already in place

## Red Flags

**Never:**
- Skip dependency analysis when multiple issues are approved together
- Dispatch parallel subagents for conflict-risk issues without serialization
- Include meta/non-code issues in the implementation plan
- Present dependency analysis only in agent reasoning (MUST be in chat)
- Assume all issues are independent without analysis
- Execute must-precede issues out of order

**Always:**
- Present the full dependency graph to the developer in chat
- Classify every issue before execution
- Execute must-precede issues first
- Group independent issues for parallel dispatch
- Exclude non-actionable issues with explicit reason
- Report each issue's classification in the execution plan