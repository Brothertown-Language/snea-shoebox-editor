# Anchor-Based Stable References

## Objective

Replace fragile section-number references with stable anchor-based references across all guidelines and skills.

---

## Problem Statement

**Current State:** All guidelines and skills use fragile reference patterns:

- **Section numbers**: `§142`, `§070.3` — break when sections are renumbered
- **Step numbers**: `Step 5` — break when steps are inserted/deleted
- **Gate numbers**: `Gate 2` — break when gates are reordered
- **Phase numbers**: `Phase 3` — break when phases change

**Impact:** When files are edited, cross-references break silently with no automated detection.

**Examples:**
- `§142 Step 5` — breaks if any step added before step 5
- `§070.3` — breaks if §070 renumbered
- `Gate 2` — breaks if gate order changed
- `Phase 1` — breaks if phases reordered

---

## Stable Anchor Pattern

**Pattern:** `filename "Section Name"` or `filename#anchor-id`

| Reference Type | Stable Format | Example |
|----------------|---------------|---------|
| Section reference | `000-critical-rules.md "Session Init Verification"` | Clear, semantic, renumber-proof |
| Anchor ID reference | `080-code-standards.md#file-locations` | Explicit, unique, stable |
| Section with context | `010-approval-gate.md "Mandatory Pre-Close Checklist"` | Multiple headings resolved by context |
| Cross-file reference | `git-workflow task "review-prep"` | Skill task references use task name |

---

## Anchor ID Syntax

**For headings that need explicit anchors:**

```markdown
## Section Name {#section-name}
```

**Use explicit anchors when:**
- Heading text is not unique in the file
- Heading text is long or contains special characters
- Reference needs to be unambiguous
- Heading may be renamed in future

**Examples:**

```markdown
## File Locations {#file-locations}

Guidelines for file placement...

## Code Structure {#code-structure}

Patterns for organizing code...
```

---

## Reference Style Guide

### ✅ Correct References

**Section references (primary):**
```markdown
See `000-critical-rules.md "Session Init Verification"` for enforcement points.
```

**Anchor ID references (when unique):**
```markdown
See `080-code-standards.md#file-locations` for file placement rules.
```

**Skill task references:**
```markdown
After authorization, invoke `/skill git-workflow --task pre-work` (see `git-workflow` skill).
```

### 🚫 Incorrect References

**Section numbers:**
```markdown
See §142 for enforcement rules.  # ❌ Fragile — breaks on renumbering
```

**Step/Gate/Phase numbers without context:**
```markdown
See Step 5 in the approval workflow.  # ❌ Fragile — breaks on insertion
```

**Ambiguous references:**
```markdown
See the guidelines.  # ❌ Vague — which file? which section?
```

---

## Conversion Strategy

### Phase 1: Anchor Infrastructure (Complete)

1. ✅ Created verification script (`verify-anchor-refs.py`)
2. ✅ Created anchor reference style guide (this document)
3. ⏳ Add anchor IDs to section headings
4. ⏳ Add pre-commit hook

### Phase 2: Guideline Conversion (In Progress)

Replace all fragile references in guideline files:

- `§123` → `filename "Section Name"`
- `Step N` → `filename "Step Description"` or context-based reference
- `Gate N` → `filename "Gate Description"` or workflow name
- `Phase N` → Spec phase name or `filename "Phase Description"`

### Phase 3: Skill Conversion (Pending)

Replace all fragile references in skill files:

- Task step references → task names
- SKILL.md cross-references → filename + section
- Task internal references → step descriptions

### Phase 4: Verification (Pending)

- Run verification script across all converted files
- Test renumbering resistance
- Document anchor patterns

---

## Verification Script

**Location:** `.opencode/skills/approval-gate/verify-anchor-refs.py`

**Usage:**
```bash
uv run python .opencode/skills/approval-gate/verify-anchor-refs.py
```

**Output:**
```
❌ Found 113 fragile references in 20 files
✅ No fragile references found
```

---

## Pre-Commit Hook (Planned)

**Location:** `.githooks/pre-commit`

**Behavior:**
- Runs verification script before each commit
- Blocks commit if fragile references found
- Suggests stable anchor patterns

---

## Cross-References

- **File Location Standards:** `080-code-standards.md "File Locations"`
- **Reference Enforcement:** `000-critical-rules.md "Critical Violation: Inferring GitHub Owner"`
- **Git Workflow:** `git-workflow` skill → `pre-work` task
- **Markdown Linting:** AGENTS.md "Linting & Static Analysis"