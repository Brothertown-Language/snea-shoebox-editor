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

Each parallel issue includes dispatch context:
- #662 (`.opencode/skills/`) → `worktree_path: .worktrees/spec-662`
- #614 (`src/`) → `worktree_path: .worktrees/spec-614`

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

### Step 6.5: Capture Dev Base Hash (Before Dispatch)

Before dispatching any parallel worktrees, the orchestrating agent MUST capture the current dev branch hash:

```bash
git rev-parse origin/dev
```

This `dev_base_hash` MUST be included in the dispatch context for each parallel issue. See Step 7 for the complete dispatch context schema.

### Step 7: Dispatch Context for Parallel Issues

For each issue in a parallel-safe group, the dispatch context MUST include worktree information:

```yaml
# Dispatch Context Per Issue
issue: <number>
branch: "spec/<short-name>"
worktree_path: ".worktrees/spec-<short-name>"
dev_base_hash: "<7-char-sha>"
env_vars:
  WORKTREE_PATH: ".worktrees/spec-<short-name>"
  BRANCH_NAME: "spec/<short-name>"
  GIT_OWNER: "<from-session>"
  GIT_REPO: "<from-session>"
  DEV_NAME: "<from-session>"
  DEV_EMAIL: "<from-session>"
```

The `worktree_path` is derived from the branch name by replacing `/` with `-`:
- Branch `spec/foo` → Worktree path `.worktrees/spec-foo`
- Branch `feature/bar` → Worktree path `.worktrees/feature-bar`

The `dev_base_hash` ensures all parallel worktrees start from the same base commit on `dev`.

### Step 8: Write Batch State File

After the execution plan is presented and accepted, write a batch state file that persists the plan for sub-agent dispatch:

```bash
mkdir -p .opencode/tmp
```

**File:** `.opencode/tmp/batch-<timestamp>.md`

**Contents:**
```markdown
# Batch Execution Plan

**Session:** <timestamp>
**Authorized Issues:** #A, #B, #C
**Authorization Context:** User said "approved" on <date>

## Execution Order

1. #A — <title> (touches <files>)
2. #B — <title> (depends on #A, touches <files>)
3. #C — <title> (independent, touches <files>)

## Completed

- [ ] #A — branch: <name>, status: pending
- [ ] #B — branch: <name>, status: pending
- [ ] #C — branch: <name>, status: pending

## Results

(Agent appends completion summaries here as issues finish)
```

**Key properties:**
- Session-scoped via timestamp — stale files are detectable
- Survives context turnover — agent can re-read after HALT
- Hybrid: in-line context passed to each sub-agent + file backup for recovery
- Cleaned up after batch completes (or on new session start)

### Step 9: Yield to batch-orchestrate

After the batch state file is written, yield control to `implementation-workflow --task batch-orchestrate`:

```
/skill implementation-workflow --task batch-orchestrate
```

**batch-orchestrate** reads the batch state file and handles:
- Creating worktrees for the batch
- Dispatching sub-agents for each issue
- Collecting results and updating batch state
- Running review-prep after all issues complete

This handoff ensures:
- No HALTs between issues in the batch
- Each sub-agent gets isolated context
- The orchestrator stays clean — no implementation pollution
- Batch state survives context turnover

## Single-Issue Shortcut

**When only ONE issue is approved:** Skip dependency analysis entirely. The `batch-orchestrate` task handles single-issue dispatch as the default code path (single-item batch with one sub-agent).

**This task is ONLY invoked when TWO OR MORE issues are approved together for full dependency analysis.** For single issues, the flow goes directly: `verify-authorization` → `implementation-workflow/orchestrate` → `batch-orchestrate`.

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