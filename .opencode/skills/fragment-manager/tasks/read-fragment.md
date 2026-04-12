# Task: read-fragment

## Purpose

Read fragment master content and show metadata.

## Entry Criteria

- Fragment ID specified
- Fragment exists in registry

## Procedure

### Step 1: Load Registry

```bash
grep -A 30 "id: fragment-id" .opencode/.guidelines/registry.yaml
```

Extract:
- Master file path
- Hash
- Content type
- Estimated words
- Description
- Sync status
- Last sync timestamp

### Step 2: Read Master File

```bash
cat .opencode/.guidelines/fragment-id.md
```

Show full content with line numbers.

### Step 3: Show Destination Status

For each destination:
```bash
# Show destination location
echo "Destination: .opencode/skills/skill/SKILL.md"
echo "Lines: {start}-{end}"
echo "Hash: {dest_hash}"
echo "Status: {sync_status}"
```

### Step 4: Report

Display:
- Fragment ID
- Master file path and hash
- Content (full)
- Destinations (list with hashes and line ranges)
- Sync status summary

## Edge Cases

### Fragment Not Found

If fragment ID not in registry:
1. STOP - fragment does not exist
2. Ask user: "Fragment with ID '{id}' not found in registry. Use 'create-fragment' to create it."

### Master File Missing

If registry entry exists but master file missing:
1. WARN: "Master file missing at {path}"
2. Ask user: "Registry references missing file. Recreate from destinations or remove fragment from registry?"