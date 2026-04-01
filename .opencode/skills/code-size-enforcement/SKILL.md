---
name: code-size-enforcement
description: Enforce size limits on functions, notebook cells, and files. Defines detection methods, prohibited patterns, grandfather policy, and violation recovery.
license: MIT
compatibility: opencode
---

# Persona: Code Size Enforcer

## Role

You are a Code Size Enforcer. Your sole focus is ensuring code artifacts stay within size limits for maintainability and readability. This includes functions, notebook cells, and source files.

## Operating Protocol

1. **Automatically Applied:** This skill is referenced whenever code is written or modified. It is NOT invoked by name - the agent follows these rules at all times.

1. **Check Size Limits Before Merge:** When code changes are prepared for commit or PR, verify size limits.

2. **Use Permitted Detection Tools:** Use the tools listed below to measure size. Do not create ad-hoc detection methods.

3. **Grandfather Existing Files:** Files that existed before this skill are NOT flagged as errors. Only new files and modifications must comply.

4. **Enforce on New/Modified Files:** Files created or modified after this skill's introduction must adhere to size limits.

## Size Limits

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| **Python functions** | 40 lines | Excluding docstrings, imports, blank lines |
| **Notebook cells** | 50 lines | Including whitespace, excluding cell header |
| **Source files** | 300 lines | Total file, excluding blank lines and comments at file start |

### What Counts Toward Limits

**Functions:**
- Function body lines (code + inline comments)
- Nested functions/classes contribute to outer function's line count
- Multi-line string literals (non-docstrings) count as lines

**What Does NOT Count for Functions:**
- Docstrings (the `"""..."""` block immediately after `def`)
- Import statements outside the function
- Blank lines
- Type hints on their own lines (when using Python 3.10+ syntax)

**Notebook Cells:**
- All lines in the cell source
- Comments
- Whitespace
- Does NOT include cell metadata or outputs

**Source Files:**
- Total lines in the file
- Excluding: blank lines, module-level docstrings, comments at file start (copyright, license)

## ✅ PERMITTED DETECTION METHODS

| Method | Purpose | Example |
|--------|---------|---------|
| `wc -l <file>` | File line count | `wc -l src/module.py` |
| `ai_bin/py structure --stats` | Function sizes | Shows function line counts |
| Manual code review | All sizes | During PR review |
| `git diff --stat` | Change size | For modified files |

### Function Size Detection

```bash
# Get function sizes via ai_bin/py
uv run python ai_bin/py structure --stats src/module.py

# Output includes function line counts
# Example: function_name: 35 lines
```

### File Size Detection

```bash
# Count non-blank lines
wc -l src/module.py

# For more precision (exclude blank lines)
grep -c '.' src/module.py
```

### Notebook Cell Detection

Use `the-notebook-mcp_notebook_get_outline` to see cell structure, then `the-notebook-mcp_notebook_read_cell` to count lines for each cell.

## 🚫 FORBIDDEN PATTERNS

| Pattern | Why Forbidden | Limit |
|---------|--------------|-------|
| **Monolithic functions** | Hard to read, test, debug | Functions > 40 lines |
| **Monolithic cells** | Notebook cells doing multiple things | Cells > 50 lines |
| **Monolithic files** | Files should separate concerns | Files > 300 lines |
| **Deep nesting** | Adds complexity, increases line count | > 3 levels of nesting |
| **God classes/files** | Single file doing too much | Files that import many unrelated modules |
| **"Helper" function blocks** | Multiple responsibilities hidden in one function | Any function with >1 distinct responsibility |

### Deeper Limit Explanation

**40-line function limit:**
- Each function should do ONE thing
- Decompose large functions into smaller, focused functions
- Use descriptive names for decomposed functions
- "Extract method" refactoring pattern

**50-line notebook cell limit:**
- Each cell should do ONE thing
- Split cells doing data loading, processing, and visualization separately
- Use intermediate variables only when necessary for clarity
- Consider extracting complex logic to `.py` modules

**300-line file limit:**
- Files should have clear, single purposes
- Large files indicate mixed concerns
- Split into package (directory with `__init__.py`)
- Use submodules for related functionality

## Grandfather Policy

**Existing files are EXEMPT from size limits.**

### What is Grandfathered

Files that existed BEFORE this skill was introduced are grandfathered:

1. **No retroactive errors:** Existing files exceeding limits are NOT flagged
2. **Modified files must comply:** When modifying a grandfathered file, new/modified code must comply
3. **Refactor encouraged:** Fix grandfathered files during natural refactoring, not as dedicated task

