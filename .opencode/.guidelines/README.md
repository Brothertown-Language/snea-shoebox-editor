# Fragment Registry Documentation

## Purpose

The fragment registry tracks duplicate text blocks (fragments) that appear in multiple skills, enabling synchronization and drift detection.

## Registry File Location

`.opencode/.guidelines/registry.yaml`

## Schema (Version 2)

```yaml
version: 2
schema_version: "2.0.0"
last_updated: YYYY-MM-DD

fragments:
  - id: fragment-name
    master:
      path: .opencode/.guidelines/fragment-name.md
      hash: sha256:abc123...
      last_modified: YYYY-MM-DDTHH:MM:SSZ
      lines: NN
    content:
      type: text-block
      estimated_tokens: NNN
      description: "Fragment description"
    destinations:
      - path: .opencode/skills/skill-name/SKILL.md
        hash: sha256:abc123...
        line_range:
          start: N
          end: N
        verified_date: YYYY-MM-DDTHH:MM:SSZ
    sync_status: synchronized
    last_sync: YYYY-MM-DDTHH:MM:SSZ
    notes: "Fragment notes"

purged:
  - id: obsolete-fragment
    source: original/location
    purged_date: YYYY-MM-DD
    notes: "Reason for removal"
```

## Field Descriptions

### Fragment Entry

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the fragment |
| `master.path` | string | Path to fragment master file |
| `master.hash` | string | SHA256 hash of master content |
| `master.last_modified` | datetime | ISO 8601 timestamp of last modification |
| `master.lines` | int | Number of lines in master file |
| `content.type` | string | Content type (text-block, section, table, code-block) |
| `content.estimated_tokens` | int | Approximate token count |
| `content.description` | string | Brief description of fragment purpose |
| `destinations` | array | List of skill files containing this fragment |
| `sync_status` | enum | synchronized, drifted, conflicted |
| `last_sync` | datetime | ISO 8601 timestamp of last sync |
| `notes` | string | Additional context or notes |

### Destination Entry

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Path to skill file containing copy |
| `hash` | string | SHA256 hash of content at this location |
| `line_range.start` | int | Starting line number (1-indexed) |
| `line_range.end` | int | Ending line number (inclusive) |
| `verified_date` | datetime | ISO 8601 timestamp of last verification |

### Sync Status Values

| Status | Description |
|--------|-------------|
| `synchronized` | Master and all destinations match |
| `drifted` | One or more destinations differ from master |
| `conflicted` | Merge conflict requiring manual resolution |

## Fragment Master File Format

```markdown
# Fragment: Fragment Name

[Content block]

<!--
Fragment ID: fragment-id
Estimated tokens: NNN
Type: text-block
Sync status: synchronized
-->
```

**Key Points:**
- Fragment master files contain ONLY the content block
- No project-specific context (skills provide context)
- Fragment ID in HTML comment for reference
- Sync status updated during sync operations

## Registry Maintenance

### Adding a New Fragment

Use the fragment-manager skill:

```bash
/skill fragment-manager --task create-fragment
```

1. Extract duplicate content from skill file
2. Create master file in `.opencode/.guidelines/`
3. Calculate SHA256 hash
4. Add entry to registry.yaml
5. Mark destinations with line ranges

### Syncing Fragments

```bash
/skill fragment-manager --task sync-fragment --fragment-id <id>
```

1. Load registry entry
2. Read master content
3. Update each destination at line_range
4. Update destination hashes
5. Update sync_status and last_sync

### Checking for Drift

```bash
/skill fragment-manager --task check-drift
```

1. Calculate master hash
2. Compare to each destination hash
3. Update sync_status
4. Generate drift report

## Hash Verification

SHA256 hashes ensure content integrity:

```bash
# Calculate hash for master
sha256sum .opencode/.guidelines/branch-first-protocol.md

# Calculate hash for destination
sha256sum .opencode/skills/git-workflow/tasks/pre-work.md
```

Hashes change only when content changes.

## Purged Fragments

When a fragment becomes obsolete:

```yaml
purged:
  - id: obsolete-fragment
    source: original/location
    purged_date: 2026-04-06
    notes: "Replaced by new fragment pattern"
```

**Note:** Purged fragments remain in the registry for historical reference.

## Best Practices

### Fragment Content

- Keep fragments self-contained
- Avoid project-specific context
- Use stable anchors (function names, section headers)
- Minimum viable content (no extra context)

### Fragment Size

- Target: 50-300 lines per fragment
- Larger fragments: Consider splitting
- Smaller fragments: Consider merging related content

### Line Range Stability

- Use section headers as anchors
- Update line ranges after file edits
- Verify range accuracy after reorganization

### Sync Frequency

- Sync immediately after master updates
- Check drift weekly for critical fragments
- Always sync before releases

## Integration with Skills

Skills reference fragments in their content:

```markdown
## Critical Rules

🚫 ZERO TOLERANCE: Branch Before Edit

**The agent MUST create a feature branch BEFORE ANY filesystem change.**

[Fragment content embedded here]

<!--
Fragment ID: branch-first-protocol
Sync status: synchronized
-->
```

**Key Points:**
- Skills embed the actual content (copies, not references)
- Fragment ID in comment for tracking
- Sync status shows synchronization state

## Troubleshooting

### Hash Mismatch

**Problem:** Registry hash differs from file hash

**Solution:**
1. Check if file was manually edited
2. Re-calculate hash: `sha256sum <file>`
3. Update registry with correct hash
4. Re-run check-drift

### Line Range Invalid

**Problem:** Content at line range doesn't match fragment

**Solution:**
1. File structure changed
2. Re-scan file for matching content
3. Update line_range in registry
4. Verify with check-drift

### Fragment Overlap

**Problem:** Two fragments overlap in same file

**Solution:**
1. Adjust line ranges (no overlap)
2. Or merge fragments into one
3. Or remove one fragment from this destination

## See Also

- `.opencode/skills/fragment-manager/SKILL.md` - Fragment Manager skill
- `.opencode/skills/skill-creator/SKILL.md` - Step 7: Register Fragments