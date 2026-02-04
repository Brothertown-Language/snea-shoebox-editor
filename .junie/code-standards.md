<!-- Copyright (c) 2026 Brothertown Language -->

# Code Standards and Organization

## Copyright Headers
All `.py` (Python) and `.md` (Markdown) files must include the appropriate copyright header, except for data files.
- **For Python files:**
  ```python
  # Copyright (c) 2026 Brothertown Language
  ```
- **For Markdown files:**
  ```markdown
  <!-- Copyright (c) 2026 Brothertown Language -->
  ```
- **Rule:** If you are editing an existing file that already has a header, **DO NOT** modify or remove it.
- **Rule:** If you are creating a new file, you **MUST** add the appropriate header at the very top.

## Code Style
Consistency with the existing codebase is mandatory.
- **Mirror Patterns:** Follow the existing patterns and idioms in the codebase exactly.
- **Formatting:** Match the indentation, naming conventions, and import order used in the file or module you are working on.
- **Comments:** Match the frequency and language of existing comments. Do not add excessive comments if the surrounding code is sparsely commented, unless explicitly requested.

## File Naming
- **Conventions:** Follow the project's established conventions for casing (e.g., snake_case vs PascalCase) and separators.
- **Sequential Files:** If files are numbered sequentially, maintain continuous numbering and preserve the exact numbering format.

## Method Design and Organization
Good code organization is critical for maintainability.
- **Discrete Methods:** **ALWAYS** break code into discrete methods. Each method should perform one single, well-defined task.
- **Single Responsibility:** **NEVER** create multi-function methods. Methods must have a single, clear responsibility.
- **Cohesion:** Keep methods focused and cohesive.
- **Composition:** Prefer composition over complex, multi-purpose functions.

## Type Annotations
Explicit typing is required for all Python code.
- **Strict Typing:** **ALWAYS** use strict typing for all function parameters, return values, and variables.
- **Avoid Any:** **NEVER** use the `Any` type unless it is absolutely, demonstrably unavoidable.
- **Typing Module:** Leverage Python's `typing` module (e.g., `List`, `Dict`, `Optional`, `Union`, `Callable`).
- **Mandatory:** Type hints are a mandatory requirement, not an optional suggestion.

## Memory and Long-Term Tracking
- **Storage:** Use the `.junie/` directory for storing long-term information and memory files.
- **Structure:** Organize memory files hierarchically for quick and accurate information retrieval.
- **Formatting:** Maintain consistent formatting across all memory files.
- **Updates:** Update memory files and guidelines only when explicitly instructed to "remember" something. When instructed to "remember", update the relevant guidelines and make no other unrelated changes.
