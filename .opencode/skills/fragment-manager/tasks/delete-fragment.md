# Task: delete-fragment

## Purpose

Delete fragment master and remove from registry.

## ⚠️ DANGER: DESTRUCTIVE OPERATION

This operation permanently removes the fragment master file.

## Entry Criteria

- Fragment ID specified
- Fragment exists in registry
- User explicitly confirms deletion

## Procedure

### Step 1: Verify Fragment Exists

```bash
grep -A 30 "id: fragment-id" .opencode/.guidelines/registry.yaml
```

Show fragment details to user.

### Step 2: REQUIRE EXPLICIT CONFIRMATION

**MUST ask user before proceeding:**

```
⚠️ CONFIRM DELETION

Fragment: {fragment-id}
Master: .opencode/.guidelines/fragment-id.md
Destinations: {count} destinations

This will:
1. DELETE the master file
2. REMOVE entry from registry
3. Leave destination copies unchanged in skills

Destinations will still have the content but will no longer be tracked.

Proceed with deletion?

Type 'DELETE {fragment-id}' to confirm:
```

**DO NOT proceed without explicit confirmation string.**

### Step 3: Create Backup (MANDATORY)

Before deletion:
```bash
mkdir -p .opencode/.backups/$(date +%Y%m%d)
cp .opencode/.guidelines/fragment-id.md .opencode/.backups/$(date +%Y%m%d)/fragment-id-deleted.md
```

Backup is kept for rollback if needed.

### Step 4: Delete Master File

```bash
rm .opencode/.guidelines/fragment-id.md
```

### Step 5: Update Registry

Remove fragment entry from `.opencode/.guidelines/registry.yaml`:
- Delete entire fragment block from `fragments:` list
- Update `last_updated` date
- Decrement `total_fragments` count

### Step 6: Report Completion

```
✅ Fragment deleted: {fragment-id}
- Master file removed: .opencode/.guidelines/fragment-id.md
- Registry updated
- Backup saved: .opencode/.backups/{date}/fragment-id-deleted.md

⚠️ NOTE: Content still exists in {count} destination skills but is no longer tracked.
```

## Edge Cases

### Fragment in Use

If destinations exist:
1. WARN: "Fragment has {count} destinations. Deleting will orphan these copies."
2. Ask user to confirm they understand

### Delete Wrong Fragment

If user regrets deletion:
1. Restore from backup: `cp .opencode/.backups/{date}/fragment-id-deleted.md .opencode/.guidelines/fragment-id.md`
2. Re-add entry to registry manually
3. Re-run `create-fragment` with fragment-id