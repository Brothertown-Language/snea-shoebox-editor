# Cross-Reference Standard for AI Agent Configuration Files

**Version:** 1.0  
**Created:** 2026-03-31  
**Status:** Active

---

## Purpose

This document defines the standard format for cross-references in `.opencode/guidelines/`, `.opencode/skills/`, and `AGENTS.md` files. Following these standards ensures references remain stable across file edits, renames, and reorganizations.

---

## Standard 1: Skill References

**Pattern:** Use skill name (directory name) without path or extension.

### Correct Format

```markdown
See `skill-name` skill for details.
See `skill-name` skill → "Section Name" for specific section.
```

### Examples

```markdown
See `approval-gate` skill for complete workflow.
See `mcp-tool-usage` skill → "Tool Preference Tables" for hierarchy.
See `github-comments` skill → "Responding to User Comments (MANDATORY)" section.
```

### Forbidden Patterns

```markdown
❌ See `.opencode/skills/approval-gate/SKILL.md`
❌ See `approval-gate/SKILL.md`
❌ See `./skills/approval-gate/SKILL.md`
```

### Why This Works

- Skills have unique names that don't change with directory structure
- Simpler and more readable than full paths
- Single find-replace can update all skill references
- Future-proof: can add anchor links later without changing pattern

---

## Standard 2: Guideline References

**Pattern:** Use filename without path. Section references use heading name with arrow notation.

### Correct Format

```markdown
See `filename.md` for complete rules.
See `filename.md` → "Section Name" for specific section.
```

### Examples

```markdown
See `000-critical-rules.md` for complete rules.
See `010-approval-gate.md` → "Single-Task Exemption" for the exemption details.
See `080-code-standards.md` → "Code Standards for Notebooks" section.
```

### Forbidden Patterns

```markdown
❌ See `.opencode/guidelines/080-code-standards.md`
❌ See `guidelines/080-code-standards.md`
❌ See `file.md:42`  (line numbers break on edit)
```

---

## Standard 3: AGENTS.md References

**Pattern:** Use heading name with arrow notation or direct reference.

### Correct Format

```markdown
See `AGENTS.md` → "Section Name" section.
See the "Rule Name" rule in `AGENTS.md`.
```

### Examples

```markdown
See `AGENTS.md` → "Critical Rules" section.
See the "Never Prompt in Comments" rule in `AGENTS.md`.
See `AGENTS.md` → "MCP Capability Testing (Universal)" section.
```

### Forbidden Patterns

```markdown
❌ See `AGENTS.md` § 125 (section numbers change)
❌ See section 3.2 (numbered sections break on renumbering)
❌ See below (relative position is unreliable)
```

---

## Standard 4: Section References

**Pattern:** Use heading name with arrow notation or direct reference.

### Correct Format

```markdown
See the "Sub-issue Verification Gate" section.
See `filename.md` → "Section Name" section.
```

### Examples

```markdown
See the "Mandatory First Step" section of `000-session-init.md`.
See the "Missing Progress Comments" section in `000-critical-rules.md`.
```

### Forbidden Patterns

```markdown
❌ See section 3.2 (numbered sections break on renumbering)
❌ See below (relative position is unreliable)
❌ See line 42 (line numbers break on edit)
❌ See the section above (relative position is unreliable)
```

---

## Pattern Summary

| Reference Type | Correct Format | Forbidden |
|---------------|----------------|-----------|
| Skill | `skill-name` skill | `.opencode/skills/name/SKILL.md` |
| Guideline | `filename.md` | `guidelines/filename.md`, `file.md:42` |
| AGENTS.md | `AGENTS.md` → "Section" | `AGENTS.md` § 125 |
| Section | `"Section Name" section` | `section 3.2`, `below`, `line 42` |

---

## Rationale

### Why Skill Name (Not Path)

1. **Stability:** Directory structure may change; names remain constant
2. **Readability:** `approval-gate` is clearer than `.opencode/skills/approval-gate/SKILL.md`
3. **Maintainability:** Single find-replace updates all references
4. **Future-proof:** Can add anchor links without changing pattern

### Why Section Names (Not Line Numbers)

1. **Edit resistance:** Line numbers shift on every edit above them
2. **Human-readable:** Section names convey meaning
3. **Maintainability:** Update once per section rename
4. **Tools:** IDE "Find Usages" works with names

### Why Arrow Notation (Not Anchors)

1. **Human-readable:** `→ "Section Name"` is self-documenting
2. **No tooling dependency:** Anchors require Markdown anchor generation
3. **Interim solution:** Can adopt anchors later without changing section references
4. **Flexibility:** Works with or without future anchor support

---

## Migration Guide

### From File Paths to Skill Names

**Before:**
```markdown
See `.opencode/skills/approval-gate/SKILL.md` for workflow.
```

**After:**
```markdown
See `approval-gate` skill for workflow.
```

### From Line Numbers to Section Names

**Before:**
```markdown
Guidelines in `00-spec-creation.md:69-108` describe requirements.
```

**After:**
```markdown
Guidelines in the "Mandatory Elements" section of `140-planning-spec-creation.md` describe requirements.
```

### From Section Numbers to Names

**Before:**
```markdown
violates `AGENTS.md` § 125
```

**After:**
```markdown
violates the "Never Prompt in Comments" rule in `AGENTS.md`
```

---

## Validation Checklist

When adding or modifying cross-references, verify:

- [ ] No full file paths for skills (use skill name only)
- [ ] No line number references (use section names)
- [ ] No section number references (use heading names)
- [ ] Arrow notation format: `filename.md` → "Section Name"
- [ ] Quoted section names: `"Section Name"` not `Section Name`
- [ ] Referenced files exist
- [ ] Referenced sections exist in target files

---

## File Locations

| Type | Location |
|------|----------|
| Guideline files | `.opencode/guidelines/*.md` |
| Skill files | `.opencode/skills/*/SKILL.md` |
| Main entry | `AGENTS.md` |

---

## Related

- Issue #439: Cross-reference audit and standardization
- `.opencode/guidelines/080-code-standards.md`: Code formatting standards
- `.opencode/skills/approval-gate/SKILL.md`: Authorization workflow