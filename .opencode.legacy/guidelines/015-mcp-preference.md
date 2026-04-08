# MCP Tool MANDATORY Usage

> **See `mcp-tool-usage` skill for complete tool preference tables, tier boundaries, and fallback hierarchy.**

## 1. MANDATORY: PyCharm MCP for ALL File Access

This guideline is ENFORCED at the highest priority level. PyCharm MCP tools are the ONLY permitted mechanism for accessing ANY files when MCP is available.

### Scope Definition

**ALL files**: Every file and directory in the project, including `./tmp/`, notebooks, configs, and temporary outputs. There are NO exceptions.

## Three-Tier Boundary System

For complete tier boundaries and tool selection matrix, **see `mcp-tool-usage` skill**.

Quick reference:
- **Tier 1 (MANDATORY)**: Always use MCP tools when available - no exceptions
- **Tier 2 (ASK FIRST)**: Use direct tools only with explicit acknowledgment and `# FALLBACK: MCP unavailable` comment
- **Tier 3 (PROHIBITED)**: Never bypass MCP tools when available

## PR Creation Skill Enforcement (MANDATORY)

**⚠️ CRITICAL VIOLATION: Bypassing `git-workflow` skill for PR creation.**

When user says `"create a PR"`, `"pr"`, `"push and create PR"`, or ANY PR-related command:

| Trigger | Required Action | PROHIBITED |
|---------|----------------|------------|
| `"create a PR"` | Invoke `/skill git-workflow --task pr-creation` | Manual git commands, `github_create_pull_request` directly |
| `"pr"` | Invoke `/skill git-workflow --task pr-creation` | Manual squash/push/create PR |
| `"push and create PR"` | Invoke `/skill git-workflow --task pr-creation` | `git push && github_create_pull_request` |

**Why enforcement is mandatory:**

The `git-workflow` skill handles:
1. Squash verification (commits must be squashed to single commit)
2. Branch state verification (clean working tree)
3. Co-author trailer verification
4. Proper PR body format
5. Compare URL generation workflow

**Direct `github_create_pull_request` bypasses ALL of these.**

### 🚫 PROHIBITED

| Bypass Method | Why It's Wrong |
|---------------|----------------|
| `github_create_pull_request` directly | Skips squash verification, co-author trailers, PR body format |
| Manual `git push && gh pr create` | Skips skill enforcement, workflow checks |
| Manual squash without skill | May miss co-author trailers, wrong commit format |

### ✅ REQUIRED

| Situation | Correct Action |
|-----------|---------------|
| User says "create a PR" | Invoke `/skill git-workflow --task pr-creation` |
| User says "pr" | Invoke `/skill git-workflow --task pr-creation` |
| User says "push and create PR" | Invoke `/skill git-workflow --task pr-creation` |
| After implementation completes | Invoke `/skill git-workflow --task review-prep` (automatic) |

**See `git-workflow` skill for complete PR creation workflow.**

---

## Srclight MCP Server (Code Indexing)

Key points:
- Srclight indexes Python code ONLY (not markdown/docs)
- Use srclight PREFERENTIALLY for Python semantic analysis
- Use PyCharm MCP for file operations and non-Python files
- Use `ai_bin/guidelines` for guideline search

### Setup

```bash
./scripts/setup_srclight.sh
```

### Troubleshooting

| Error | Solution |
|-------|----------|
| "Index not found" | Run `./scripts/setup_srclight.sh` |
| "Cannot reach Ollama" | Start Ollama: `ollama serve` |
| "Model not found" | Pull model: `ollama pull qwen3-embedding` |
| "No semantic results" | Reindex: `uvx srclight index --embed qwen3-embedding` |