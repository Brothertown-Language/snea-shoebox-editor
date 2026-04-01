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

## Srclight MCP Server (Code Indexing)

**For detailed tool selection guidance, see `016-srclight-preference.md`.**

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