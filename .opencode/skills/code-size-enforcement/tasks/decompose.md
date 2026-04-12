# Task: decompose

## Purpose

Provide decomposition patterns and guidance for oversized code artifacts.

## Decomposition Patterns

### Oversized Functions (> ~100 words)

Extract helper functions using the "Extract Method" refactoring pattern:

```python
# BEFORE (~120 words - exceeds ~100 word limit)
def process_data(data: dict) -> dict:
    # ... ~120 words of processing ...

# AFTER (decomposed)
def process_data(data: dict) -> dict:
    validated = validate_data(data)
    transformed = transform_data(validated)
    return enrich_data(transformed)

def validate_data(data: dict) -> dict:
    # ... ~35 words ...

def transform_data(data: dict) -> dict:
    # ... ~35 words ...

def enrich_data(data: dict) -> dict:
    # ... ~20 words ...
```

Principles:
- Each function should do ONE thing
- Use descriptive names for decomposed functions
- The outer function becomes an orchestrator calling helpers

### Oversized Notebook Cells (> ~120 words)

Split cells doing multiple things into focused cells:

```python
# BEFORE (single ~150-word cell doing data loading and processing)
# Cell 1: Load and process data (~150 words)

# AFTER (split into focused cells)
# Cell 1: Load data (~35 words)
# Cell 2: Validate data (~25 words)
# Cell 3: Transform data (~35 words)
# Cell 4: Display summary (~20 words)
```

Principles:
- Each cell should do ONE thing
- Use intermediate variables only when necessary for clarity
- Consider extracting complex logic to `.py` modules

### Oversized Files (> ~750 words)

Split monolithic files into package structure:

```python
# BEFORE: monolithic_file.py (~800 words)

# AFTER: package structure
monolithic/
    __init__.py
    core.py      # main logic (~350 words)
    helpers.py   # utility functions (~250 words)
    types.py     # type definitions (~120 words)
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