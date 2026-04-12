# Task: collect

Collect evidence for incomplete success criteria when verification identifies gaps.

## Process

For each missing criterion:

### 1. Identify What Evidence Is Needed

| Need | Collection Method |
|------|-------------------|
| Test output? | Run test, capture output |
| File creation? | Show file path and content hash |
| Code change? | Show `git diff` output |
| API response? | Show status code and body |

### 2. Collect Evidence

- Run required verification commands
- Store output in `./tmp/` or post to issue
- Verify evidence is complete and accurate

### 3. Update Verification Status

- Mark criterion as verified
- Post evidence to issue
- Proceed to next missing criterion

## Common Verification Commands

### Code Changes

```bash
# Show changed files
git diff --name-only

# Show changed content
git diff

# Show staged changes
git diff --cached
```

### Test Verification

```bash
# Run specific test
uv run pytest test/test_file.py::test_function_name

# Run with coverage
uv run pytest --cov=src/module test/
```

### Code Quality

```bash
# Lint check
uv run ruff check --fix src/ test/

# Format check
uv run ruff format src/ test/

# Type check
uv run pyright src/
```

### File Verification

```bash
# File exists
ls -la path/to/file

# File content preview
head -20 path/to/file

# File hash
md5sum path/to/file
```

## Evidence Storage

- Post as comment to plan issue (primary)
- Store artifacts in `./tmp/` (secondary for large outputs)
- Link evidence to plan via comments

## Integration

### Dispatch Order

```
executing-plans → verification-before-completion → (completion claim allowed)
```

### GitBucket Platform Adaptations

- Post verification reports to plan issue
- Store large artifacts in `./tmp/`
- Link evidence to plan via comments

### Git-Workflow Integration

- Verification happens BEFORE branch push
- Evidence collected during execution phase
- PR created only after all verification passes