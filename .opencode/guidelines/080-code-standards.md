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

> **See `code-size-enforcement` skill for complete size limit enforcement rules, detection methods, and violation recovery.**

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

## Tool Selection by File Type

### 🚫 PROHIBITED Misuse

**DO NOT run Python tools on non-Python files:**

| Tool | Python Files | Markdown Files |
|------|--------------|----------------|
| `ruff` | ✅ REQUIRED | 🚫 PROHIBITED |
| `pyright` | ✅ REQUIRED | 🚫 PROHIBITED |
| `vulture` | ✅ OPTIONAL | 🚫 PROHIBITED |
| `pymarkdownlnt` | 🚫 PROHIBITED | ✅ REQUIRED |
| `mdformat` | 🚫 PROHIBITED | ✅ REQUIRED |

Running `ruff check` or `ruff format` on `.md` files is a **CRITICAL GUIDELINE VIOLATION**.

### Correct Tool Usage

**Python files (`.py`):**
```bash
uvx ruff check --fix src/ test/   # Lint + auto-fix
uvx ruff format src/ test/        # Format
uvx pyright src/                  # Type check
uvx vulture src/                  # Dead code scan
```

**Markdown files (`.md`):**
```bash
uvx pymarkdownlnt scan -r .opencode/guidelines/ docs/   # Lint
uvx mdformat .opencode/guidelines/ docs/                # Format
```

**Rationale:** Python linters (`ruff`, `pyright`, `vulture`) are designed for Python syntax and will produce incorrect or useless results when run on markdown files. Use markdown-specific tools (`pymarkdownlnt`, `mdformat`) for markdown files.

## Numbering — ENFORCED

All enumeration lists, numbered sections, and step sequences in documentation MUST use **natural counting** (starting at 1).

**Prohibited:**
- Zero-indexed numbered lists (`0. First item`, `1. Second item`)
- Step 0 in procedures (use Step 1 as the first step)
- Phase 0 in specs (use Phase 1 as the first phase)

**Exceptions:**
- Code comments explaining 0-indexed array access
- Technical documentation explicitly explaining zero-based indexing concepts

**Rationale:** Documentation is for humans. Natural counting matches human cognition.

## AI Co-Authored Attribution (MANDATORY)

**AI-generated creative content MUST include co-authored attribution where the content format supports it.**

### What Counts as AI-Generated Content

AI co-authorship applies to **creative, original content authored by AI**:
- Original code written by AI
- Original documentation written by AI
- Original designs/architectures conceived by AI
- New modules, classes, functions created by AI

### What Does NOT Require AI Attribution

**Standard/boilerplate content does NOT require AI attribution:**
- Standard licenses (MIT, Apache, GPL, etc.) - these are established legal templates
- Auto-generated files (lock files, build artifacts, `__pycache__`)
- Framework boilerplate (default configs, standard project structures)
- Minor edits to existing files (typo fixes, formatting)
- Files with no creative content (empty `__init__.py`, pure config)

**Copy-pasted content from ANY external source does NOT get AI attribution:**
- Code copied from Stack Overflow, blogs, tutorials
- Code copied from other projects/repositories
- Documentation copied from official sources
- Configuration copied from templates/examples
- **If it was copy-pasted, it's NOT AI-co-authored** - the original source holds copyright

**Rationale:** AI attribution is about transparency in creative work. Copying a standard MIT license, copying code from Stack Overflow, or copy-pasting documentation from another project requires no AI creativity - those sources hold their own copyrights. Only genuinely original content created by AI deserves AI co-authorship attribution.

### Files Requiring Attribution

| File Type | Attribution Location | Format |
|-----------|---------------------|--------|
| Python files (`.py`) | Module docstring | `"""Co-authored with AI: AI-Name (model-id)"""` |
| README files | Footer section | `## Co-Authored With AI` section |
| New repositories | README.md | AI co-authored section (see below) |
| Original docs | Footer | `*Co-authored with AI: AI-Name (model-id)*` |

### Files NOT Requiring Attribution

| File Type | Reason |
|-----------|--------|
| LICENSE files | Standard legal templates (MIT, Apache, etc.) |
| `pyproject.toml`, `setup.py` | Boilerplate configuration |
| Lock files (`uv.lock`, `package-lock.json`) | Auto-generated |
| Empty `__init__.py` | No content |
| Standard `.gitignore` | Established template |
| Copy-pasted code/docs | Original source holds copyright |

### Attribution Format

```
Co-authored with AI: <AI-Name> (<model-id>)
```

**Example:**
```
Co-authored with AI: OpenCode (ollama-cloud/glm-5)
```

### Repository Creation

When creating a new repository, the README MUST include:

```markdown
## Co-Authored With AI

This repository was created with assistance from AI:

- **AI Agent**: OpenCode
- **Model**: ollama-cloud/glm-5
- **Date**: YYYY-MM-DD
```

**Note:** The LICENSE file uses standard MIT license without modification. AI attribution goes in README, not LICENSE.

### Python Files

Every Python file with original AI-authored code MUST include attribution in the module docstring:

```python
"""Module description.

Co-authored with AI: OpenCode (ollama-cloud/glm-5)
"""
```

### Why This Matters

AI co-authored attribution:
1. Maintains transparency about content origin
2. Follows emerging best practices for AI-assisted work
3. Enables proper credit and traceability
4. Helps identify AI-generated content for review
5. **Respects copyright** - only claims co-authorship on genuinely original AI work

## Cross-Reference Standards

**Cross-references in specs, issues, and documentation MUST use stable anchors, NOT line numbers.**

### Required Format

| Reference Type | Format | Example |
|----------------|--------|---------|
| Function | `file.py` `function_name()` | `process_data()` in `pubmed_client.py` |
| Class | `file.py` `ClassName` | `MeshValidator` in `validator.py` |
| Section | `file.md` `"Section Name"` | `"Cross-Reference Standards"` in `080-code-standards.md` |
| Code snippet | Include snippet (<20 lines) | See examples below |

### Forbidden Format

| Reference Type | Format | Why Forbidden |
|----------------|--------|---------------|
| Line number | `file.py:42` | Breaks on every edit |
| Line range | `file.py:42-48` | Breaks on every edit |
| Bare number | "line 42" | No context, breaks on edit |

### Why This Matters

Line numbers shift when:
- Lines are added above the reference
- Lines are deleted above the reference
- Any edit changes file length

Stable anchors (function names, class names, section headers) remain valid across edits.

### Examples

**❌ WRONG (Line Numbers):**
```
See `file.py:42` for the function definition.
See `guidelines.md:150` for the rule.
```

**✅ CORRECT (Stable Anchors):**
```
See `process_data()` in `file.py` for the function definition.
See `"Cross-Reference Standards"` section in `guidelines.md` for the rule.
```
