# Secret Detection — Semaphore Approach

This project uses a **semaphore-based** secret detection system. The pre-commit hook for `detect-secrets` is **opt-in** — it only runs when a `.secrets.baseline` file exists in the project root.

## How It Works

### Pre-commit Hook (`.opencode/tools/detect-secrets-wrapper.sh`)

The wrapper script implements the semaphore pattern:

    test -f .secrets.baseline || exit 0
    detect-secrets-hook --baseline .secrets.baseline "$@"

- **`.secrets.baseline` exists** → runs `detect-secrets-hook` against staged files
- **`.secrets.baseline` missing** → exits immediately (no scanning)

The `.secrets.baseline` file is gitignored — each developer opts in locally.

### Session-init Guard (`.opencode/tools/session-init`)

The `_check_credential_files_gitignored()` function runs on every session startup and warns if credential files exist but are not gitignored:

- `.env`
- `.streamlit/secrets.toml`
- `.streamlit/secrets.toml.production`

### `.gitignore` Coverage

16 credential file patterns are tracked in `.gitignore` including `.env.*`, `secrets.toml`, `*.pem`, `*.key`, `service-account*.json`, etc.

## Opting In

1. Install detect-secrets:
   ```
   pip install detect-secrets
   ```

2. Create the baseline (this enables the hook):
   ```
   detect-secrets scan --exclude-files '^(tests/|\.opencode/)' > .secrets.baseline
   ```

3. Verify the hook is active:
   ```
   pre-commit install
   ```

## Pre-commit Config (`.pre-commit-config.yaml`)

The hook is configured as a local hook:

    - repo: local
      hooks:
        - id: detect-secrets
          name: detect-secrets
          entry: .opencode/tools/detect-secrets-wrapper.sh
          language: script
          stages: [pre-commit]

## Related

- Credential leakage remediation: `docs/security/credential-leakage-remediation.md`
- Credential guard tests: `tests/test_credential_guard.py`
- Session-init script: `.opencode/tools/session-init`