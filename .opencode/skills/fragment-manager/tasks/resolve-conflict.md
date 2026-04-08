# Task: resolve-conflict

## Purpose

Handle merge conflicts when drift is detected or manual edits exist.

## Entry Criteria

- Fragment ID specified
- Drift detected between master and destination(s)
- User intervention needed

## Conflict Types

### Type 1: Destination Has Manual Edits

**Scenario:** Developer edited destination copy, now different from master.

**Detection:**
- Master hash unchanged since last sync
- Destination hash differs from master

**Resolution Options:**

```
⚠️ CONFLICT: Manual Edit Detected

Fragment: {fragment-id}
Destination: {dest_path}

Master hash (unchanged): {master_hash}
Destination hash (changed): {dest_hash}

The destination was manually edited since last sync.

Options:
a) Keep master version (overwrite destination - manual edits LOST)
b) Keep destination version (update master from destination)
c) Mark for manual resolution (HALT and show diff)
d) Abort operation

Your choice:
```

**Option (a):** Sync master to destination (manual edits lost)
- Create backup first
- Run sync-fragment

**Option (b):** Update master from destination
- Extract content from destination
- Update master file
- Update registry hash
- Sync to other destinations

**Option (c):** Show diff and HALT
- Generate diff: `diff <(master) <(destination)`
- HALT for human review

### Type 2: Fragment Overlap

**Scenario:** Two fragments overlap in same destination file.

**Detection:**
- Fragment A line range: 50-70
- Fragment B line range: 60-80
- Overlap: lines 60-70

**Resolution:**

```
⚠️ CONFLICT: Fragment Overlap

Fragment A: {id1}
Fragment B: {id2}
Destination: {dest_path}
Overlap: lines 60-70

Fragments cannot share the same lines.

Options:
a) Adjust Fragment A line range (end at 59)
b) Adjust Fragment B line range (start at 71)
c) Merge fragments (combine into one)
d) Abort - manual resolution required

Your choice:
```

### Type 3: File Structure Changed

**Scenario:** Destination file reorganized, line ranges invalid.

**Detection:**
- Line range exceeds file length
- Content at line range doesn't match fragment

**Resolution:**

```
⚠️ CONFLICT: File Structure Changed

Fragment: {fragment-id}
Destination: {dest_path}

Registry line range: {start}-{end}
Actual file length: {actual_lines}

The file has been reorganized since the last sync.

Options:
a) Re-scan file for matching content (update line range)
b) Remove destination from fragment (fragment no longer used)
c) Abort - manual rescan required

Your choice:
```

### Type 4: Registry Conflict

**Scenario:** Registry has ambiguous ID, cyclic dependency, or conflicting destinations.

**Detection:**
- Same fragment ID appears twice
- Fragment A includes Fragment B, B includes A
- Same destination registered for different fragments

**Resolution:**

```
⚠️ CONFLICT: Registry Error

Error: {error_type}
Details: {error_details}

This is a registry configuration error.

Resolution:
1. Manually edit .opencode/.guidelines/registry.yaml
2. Fix the conflicting entry
3. Re-run the operation

Common fixes:
- Duplicate ID: Rename one fragment
- Cyclic dependency: Split or merge fragments
- Destination conflict: Remove duplicate destination
```

## Resolution Workflow

### For All Conflict Types

1. **STOP immediately** - do not proceed with sync
2. **Generate conflict report** - show detection details
3. **Present options** - a/b/c/d choices
4. **WAIT for user decision** - no auto-resolution
5. **Execute chosen resolution**
6. **Verify result** - check hash matches expectation

### After Conflict Resolution

1. Update registry status
2. Create verification report
3. Recommend running `check-drift` to verify all fragments

## Rollback Procedure

If resolution causes unexpected issues:

1. Restore from backups: `.opencode/.backups/{date}/`
2. Verify registry state
3. Re-run `check-drift`
4. Report rollback completion