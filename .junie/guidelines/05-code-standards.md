# Code Standards

## Typing

- Mandatory explicit type hints (Pydantic/Dataclasses) project-wide. Avoid `Any`; use concrete types wherever possible.
  `Any` is acceptable only when imposed by third-party signatures.
- Use Python 3.12+ built-in types (`list[str]`, `dict[str, Any]`), not `typing.List`/`Dict`.
- **Strict Enum Mapping**: DB-stored enums use plain string values (`NEW_DISCOVERY = "new_discovery"`).
  Emojis/presentation strings handled as properties or mapping functions, never stored in DB.

## Design Principles

- **KISS**: Simplest correct solution. No unnecessary abstraction or cleverness.
- **DRY & Modularity**: No duplicated logic. Break into discrete, focused methods — no monolithic blocks.
- **Single Responsibility**: Every method performs exactly one task. Decompose long procedural blocks.
- **No Re-exports**: Don't add re-exports in `__init__.py` via `__all__`. Import from concrete module paths. Existing
  re-exports are assumed approved — do not remove them without explicit instruction. When editing an `__init__.py` for
  another purpose, leave existing `__all__` entries untouched.

## Modern Python

- **Pathlib**: `pathlib.Path` exclusively for file/dir ops. No `os.path.join`, `os.mkdir`, string concatenation. Use `/`
  operator.
- **f-strings**: For all string interpolation. No `.format()` or `%` unless required by external libs.
- **Metadata Integrity**: Use `shutil.copy2` (not `shutil.copy`). Never discard metadata unless explicitly instructed.

## Libraries & Packages

- All DB/system ops use existing project libraries. Direct data file manipulation prohibited unless instructed.
