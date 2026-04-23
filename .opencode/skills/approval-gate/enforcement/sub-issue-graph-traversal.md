# Sub-Issue Graph Traversal Module

## Overview

Sub-issue graph traversal verifies the complete issue hierarchy before implementation proceeds. This module defines the algorithm for traversing sub-issue graphs, depth limits, and edge types.

## Traversal Algorithm

```
function traverse_sub_issue_graph(parent_issue_number, depth=0, max_depth=5):
    if depth > max_depth:
        HALT with "Sub-issue graph exceeds max depth"
    
    sub_issues = github_issue_read(method=get_sub_issues, issue_number=parent_issue_number)
    
    results = []
    for sub in sub_issues:
        # Verify sub-issue state against live data
        live_state = github_issue_read(method=get, issue_number=sub.number)
        
        # Edge type classification
        edge_type = classify_edge(parent_issue_number, sub.number)
        
        result = {
            number: sub.number,
            title: live_state.title,
            state: live_state.state,
            state_reason: live_state.state_reason,
            edge_type: edge_type,
            depth: depth + 1,
            children: traverse_sub_issue_graph(sub.number, depth + 1, max_depth)
        }
        results.append(result)
    
    return results
```

## Edge Types

| Edge Type | Meaning | Verification |
|-----------|---------|-------------|
| `plan_to_task` | Plan sub-issue (authorized work item) | Verify plan body references issue |
| `spec_to_plan` | Spec references plan via body text | Verify body text link exists |
| `bug_to_fix` | Bug report → fix spec | Verify bug report has fix spec sub-issue |
| `duplicate_of` | Duplicate → canonical issue | Verify target issue exists |

## Depth Limits

- **Maximum depth**: 5 levels of sub-issue nesting
- **Practical depth**: Most hierarchies are 2-3 levels (spec → plan → task)
- **Circular reference detection**: Maintain visited set during traversal; HALT if cycle detected

## Phase-Count Cross-Reference

Verify sub-issue count matches plan body phase count:

1. Parse plan body for `### Phase N:` or `#### Task N:` heading patterns
2. Count expected phases from headings
3. Get `github_issue_read(method=get_sub_issues)` count
4. If plan has N > 1 phases and sub-issues count < N:
   - Report STRUCTURE-VIOLATION
   - Block implementation
   - Offer remediation via `issue-operations --task link-sub-issue`
5. Single-task plans (0 or 1 phases) skip the count check