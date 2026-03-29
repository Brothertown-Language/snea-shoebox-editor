# GitHub Workflow: AI Identity in Comments

**See `.opencode/skills/github-comments/SKILL.md` for complete comment protocol.**

## 🤖 MANDATORY: AI Identity Prefix

ALL comments on issues and PRs MUST be prefixed with AI identity:

```
AI: <AgentName> <ModelID> on behalf of <HumanName> 🤖 <response>
```

**Dynamic Components:**
- `<AgentName>`: AI's actual name (e.g., `OpenCode Desktop`, `OpenCode`)
- `<ModelID>`: Model identifier with provider (e.g., `ollama-cloud/glm-5`)
- `<HumanName>`: From `git config user.name` (fallback to `$USER`)

**⚠️ CRITICAL: NEVER copy example values literally. Detect your own identity at runtime.**

### Signature for Issue/PR Bodies (NOT comments)

```markdown
*Created by AI: <AgentName> <ModelID>*
```

Place at END of issue bodies and PR descriptions, preceded by blank line.

---

## 🚫 CRITICAL VIOLATIONS (Zero Tolerance)

| Violation | Consequence |
|-----------|--------------|
| Missing progress comments after task completion | CRITICAL — implementation incomplete |
| Ignoring user comments without posting response | CRITICAL — user cannot see your reasoning |
| Closing issue without explanation comment | CRITICAL — no audit trail |
| Editing issue body to add "CLOSED" text | CRITICAL — destroys history |
| Proceeding to next task without posting comment | CRITICAL — breaks workflow |

**See `github-comments` skill for:**
- Comment type decision table
- Progress comment format and timing
- Issue body update rules
- Closure comment format
- When NOT to comment

---

## Integration with Guidelines

| Guideline | Section |
|-----------|---------|
| `120-github-issue-first.md` | Issue workflow, sub-issues |
| `000-critical-rules.md` | Critical violation enforcement |
| `github-comments` skill | Complete comment protocol |

---