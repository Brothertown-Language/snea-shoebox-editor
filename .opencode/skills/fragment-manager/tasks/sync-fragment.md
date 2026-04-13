# Task: sync-fragment

## Purpose

Copy fragment master to all destinations, updating their content.

## Entry Criteria

- Fragment ID specified
- Fragment exists in registry
- Master and destinations defined

## Procedure

### Step 1: Run Drift Detection First

**MANDATORY: Check drift before syncing.**

Run `check-fragment` task:

- If all destinations synchronized → Proceed to Step 3
- If any destination drifted → Proceed to Step 2
- If conflict detected → STOP, run `resolve-conflict`

### Step 2: Handle Drift

If destinations have drifted:

```
⚠️ DRIFT DETECTED

Fragment: {fragment-id}
Drifted destinations: {count}

Options:
a) Sync all (overwrite drifted destinations with master)
b) Sync only synchronized destinations (preserve drifts)
c) Review drift details first
d) Abort sync

Your choice:
```

If user chooses (a) or (b):

- Create backups first (see Step 3)
- Proceed with partial or full sync

### Step 3: Create Backups (MANDATORY)

Before modifying destinations:

```bash
mkdir -p .opencode/.backups/$(date +%Y%m%d)
for dest in $destinations; do
    cp "$dest" ".opencode/.backups/$(date +%Y%m%d)/$(basename $dest).bak"
done
```

### Step 4: Read Master Content

```bash
master_content=$(cat .opencode/.guidelines/fragment-id.md)
```

### Step 5: Update Each Destination

For each destination in registry:

1. **Read destination file:**

   ```python
   content = pycharm_get_file_text_by_path(pathInProject=dest_path)
   lines = content.split('\n')
   ```

2. **Replace content at line_range:**

   ```python
   # Remove old content
   updated_lines = lines[:start-1] + [master_content] + lines[end:]

   # Write back
   pycharm_replace_text_in_file(
       pathInProject=dest_path,
       oldText=content,
       newText='\n'.join(updated_lines)
   )
   ```

3. **Verify update:**

   ```bash
   sha256sum "$dest_path"
   ```

4. **Update destination hash in registry:**

   ```yaml
   destinations:
     - path: '...'
       hash: sha256:new-hash...
       verified_date: YYYY-MM-DDTHH:MM:SSZ
   ```

### Step 6: Update Registry Status

```yaml
sync_status: synchronized
last_sync: YYYY-MM-DDTHH:MM:SSZ
```

### Step 7: Report Completion

```
✅ Sync complete: {fragment-id}
- Master hash: {master_hash}
- Destinations updated: {count}
- Sync status: synchronized
- Backups saved: .opencode/.backups/{date}/
```

## Edge Cases

### Partial Sync Failure

If some destinations fail:

1. Rollback failed destinations from backups
2. Report which destinations failed
3. Ask user: "Retry failed destinations or abort?"

### Line Range Changed

If destination file structure changed:

1. STOP - line range no longer accurate
2. Re-scan file for matching content
3. Update line_range in registry
4. Retry sync

### Master Hash Changed Mid-Sync

If master modified during sync:

1. STOP immediately
2. Do not continue with stale master
3. Re-run from Step 1
