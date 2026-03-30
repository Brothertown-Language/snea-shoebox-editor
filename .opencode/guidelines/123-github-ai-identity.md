# GitHub Workflow: AI Identity in Comments

**See `.opencode/skills/github-comments/SKILL.md` for complete comment protocol.**

## 🤖 MANDATORY: AI Identity for AI-Generated Content

ALL AI-GENERATED comments on issues and PRs MUST end with AI byline:

```
🤖 *AI: <AgentBrand> on behalf of <HumanName>* <ContextEmoji> <TypeText>
```

**⚠️ Clarification: Copied content does NOT get AI byline.**

Content copied from ANY source (Stack Overflow, documentation, external sources) retains original copyright. AI bylines apply ONLY to genuinely AI-generated content.

**See `088-ai-authorship.md` for complete attribution rules.**

---

## Required Byline Format Table (MANDATORY)

**ALL bylines AND issue body signatures MUST include "on behalf of <HumanName>".**

**ALL bylines AND issue body signatures MUST include "on behalf of <HumanName>".**

| Type | Required Format |
|------|-----------------|
| Progress (task completion) | `🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✅ Task Complete: <task-name>` |
| Body update | `🤖 *AI: <AgentBrand> on behalf of <HumanName>* 📝 Updated: <reason>` |
| Spec alteration | `🤖 *AI: <AgentBrand> on behalf of <HumanName>* 📝 Spec altered: <summary>` |
| Closure | `🤖 *AI: <AgentBrand> on behalf of <HumanName>* ❌ Closed - <reason>` |
| General response | `🤖 *AI: <AgentBrand> on behalf of <HumanName>* 🤖` |
| Issue body signature | `<content>\n\n🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✨ Created` |

### Signature for Issue/PR Bodies (NOT comments)

```markdown
<issue content>

🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✨ Created
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