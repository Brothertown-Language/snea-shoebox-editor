# Task: compare

## Purpose

Compare clean-room plan against existing plan to identify discrepancies at phase-level, step-level, and content-level. Uses semantic matching to avoid false positives from naming differences.

## Operating Protocol

1. **Invoked by:** audit task (Step 5) or directly via `/skill plan-fidelity-auditor --task compare`
2. **Requires:** Both plans available for comparison

## Entry Criteria

- Clean-room plan generated (markdown content)
- Existing plan extracted from the spec issue
- Issue number for context

## Exit Criteria

- Discrepancy list generated
- Each discrepancy classified (auto-fix or flag-for-review)
- Semantic matching applied to reduce false positives
- Results ready for auto-fix task or reporting

## Procedure

### Step 1: Parse Both Plans

**Clean-room plan structure:**
Extract phases, steps, and key content from the subtask output.

**Existing plan structure:**
Extract phases and steps from the spec issue body. Look for `## Phase N:` headers and `☐`/`↻`/`☑`/`☒` step markers.

**Parse into comparable format:**
```python
# Parsed structure
{
  "phases": [
    {
      "name": "Phase concern name",
      "steps": ["Step description 1", "Step description 2"],
      "verification": ["How to verify 1"],
      "key_concepts": ["concept1", "concept2"]
    }
  ],
  "edge_cases": ["Edge case 1"],
  "success_criteria": ["Criterion 1"],
  "affected_files": ["path/to/file.py"]
}
```

### Step 2: Phase-Level Comparison

**For each clean-room phase, attempt to match with existing phases:**

1. **Exact match:** Same concern name → direct comparison
2. **Semantic match:** Different name, same conceptual scope → compare content
3. **No match:** Clean-room phase has no counterpart → `MISSING_PHASE`

**For each existing phase with no clean-room counterpart:** `EXTRA_PHASE` (potential scope creep)

**Semantic matching rules:**
| Pattern | Match? | Examples |
|---------|--------|----------|
| Same concept, different wording | YES | "User Schema" ≈ "Database Tables", "Auth Setup" ≈ "OAuth2 Integration" |
| Overlapping but not identical | CONTEXTUAL | "User Data Access" ≈ "Repository Layer" — compare steps |
| Distinct concepts | NO | "API Endpoints" ≠ "UI Components" |

**Comparison results format:**
```yaml
phase_comparison:
  - clean_room_phase: "Database Schema Setup"
    existing_phase: "Phase 1: User Schema"
    match_type: "semantic"  # exact, semantic, none
    discrepancy: null  # null if matched
  - clean_room_phase: "Error Handling Layer"
    existing_phase: null
    match_type: "none"
    discrepancy: "MISSING_PHASE"
  - existing_phase: "UI Components"
    clean_room_phase: null
    match_type: "none"
    discrepancy: "EXTRA_PHASE"
```

### Step 3: Step-Level Comparison

**For each matched phase pair, compare steps:**

1. **Extract steps** from both plans for the matched phase
2. **Attempt semantic matching** between steps
3. **Identify:**
   - `MISSING_STEP`: Steps in clean-room not in existing
   - `EXTRA_STEP`: Steps in existing not in clean-room
   - `ORDERING_DIFFERENCE`: Same steps in different order

**Simple fix classification:**
| Step Type | Auto-Fix? | Rationale |
|----------|-----------|-----------|
| Missing file reference | YES | Simple addition, no scope change |
| Discovered repo change | YES | Spec needs updating for current codebase |
| Additional affected file | YES | Completeness improvement |
| Missing verification step | YES | Quality improvement, no scope change |
| Missing phase | NO | Substantive scope change |
| Different approach | NO | Architectural decision needed |
| Different ordering | NO | May be intentional dependency |

### Step 4: Content-Level Comparison

**Compare key content between matched phase/step pairs:**

| Content Area | What to Compare | Discrepancy Class |
|--------------|----------------|-------------------|
| Approaches | Implementation strategy differences | `APPROACH_DIFFERENCE` |
| Edge cases | Missing or different edge case coverage | `MISSING_EDGE_CASE` |
| File references | Missing files that should be affected | `MISSING_FILE_REF` |
| Assumptions | Different underlying assumptions | Flag for review |
| Constraints | Different constraint handling | Flag for review |

### Step 5: Scope Assessment

**Compare overall plan sizes:**

```python
scope_ratio = clean_room_phase_count / existing_phase_count

if scope_ratio > 1.5:
    # Clean-room is significantly larger
    discrepancy_class = "SCOPE_EXPANSION"
    action = "Flag for human review — clean-room identifies more work than originally scoped"

elif scope_ratio < 0.67:
    # Existing is significantly larger
    discrepancy_class = "POSSIBLE_SCOPE_CREEP"
    action = "Flag for human review — original may include unnecessary work"

else:
    # Roughly the same scope
    action = "Proceed with detailed comparison"
```

### Step 6: Generate Discrepancy Report

**Compile all discrepancies into a structured report:**

```yaml
discrepancies:
  # Phase-level
  - type: "MISSING_PHASE"
    clean_room: "Error Handling Layer"
    existing: null
    auto_fix: false
    reason: "Clean-room identifies error handling as separate concern"

  - type: "EXTRA_PHASE"
    clean_room: null
    existing: "UI Polish"
    auto_fix: false
    reason: "Existing includes UI polish — may be scope creep"

  # Step-level
  - type: "MISSING_STEP"
    phase: "Database Schema Setup"
    clean_room: "Add migration rollback support"
    existing: null
    auto_fix: true
    reason: "Missing verification for schema changes"

  # Content-level
  - type: "MISSING_FILE_REF"
    phase: "User Data Access"
    clean_room: "src/repositories/user_repository.py"
    existing: "Not mentioned"
    auto_fix: true
    reason: "Repository file should be referenced"

  # Scope
  - type: "SCOPE_EXPANSION"
    ratio: "1.8"
    auto_fix: false
    reason: "Clean-room identifies more work than originally scoped"
```

### Step 7: Yield Comparison Results

**Pass structured results to auto-fix task or reporting:**

```yaml
# Yield-back context
status: "comparison_complete"
total_discrepancies: N
auto_fix_count: M
flag_for_review_count: K
discrepancies: "<structured list>"
clean_room_plan: "<full markdown>"
existing_plan: "<full markdown>"
semantic_matches: "<list of matched phase pairs>"
scope_assessment: "balanced|expansion|creep"
```

## Context Required

- Related tasks: `audit` (invokes this), `auto-fix` (uses results)
- Related skills: `writing-plans` (provides clean-room plan)