# Task: audit-sub-issue

Audit a single sub-issue for fresh-start context and content quality.

## Purpose

Per-sub-issue auditing with independent draft generation to prevent context pollution. This task is invoked for EACH sub-issue after auditing the parent.

## Subtask Separation Requirement (CRITICAL)

**MUST run create-draft for each sub-issue BEFORE viewing live sub-issue content.**

## Workflow

**Step 1: Generate Independent Draft**

Before viewing the live sub-issue, generate a draft:

```
Write to ./tmp/tmp-spec-{parent-issue}-{sub-issue}-draft.md
Based ONLY on:
- Parent spec context (already loaded)
- General knowledge of sub-issue structure
- Common sub-issue requirements
```

**Step 2: Load Live Sub-Issue**

After draft is complete, load the live sub-issue:

```
github_issue_read(method="get", issue_number=<sub_issue_number>)
```

**Step 3: Compare Draft vs Live**

Identify gaps and conflicts:
- What's in live sub-issue that wasn't in draft?
- What's missing from live sub-issue that should be there?
- Any context pollution from viewing live prematurely?

**Step 4: Apply Sub-Issue Checks**

| Check | Problem Class |
|-------|---------------|
| Fresh-start context | FRESH-START-VIOLATION |
| Context pollution | DRAFT-LIVE-MISMATCH |
| Parent consistency | INCONSISTENT-HIERARCHY |
| Sub-issue overlap | OVERLAPPING-SUB-ISSUES (check siblings) |
| Implementation scope | INCOMPLETE-DECOMPOSITION |

**Step 5: Auto-Fix Issues**

Apply fixes automatically per auto-fix policy.

## Cross-Issue Consistency

### Parent-Sub-Issue Consistency

Check that sub-issue doesn't contradict parent:

- Sub-issue objective aligns with parent objective
- Sub-issue scope is subset of parent scope
- Sub-issue phases don't conflict with parent phases

### Sub-Issue Overlap (Sibling Check)

When auditing a sub-issue, check for overlap with siblings:

```
Query parent's sub-issues
For each sibling:
  Compare scopes
  Flag overlaps as OVERLAPPING-SUB-ISSUES
```

## Audit Log for Sub-Issue

Add sub-issue findings to parent's audit log:

```markdown
## Sub-Issue #{sub_issue_number} Findings

Issue Location: <section/requirement>
Problem class: <class>
Status: <fixed|skipped|pending>
Fix applied: <description>
GitHub Comment: <URL>
```

## Report Format

```markdown
AI: OpenCode (ollama-cloud/glm-5) 📝 Sub-Issue Audit: #{sub_issue}

## Summary
- Draft generated: YES
- Live comparison: YES
- Issues found: N
- Issues fixed: M

## Draft-Live Comparison
- Context pollution detected: YES/NO
- Missing elements: <list>
- Extra context: <list>

## Findings
<brief summary>

---
🤖 ✅ Completed by OpenCode (ollama-cloud/glm-5)
```

## Return Value

- Sub-issue audit results
- Draft-live comparison summary
- Cross-issue consistency status
- Append findings to parent audit log