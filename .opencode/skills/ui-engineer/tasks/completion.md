# UI Engineer — completion task

## Purpose

Idempotent cleanup of temporary resources and production of a final summary after any ui-engineer task.

## Entry Criteria

- `worktree.path` is set and verified.
- One or more ui-engineer tasks have been executed (or attempted).

## Exit Criteria

- Temporary files in `./tmp/` related to ui-engineer tasks are cleaned up.
- Final summary is produced.
- Result contract returned: `{status, cleaned_up, summary}`.

## Procedure

1. List temporary files in `./tmp/` related to ui-engineer tasks (intermediate renders, build artifacts, etc.).
2. Remove temporary files that are not referenced by any final artifact.
3. Verify all final implementation files, test specs, and config files still exist and are valid.
4. Produce a final summary of all artifacts created, their locations, and any concerns.
5. Return result contract.
6. HALT — no further action after completion.