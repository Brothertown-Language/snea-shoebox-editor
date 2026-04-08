# Fragment: Commit Workflow

**Commit Policy (User-Initiated Only)**

### 🚫 NEVER DO

- **NEVER run `git restore`, `git checkout`, `git reset`, `git clean`** — these discard or modify working tree state
- **NEVER discard uncommitted changes** — even if they appear to be formatting-only, unintended, or erroneous
- **Analysis commands are read-only** — no modifications to working tree
- **NEVER commit or merge without direct instruction** — commits may ONLY be initiated by the developer
- **NEVER create a PR without direct instruction** — PRs require explicit developer request

### STOP ASKING FOR COMMITS AND PRS

The developer will say "commit" or "create a PR" when they want git operations. Until then, do nothing:

1. **After completing implementation**: Report completion concisely, then STOP and wait silently
2. **Do NOT ask**: "Commit?", "Ready to commit?", "Should I commit?", "Ready for a PR?", "Create a PR?", "Push and PR?"
3. **Do NOT automatically create PRs**: PR creation requires the same explicit instruction as commits

### ✅ ALWAYS DO

- **Include co-author trailers for both AI and human collaborator** — every implementation commit MUST include TWO trailers
- **Re-run discovery** (`git status`, `git diff`) before any commit workflow
- **If `pyproject.toml` changed, include `uv.lock`** — this is an application/CI repo
- **Use dynamic AI identity** — the AI knows its own name and email
- **Use cached human identity** — from session start values (`DEV_NAME`, `DEV_EMAIL`)

<!--
Fragment ID: commit-workflow
Estimated tokens: 225
Type: text-block
Sync status: synchronized
-->