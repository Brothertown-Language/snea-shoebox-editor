# Credential Leakage Remediation Guide

This guide covers how to detect, rotate, and purge secrets that have been accidentally committed to git history.

## Detection

### Local Detection (Before Push)

The project includes multiple guard mechanisms:

1. **`.gitignore` patterns** — Prevents credential files from being tracked. See `tests/test_credential_guard.py` for the full list of protected patterns.

2. **`detect-secrets` pre-commit hook** — Scans staged files for potential secrets. Automatically skipped unless `.secrets.baseline` exists in the project root. To enable:
   ```bash
   pip install detect-secrets
   detect-secrets scan --exclude-files '^(tests/|\.opencode/)' > .secrets.baseline
   pre-commit install
   ```

3. **`session-init` guard** — Checks `.env`, `.streamlit/secrets.toml`, and `.streamlit/secrets.toml.production` on every session startup. Reports unprotected files as warnings.

### Repository-Level Detection

Run a full repository scan:
```bash
detect-secrets scan --exclude-files '^(tests/|\.opencode/)' > .secrets.baseline
detect-secrets audit .secrets.baseline
```

## Rotation

If a secret has been pushed to a remote repository, **rotate it immediately**, regardless of purge status.

### Streamlit Secrets

1. Generate new secrets in Streamlit Cloud
2. Update `.streamlit/secrets.toml` locally
3. Verify `.streamlit/secrets.toml` is gitignored

### SSH Keys

1. Remove the compromised key from the SSH agent: `ssh-add -d ~/.ssh/id_rsa`
2. Generate a new key: `ssh-keygen -t ed25519 -C "your@email.com"`
3. Add the new public key to GitHub/GitBucket

### Service Account Keys

1. Disable the compromised key in the cloud provider console
2. Create a new service account key
3. Update any CI/CD or deployment configurations

## Purging Secrets from Git History

### Local-Only Commit (Not Pushed)

If the secret was committed locally but not yet pushed:

```bash
# Remove the file from the most recent commit
git rm --cached <secret-file>
git commit --amend

# Or reset the commit entirely
git reset HEAD~1
```

### Pushed Commit (Remote History Exists)

**⚠️ Warning:** This rewrites history. Coordinate with all collaborators before proceeding.

#### Using `git filter-repo` (Recommended)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove a specific file from all history
git filter-repo --invert-paths --path <secret-file>

# Or remove a specific secret string
git filter-repo --replace-text <(echo 'SECRET_STRING==>REDACTED')

# Force push the cleaned history
git push --force-with-lease origin dev
```

#### After Purging

1. All collaborators must re-clone the repository
2. Verify the secret no longer appears in any commit: `git log --all --full-history -- <secret-file>`
3. Notify collaborators that old clones are compromised — they must discard them
4. Update any forked repositories as well

### GitHub-Specific Aftermath

If the secret was pushed to GitHub:
1. Rotate the secret immediately (higher priority than purging)
2. Use [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning) to detect leaked tokens
3. Contact GitHub Support if a GitHub token was exposed — they can help invalidate cached copies

## Prevention Checklist

- [ ] `.gitignore` includes all credential file patterns
- [ ] `.secrets.baseline` exists and `detect-secrets` pre-commit hook is enabled
- [ ] `session-init` guard reports no unprotected credential files
- [ ] No secrets in git history: `git log --all --full-history -- '*.env' '*.key' '*.pem' 'secrets.toml*' 'service-account.json'`
- [ ] Pre-commit hooks are installed: `pre-commit install`