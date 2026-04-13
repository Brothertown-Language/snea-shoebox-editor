# Task: update-fragment

## Purpose

Update fragment master content and optionally sync to destinations.

## Entry Criteria

- Fragment ID specified
- Fragment exists in registry
- New content provided (or user will edit)

## Procedure

### Step 1: Create Backup

Before any changes:

```bash
mkdir -p .opencode/.backups/$(date +%Y%m%d)
cp .opencode/.guidelines/fragment-id.md .opencode/.backups/$(date +%Y%m%d)/fragment-id.md
```

### Step 2: Update Master Content

1. Edit master file:

   ```bash
   # User edits or agent edits with pycharm tools
   pycharm_replace_text_in_file(
       pathInProject=".opencode/.guidelines/fragment-id.md",
       oldText="old content",
       newText="new content"
   )
   ```

2. Update metadata comment at end of file if needed

### Step 3: Calculate New Hash

```bash
sha256sum .opencode/.guidelines/fragment-id.md
```

Record new hash.

### Step 4: Update Registry

Update registry entry:

```yaml
master:
  hash: sha256:new-hash...
  last_modified: YYYY-MM-DDTHH:MM:SSZ
  lines: new-count
```

### Step 5: Ask About Sync

Ask user: "Master updated. Sync to all destinations now?"

If YES:

- Proceed to `sync-fragment` task

If NO:

- Mark `sync_status: drifted`
- HALT

## Edge Cases

### Destinations Would Drift

If master updated but not synced:

1. Mark `sync_status: drifted`
2. Report: "Master updated but not synced. Destinations now out of sync."
3. Recommend: Run `sync-fragment` to update destinations

### Conflicting Changes

If destinations already have manual edits:

1. STOP - do not overwrite
2. Run `check-drift` to see current state
3. Ask user: "Destinations have manual edits. Overwrite or update master from destinations?"
