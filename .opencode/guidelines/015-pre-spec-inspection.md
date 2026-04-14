# Pre-Spec Code Inspection Checklist

**This checklist MUST be completed before proposing any approach in a spec or bug report. Incomplete inspection is the concrete minimum standard for the "Spec Without Investigation" critical violation (see `000-critical-rules.md`).**

## When to Apply

- Before any spec proposes changes to existing code
- Before any bug report proposes a fix approach
- Before any investigation phase concludes with a design recommendation

Exempt: New greenfield features with no existing code interaction; trivial typos with no code interaction.

## Mandatory Checklist

### 1. Trace Actual Call Paths

For any file being modified:

- Who imports it? Use `srclight_get_callers` or `grep` for import statements
- Who calls its public functions? Use `srclight_get_callers` on each symbol
- Are those callers production code or dead references? Verify each caller is in an actively-used module
- Document the call chain from entry point to target

**Evidence required:** List of callers with file paths and line numbers. State whether each caller is production or dead.

### 2. Verify Imports

- Does the consuming code actually import from the target module?
- Or does it use an independent path (re-export, alias, re-implementation)?
- Check `__init__.py` exports vs direct imports in consuming code
- Verify the import path the spec assumes matches the actual import path in source

**Evidence required:** Actual import statements from consuming files. Note if re-exported or aliased.

### 3. Detect Dead Code

- Is the target module/function exported but never imported by production code?
- Check `__init__.py` exports vs actual importers across the codebase
- Use `srclight_get_dependents` to find what depends on the target
- If no production dependents exist, flag the target as potentially dead before proposing changes to it

**Evidence required:** Export list from `__init__.py` vs actual import counts. Flag any exported symbol with zero production importers.

### 4. Verify Format/Protocol Assumptions

- If the spec assumes a data format (e.g., `KEY=value` vs `KEY: value`), verify against actual source output
- If the spec assumes a function signature, verify with `srclight_get_signature` — never rely on memory
- If the spec assumes a file format (JSON, YAML, TOML, INI), verify the actual parser/generator in use
- If the spec assumes a protocol (REST, CLI, IPC), verify the actual implementation

**Evidence required:** Actual format/protocol from source code with file path and line number. Quote the exact line that confirms the format.

### 5. Confirm Architectural Layer

- Is the proposed change at the correct layer (presentation, business logic, data access, infrastructure)?
- Will the change violate any existing layer boundaries?
- Does the target module belong to the layer the spec assumes?
- Check import directionality — lower layers should not import from higher layers

**Evidence required:** Statement of the target module's architectural layer, with file-path evidence supporting the classification.

### 6. Check for Existing Alternatives

- Does the codebase already have an alternative mechanism that handles the same concern?
- Search for similar function names, similar patterns, or utility modules that already solve the problem
- Check if a config flag, feature toggle, or existing hook already provides the desired behavior
- Check if a dependency (library, framework) already provides the capability

**Evidence required:** List of existing mechanisms found, with file paths. Explicit statement of whether any existing mechanism satisfies the requirement (fully, partially, or not at all).

## Enforcement

### Completeness Threshold

All six items MUST be addressed. If an item is genuinely not applicable, state "N/A" with a one-sentence justification (e.g., "N/A — new module with no existing callers"). Unmentioned items are violations.

### Integration Points

- **`brainstorming` skill → `explore` task:** This checklist is a mandatory step before "explore requirements" (see `explore.md` Step 1)
- **`spec-creation` skill:** This checklist is a mandatory pre-condition for the `requirements` task (see `SKILL.md`)
- **`000-critical-rules.md` → "Spec Without Investigation":** Incomplete inspection of this checklist constitutes that critical violation

### Tool Recommendations

| Checklist Item | Primary Tool | Fallback |
| -- | -- | -- |
| Trace call paths | `srclight_get_callers` | `grep` for import/call patterns |
| Verify imports | `grep` for import statements | `read` on `__init__.py` |
| Detect dead code | `srclight_get_dependents` | `grep` + manual cross-reference |
| Verify format/protocol | `srclight_get_signature`, `read` source | Live documentation |
| Confirm layer | `read` target module + its imports | `grep` for layer boundary markers |
| Existing alternatives | `srclight_hybrid_search` | `grep` for similar names/patterns |

```yaml+symbolic
schema_version: "1.0"
last_updated: "2026-04-13T12:00:00Z"
rules:
  - id: pre-spec-inspection-001
    title: "Code inspection checklist must be completed before spec approach"
    conditions:
      all:
        - "spec_proposes_code_changes == true"
        - "checklist_completed == false"
    actions:
      - HALT
    conflicts_with: []
    requires: []
    triggers: [brainstorming, spec-creation]
    source: "015-pre-spec-inspection.md §Mandatory Checklist"

  - id: pre-spec-inspection-002
    title: "All six checklist items must be addressed"
    conditions:
      all:
        - "checklist_started == true"
        - "all_items_addressed == false"
    actions:
      - HALT
    conflicts_with: []
    requires: [pre-spec-inspection-001]
    triggers: [spec-creation]
    source: "015-pre-spec-inspection.md §Completeness Threshold"

  - id: pre-spec-inspection-003
    title: "Incomplete inspection is Spec Without Investigation violation"
    conditions:
      all:
        - "spec_proposes_code_changes == true"
        - "checklist_completed == false"
    actions:
      - VIOLATION(spec-without-investigation)
    conflicts_with: []
    requires: []
    triggers: [approval-gate, spec-auditor]
    source: "015-pre-spec-inspection.md §Enforcement"
```