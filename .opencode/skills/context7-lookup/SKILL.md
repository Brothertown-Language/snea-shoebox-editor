---
name: context7-lookup
description: Fetch up-to-date library documentation using Context7 MCP. Avoid hallucinated APIs and outdated code examples.
license: MIT
compatibility: opencode
---

# Context7 Lookup

Context7 is an MCP server that injects up-to-date, version-specific documentation directly into your context. Use it to avoid hallucinated APIs and outdated code examples.

## What This Skill Is

This skill teaches you **how to use** Context7 MCP tools effectively. It does not replace Context7 — you must have Context7 MCP configured in OpenCode.

## When to Use Context7

- Before implementing code with external libraries/frameworks
- When unsure about current API signatures
- For fast-moving libraries: Next.js, React, Vue, Tailwind, Zod, etc.
- When the user asks about a specific library version
- When you see "use context7" in a prompt

## Prerequisites: Configure Context7 MCP in OpenCode

Add to your `opencode.json`:

### Remote Server Connection (Recommended)

```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_API_KEY"
      },
      "enabled": true
    }
  }
}
```

### Local Server Connection

```json
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"],
      "enabled": true
    }
  }
}
```

Get a free API key at [context7.com/dashboard](https://context7.com/dashboard) for higher rate limits.

## Available Tools

Once Context7 MCP is configured, you have access to two tools:

### 1. `resolve-library-id`

Resolves a library name to a Context7-compatible ID.

**Always call this first** unless the user provides an explicit ID like `/vercel/next.js`.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `libraryName` | Yes | Name of the library to search for |

```
Input: "next.js"
Output: "/vercel/next.js" (with version info)
```

### 2. `get-library-docs`

Fetches documentation for a library.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `context7CompatibleLibraryID` | Yes | Exact ID from `resolve-library-id` (e.g., `/vercel/next.js`) |
| `topic` | No | Focus on specific topic (e.g., "routing", "hooks") |
| `tokens` | No | Max tokens to return (default: 5000, min: 1000) |

## Usage Pattern

```
1. User asks about implementing something with a library
2. Call `resolve-library-id` with the library name
3. Call `get-library-docs` with the resolved ID and relevant topic
4. Use the returned documentation to provide accurate code
```

## Examples

### Example 1: Next.js Middleware

**User**: "Create a Next.js middleware for auth"

**Agent**:
1. `resolve-library-id("next.js")` → `/vercel/next.js`
2. `get-library-docs("/vercel/next.js", topic="middleware")` → Current middleware docs
3. Provide code based on actual current API

### Example 2: Specific Topic

**User**: "How do I invalidate queries in TanStack Query?"

**Agent**:
1. `resolve-library-id("tanstack query")` → `/tanstack/query`
2. `get-library-docs("/tanstack/query", topic="invalidation")` → Current invalidation patterns
3. Provide accurate `queryClient.invalidateQueries()` usage

### Example 3: Known Library ID

**User**: "Implement auth with Supabase. use library /supabase/supabase"

**Agent**:
1. Skip `resolve-library-id` (ID already provided)
2. `get-library-docs("/supabase/supabase", topic="authentication")`
3. Provide code based on current Supabase auth API

## Tips

- **Be specific with topics**: `topic="authentication"` returns more relevant docs than a general query
- **Use slash syntax**: If you know the library ID, use `/org/project` directly
- **Trust the docs**: Prefer Context7 results over training data for API signatures
- **Don't over-fetch**: If you've already fetched docs for a library in this conversation, reuse them

## Supported Libraries

Context7 supports 1000+ libraries. Check [context7.com](https://context7.com) for the full list.

Popular ones include: React, Next.js, Vue, Nuxt, Svelte, Angular, Express, Fastify, NestJS, Django, FastAPI, Prisma, Drizzle, Tailwind, Zod, TanStack Query, and many more.