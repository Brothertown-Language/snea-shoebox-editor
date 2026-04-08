---
name: brainstorming
description: Mandatory pre-spec brainstorming workflow ensuring thorough requirements exploration and alternatives analysis before spec creation.
license: MIT
compatibility: opencode
---

# Skill: brainstorming

## Overview

Mandatory pre-spec brainstorming workflow that ensures thorough requirements exploration and alternatives analysis before any spec creation. This skill is adapted from the NewsRx/opencode-gitbucket-superpowers workflow and enforces systematic thinking before implementation planning.

**Source Attribution:** This skill is adapted from NewsRx/opencode-gitbucket-superpowers workflow (branch: newsrx).

## Persona

You are a Requirements Explorer and Design Thinker. Your focus is ensuring comprehensive brainstorming happens before any spec is created.

## Tasks

| Task | Purpose | Words |
|------|---------|-------|
| `mandatory` | Full brainstorming workflow (default) | ~1200 |

## Invocation

- `/skill brainstorming` - Complete brainstorming workflow
- `/skill brainstorming --task mandatory` - Same as above

## Operating Protocol

1. **Automatic invocation (mandatory):** This skill is auto-invoked by dispatch-table.yaml when:
   - User says `spec` or `plan` or similar planning terms
   - User asks about spec creation workflow
   - User provides feature description for planning
   - DO NOT proceed to spec creation until brainstorming completes

2. **Manual invocation:** User can invoke explicitly:
   - `/skill brainstorming` to start fresh brainstorming session
   - Brainstorming can be restarted if new requirements emerge

3. **Exit conditions:** Brainstorming is COMPLETE when:
   - All five dimensions explored
   - Alternatives documented with tradeoffs
   - User confirms requirements are complete
   - HALT and wait for explicit approval to proceed to spec creation

## Mandatory Brainstorming Dimensions

Before ANY spec creation, explore these five dimensions:

### 1. Problem Understanding
- What is the problem?
- Why does it need solving?
- Who is affected?
- What is the context?
- What constraints exist?

### 2. User Requirements
- What are the user stories?
- What are the acceptance criteria?
- What are the edge cases?
- What are the performance requirements?
- What are the security requirements?

### 3. Alternatives Analysis
- What are the possible solutions?
- What are the tradeoffs of each?
- Which alternative is chosen and why?
- What alternatives were rejected and why?

### 4. Success Criteria
- How will we know it's done?
- What are the testable outcomes?
- How will it be validated?
- What evidence proves completion?

### 5. Impact Assessment
- What else does this affect?
- What are the dependencies?
- What are the risks?
- What is the blast radius?

## Brainstorming Output Format

After exploration, present structured output:

```markdown
## Brainstorming Summary

### Problem Understanding
[Problem statement with context]

### User Requirements
[User stories and acceptance criteria]

### Alternatives Considered
| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Option 1 | ... | ... | ✅/❌ |
| Option 2 | ... | ... | ✅/❌ |

### Success Criteria
1. ✅ [Testable criterion 1]
2. ✅ [Testable criterion 2]

### Impact Assessment
- Affected: [systems, teams, users]
- Dependencies: [external systems]
- Risks: [identified risks]

### Ready for Spec Creation?
- [ ] All dimensions explored
- [ ] Alternatives documented
- [ ] Success criteria defined
- [ ] User confirmed requirements complete
```

## Enforcement Mechanism

**⚠️ CRITICAL: Skills MUST enforce brainstorming — guidelines alone are insufficient.**

### What Skills MUST Check

1. **Before spec creation:**
   - Has brainstorming been invoked?
   - Is brainstorming output present?
   - Are all dimensions explored?

2. **Enforcement matrix:**
   - Brainstorming NOT invoked → INVOKE brainstorming
   - Brainstorming invoked but incomplete → COMPLETE brainstorming
   - Brainstorming complete → PROCEED to spec creation

3. **What does NOT bypass brainstorming:**
   - "skip brainstorming" → NOT allowed
   - "I already know what I want" → Still require brief exploration
   - User impatience → Document partial exploration, ask to proceed

### Enforcement Messages

**Missing brainstorming:**
```
Brainstorming required before spec creation.

This ensures thorough requirements exploration and alternatives analysis.

To invoke: Say '/skill brainstorming' or describe your feature to start brainstorming.
```

**Incomplete brainstorming:**
```
Brainstorming incomplete. The following dimensions need exploration:

- [ ] Problem Understanding
- [ ] User Requirements
- [ ] Alternatives Analysis
- [ ] Success Criteria
- [ ] Impact Assessment

Please complete exploration before proceeding to spec creation.
```

## Integration with Existing Workflow

### Dispatch Order
```
brainstorming (mandatory) → spec creation → approval-gate → git-workflow
```

### GitBucket Platform Adaptations
- Use GitBucket API for issue creation (already supported)
- Use Python client from gitbucket-api skill for issue operations (MCP tools removed)
- Platform detection via `GIT_PLATFORM=gitbucket`

### Approval Gate Integration
- Brainstorming is a PRE-REQUISITE to spec creation
- Approval gate checks for spec existence AFTER brainstorming
- Brainstorming does NOT require approval (exploration phase)

## Cross-References

- Related skills: `approval-gate` (authorization verification), `writing-plans` (plan creation)
- Related guidelines: `140-planning-spec-creation.md` (spec creation workflow), `045-open-questions.md` (open questions protocol)

## Platform Compatibility

- **GitHub:** Not applicable (this repository uses GitBucket)
- **GitBucket:** Use Python client from gitbucket-api skill (MCP tools removed)
- **Platform Detection:** Uses `GIT_PLATFORM` environment variable

## Source Attribution

This skill is adapted from the NewsRx/opencode-gitbucket-superpowers repository (branch: newsrx). The original workflow enforces mandatory brainstorming before any creative work to prevent incomplete specs and missing requirements.

**Key adaptations for OpenCode:**
- Integration with existing approval-gate and git-workflow skills
- GitBucket platform support (not GitHub-specific)
- Dispatch table integration for automatic invocation
- Simplified to five core brainstorming dimensions