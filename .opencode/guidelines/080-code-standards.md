# Code Standards

## Scope

These standards apply to **ALL code artifacts**: Python modules, Jupyter notebooks, LaTeX/XeLaTeX documents, configuration files, scripts, and any other code written or modified in this repository. No exceptions.

## Typing

- Mandatory explicit type hints (Pydantic/Dataclasses) project-wide. Avoid `Any`; use concrete types wherever possible.
  `Any` is acceptable only when imposed by third-party signatures.
- Use Python 3.12+ built-in types (`list[str]`, `dict[str, Any]`), not `typing.List`/`Dict`.
- **Strict Enum Mapping**: DB-stored enums use plain string values (`NEW_DISCOVERY = "new_discovery"`).
  Emojis/presentation strings handled as properties or mapping functions, never stored in DB.
- **Parsing Logic Changes**: Changes to `src/commons/parsing/` affecting extracted metadata require a full pipeline
  rerun from Step 100 (`0100_ingest_xml.ipynb`) — performed by the user, not the agent. A change **affects extracted
  metadata** if it alters the values, presence, or format of any field written to the database or output files. Agent
  MUST NOT write DB remediation, backfill, or migration code to compensate for parsing changes; the pipeline rerun
  handles data consistency. Flag the rerun requirement to the user after making such changes. Redundant "safety-net"
  updates in downstream notebooks prohibited.

## Design Principles — ENFORCED UNIVERSALLY

> **See `.opencode/skills/code-size-enforcement/SKILL.md` for complete size limit enforcement rules, detection methods, and violation recovery.**

- **KISS (Keep It Simple, Stupid)**: Simplest correct solution. No unnecessary abstraction or cleverness. Prefer straightforward, readable code over "clever" optimizations.
- **DRY (Don't Repeat Yourself)**: No duplicated logic. Extract shared functionality into reusable functions/modules. If you copy-paste code, you're doing it wrong.
- **Non-Monolithic**: Break large blocks into cohesive, independent components. Notebooks should have focused cells — cells that do "one thing."
- **Modular**: Each function, class, module, notebook cell, and document section should have a single clear purpose and minimal dependencies.
- **Single Function Methods**: Every function/method performs exactly ONE task. If a function has multiple responsibilities, split it. Decompose ALL tasks, plans, and algorithms into discrete single-function methods. This applies to:
  - Python functions in `.py` files
  - Notebook cells (each cell should do ONE thing)
  - LaTeX/XeLaTeX environments and macros (one purpose each)
  - Scripts and configuration files
- **No Monoliths**: Long procedural blocks are prohibited. If a function exceeds 40 lines, decompose it. If a notebook cell exceeds 50 lines, split it into multiple cells.
- **No Magic Strings or Numbers**: All literal strings and numbers that carry domain meaning must be extracted to named
  constants (`UPPER_SNAKE_CASE` at module level, or class-level `ClassVar`) before use. Inline literals are only
  acceptable for truly universal values (e.g., `0`, `1`, `""`, `True`, `False`, HTTP status `200`).
- **No Re-exports** (ABSOLUTE PROHIBITION):
  - NEVER add `from X import Y` or `__all__` to `__init__.py` files.
  - `__init__.py` must contain ONLY a module docstring describing the package purpose.
  - All imports must reference concrete module paths (e.g., `from commons.mesh.validator import MeshValidator`,
    NOT `from commons.mesh import MeshValidator`).
  - Rationale: Re-exports break IDE "Find Usages" and "Go to Definition" by creating false source locations.
  - Existing `__all__` entries in legacy files are assumed approved — do not remove them without explicit instruction.
  - When creating a NEW `__init__.py`, it must be docstring-only. When editing an existing `__init__.py`, do not add
    any imports or `__all__` entries.
- **Top-Level Documentation**: Every Python source file must include a brief top-level comment identifying the
  package's or class's purpose. Use a module docstring (preferred) or a leading `#` comment. Keep it to one or two
  concise sentences — enough for `ai_bin/py structure` to display alongside the filename.
- **Docstring/Comment Determinism**: Pydoc/docstrings and code comments must use deterministic wording. Avoid ambiguous hedge/alternative phrasing such as `maybe`, `if ... or ...`, `and/or`, or `A + B or C` when describing required behavior, validation paths, or implementation intent.
- **Labels Over Index Numbers**: When editing structured artifacts (notebooks, migration lists, cell arrays, ordered
  configs), add and use stable labels/names so that inserts, deletes, and moves which change index numbers do not cause
  edit failures. Reference items by label, not by positional index.

## Modern Python

- **Pathlib**: `pathlib.Path` exclusively for file/dir ops. No `os.path.join`, `os.mkdir`, string concatenation. Use `/`
  operator.
- **f-strings**: For all string interpolation. No `.format()` or `%` unless required by external libs.
- **Metadata Integrity**: Use `shutil.copy2` (not `shutil.copy`). Never discard metadata unless explicitly instructed.

## Libraries & Packages

- Use NLP packages (e.g., NLTK) for NLP tasks — no regex for NLP. NLP tasks include tokenization, stemming,
  lemmatization, part-of-speech tagging, named entity recognition, and sentence segmentation. Simple pattern matching
  or fixed-format extraction does not qualify and may use regex. For tasks requiring complex pattern logic beyond
  simple fixed-format extraction, prefer FSM or LALR-type grammars (e.g., `lark`, `pyparsing`) over regex — regex is
  brittle on live data.
- All DB/system ops use existing project libraries. Direct data file manipulation prohibited unless instructed.
- Use `ConfigurationManager` for all data file paths — never hardcode or assume data file locations.
  `project-config.ini` is located at project root; initialize `ConfigurationManager` with the project root path (
  resolved via root resolution per `120-scripting.md`).

## Print Statements & Output

- **NO narration/signal prints**: Never add print statements that narrate code changes, signal feature updates, or announce implementation details. Print statements are for data output and user-facing information only.
- **NO pedantic notes in code**: Lines like `print("Note: X now uses Y")` or `print("Feature Z implemented")` are prohibited. Code should speak for itself through documentation and version control.
- **Valid print uses**: Progress bars, data summaries, error messages, user-facing status, diagnostic output during development/testing.
- **Invalid print uses**: Announcing "implementation complete", narrating changes, signaling "now using X", helpful hints, tutorial-style output, any form of self-documentation via print.
- **Examples of prohibited prints**:
  - `print("Note: Visualizations now use dark mode")`
  - `print("Feature X enabled")`
  - `print("Using new algorithm for Y")`
  - `print("Implementation complete - phase 1")`
- **If context is needed**: Add a docstring, code comment, or update documentation — never a print statement.

## Linting & Static Analysis

- Run appropriate dev tools (linters, type checkers) listed in `ai_bin/start` on all modified Python files before submitting.
