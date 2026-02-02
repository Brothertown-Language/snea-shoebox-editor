---
author: Human
contributor: AI
status: active
date: 2026-02-01
---
<!-- Copyright (c) 2026 Brothertown Language -->

# Security: Dependencies and Supply Chain

## Dependency management

### Version pinning
**ALWAYS pin versions** in `pyproject.toml` for production dependencies.

Example:
```toml
[project.dependencies]
streamlit = "==1.28.0"  # Production: exact version
httpx = "==0.25.0"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",  # Dev: allow compatible updates
]
```

### Before adding new packages

**Review dependencies** before adding:
1. **Known vulnerabilities** - Check CVE databases, GitHub security advisories
2. **Maintenance status** - Last update, active maintainers, issue response time
3. **License compatibility** - Verify license works with private repository
4. **Dependency tree** - Review transitive dependencies for security issues

### Regular updates

**Update regularly** to get security patches:
```bash
# Check for outdated packages
uv pip list --outdated

# Update specific package
uv pip install --upgrade package-name

# Update all dev dependencies
uv pip install --upgrade -e ".[dev]"
```

**After updates:**
1. Run full test suite
2. Test critical user flows manually
3. Review changelog for breaking changes
4. Update pinned versions in pyproject.toml

## Third-party code

### Verify sources
**Before copying code** from external sources:
1. Verify the source is reputable (official docs, well-known projects)
2. Understand what the code does - never blindly copy
3. Adapt to project style and standards
4. Add error handling and type annotations

### Check licenses
**License compatibility:**
- Private repository allows most licenses
- Be aware of copyleft licenses (GPL, AGPL) - may require disclosure
- Prefer permissive licenses (MIT, Apache, BSD)
- **Document attribution** if required by license

### Security review
**Review for security issues:**
- Input validation and sanitization
- SQL injection vulnerabilities
- Command injection risks
- Path traversal issues
- Hardcoded credentials or secrets
- Unsafe deserialization

### Attribution
**If license requires attribution:**
1. Add comment in code with source URL and license
2. Update LICENSE file if needed
3. Document in README or CONTRIBUTING.md

Example:
```python
# Adapted from: https://example.com/source
# License: MIT
# Copyright (c) 2024 Original Author
def adapted_function():
    pass
```

## Supply chain security

### Package verification
- Use `uv` package manager (built-in verification)
- Verify package signatures when available
- Check package maintainer reputation
- Review package source code for critical dependencies

### Dependency scanning
- Monitor security advisories for used packages
- Use GitHub Dependabot (if enabled)
- Review security alerts promptly
- Update vulnerable packages immediately

### Minimal dependencies
- Only add dependencies when truly needed
- Prefer standard library when possible
- Evaluate alternatives with fewer transitive dependencies
- Remove unused dependencies regularly
