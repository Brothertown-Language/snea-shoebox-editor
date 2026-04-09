# Task: overview

Code size enforcer ensuring functions, notebook cells, and files stay within maintainable size limits.

## Size Limits

| Artifact | Limit | Measurement |
|----------|-------|-------------|
| **Python functions** | 350 words | Excluding docstrings, imports, blank lines |
| **Notebook cells** | 450 words | Including whitespace, excluding cell header |
| **Source files** | 2700 words | Total file, excluding blank lines and comments at file start |

## What Counts Toward Limits

### Word Count vs Line Count

Word counts provide a more accurate measure of LLM context usage and cognitive load than line counts. A dense 30-line function with minimal comments may have more complexity than a verbose 40-line function with extensive documentation. Word counts capture the actual content density.

**Why Words:**
- Better proxy for LLM token consumption
- Reflects actual complexity and information density
- Language-agnostic measure (works across Python, Markdown, configs)
- More granular than line counts

**Conversion Guidance:**
- Average code line has ~8-12 words (including comments)
- Python functions: 40 lines ≈ 350 words
- Notebook cells: 50 lines ≈ 450 words
- Source files: 300 lines ≈ 2700 words

### Functions
- Function body words (code + inline comments)
- Nested functions/classes contribute to outer function's word count
- Multi-line string literals (non-docstrings) count as words

### What Does NOT Count for Functions
- Docstrings (the `"""..."""` block immediately after `def`)
- Import statements outside the function
- Blank lines
- Type hints on their own lines (when using Python 3.10+ syntax)

### Notebook Cells
- All words in the cell source
- Comments
- Whitespace is excluded from word count
- Does NOT include cell metadata or outputs

### Source Files
- Total words in the file
- Excluding: blank lines, module-level docstrings, comments at file start

## ✅ PERMITTED DETECTION METHODS

### Word Count Methods (Preferred)

| Method | Purpose | Example |
|--------|---------|---------|
| `wc -w <file>` | Total file word count | `wc -w src/module.py` |
| `wc -w <<EOF` | Count words in snippet | `wc -w <<EOF` + paste text + `EOF` |
| `ai_bin/py structure --words` | Function word counts | Shows function word counts |
| Manual code review | All sizes | During PR review |
| `git diff --word-diff` | Change size | For modified files |

### Line Count Methods (Legacy)

| Method | Purpose | Example |
|--------|---------|---------|
| `wc -l <file>` | File line count (legacy) | `wc -l src/module.py` |
| `ai_bin/py structure --stats` | Function line counts (legacy) | Shows function line counts |
| Manual code review | All sizes | During PR review |

**Note:** Word counts are the preferred measurement. Line counts are provided for backward compatibility and legacy tools.

## 🚫 FORBIDDEN PATTERNS

| Pattern | Why Forbidden | Limit |
|---------|--------------|-------|
| **Monolithic functions** | Hard to read, test, debug | Functions > 350 words |
| **Monolithic cells** | Notebook cells doing multiple things | Cells > 450 words |
| **Monolithic files** | Files should separate concerns | Files > 2700 words |
| **Deep nesting** | Adds complexity, increases word count | > 3 levels of nesting |
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

# 342 words, UNDER 350-word limit ✅
```

### ✅ CORRECT: Decomposed Function

```python
def process_user_data(user: User) -> ProcessedUser:
    validated = validate_user(user)
    enriched = enrich_user(validated)
    return transform_user(enriched)

def validate_user(user: User) -> ValidatedUser:
    # ... 130 words ...

def enrich_user(user: ValidatedUser) -> EnrichedUser:
    # ... 105 words ...

def transform_user(user: EnrichedUser) -> ProcessedUser:
    # ... 85 words ...
```

### ❌ WRONG: Oversized Function

```python
def process_everything(data: dict) -> dict:
    # ... 850 words of processing ...
    # ❌ Exceeds 350-word limit
```

## Migration from Line Counts to Word Counts

### Why the Change

Line counts were historically used as a simple measure of complexity, but they are a poor proxy for LLM context usage. A 40-line function with verbose docstrings may have fewer actual code words than a dense 30-line function. Word counts better reflect:

1. **LLM context consumption** - More accurate token estimation
2. **Cognitive load** - Actual content density matters more than line breaks
3. **Cross-language consistency** - Works for Python, Markdown, configs alike

### Conversion Factors

| Artifact | Old Limit (Lines) | New Limit (Words) | Factor |
|----------|-------------------|-------------------|--------|
| Python functions | 40 | 350 | ~8.75 words/line |
| Notebook cells | 50 | 450 | ~9 words/line |
| Source files | 300 | 2700 | ~9 words/line |

### Grandfather Policy (Unchanged)

The grandfather policy applies to word counts exactly as it did for line counts:
- Files created before this change are exempt
- Modified grandfathered files must comply for new/modified code
- Refactor grandfathered files during natural refactoring, not as dedicated tasks

### Measurement Tools

Word counts can be measured with:
```bash
# File word count
wc -w src/module.py

# Word count of code snippet
wc -w <<EOF
# paste code here
EOF
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