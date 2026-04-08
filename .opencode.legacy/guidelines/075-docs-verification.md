# Mandatory Live Documentation Verification

## Zero Tolerance Rule

**🚫 CRITICAL VIOLATION: Implementing code without verifying against live documentation.**

Before writing ANY implementation code, verify against authoritative sources:

1. API signatures and parameters
2. Environment variable names
3. Configuration file formats
4. Function signatures and type hints
5. Library/framework version requirements

## Rule

**ALWAYS verify against live documentation before implementing.**

### What Must Be Verified

| Item | Sources |
|------|---------|
| **API signatures** | Official docs, source code, type hints |
| **Environment variables** | Documentation, `.env.example`, config files |
| **Function parameters** | Type hints, docstrings, source code |
| **Library usage** | Official docs, migration guides |
| **Configuration formats** | Schema definitions, example configs |

### Verification Sources (Priority Order)

1. **Official documentation** (highest priority)
   - Library/framework official docs
   - API reference documentation
   
2. **Source code and type hints**
   - `pycharm_get_symbol_info` or `srclight_get_signature`
   - Inline type hints and docstrings
   
3. **Example files in codebase**
   - Existing usage examples in `src/`
   - Test files showing correct API usage
   
4. **Configuration files**
   - `.env.example`, `pyproject.toml`, config schemas

### What COUNTS as Verification

✅ **Verification Required:**
- Calling `srclight_get_signature` to check function parameters
- Reading source code to confirm API usage
- Checking official documentation URLs
- Reviewing type hints in IDE or via MCP tools
- Examining existing working code as reference

❌ **NOT Verification:**
- Assuming based on similar libraries
- Relying on memory from previous implementations
- Guessing parameter names
- Using outdated blog posts or tutorials

### Prohibited Patterns

```python
# ❌ WRONG: Assuming parameter name
result = some_api.call(name="foo")  # Did you verify 'name' is correct?

# ✅ CORRECT: Verify first
# Checked official docs: parameter is 'query', not 'name'
result = some_api.call(query="foo")
```

```python
# ❌ WRONG: Assuming environment variable
host = os.environ["OLLAMA_HOST"]  # Did you verify the correct name?

# ✅ CORRECT: Verify from config
# Checked .env.example and docs: correct name is OLLAMA_API_URL
host = os.environ["OLLAMA_API_URL"]
```

### Code Review Checklist

When reviewing code, verify:

- [ ] API calls match official documentation
- [ ] Environment variable names match configuration files
- [ ] Function parameters match type signatures
- [ ] Library usage matches current version docs
- [ ] Configuration formats match schema definitions

## Examples

### Example 1: Pydantic Model Field Validator

**❌ WRONG (Assumption-Based):**
```
from pydantic import BaseModel, validator

class User(BaseModel):
    name: str
    
    @validator("name")
    def validate_name(cls, v):
        return v.strip()
```

**Why Wrong:** `@validator` was deprecated in Pydantic v2. Assumed without checking.

**✅ CORRECT (Verified):**
```
# Checked Pydantic v2 docs: use @field_validator with mode parameter
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return v.strip()
```

### Example 2: Environment Variable

**❌ WRONG (Assumption-Based):**
```
database_url = os.environ["DATABASE_URL"]
```

**✅ CORRECT (Verified):**
```
# Checked .env.example and config documentation
database_url = os.environ.get("DATABASE_URL", "sqlite:///./default.db")
```

## Integration with Engineering Approach

This verification is MANDATORY before and during implementation. See `engineering-approach` skill for the pre-implementation and during-implementation checklists.

## Related Guidelines

- `000-critical-rules.md` — Zero tolerance enforcement
- `080-code-standards.md` — Code quality standards
- `130-authority-source.md` — Code as authoritative source