# Task: build-dependency-graph

## Purpose

Assemble the flat item list, perform cross-issue analysis, classify each issue, and build the dependency graph with execution order. Contains the full classification detail tables for must-precede, conflict-risk, independent, meta, superseded, moot, partial implementation, stale assumption, cross-issue sub-issue, and merge-time conflict detection.

## Entry Criteria

- Screening results collected and classifications resolved (from `collect-screening-results`)
- Status inconsistencies reconciled (from `reconcile-status`)
- All approved issues have verified file_references and symbol_references in screening results

## Exit Criteria

- Flat item list assembled (included, excluded, scope-reduced issues identified)
- Cross-issue analysis complete (stale assumptions, supersession, sub-issue pairs, merge-time conflicts)
- Each issue classified by dependency category
- Dependency graph built with execution order and parallel-safe groups
- No additional GitHub API calls needed beyond screening data

## Procedure

### Step 1: Assemble Flat Item List

From the collected screening results, assemble the flat item list:

- For each `included` issue: add its `flat_items` to the execution list
- For each `excluded` issue: add to "Excluded" section with reason
- For each `scope-reduced` issue: add its remaining phases to the execution list
- For issues with `requires_reconciliation: true`: these were handled by `reconcile-status` — use their post-reconciliation classification
- For issues with `requires_developer: true` AFTER reconciliation (only `uncertain` findings): HALT for developer review

### Step 2: Cross-Issue Analysis

Analyze cross-issue relationships using file/symbol references from screening results. **No additional API calls needed** — screening results already contain verified file and symbol references.

#### Cross-Issue Checks

1. **Stale assumptions across issues:** If issue A's `file_references` overlap with issue B's `file_references`, check intent alignment:
   - Same intent → serialize (B before A if B provides the canonical change)
   - Different intent → HALT for developer review

1. **Supersession across issues:** If issue B's `file_references` are a superset of issue A's, and B's scope description fully encompasses A's:
   - Unambiguous → exclude A (superseded by B)
   - Ambiguous → HALT for developer review

1. **Cross-issue sub-issue pairs:** If a parent and its sub-issues are both included:
   - Default: omit sub-issues — parent's cascade covers them
   - Exception: isolated sub-issues with no file overlap → dispatch to own sub-agent
   - Edge case: parent excluded but sub-issues included → include independently

1. **Merge-time conflict risk:** Issues touching the same file in different sections. Noted in execution plan for `assemble-work` handling. Do NOT block execution.

### Step 3: Classify Each Issue

Determine each issue's category based on cross-issue analysis:

| Category | Criteria | Action |
|----------|----------|--------|
| **Must-precede** | Issue A modifies files that Issue B also needs to edit | Execute A before B |
| **Independent** | Issue A and B touch completely different files | Can run in parallel |
| **Conflict-risk** | Issue A and B both modify overlapping files | Serialize or coordinate |
| **Meta/Non-code** | Issue describes behavior/rule with NO code changes | Exclude from implementation |

**Classification heuristics:**

1. **File overlap analysis:** Use `file_references` from screening results. No API calls needed.
1. **Skill overlap:** Issues using the same skills that mutate shared state (e.g., both update `000-critical-rules.md`) are conflict-risk.
1. **Logical ordering:** When Issue A's output becomes Issue B's input (e.g., A creates a skill that B references), A must precede B.
1. **Scope analysis:** `.opencode/`-only changes vs `src/` changes vs doc-only changes.

**Add edges from screening results:**

- Same-intent stale assumption pairs → must-precede edge
- Cross-issue sub-issue pairs → dependency edge (parent covers sub-issues unless isolated)

### Step 4: Build Dependency Graph

Create a directed graph where:

- Nodes = remaining (non-excluded) approved issues
- Edges = "must-precede" relationships (including stale-assumption and cross-sub-issue edges from cross-issue analysis)
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

### Excluded (Pre-Analysis Screening)
- #F — meta/behavioral issue, no code changes required
- #G — already-implemented (PR #M merged)
- #H — superseded by #B

