# UI Design — interaction-spec task

## Purpose

Produce a toolkit-agnostic interaction specification in YAML from a spec or design context.

## Entry Criteria

- Spec or context document is available and has been read.
- `worktree.path` is set and verified.
- Navigation flows, component states, and data requirements are understood.

## Exit Criteria

- Interaction spec YAML file exists in the worktree.
- YAML validates against `templates/interaction_spec_schema.yaml`.
- No framework-specific properties in the spec (no Streamlit, React, Vue, Godot, Flutter, Android references).
- `completion` subtask has been invoked.
- Result contract returned: `{status, artifact_path, summary, concerns}`.

## Procedure

1. Read the spec or context for the interaction flows being specified.
2. Create a YAML file based on `templates/interaction_spec_schema.yaml` structure.
3. Fill in metadata, layout regions, components, navigation, data_flow, and accessibility sections.
4. Ensure `target_framework` is omitted or set to a generic value (not a specific framework).
5. Validate the YAML with `scripts/validate_interaction_spec.py`.
6. Ensure no framework-specific properties exist anywhere in the spec.
7. Invoke `completion` subtask.
8. Return result contract.