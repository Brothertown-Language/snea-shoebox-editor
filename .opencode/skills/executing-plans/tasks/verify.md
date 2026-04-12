# Task: verify

Run verification for the current step, ensuring evidence is collected and quality gates are met.

## Verification Process

### 1. Standard Verifications

Run appropriate verifications based on step type:

**Code verification:**
```bash
uv run ruff check --fix src/ test/
uv run ruff format src/ test/
uv run pyright src/
```

**Test verification:**
```bash
uv run pytest test/test_file.py::test_function_name
```

**File verification:**
```bash
ls -la path/to/file
head -20 path/to/file
```

### 2. Custom Verifications

From plan's verification methods:

```markdown
- ☐ Verification: Run unit tests and check coverage
  → Evidence: `pytest --cov=src/module`
```

### 3. Collect Evidence

| Evidence Type | Collection Method |
|---------------|-------------------|
| Code changes | `git diff` output |
| Test results | Test pass/fail output |
| Lint check | `ruff check` output |
| Type check | `pyright` output |
| File creation | Path and content hash |
| API response | Status code and body |

### 4. Mark Step Complete

- All evidence collected → Mark step as ☑
- Evidence incomplete → HALT and require evidence
- Verification failed → Report failure and require fix

## Enforcement

- Evidence missing for task → REQUIRE evidence before marking complete
- Verification not run → RUN verification before marking complete
- Verification failed → FIX issues before proceeding