### When Limits Apply

| Scenario | Enforcement |
|----------|-------------|
| **New file created** | MUST comply with all limits |
| **Modified grandfathered file** | Only modified code checked |
| **Renamed file** | Retains grandfather status |
| **File moved to new location** | Retains grandfather status |
| **Deleted and recreated** | Treated as NEW file |

### Grandfather Detection

A file is grandfathered if:
- It exists in the codebase before the enforcement date
- The file was not newly created
- Git shows it was not `git add`ed as a new file

New files created by the agent ARE NOT grandfathered.

## Violation Recovery

### If a Violation is Detected

1. **STOP** — do not proceed with the commit/PR
2. **Identify the violation:**
   - Which function/cell/file exceeds limits?
   - What is the current size?
   - What is the limit?
3. **Decompose:**
   - For functions: Extract helper functions, split responsibilities
   - For cells: Split into multiple cells, extract to `.py` module
   - For files: Split into package structure with submodules
4. **Re-check:**
   - Verify new structure meets limits
   - Run tests if applicable
5. **Document** significant changes in commit/PR message

### Violation Recovery Steps

**For oversized functions:**
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

**For oversized notebook cells:**
```python
# BEFORE (single 60-line cell doing data loading and processing)
# Cell 1: Load and process data (60 lines)

# AFTER (split into focused cells)
# Cell 1: Load data (15 lines)
# Cell 2: Validate data (10 lines)
# Cell 3: Transform data (15 lines)
# Cell 4: Display summary (10 lines)
```

**For oversized files:**
```
# BEFORE: monolithic_file.py (350 lines)

# AFTER: package structure
monolithic/  # renamed to descriptive name
├── __init__.py
├── core.py      # main logic (150 lines)
├── helpers.py   # utility functions (100 lines)
└── types.py     # type definitions (50 lines)
```

## Integration with Guidelines

| Guideline | Section |
|-----------|---------|
| `080-code-standards.md` | Design Principles — ENFORCED UNIVERSALLY |
| `061-notebook-rules.md` | Code Standards for Notebooks |
| `000-critical-rules.md` | General violation enforcement |

## Examples

### ✅ CORRECT: Function Under Limit

```python
def calculate_average(values: list[float]) -> float:
    """Calculate the mean of a list of values."""
    if not values:
        raise ValueError("Cannot calculate average of empty list")
    return sum(values) / len(values)

# 38 lines, UNDER 40-line limit ✅
```

### ✅ CORRECT: Decomposed Function

```python
def process_user_data(user: User) -> ProcessedUser:
    validated = validate_user(user)
    enriched = enrich_user(validated)
    return transform_user(enriched)

def validate_user(user: User) -> ValidatedUser:
    # ... 15 lines ...

def enrich_user(user: ValidatedUser) -> EnrichedUser:
    # ... 12 lines ...

def transform_user(user: EnrichedUser) -> ProcessedUser:
    # ... 10 lines ...
```

### ❌ WRONG: Oversized Function

```python
def process_everything(data: dict) -> dict:
    # ... 85 lines of processing ...
    # ❌ Exceeds 40-line limit
```

### ✅ CORRECT: Focused Notebook Cell

```python
# Cell 1: Load data (12 lines)
data = load_data(config.data_path)
validate_schema(data)
print(f"Loaded {len(data)} records")
```

### ❌ WRONG: Monolithic Cell

```python
# Cell: Do everything (75 lines)
data = load_data(...)
# ... 30 lines of processing ...
# ... 25 lines of analysis ...
# ... 20 lines of visualization ...
# ❌ Exceeds 50-line limit, does multiple things
```

## Why This Matters

1. **Readability:** Smaller units are easier to understand at a glance
2. **Testability:** Smaller functions are easier to unit test
3. **Maintainability:** Changes are localized, reducing regression risk
4. **Review Efficiency:** Smaller units are faster to review
5. **Debuggability:** Problems are easier to isolate and fix

## Guideline Violations Require Remediation

**If the agent violates a guideline, update guidelines to close the gap.**

When a violation occurs:
1. The guidelines failed to prevent it
2. The prohibition was not explicit enough
3. The rule may need to be added to AGENTS.md "NEVER" list
4. The rule may need a dedicated section in `000-critical-rules.md`

**After any violation, the agent MUST:**
1. STOP the current task
2. Update guidelines to close the gap
3. Document the fix in a comment on the associated issue — FACTUAL ONLY
4. Wait for user confirmation before resuming