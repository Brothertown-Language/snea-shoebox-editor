---
name: fragment-manager
description: Use when managing duplicate content blocks (fragments) across guidelines or skills. Triggers on: fragment, duplicate content, sync content, content block, shared content, master copy, synchronize.
license: MIT
compatibility: opencode
---

# Skill: fragment-manager

## Overview

Fragment Manager handles duplicate text blocks (fragments) that appear in multiple skills. It provides:
- CRUD operations on fragment master files in `.opencode/.guidelines/`
- Synchronization from masters to destination copies
- Drift detection between masters and copies
- Conflict resolution when changes diverge

## Architecture

**Fragment Registry Schema:**
- `.opencode/.guidelines/registry.yaml` - Tracks fragment masters and destinations
- `.opencode/.guidelines/*.md` - Fragment master files (golden copies)
- `.opencode/skills/*/SKILL.md` - Destination copies (embedded in skills)

**Key Principles:**
- Skills remain self-contained (copies, not references)
- Masters are minimal (content blocks only, no context)
- Syncs require verification (hash matching)
- Conflicts require human intervention

## Tasks

| Task | Purpose | When to Use |
|------|---------|-------------|
| `create-fragment` | Create new fragment master from existing content | When duplicate content is found in skills |
| `read-fragment` | Read fragment master content | When inspecting fragment details |
| `update-fragment` | Update master content | When master needs changes |
| `delete-fragment` | Delete fragment master and registry entry | When fragment is obsolete |
| `sync-fragment` | Copy master to all destinations | When masters are updated |
| `check-drift` | Detect drift between masters and copies | Periodic validation, before syncs |
| `status-report` | Show sync status for all fragments | Overview of fragment health |
| `resolve-conflict` | Handle merge conflicts | When drift is detected |

## Invocation

- `/skill fragment-manager --task create-fragment` - Create new fragment
- `/skill fragment-manager --task sync-fragment` - Sync master to destinations
- `/skill fragment-manager --task check-drift` - Detect drift
- `/skill fragment-manager --task status-report` - Overview
- `/skill fragment-manager` - Skill overview only

## Operating Protocol

1. **Read registry first**: Always load `.opencode/.guidelines/registry.yaml`
2. **Verify hashes**: Compare SHA256 of master vs destinations
3. **Stop on conflicts**: If drift detected, ASK before proceeding
4. **Preserve backups**: Keep `.opencode/.backups/` before dangerous operations
5. **Update registry**: After any operation, update timestamp and status

## Conflict Resolution Protocol

**When to STOP and ASK:**
1. Destination content differs from master AND master unchanged
2. File structure changed (lines shifted, sections reorganized)
3. Registry has conflicts (ambiguous ID, cyclic dependency)
4. Sync fails for any destination

**Confirmation Format:**
```
⚠️ CONFLICT DETECTED

Fragment: {fragment_id}
Conflict: {edge_case_description}

Detection:
- Master hash: {master_hash}
- Destination hash: {dest_hash}
- Line range: {start}-{end}

Options:
a) Overwrite destination with master
b) Keep destination version (update master?)
c) Mark for manual resolution
d) Abort operation

Your choice:
```

## Registry Schema (v2)

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
```

## Cross-References

- Related skills: `skill-creator` (fragment registration prompt)
- Related files: `.opencode/.guidelines/registry.yaml`, `.opencode/dispatch-table.yaml`

## Edge Cases

See individual task files for edge case handling protocols.