### Scope-Reduced
- #I — partially-implemented (phase 1 done by PR #M; phases 2, 3 remaining)
```

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

### Superseded Detection

Issue A is superseded by work peer B when:

- B's file list is a superset of A's file list
- B's scope description fully encompasses A's scope
- All of A's success criteria would be met by implementing B

**Ambiguous supersession** (partial overlap, unclear which is canonical): HALT for developer review.

### Moot Detection

An issue is moot when:

- Its spec references files/directories that have been restructured or removed since spec creation
- None of its remaining success criteria are achievable given the current codebase state
- The problem it describes no longer exists

### Partial Implementation Detection Heuristic

An issue is partially implemented when:

- A merged PR references the issue number in its body or commits
- Some (but not all) success criteria are already met in the current codebase
- The issue's phases can be mapped to the PR's changes to identify which are done

### Stale Assumption Detection

An issue has stale assumptions when:

- Its spec references specific function names, class names, or file paths that another issue in the work set modifies or deletes
- The reference is integral to the issue's implementation instructions (not just background context)

**Same intent (auto-resolvable):** Both issues want the same outcome for the referenced code.
**Different intent (HALT):** The issues have conflicting goals for the referenced code.

### Cross-Issue Sub-Issue Detection

A cross-issue sub-issue pair exists when:

- Issue A is a parent issue with sub-issues
- One or more of A's sub-issues are also in the approved work set
- Detected via `flat_items` from screening results

### Merge-Time Conflict Detection

Issues have a merge-time conflict risk when:

- They touch the same file but in different sections or with non-contradictory changes
- They are independent during implementation but may produce overlapping diffs
- This is distinct from conflict-risk (which affects implementation order)

## Adversarial Interdependency Verification

**Before trusting spec-claimed dependencies, verify them against actual codebase state.** Use `file_references` and `symbol_references` from screening results to avoid redundant API calls.

### Verify File Overlap Claims Against Actual Code

For each pair of issues with overlapping `file_references`, use srclight to verify actual dependency:
- `srclight_get_dependents` or `srclight_get_callers` to verify import/call chains
- If spec claims "A modifies X which B needs" but srclight shows no dependency → VERIFICATION-GAP
- If srclight shows dependency not mentioned in either spec → MISSING-ELEMENT

### Verify Must-Precede Claims

For each must-precede relationship claimed in specs:
- Check if A actually creates/modifies symbols that B uses
- `srclight_get_callers(symbol_name="<symbol_from_A>", project="<project>")`
- If callers include code from B's scope → dependency verified
- If callers do NOT include code from B's scope → VERIFICATION-GAP

### Verify Independence Claims

For each pair of issues claimed as "independent":
- `srclight_get_dependents(symbol_name="<key_symbol>", project="<project>", transitive=True)`
- If transitive dependents include code from the other issue's scope → NOT independent
- Downgrade from "parallel-safe" to "conflict-risk" or "must-precede"

### Verify Code References Exist

For each file path or symbol from screening `file_references`/`symbol_references`:
- File paths: verify with glob or read that the file exists
- Symbol names: verify with srclight_get_signature that the symbol exists
- If file/symbol does not exist → VERIFICATION-GAP

### Finding Classification

| Finding | Problem Class | Classification | Action |
|--------|---------------|----------------|--------|
| File overlap claimed but no actual dependency | VERIFICATION-GAP | flag-for-review | Re-classify as independent unless other evidence |
| Dependency exists but not mentioned in specs | MISSING-ELEMENT | conditional | Add to dependency graph, adjust execution order |
| Independence claimed but transitive dependency exists | CONFLICTING | conditional | Downgrade to conflict-risk or must-precede |
| Code reference to non-existent file/symbol | VERIFICATION-GAP | flag-for-review | Developer must confirm: planned or typo |

## Enforcement References

- Evidence format + finding classification: see `enforcement/adversarial-verification.md`
- Scope parsing: see `enforcement/scope-parsing.md`
- Auto-dispatch routing: see `enforcement/auto-dispatch-table.md`
- Closed-issue verification: see `enforcement/closed-issue-verification.md`
- Sub-issue graph traversal: see `enforcement/sub-issue-graph-traversal.md`