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
  rerun from Step 100 (`0100_ingest_xml.ipynb`) — performed by the user, not the agent.

## Design Principles — ENFORCED UNIVERSALLY

> **See `code-size-enforcement` skill for complete size limit enforcement rules, detection methods, and violation recovery.**

- **KISS (Keep It Simple, Stupid)**: Simplest correct solution. No unnecessary abstraction or cleverness.
- **DRY (Don't Repeat Yourself)**: No duplicated logic. Extract shared functionality into reusable functions/modules.
- **Non-Monolithic**: Break large blocks into cohesive, independent components.
- **Modular**: Each function, class, module, notebook cell should have a single clear purpose and minimal dependencies.
- **Single Function Methods**: Every function/method performs exactly ONE task.
- **No Monoliths**: Long procedural blocks are prohibited. If a function exceeds 350 words, decompose it.
- **No Magic Strings or Numbers**: Extract domain meaning to named constants (`UPPER_SNAKE_CASE`).
- **No Re-exports** (ABSOLUTE PROHIBITION):
  - NEVER add `from X import Y` or `__all__` to `__init__.py` files.
  - `__init__.py` must contain ONLY a module docstring.
  - All imports must reference concrete module paths.
- **Top-Level Documentation**: Every Python source file must include a brief top-level comment.
- **Docstring/Comment Determinism**: Use deterministic wording. Avoid ambiguous phrasing.
- **Labels Over Index Numbers**: Reference items by label, not by positional index.

## Modern Python

- **Pathlib**: `pathlib.Path` exclusively for file/dir ops. No `os.path.join`, `os.mkdir`, string concatenation.
- **f-strings**: For all string interpolation. No `.format()` or `%` unless required by external libs.
- **Metadata Integrity**: Use `shutil.copy2` (not `shutil.copy`).

## Libraries & Packages

- Use NLP packages (e.g., NLTK) for NLP tasks — no regex for NLP. For complex pattern logic, prefer FSM/LALR grammars.
- All DB/system ops use existing project libraries. Direct data file manipulation prohibited unless instructed.
- Use `ConfigurationManager` for all data file paths — never hardcode or assume data file locations.

---

## Print Statements & Output

- **NO narration/signal prints**: Never add print statements that narrate code changes or announce implementation details.
- **NO pedantic notes in code**: Lines like `print("Note: X now uses Y")` are prohibited.
- **Valid print uses**: Progress bars, data summaries, error messages, user-facing status, diagnostic output.
- **Invalid print uses**: Announcing "implementation complete", narrating changes, tutorial-style output.
- **If context is needed**: Add a docstring or code comment — never a print statement.

---

## Linting & Static Analysis

### ⚠️ MANDATORY: Pre-Lint File Type Verification

**Running the wrong linter on the wrong file type is a CRITICAL GUIDELINE VIOLATION.**

**Verification Before Each Lint Command:**

1. **Verify file type**: `ls -la src/ | head -5`
2. **Select CORRECT tool for file type**:
   - Python files? Use Python tools (`ruff`, `pyright`)
   - Markdown files? Use markdown tools (`pymarkdownlnt`, `mdformat`)
   - Mixed? Run SEPARATE commands for each type

### Correct Tool Usage

| Tool | Python Files | Markdown Files |
|------|--------------|----------------|
| `ruff` | ✅ REQUIRED | 🚫 PROHIBITED |
| `pyright` | ✅ REQUIRED | 🚫 PROHIBITED |
| `vulture` | ✅ OPTIONAL | 🚫 PROHIBITED |
| `pymarkdownlnt` | 🚫 PROHIBITED | ✅ REQUIRED |
| `mdformat` | 🚫 PROHIBITED | ✅ REQUIRED |

**Running `ruff check` on `.md` files is a CRITICAL GUIDELINE VIOLATION.**

---

## Numbering — ENFORCED

All enumeration lists, numbered sections, and step sequences in documentation MUST use **natural counting** (starting at 1).

**Prohibited:**
- Zero-indexed numbered lists (`0. First item`, `1. Second item`)
- Step 0 in procedures (use Step 1 as the first step)
- Phase 0 in specs (use Phase 1 as the first phase)

**Exceptions:**
- Code comments explaining 0-indexed array access
- Technical documentation explicitly explaining zero-based indexing concepts

---

## AI Co-Authored Attribution (MANDATORY)

**AI-generated creative content MUST include co-authored attribution where the content format supports it.**

### ⚠️ MANDATORY: Dynamic Runtime Identity Detection

**Agents MUST use their ACTUAL runtime identity — NEVER copy placeholder values from examples.**

| Identity Component | How to Detect | FORBIDDEN |
|-------------------|---------------|-----------|
| `<AgentName>` | Agent's actual name at runtime | Copying "OpenCode" or "AI Assistant" from examples |
| `<ModelID>` | Backing model ID at runtime | Copying "ollama-cloud/*" from examples |
| `<ai-email>` | Agent's noreply email | Using project domain email |

**Example Values in Guidelines are ILLUSTRATIVE:**
- `<AgentName> (<ModelID>)` → Example only
- `AI Assistant (model-id)` → Placeholder only
- **DETECT YOUR OWN IDENTITY** at runtime

**When Identity Unknown:**
- STOP and ask user for clarification
- DO NOT use example values as defaults
- DO NOT guess or invent identity values

### What Counts as AI-Generated Content

AI co-authorship applies to **creative, original content authored by AI**:
- Original code written by AI
- Original documentation written by AI
- Original designs/architectures conceived by AI
- New modules, classes, functions created by AI

### What Does NOT Require AI Attribution

**Standard/boilerplate content does NOT require AI attribution:**
- Standard licenses (MIT, Apache, GPL, etc.) - established legal templates
- Auto-generated files (lock files, `__pycache__`)
- Framework boilerplate (default configs, project structures)
- Minor edits (typo fixes, formatting)
- **Copy-pasted content from ANY external source** - original source holds copyright

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
| LICENSE files | Standard legal templates (MIT, Apache, GPL) |
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
Co-authored with AI: MyAIAgent (provider/model-name)
```

### Repository Creation

When creating a new repository, the README MUST include:

```markdown
## Co-Authored With AI

This repository was created with assistance from AI:

- **AI Agent**: <AI-Name>
- **Model**: <model-id>
- **Date**: YYYY-MM-DD
```

**Note:** The LICENSE file uses standard MIT license without modification. AI attribution goes in README, not LICENSE.

### Python Files

Every Python file with original AI-authored code MUST include attribution in the module docstring:

```python
"""Module description.

Co-authored with AI: MyAIAgent (provider/model-name)
"""
```

### Why This Matters

AI co-authored attribution:
1. Maintains transparency about content origin
2. Follows emerging best practices for AI-assisted work
3. Enables proper credit and traceability
4. Helps identify AI-generated content for review
5. **Respects copyright** - only claims co-authorship on genuinely original AI work

---

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