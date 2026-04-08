# Task: file-locations

Pattern verification for WHERE files go. Blast radius: HIGH. Invoke before creating ANY file.

## Pattern Table

| Requirement | Guideline Reference |
|-------------|-------------------|
| Temp files go in `./tmp/` | `070-environment.md` - Temp Files & Cleanliness |
| Test files go in `test/` | `AGENTS.md` - Build / Lint / Test Commands |
| Migrations go in `_Migration` entries | `100-persistence.md` - Schema Standards |
| Agent scripts go in `ai_bin/` | `AGENTS.md` - Project Structure |
| Standalone scripts go in `scripts/` | `070-environment.md` - Scripting |
| Notebooks go in notebooks directory | `061-notebook-rules.md` |
| No temp files at project root | `060-tool-usage.md` - Path Rules |
| No temp files in `src/` or `notebooks/` | `100-persistence.md` - Database Location |

## Violation Table

| Violation | Correct Action |
|-----------|---------------|
| Standalone migration file | Move to `_Migration` entry in `src/commons/persistence/pg/schema.py` |
| Temp file at project root | Delete, recreate in `./tmp/` |
| Test file in `src/` | Move to `test/` directory |
| Agent script outside `ai_bin/` | Move to `ai_bin/` |
| Using `/tmp/` | Use `./tmp/` instead |
| Files in `.tmp/` | Use `./tmp/` instead |

## Invocation

```
/skill implementation-quality --task file-locations
```

Invoke before:
- Creating new files
- Moving files
- Generating output files
- Writing temp scripts

## Pre-Creation Checklist

- [ ] Location follows pattern table
- [ ] No violations from violation table
- [ ] Directory exists or will be created
- [ ] Path is relative (not absolute)
- [ ] Path is within `./tmp/` for temp files

## Cross-References

- `070-environment.md` - Project structure rules
- `100-persistence.md` - Migration requirements
- `060-tool-usage.md` - Path rules (no absolute paths)