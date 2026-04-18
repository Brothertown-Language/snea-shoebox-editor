# Task: status-report

## Purpose

Show sync status overview for all fragments.

## Entry Criteria

- Registry exists
- At least one fragment defined

## Procedure

### Step 1: Load Registry

```bash
cat .opencode/.guidelines/registry.yaml
```

Parse all fragments.

### Step 2: Run Quick Drift Check

For each fragment:

- Calculate master hash
- Check if master hash matches registry
- Flag fragments that need verification

### Step 3: Generate Summary Report

```
Fragment Registry Status Report
==============================

Generated: YYYY-MM-DD HH:MM:SS
Registry version: 2
Schema version: 2.0.0

Summary
-------
Total fragments: 9
Synchronized: 8
Drifted: 1
Conflicted: 0

Fragments
---------

1. branch-first-protocol ✅
   Master: .opencode/.guidelines/branch-first-protocol.md
   Destinations: 1
   Last sync: 2026-04-06T21:15:00Z
   
2. commit-workflow ✅
   Master: .opencode/.guidelines/commit-workflow.md
   Destinations: 1
   Last sync: 2026-04-06T21:15:00Z

3. ai-identity ✅
   Master: .opencode/.guidelines/ai-identity.md
   Destinations: 1
   Last sync: 2026-04-06T21:20:00Z

... (remaining fragments)

Drifted Fragments
-----------------

⚠️ pr-workflow (DRIFTED)
   Master hash: abc123...
   Destination 1 (git-workflow/tasks/pr-creation.md): def456... (MISMATCH)
   Destination 2 (pr-creation-workflow/SKILL.md): abc123... (match)
   
   Recommendation: Run 'sync-fragment pr-workflow' to synchronize

Actions Needed
--------------

1 fragment needs attention:
  - pr-workflow: Run check-drift for details, then sync or resolve conflict

Run '/skill fragment-manager --task check-drift' for detailed drift analysis.
```

## Output Formats

### Compact (default)

One-line per fragment with status emoji.

### Verbose

Include last modified dates, hash values, line ranges.

### JSON Export

```bash
# Use the registry tool for structured output, or parse YAML directly:
./.opencode/tools/guidelines search fragment-status
# For programmatic access, write a script to ./tmp/ and run it:
./tmp/registry-export.py
```

## Edge Cases

### Empty Registry

If no fragments defined:

```
Fragment Registry Status Report
==============================

Registry: EMPTY

No fragments tracked yet.
Run 'create-fragment' to add the first fragment master.
```

### Registry Corrupted

If YAML parsing fails:

1. STOP - do not proceed
2. Report: "Registry YAML parse error: {error}"
3. Recommend: Manual inspection and repair
