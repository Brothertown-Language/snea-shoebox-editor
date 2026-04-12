# Task: decompose

## Purpose

Provide decomposition patterns and guidance for oversized code artifacts.

## Decomposition Patterns

### Oversized Functions (> 40 lines)

Extract helper functions using the "Extract Method" refactoring pattern:

```python
# BEFORE (45 lines - exceeds 40 line limit)
def process_data(data: dict) -> dict:
    # ... 45 lines of processing ...

# AFTER (decomposed)
def process_data(data: dict) -> dict:
    validated = validate_data(data)
    transformed = transform_data(validated)
    return enrich_data(transformed)

def validate_data(data: dict) -> dict:
    # ... 15 lines ...

def transform_data(data: dict) -> dict:
    # ... 15 lines ...

def enrich_data(data: dict) -> dict:
    # ... 10 lines ...
```

Principles:
- Each function should do ONE thing
- Use descriptive names for decomposed functions
- The outer function becomes an orchestrator calling helpers

### Oversized Notebook Cells (> 50 lines)

Split cells doing multiple things into focused cells:

```python
# BEFORE (single 60-line cell doing data loading and processing)
# Cell 1: Load and process data (60 lines)

# AFTER (split into focused cells)
# Cell 1: Load data (15 lines)
# Cell 2: Validate data (10 lines)
# Cell 3: Transform data (15 lines)
# Cell 4: Display summary (10 lines)
```

Principles:
- Each cell should do ONE thing
- Use intermediate variables only when necessary for clarity
- Consider extracting complex logic to `.py` modules

### Oversized Files (> 300 lines)

Split monolithic files into package structure:

```python
# BEFORE: monolithic_file.py (350 lines)

# AFTER: package structure
monolithic/
    __init__.py
    core.py      # main logic (150 lines)
    helpers.py   # utility functions (100 lines)
    types.py     # type definitions (50 lines)
```

Principles:
- Files should have clear, single purposes
- Large files indicate mixed concerns
- Use package structure (directory with `__init__.py`)
- Use submodules for related functionality

## Nested Nesting Reduction

When nesting exceeds 3 levels, refactor using:
- Early returns (guard clauses)
- Extract nested logic into separate functions
- Use dictionary dispatch instead of if/elif chains
- Use comprehensions and generator expressions

## Verification After Decomposition

1. Verify new structure meets all size limits
2. Run tests if applicable
3. Document significant changes in commit/PR message