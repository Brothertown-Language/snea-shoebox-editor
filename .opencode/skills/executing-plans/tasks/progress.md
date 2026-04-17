# Task: progress

Report current progress and track execution state.

## Progress Reporting

### Standard Verifications

1. **Code verification:**
   ```bash
   uv run ruff check --fix src/ test/
   uv run ruff format src/ test/
   uv run pyright src/
   ```

2. **Test verification:**
   ```bash
   uv run pytest test/test_file.py::test_function_name
   ```

3. **File verification:**
   ```bash
   ls -la path/to/file
   head -20 path/to/file
   ```

### Custom Verifications

From plan's verification methods:

```markdown
- ☐ Verification: Run unit tests and check coverage
  → Evidence: `pytest --cov=src/module`
```

### Progress Comment Format

```markdown
**Progress:** Step N of M complete

**Evidence:**
- [Task 1]: [Evidence]
- [Task 2]: [Evidence]
- Verification: [Result]

**Next:** Step N+1 - [Next concern]

---
🤖 <AgentName> (<ModelId>) 🔄 working
```

## Multi-Step Execution Example

```markdown
**Plan Issue #123:**

## Step 1: Database Schema
- ☑ Create users table
  Evidence: `users_table_created.sql`
- ☑ Add authentication fields
  Evidence: `auth_fields_added.sql`
- ☑ Write migration script
  Evidence: `migration_001.py`

**Verification:** Run migration in test environment
**Evidence:** Migration test passed

---
🤖 <AgentName> (<ModelId>) ✅ completed

## Step 2: API Endpoints
- ☐ Create login endpoint
- ☐ Create logout endpoint
- ☐ Create refresh endpoint

---
🤖 <AgentName> (<ModelId>) 🔄 working
```