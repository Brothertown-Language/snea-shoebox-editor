# Task: check-drift

## Purpose

Detect when destination copies diverge from master.

## Entry Criteria

- Fragment ID specified (or 'all' to check all fragments)
- Registry exists with fragment entries

## Procedure

### Step 1: Load Registry

```bash
cat .opencode/.guidelines/registry.yaml
```

Parse all fragments or specific fragment.

### Step 2: Calculate Master Hash

```bash
sha256sum .opencode/.guidelines/fragment-id.md
```

Compare to registry `master.hash`.

### Step 3: Check Each Destination

For each destination:

1. **Calculate destination hash:**
   ```bash
   sha256sum "$dest_path"
   ```

2. **Compare to master hash:**
   - If match → `synchronized`
   - If mismatch → `drifted`

3. **Update status in memory:**
   ```
   Fragment: fragment-id
   Destination: skill/SKILL.md
   Master hash: abc123...
   Dest hash: def456...
   Status: DRIFTED ⚠️
   ```

### Step 4: Update Registry Status

Update sync_status for fragment:
- If all destinations match master → `synchronized`
- If any destination differs → `drifted`

### Step 5: Generate Drift Report

Display for each fragment:

```
Fragment Status Report
======================

Fragment: branch-first-protocol
Master: .opencode/.guidelines/branch-first-protocol.md
Hash: sha256:abc123...
Status: synchronized ✅

Destinations:
  1. git-workflow/tasks/pre-work.md
     Hash: sha256:abc123... (MATCH) ✅
     Lines: 7-84

Fragment: commit-workflow
Master: .opencode/.guidelines/commit-workflow.md
Hash: sha256:abc123...
Status: drifted ⚠️

Destinations:
  1. git-workflow/tasks/commit-prep.md
     Hash: sha256:def456... (MISMATCH) ⚠️
     Lines: 7-39
     Drifted since: 2026-04-05

DRIFT DETECTED: 1 of 9 fragments have drifted
```

## Exit Criteria

- All destinations checked
- Registry sync_status updated
- Drift report generated

## Edge Cases

### Master Hash Mismatch

If master file hash differs from registry:
```
⚠️ REGISTRY STALE

Fragment: {fragment-id}
Registry hash: {reg_hash}
Actual master hash: {file_hash}

Which is correct?
a) Registry is stale (update from file)
b) File is stale (sync from registry's expected content)
c) Both changed (manual investigation needed)
```

### Destination File Missing

If destination file doesn't exist:
1. WARN: "Destination file missing: {path}"
2. Mark destination as `deleted`
3. Ask: "Remove from registry or recreate file?"

### Line Range Invalid

If destination file has fewer lines than line_range.end:
1. Content may have been deleted or moved
2. Report: "Line range exceeds file length"
3. Recommend: Manual rescan to find new location