# Task: overview

Code size enforcer ensuring functions, notebook cells, and files stay within maintainable size limits.

## Size Limits

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| **Python functions** | 40 lines | Excluding docstrings, imports, blank lines |
| **Notebook cells** | 50 lines | Including whitespace, excluding cell header |
| **Source files** | 300 lines | Total file, excluding blank lines and comments at file start |

## What Counts Toward Limits

### Functions
- Function body lines (code + inline comments)
- Nested functions/classes contribute to outer function's line count
- Multi-line string literals (non-docstrings) count as lines

### What Does NOT Count for Functions
- Docstrings (the `"""..."""` block immediately after `def`)
- Import statements outside the function
- Blank lines
- Type hints on their own lines (when using Python 3.10+ syntax)

### Notebook Cells
- All lines in the cell source
- Comments
- Whitespace
- Does NOT include cell metadata or outputs

### Source Files
- Total lines in the file
- Excluding: blank lines, module-level docstrings, comments at file start

## ✅ PERMITTED DETECTION METHODS

| Method | Purpose | Example |
|--------|---------|---------|
| `wc -l <file>` | File line count | `wc -l src/module.py` |
| `ai_bin/py structure --stats` | Function sizes | Shows function line counts |
| Manual code review | All sizes | During PR review |
| `git diff --stat` | Change size | For modified files |

## 🚫 FORBIDDEN PATTERNS

| Pattern | Why Forbidden | Limit |
|---------|--------------|-------|
| **Monolithic functions** | Hard to read, test, debug | Functions > 40 lines |
| **Monolithic cells** | Notebook cells doing multiple things | Cells > 50 lines |
| **Monolithic files** | Files should separate concerns | Files > 300 lines |
| **Deep nesting** | Adds complexity, increases line count | > 3 levels of nesting |
| **God classes/files** | Single file doing too much | Files importing many unrelated modules |
| **"Helper" function blocks** | Multiple responsibilities hidden in one function | Any function with >1 distinct responsibility |

## Grandfather Policy

**Existing files are EXEMPT from size limits.**

### What is Grandfathered
1. **No retroactive errors** - Existing files exceeding limits are NOT flagged
2. **Modified files must comply** - When modifying a grandfathered file, new/modified code must comply
3. **Refactor encouraged** - Fix grandfathered files during natural refactoring, not as dedicated task

### When Limits Apply

| Scenario | Enforcement |
|----------|-------------|
| **New file created** | MUST comply with all limits |
| **Modified grandfathered file** | Only modified code checked |
| **Renamed file** | Retains grandfather status |
| **File moved to new location** | Retains grandfather status |
| **Deleted and recreated** | Treated as NEW file |

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
4. **Re-check:** Verify new structure meets limits; run tests if applicable
5. **Document** significant changes in commit/PR message

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

## Why This Matters

1. **Readability:** Smaller units are easier to understand at a glance
2. **Testability:** Smaller functions are easier to unit test
3. **Maintainability:** Changes are localized, reducing regression risk
4. **Review Efficiency:** Smaller units are faster to review
5. **Debuggability:** Problems are easier to isolate and fix

## Cross-References

- `080-code-standards.md` - Design Principles — ENFORCED UNIVERSALLY
- `061-notebook-rules.md` - Code Standards for Notebooks
- `000-critical-rules.md` - General violation enforcement