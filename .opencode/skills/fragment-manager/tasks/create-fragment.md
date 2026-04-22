# Task: create-fragment

## Purpose

Create new fragment master from existing content in skills.

## Entry Criteria

- Duplicate content identified in skills
- Fragment ID unique in registry
- Content location in skill file identified

## Procedure

### Step 1: Extract Content from Source

1. Identify duplicate content in skill file:

   ```bash
   # Find content in skill file
   grep -n "## Critical Rule" .opencode/skills/some-skill/SKILL.md
   ```

2. Extract exact line range:

   - Start: Section header or marker
   - End: End of content block (before next section)

### Step 2: Create Fragment Master File

1. Create file in `.opencode/.guidelines/`:

   ```bash
   touch .opencode/.guidelines/fragment-id.md
   ```

2. Write content with fragment metadata:

   ```markdown
   # Fragment: Fragment Name

   [Content block extracted from skill]

   <!--
   Fragment ID: fragment-id
    Estimated words: NNN
   Type: text-block
   Sync status: synchronized
   -->
   ```

3. Content should be self-contained (no project-specific context)

### Step 3: Calculate Hash

```bash
sha256sum .opencode/.guidelines/fragment-id.md
```

Record the hash in registry.

### Step 4: Update Registry

Add entry to `.opencode/.guidelines/registry.yaml`:

```yaml
fragments:
  - id: fragment-id
    master:
      path: .opencode/.guidelines/fragment-id.md
      hash: sha256:abc123...
      last_modified: YYYY-MM-DDTHH:MM:SSZ
      lines: NN
    content:
      type: text-block
      estimated_words: NNN
      description: Fragment description
    destinations:
      - path: .opencode/skills/some-skill/SKILL.md
        hash: sha256:abc123...
        line_range:
          start: N
          end: N
        verified_date: YYYY-MM-DDTHH:MM:SSZ
    sync_status: synchronized
    last_sync: YYYY-MM-DDTHH:MM:SSZ
    notes: Fragment notes
```

### Step 5: Verify Entry

1. Read registry: `cat .opencode/.guidelines/registry.yaml`
2. Verify fragment appears in fragments list
3. Verify hash matches actual file

## Exit Criteria

- Fragment master file created
- Registry updated with entry
- Hash calculated and recorded
- Line range documented

## Edge Cases

### Multiple Destinations

If fragment appears in multiple skills:

1. Add all destinations to registry entry
2. Each destination has its own line_range
3. Verify each destination has same hash

### Fragment Already Exists

If fragment ID already in registry:

1. STOP - do not create duplicate
2. Ask user: "Fragment with ID '{id}' already exists. Choose a different ID or update the existing fragment."
3. If updating, use `update-fragment` task instead
