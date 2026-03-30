# AI Authorship Attribution

## Scope

This guideline governs AI authorship attribution for content CREATED by AI agents.

**Applies to:**
- Code written by AI (implementation, refactoring)
- Documentation written by AI (guidelines, SKILL.md files, README)
- Comments authored by AI (GitHub issue comments, PR comments)
- Specs written by AI (GitHub issue bodies)
- Commit messages written by AI

**Does NOT apply to:**
- Copy-pasted content (retains original source copyright)
- Minimally edited human content (human remains primary author)
- Quoted/cited content (attribution to original source)

---

## Mandatory AI Co-Authorship for AI-Generated Content

### When AI Co-Authorship is REQUIRED

**MANDATORY for all AI-Generated Content:**

1. **Commit trailers** — All commits from AI sessions MUST include co-author trailers
2. **GitHub issue comments** — All AI-generated comments MUST end with AI byline
3. **GitHub issue bodies** — Specs created by AI MUST end with creation signature
4. **PR descriptions** — PR descriptions written by AI MUST end with creation signature
5. **Guideline files** — New guidelines authored by AI MUST include attribution
6. **SKILL.md files** — Skills authored by AI MUST include attribution

### AI Co-Authorship Format

**Commits:**
```
Co-authored-by: <AI-Name> (<model-id>) <ai-email>
Co-authored-by: <Human-Name> <human-email>
```

**Issue Comments/PR Comments:**
```
<content>

🤖 *AI: <AgentBrand> on behalf of <HumanName>* <ContextEmoji> <TypeText>
```

**Issue/PR Bodies (Creation):**
```
<content>

🤖 *AI: <AgentBrand> on behalf of <HumanName>* ✨ Created
```

**Guideline/Skill Files:**
```markdown
<!--
AI-Authored: <AI-Name> (<model-id>)
Created: <YYYY-MM-DD>
On-Behalf-Of: <Human-Name>
-->
```

---

## When AI Co-Authorship is NOT Applicable

### Copy-Pasted Content Rule

**CRITICAL CLARIFICATION:** Content copied from ANY source does NOT receive AI co-authorship.

The original source holds the copyright. AI is merely reproducing existing content.

| Source | Correct Attribution |
|--------|---------------------|
| Stack Overflow answer | Link to original answer in comment, NO AI co-authorship |
| Documentation from another project | Quote with citation, NO AI co-authorship |
| Code from tutorial/blog | Cite source in comment, NO AI co-authorship |
| AI-generated original code | AI co-authorship REQUIRED |
| AI-modified existing human code | AI co-authorship for modification, human as primary author |

### Examples

**❌ WRONG: Copying Stack Overflow**
```python
# AI copies Stack Overflow answer verbatim
def parse_json(data):
    return json.loads(data)
# AI should NOT add co-authorship - Stack Overflow holds copyright
```

**✅ CORRECT: Original AI Code**
```python
# AI writes original implementation
def parse_json_safe(data: str) -> dict:
    """Parse JSON with error handling."""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}
# AI MUST add co-authorship in commit
```

**✅ CORRECT: AI Modifying Human Code**
```python
# Human wrote original function
# AI adds type hints and error handling
# Commit: "Add type hints and error handling to parse_json"
# Co-authored-by: AI-Name (model-id) <ai-email>
# Co-authored-by: Human-Name <human-email>
```

---

## Determination Rules

### Apply this decision tree:

```
Is content AI-generated?
├─ YES → Is it copied from another source?
│        ├─ YES → NO AI co-authorship (cite original source)
│        └─ NO → AI co-authorship REQUIRED
└─ NO → Human author only
```

### Edge Cases

| Scenario | Attribution |
|----------|-------------|
| AI paraphrases Stack Overflow | Cite SO, optional AI co-authorship for paraphrase creativity |
| AI writes code based on SO concepts | AI co-authorship (concepts transformed to original implementation) |
| AI fixes typo in human code | Minimal change - no co-authorship needed |
| AI refactors human code significantly | AI co-authorship REQUIRED |
| AI generates docstring for human code | AI co-authorship for docstring portion |
| AI translates code to different language | AI co-authorship (creative transformation) |

---

## Integration with Existing Workflows

### Git Commit Workflow (111-git-commit-workflow.md)

When AI generates implementation:
1. AI determines its own identity dynamically
2. AI uses cached human identity from session init
3. Commit includes BOTH co-author trailers

### GitHub Comments (github-comments/SKILL.md)

All AI-generated comments must include byline:
- Progress comments end with byline
- Body updates end with byline
- Issue/PR creation ends with creation signature

### Spec Creation (140-planning-spec-creation.md)

Specs authored by AI:
- Issue body ends with creation signature
- Any edits to spec body end with update signature

---

## Why This Matters

1. **Transparency:** Users can distinguish AI-generated content from human content
2. **Accountability:** Clear attribution for debugging and review
3. **Legal:** Proper copyright attribution for AI-assisted work
4. **Context:** Future readers understand how content was created

---

## Related Guidelines

| Guideline | Section |
|-----------|---------|
| `000-critical-rules.md` | Critical Violation sections |
| `111-git-commit-workflow.md` | Co-Author Trailer Workflow |
| `123-github-ai-identity.md` | AI identity format |
| `github-comments/SKILL.md` | Comment byline format |
| `git-workflow/SKILL.md` | Squash commit trailers |

---

*Content attribution ensures intellectual property and creative work are properly credited.*